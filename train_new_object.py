import os
import cv2
import numpy as np
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

class NewObjectDetector:
    def __init__(self, dataset_path, new_class_name):
        self.dataset_path = dataset_path
        self.new_class_name = new_class_name
        self.classes = ["background", "person", new_class_name]  # Thêm class mới
        self.num_classes = len(self.classes)
        
    def parse_annotation(self, xml_path):
        """Parse XML annotation file"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        filename = root.find('filename').text
        size = root.find('size')
        width = int(size.find('width').text)
        height = int(size.find('height').text)
        
        objects = []
        for obj in root.findall('object'):
            name = obj.find('name').text
            bndbox = obj.find('bndbox')
            xmin = int(bndbox.find('xmin').text)
            ymin = int(bndbox.find('ymin').text)
            xmax = int(bndbox.find('xmax').text)
            ymax = int(bndbox.find('ymax').text)
            
            objects.append({
                'name': name,
                'bbox': [xmin, ymin, xmax, ymax]
            })
            
        return {
            'filename': filename,
            'width': width,
            'height': height,
            'objects': objects
        }
    
    def load_dataset(self):
        """Load và preprocess dataset"""
        images = []
        labels = []
        
        images_path = os.path.join(self.dataset_path, 'images')
        annotations_path = os.path.join(self.dataset_path, 'annotations')
        
        for xml_file in os.listdir(annotations_path):
            if xml_file.endswith('.xml'):
                xml_path = os.path.join(annotations_path, xml_file)
                annotation = self.parse_annotation(xml_path)
                
                # Load image
                img_path = os.path.join(images_path, annotation['filename'])
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    img = cv2.resize(img, (300, 300))  # SSD input size
                    img = img / 255.0  # Normalize
                    
                    # Create label
                    label = np.zeros(self.num_classes)
                    for obj in annotation['objects']:
                        if obj['name'] == self.new_class_name:
                            label[2] = 1  # Index 2 for new class
                        elif obj['name'] == 'person':
                            label[1] = 1  # Index 1 for person
                    
                    images.append(img)
                    labels.append(label)
        
        return np.array(images), np.array(labels)
    
    def create_model(self):
        """Tạo model với transfer learning"""
        # Base model - MobileNetV2
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(300, 300, 3)
        )
        
        # Freeze base model layers
        for layer in base_model.layers:
            layer.trainable = False
        
        # Add custom layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x)
        x = Dense(512, activation='relu')(x)
        output = Dense(self.num_classes, activation='sigmoid')(x)
        
        model = Model(inputs=base_model.input, outputs=output)
        return model
    
    def train(self, epochs=50, batch_size=32):
        """Train model"""
        # Load dataset
        print("Loading dataset...")
        X, y = self.load_dataset()
        
        # Split dataset
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Create model
        print("Creating model...")
        model = self.create_model()
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Data augmentation
        datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2
        )
        
        # Train model
        print("Training model...")
        history = model.fit(
            datagen.flow(X_train, y_train, batch_size=batch_size),
            validation_data=(X_val, y_val),
            epochs=epochs,
            steps_per_epoch=len(X_train) // batch_size
        )
        
        # Save model
        model.save(f'model_{self.new_class_name}.h5')
        print(f"Model saved as model_{self.new_class_name}.h5")
        
        return model, history

# Usage example
if __name__ == "__main__":
    detector = NewObjectDetector(
        dataset_path="dataset/new_object",
        new_class_name="car"
    )
    
    model, history = detector.train(epochs=30) 