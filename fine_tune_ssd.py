import os
import cv2
import numpy as np
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.preprocessing.image import ImageDataGenerator

class SSDFineTuner:
    def __init__(self, original_model_path, new_class_name):
        self.original_model_path = original_model_path
        self.new_class_name = new_class_name
        self.original_classes = ["background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"]
        
        # Thêm class mới
        self.new_classes = self.original_classes + [new_class_name]
        self.num_classes = len(self.new_classes)
        
    def convert_caffe_to_keras(self):
        """Convert Caffe model sang Keras format"""
        # Sử dụng OpenCV để load Caffe model
        net = cv2.dnn.readNetFromCaffe(
            "detector/MobileNetSSD_deploy.prototxt",
            "detector/MobileNetSSD_deploy.caffemodel"
        )
        
        # Tạo Keras model tương ứng
        # Note: Đây là simplified version, trong thực tế cần implement đầy đủ SSD architecture
        return self.create_ssd_model()
    
    def create_ssd_model(self):
        """Tạo SSD model với số classes mới"""
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Reshape
        
        # Base model
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(300, 300, 3)
        )
        
        # Freeze early layers
        for layer in base_model.layers[:-10]:
            layer.trainable = False
        
        # Add SSD detection heads
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        
        # Classification head
        classification = Dense(self.num_classes, activation='softmax', name='classification')(x)
        
        # Regression head (bounding box coordinates)
        regression = Dense(4, name='regression')(x)
        
        model = tf.keras.Model(inputs=base_model.input, outputs=[classification, regression])
        return model
    
    def prepare_ssd_dataset(self, dataset_path):
        """Chuẩn bị dataset cho SSD training"""
        images = []
        labels = []
        bboxes = []
        
        images_path = os.path.join(dataset_path, 'images')
        annotations_path = os.path.join(dataset_path, 'annotations')
        
        for xml_file in os.listdir(annotations_path):
            if xml_file.endswith('.xml'):
                xml_path = os.path.join(annotations_path, xml_file)
                annotation = self.parse_annotation(xml_path)
                
                img_path = os.path.join(images_path, annotation['filename'])
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    img = cv2.resize(img, (300, 300))
                    img = img / 255.0
                    
                    # Prepare labels và bboxes
                    for obj in annotation['objects']:
                        class_name = obj['name']
                        if class_name in self.new_classes:
                            class_idx = self.new_classes.index(class_name)
                            
                            # Normalize bbox coordinates
                            bbox = obj['bbox']
                            x_center = (bbox[0] + bbox[2]) / 2 / annotation['width']
                            y_center = (bbox[1] + bbox[3]) / 2 / annotation['height']
                            width = (bbox[2] - bbox[0]) / annotation['width']
                            height = (bbox[3] - bbox[1]) / annotation['height']
                            
                            images.append(img)
                            labels.append(class_idx)
                            bboxes.append([x_center, y_center, width, height])
        
        return np.array(images), np.array(labels), np.array(bboxes)
    
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
    
    def custom_loss(self, y_true, y_pred):
        """Custom loss function cho SSD"""
        # Classification loss
        class_loss = tf.keras.losses.sparse_categorical_crossentropy(y_true, y_pred)
        
        # Regression loss (smooth L1)
        # Note: Simplified version
        return class_loss
    
    def train(self, dataset_path, epochs=50, batch_size=16):
        """Fine-tune SSD model"""
        print("Loading dataset...")
        X, y, bboxes = self.prepare_ssd_dataset(dataset_path)
        
        # Split dataset
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print("Creating model...")
        model = self.create_ssd_model()
        
        # Compile model
        model.compile(
            optimizer=SGD(learning_rate=0.001, momentum=0.9),
            loss=self.custom_loss,
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
        
        print("Training model...")
        history = model.fit(
            datagen.flow(X_train, y_train, batch_size=batch_size),
            validation_data=(X_val, y_val),
            epochs=epochs,
            steps_per_epoch=len(X_train) // batch_size
        )
        
        # Save model
        model.save(f'ssd_model_{self.new_class_name}.h5')
        print(f"Model saved as ssd_model_{self.new_class_name}.h5")
        
        return model, history

# Usage example
if __name__ == "__main__":
    fine_tuner = SSDFineTuner(
        original_model_path="detector/MobileNetSSD_deploy.caffemodel",
        new_class_name="bicycle"
    )
    
    model, history = fine_tuner.train(
        dataset_path="dataset/new_object",
        epochs=30
    ) 