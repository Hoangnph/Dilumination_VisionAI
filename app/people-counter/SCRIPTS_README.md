# 🚀 Scripts Guide - People Counting Project

Hướng dẫn sử dụng các scripts để chạy demo dự án People Counting một cách dễ dàng.

## 📋 Danh sách Scripts

### 1. 🎯 `quick_start.py` - Quick Start (Khuyến nghị)
**Script đơn giản nhất để chạy nhanh các demo phổ biến**

```bash
# Demo cơ bản với video test
python quick_start.py

# Demo với webcam
python quick_start.py --webcam

# Demo với output video
python quick_start.py --output result.mp4

# Performance benchmark
python quick_start.py --benchmark

# Custom video file
python quick_start.py --input my_video.mp4

# Custom confidence
python quick_start.py --confidence 0.3
```

### 2. 🎮 `run_demo.py` - Interactive Menu
**Script với menu tương tác đầy đủ tính năng**

```bash
python run_demo.py
```

Menu options:
- `1` - Chạy với video test có sẵn
- `2` - Chạy với webcam real-time  
- `3` - Chạy với video + lưu output
- `4` - Tùy chỉnh parameters
- `5` - Performance benchmark
- `6` - Enhanced people counter
- `7` - YOLO integration demo
- `8` - Training demo (new objects)
- `9` - Hiển thị hướng dẫn
- `0` - Thoát

### 3. 🔧 `run_demo.sh` - Bash Script
**Script bash với menu tương tự (cho Linux/Mac)**

```bash
./run_demo.sh
```

## ⚡ Quick Examples

### Chạy demo nhanh nhất:
```bash
python quick_start.py
```

### Webcam demo:
```bash
python quick_start.py --webcam
```

### Tạo output video:
```bash
python quick_start.py --output demo_output.mp4
```

### Test performance:
```bash
python quick_start.py --benchmark
```

### Interactive menu:
```bash
python run_demo.py
```

## 📊 Output Files

Sau khi chạy, bạn sẽ có:

- **`utils/data/logs/counting_data.csv`** - Kết quả counting (in/out)
- **`output_TIMESTAMP.mp4`** - Video đã xử lý (nếu dùng --output)
- **Console output** - Thống kê FPS, timing, detections

## 🔧 Parameters

### Common Parameters:
- `--confidence` - Confidence threshold (0.1-0.9, default: 0.4)
- `--input` - Input video file hoặc webcam (0)
- `--output` - Output video file path
- `--skip-frames` - Skip frames để tăng tốc (10-50, default: 30)

### Examples với parameters:
```bash
# Confidence thấp hơn (nhiều detections hơn)
python quick_start.py --confidence 0.2

# Với video custom
python quick_start.py --input my_video.mp4 --output result.mp4

# Menu với custom settings
python run_demo.py
```

## 🎯 Use Cases

### 1. **Demo nhanh cho khách hàng:**
```bash
python quick_start.py --output client_demo.mp4
```

### 2. **Test performance trên hardware mới:**
```bash
python quick_start.py --benchmark
```

### 3. **Development & testing:**
```bash
python run_demo.py  # Chọn option 4 cho custom params
```

### 4. **Real-time monitoring:**
```bash
python quick_start.py --webcam
```

## 🛠️ Troubleshooting

### Script không chạy được:
```bash
# Đảm bảo files có permission
chmod +x *.py *.sh

# Kiểm tra Python version
python --version  # Cần Python 3.6+
```

### Missing dependencies:
```bash
pip install opencv-python imutils numpy dlib scipy
```

### Model files không tìm thấy:
```bash
# Kiểm tra structure
ls detector/
# Cần có: MobileNetSSD_deploy.prototxt và MobileNetSSD_deploy.caffemodel
```

### Video test không có:
```bash
# Kiểm tra test video
ls utils/data/tests/
# Cần có: test_1.mp4
```

## 📈 Performance Tips

1. **Tăng tốc độ:** Tăng `--skip-frames` (30-50)
2. **Tăng accuracy:** Giảm `--confidence` (0.2-0.3)  
3. **Balance:** Confidence 0.4, skip-frames 30 (default)
4. **Real-time:** Dùng webcam với skip-frames 15-20

## 🎨 Customization

### Thay đổi model:
Sửa trong script base_cmd:
```python
"--prototxt", "path/to/your.prototxt",
"--model", "path/to/your.caffemodel"
```

### Thêm script mới:
1. Copy `quick_start.py` 
2. Modify theo nhu cầu
3. Add vào menu của `run_demo.py`

## 🎉 Ready to Use!

```bash
# Bắt đầu ngay:
python quick_start.py

# Hoặc interactive:
python run_demo.py
```

**Happy Counting! 🎯👥📊** 