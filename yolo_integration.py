import cv2
import numpy as np
import os
from ultralytics import YOLO

class YOLOObjectDetector:
    def __init__(self, new_class_name):
        self.new_class_name = new_class_name
        self.model = None
        
    def load_pretrained_model(self, model_path="yolov8n.pt"):
        """Load pre-trained YOLO model"""
        self.model = YOLO(model_path)
        return self.model
    
    def train_custom_model(self, dataset_path, epochs=100):
        """Train YOLO model với custom dataset"""
        # Tạo YAML config file
        self.create_yaml_config(dataset_path)
        
        # Train model
        model = YOLO('yolov8n.pt')  # Load pre-trained model
        results = model.train(
            data=f'{dataset_path}/dataset.yaml',
            epochs=epochs,
            imgsz=640,
            batch=16,
            name=f'yolo_{self.new_class_name}'
        )
        
        self.model = model
        return model
    
    def create_yaml_config(self, dataset_path):
        """Tạo YAML config file cho YOLO training"""
        yaml_content = f"""
# Dataset config for {self.new_class_name}
path: {dataset_path}
train: images/train
val: images/val

# Classes
nc: 1  # number of classes
names: ['{self.new_class_name}']
        """
        
        with open(f'{dataset_path}/dataset.yaml', 'w') as f:
            f.write(yaml_content)
    
    def detect_objects(self, frame):
        """Detect objects trong frame"""
        if self.model is None:
            raise ValueError("Model chưa được load")
        
        results = self.model(frame)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': float(confidence),
                        'class_id': class_id,
                        'class_name': self.new_class_name
                    })
        
        return detections

# Integration với people_counter.py
class YOLOIntegration:
    def __init__(self, new_class_name):
        self.yolo_detector = YOLOObjectDetector(new_class_name)
        self.new_class_name = new_class_name
        
    def integrate_with_people_counter(self):
        """Tích hợp YOLO detection vào people_counter.py"""
        
        # Modified detection logic
        def enhanced_detection(frame, net, yolo_model):
            detections = []
            
            # 1. Run original SSD detection for person
            blob = cv2.dnn.blobFromImage(frame, 0.007843, (frame.shape[1], frame.shape[0]), 127.5)
            net.setInput(blob)
            ssd_detections = net.forward()
            
            # Process SSD detections (person only)
            for i in range(ssd_detections.shape[2]):
                confidence = ssd_detections[0, 0, i, 2]
                if confidence > 0.4:
                    idx = int(ssd_detections[0, 0, i, 1])
                    if idx == 15:  # person class index
                        box = ssd_detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                        detections.append({
                            'bbox': box.astype("int"),
                            'confidence': confidence,
                            'class_name': 'person'
                        })
            
            # 2. Run YOLO detection for new class
            yolo_detections = yolo_model.detect_objects(frame)
            for detection in yolo_detections:
                detections.append(detection)
            
            return detections
        
        return enhanced_detection

# Usage example
if __name__ == "__main__":
    # Train YOLO model với class mới
    yolo_integration = YOLOIntegration("bicycle")
    
    # Train model
    model = yolo_integration.yolo_detector.train_custom_model(
        dataset_path="dataset/bicycle",
        epochs=50
    )
    
    # Test detection
    frame = cv2.imread("test_image.jpg")
    detections = yolo_integration.yolo_detector.detect_objects(frame)
    
    for detection in detections:
        bbox = detection['bbox']
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.putText(frame, f"{detection['class_name']}: {detection['confidence']:.2f}",
                   (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imshow("Detection", frame)
    cv2.waitKey(0) 