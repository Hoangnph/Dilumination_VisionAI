# HƯỚNG DẪN THÊM ĐỐI TƯỢNG PHÁT HIỆN MỚI

## TỔNG QUAN

Dự án People-Counting-in-Real-Time hiện tại chỉ có thể phát hiện 21 classes từ MobileNet SSD pre-trained model. Để thêm đối tượng phát hiện mới, bạn có 4 phương pháp chính:

## PHƯƠNG PHÁP 1: TRANSFER LEARNING (Khuyến nghị cho người mới)

### Bước 1: Chuẩn bị dữ liệu

#### 1.1 Cấu trúc thư mục
```
dataset/
├── new_object/
│   ├── images/
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── ...
│   └── annotations/
│       ├── img1.xml
│       ├── img2.xml
│       └── ...
```

#### 1.2 Format annotation (XML)
```xml
<annotation>
    <filename>img1.jpg</filename>
    <size>
        <width>500</width>
        <height>300</height>
    </size>
    <object>
        <name>bicycle</name>
        <bndbox>
            <xmin>100</xmin>
            <ymin>50</ymin>
            <xmax>200</xmax>
            <ymax>150</ymax>
        </bndbox>
    </object>
</annotation>
```

### Bước 2: Train model mới
```bash
# Chạy script training
python train_new_object.py
```

### Bước 3: Sử dụng model mới
```bash
# Chạy với model đã train
python enhanced_people_counter.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --custom-classes "bicycle" \
    --custom-model model_bicycle.h5
```

## PHƯƠNG PHÁP 2: FINE-TUNING MOBILENET SSD

### Bước 1: Chuẩn bị dữ liệu
Tương tự như phương pháp 1, nhưng cần nhiều dữ liệu hơn (ít nhất 500-1000 images).

### Bước 2: Fine-tune model
```bash
python fine_tune_ssd.py
```

### Bước 3: Sử dụng model đã fine-tune
```bash
python enhanced_people_counter.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model ssd_model_bicycle.h5
```

## PHƯƠNG PHÁP 3: SỬ DỤNG YOLO

### Bước 1: Cài đặt YOLO
```bash
pip install ultralytics
```

### Bước 2: Chuẩn bị dữ liệu cho YOLO
```
dataset/
├── bicycle/
│   ├── images/
│   │   ├── train/
│   │   └── val/
│   └── labels/
│       ├── train/
│       └── val/
```

### Bước 3: Train YOLO model
```bash
python yolo_integration.py
```

### Bước 4: Sử dụng YOLO model
```bash
python enhanced_people_counter.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --custom-classes "bicycle" \
    --custom-model runs/detect/train/weights/best.pt
```

## PHƯƠNG PHÁP 4: TÍCH HỢP TRỰC TIẾP

### Bước 1: Sử dụng enhanced_people_counter.py
File này đã được nâng cấp để hỗ trợ multiple object detection.

### Bước 2: Cấu hình
```bash
python enhanced_people_counter.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --custom-classes "bicycle,car,motorcycle" \
    --custom-model your_custom_model.pt
```

## SO SÁNH CÁC PHƯƠNG PHÁP

| Phương pháp | Ưu điểm | Nhược điểm | Độ khó | Thời gian |
|-------------|---------|------------|--------|-----------|
| Transfer Learning | Dễ thực hiện, ít dữ liệu | Độ chính xác thấp | Thấp | 1-2 giờ |
| Fine-tuning SSD | Độ chính xác cao | Cần nhiều dữ liệu | Trung bình | 4-8 giờ |
| YOLO | Hiệu năng tốt, dễ sử dụng | Cần GPU | Thấp | 2-4 giờ |
| Tích hợp | Linh hoạt | Phức tạp | Cao | 1-2 giờ |

## YÊU CẦU DỮ LIỆU

### Số lượng tối thiểu
- **Transfer Learning**: 50-100 images
- **Fine-tuning**: 500-1000 images
- **YOLO**: 200-500 images

### Chất lượng dữ liệu
- Đa dạng góc nhìn
- Đa dạng điều kiện ánh sáng
- Đa dạng background
- Kích thước object khác nhau

## VÍ DỤ THỰC TẾ

### Thêm detection cho "bicycle"

#### 1. Thu thập dữ liệu
```bash
# Tạo thư mục dataset
mkdir -p dataset/bicycle/images
mkdir -p dataset/bicycle/annotations

# Copy images vào thư mục
cp your_bicycle_images/*.jpg dataset/bicycle/images/
```

#### 2. Tạo annotations
Sử dụng công cụ như LabelImg để tạo bounding boxes:
```bash
pip install labelImg
labelImg dataset/bicycle/images/ dataset/bicycle/annotations/
```

#### 3. Train model
```bash
python train_new_object.py
```

#### 4. Test model
```bash
python enhanced_people_counter.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --custom-classes "bicycle" \
    --custom-model model_bicycle.h5 \
    --input test_video.mp4
```

## TROUBLESHOOTING

### Lỗi thường gặp

#### 1. Model không load được
```python
# Kiểm tra đường dẫn file
import os
print(os.path.exists("your_model_path"))
```

#### 2. Detection không hoạt động
```python
# Kiểm tra confidence threshold
# Giảm confidence xuống 0.3 hoặc 0.2
--confidence 0.3
```

#### 3. Performance chậm
```python
# Tăng skip frames
--skip-frames 50

# Hoặc sử dụng threading
# Trong config.json: "Thread": true
```

#### 4. Memory error
```python
# Giảm batch size trong training
batch_size=8

# Hoặc giảm image size
img = cv2.resize(img, (224, 224))
```

## TỐI ƯU HÓA

### 1. Data Augmentation
```python
# Trong training script
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2,
    brightness_range=[0.8, 1.2]
)
```

### 2. Model Optimization
```python
# Sử dụng quantization
import tensorflow as tf
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

### 3. Inference Optimization
```python
# Sử dụng GPU nếu có
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

## KẾT LUẬN

- **Người mới**: Sử dụng Transfer Learning hoặc YOLO
- **Có kinh nghiệm**: Fine-tuning SSD
- **Production**: Tích hợp multiple models

Chọn phương pháp phù hợp với:
- Số lượng dữ liệu có sẵn
- Yêu cầu độ chính xác
- Thời gian và tài nguyên
- Kinh nghiệm technical 