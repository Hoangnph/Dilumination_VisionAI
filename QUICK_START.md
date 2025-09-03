# 🚀 People Counting Demo - Quick Start

## 📋 Tổng quan
Project đếm người real-time sử dụng MobileNet SSD và CentroidTracker.

## 🎯 Phiên bản hoàn chỉnh
**`people_counter_complete.py`** - Phiên bản đầy đủ tính năng với:
- ✅ **Tất cả tính năng từ phiên bản gốc**
- ✅ **Email alerts** - Gửi cảnh báo khi vượt ngưỡng
- ✅ **Logging system** - Lưu dữ liệu vào CSV
- ✅ **Scheduler** - Chạy theo lịch trình
- ✅ **Timer** - Tự động dừng sau 8 giờ
- ✅ **Threading** - Hỗ trợ đa luồng
- ✅ **Configuration** - Đọc từ `utils/config.json`
- ✅ **Tracking tốt hơn** (skip-frames=3)
- ✅ **Logic đếm chính xác**

## 🚀 Cách chạy nhanh

### 1. Sử dụng script demo (Khuyến nghị)
```bash
./run_demo.sh
```

### 2. Chạy trực tiếp
```bash
# Video test
python people_counter_complete.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --input utils/data/tests/test_1.mp4 \
    --skip-frames 3 \
    --confidence 0.3

# Webcam
python people_counter_complete.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --skip-frames 3 \
    --confidence 0.3
```

## 📁 Cấu trúc file
```
├── people_counter_complete.py  # ✅ Phiên bản hoàn chỉnh (khuyến nghị)
├── people_counter.py           # Phiên bản gốc (có vấn đề dlib)
├── run_demo.sh                 # Script demo tương tác
├── QUICK_START.md              # Hướng dẫn sử dụng
├── output/                     # 📁 Thư mục lưu video output
├── detector/                   # Model MobileNet SSD
└── utils/data/tests/           # Video test
```

## ⚙️ Tham số quan trọng
- `--skip-frames 3`: Tần suất detection (1-10, càng nhỏ càng chính xác)
- `--confidence 0.3`: Ngưỡng tin cậy (0.1-0.9)
- `--input`: Đường dẫn video hoặc webcam
- `--output`: Lưu video output

## 📊 Kết quả
- **Enter**: Số người vào
- **Exit**: Số người ra  
- **Inside**: Số người đang ở trong
- **Objects**: Số đối tượng đang được track
- **Status**: Trạng thái (Detecting/Tracking)

## 🔧 Tính năng nâng cao
- **📧 Email Alerts**: Gửi cảnh báo khi số người vượt ngưỡng
- **📝 Logging**: Lưu dữ liệu vào `utils/data/logs/counting_data.csv`
- **⏰ Scheduler**: Chạy tự động theo lịch trình (09:00 hàng ngày)
- **⏱️ Timer**: Tự động dừng sau 8 giờ
- **🧵 Threading**: Hỗ trợ đa luồng cho performance tốt hơn
- **⚙️ Configuration**: Cấu hình từ `utils/config.json`

## 🔧 Troubleshooting
- Nếu tracking không tốt: giảm `skip-frames`
- Nếu detection sai: tăng `confidence`
- Nếu FPS thấp: tăng `skip-frames`
- Nếu email không gửi được: kiểm tra `utils/mailer.py`
- Nếu logging không hoạt động: kiểm tra `"Log": true` trong `utils/config.json`
- Nếu video chạy nhiều lần: đã được sửa trong phiên bản mới

## 📝 Lưu ý
- Nhấn 'q' để thoát
- Video output sẽ được lưu vào thư mục `output/` với timestamp
- Log được lưu trong `utils/data/logs/`
- Cấu hình trong `utils/config.json`:
  - `Threshold`: Ngưỡng số người để gửi cảnh báo
  - `ALERT`: Bật/tắt email alerts
  - `Log`: Bật/tắt logging
  - `Timer`: Bật/tắt timer tự động
  - `Scheduler`: Bật/tắt scheduler
  - `Thread`: Bật/tắt threading
