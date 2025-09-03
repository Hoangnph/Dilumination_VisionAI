#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project info
echo -e "${BLUE}🚀 People Counting Demo Script${NC}"
echo -e "${BLUE}================================${NC}"

# Check if required files exist
if [ ! -f "detector/MobileNetSSD_deploy.prototxt" ] || [ ! -f "detector/MobileNetSSD_deploy.caffemodel" ]; then
    echo -e "${RED}❌ Model files not found in detector/ directory${NC}"
    exit 1
fi

# Function to show menu
show_menu() {
    echo -e "\n${GREEN}📋 Chọn demo để chạy:${NC}"
    echo "1. 📹 Chạy với video test có sẵn"
    echo "2. 🎥 Chạy với webcam"
    echo "3. 📊 Chạy với video test + output file"
    echo "4. ⚙️  Chạy với custom parameters"
    echo "5. 📈 Performance benchmark"
    echo "6. 🔍 Enhanced people counter"
    echo "7. 🤖 YOLO integration"
    echo "8. ❓ Hiển thị help"
    echo "9. 🚪 Thoát"
    echo -n -e "\n${YELLOW}Nhập lựa chọn (1-9): ${NC}"
}

# Function to run with test video
run_test_video() {
    echo -e "\n${GREEN}📹 Chạy với video test...${NC}"
    python people_counter_complete.py \
        --prototxt detector/MobileNetSSD_deploy.prototxt \
        --model detector/MobileNetSSD_deploy.caffemodel \
        --input utils/data/tests/test_1.mp4 \
        --skip-frames 3 \
        --confidence 0.3
}

# Function to run with webcam
run_webcam() {
    echo -e "\n${GREEN}🎥 Chạy với webcam...${NC}"
    echo -e "${YELLOW}⌨️  Nhấn 'q' để thoát${NC}"
    python people_counter_complete.py \
        --prototxt detector/MobileNetSSD_deploy.prototxt \
        --model detector/MobileNetSSD_deploy.caffemodel \
        --skip-frames 3 \
        --confidence 0.3
}

# Function to run with output
run_with_output() {
    echo -e "\n${GREEN}📊 Chạy với video test + lưu output...${NC}"
    OUTPUT_FILE="output/output_$(date +%Y%m%d_%H%M%S).mp4"
    python people_counter_complete.py \
        --prototxt detector/MobileNetSSD_deploy.prototxt \
        --model detector/MobileNetSSD_deploy.caffemodel \
        --input utils/data/tests/test_1.mp4 \
        --output "$OUTPUT_FILE" \
        --skip-frames 3 \
        --confidence 0.3
    echo -e "${GREEN}✅ Output saved to: $OUTPUT_FILE${NC}"
}

# Function to run with custom parameters
run_custom() {
    echo -e "\n${GREEN}⚙️  Chạy với custom parameters...${NC}"
    
    echo -n -e "${YELLOW}Confidence threshold (0.1-0.9, default 0.3): ${NC}"
    read confidence
    confidence=${confidence:-0.3}
    
    echo -n -e "${YELLOW}Skip frames (1-10, default 3): ${NC}"
    read skip_frames
    skip_frames=${skip_frames:-3}
    
    echo -n -e "${YELLOW}Input source (file path hoặc 0 cho webcam, default test video): ${NC}"
    read input_source
    input_source=${input_source:-"utils/data/tests/test_1.mp4"}
    
    echo -n -e "${YELLOW}Output file (optional, để trống để lưu vào output/): ${NC}"
    read output_file
    
    CMD="python people_counter_complete.py \
        --prototxt detector/MobileNetSSD_deploy.prototxt \
        --model detector/MobileNetSSD_deploy.caffemodel \
        --confidence $confidence \
        --skip-frames $skip_frames"
    
    if [ "$input_source" != "utils/data/tests/test_1.mp4" ]; then
        CMD="$CMD --input $input_source"
    else
        CMD="$CMD --input utils/data/tests/test_1.mp4"
    fi
    
    if [ ! -z "$output_file" ]; then
        CMD="$CMD --output $output_file"
    else
        # Auto-save to output directory if no output file specified
        OUTPUT_FILE="output/output_$(date +%Y%m%d_%H%M%S).mp4"
        CMD="$CMD --output $OUTPUT_FILE"
        echo -e "${BLUE}Auto-saving to: $OUTPUT_FILE${NC}"
    fi
    
    echo -e "\n${BLUE}🔄 Running: $CMD${NC}"
    eval $CMD
}

# Function to run performance benchmark
run_benchmark() {
    echo -e "\n${GREEN}📈 Chạy performance benchmark...${NC}"
    
    # Create temporary benchmark script
    cat > temp_benchmark.py << 'EOF'
import cv2
import numpy as np
import time

def benchmark():
    print("🔄 Starting benchmark...")
    
    net = cv2.dnn.readNetFromCaffe(
        'detector/MobileNetSSD_deploy.prototxt',
        'detector/MobileNetSSD_deploy.caffemodel'
    )
    
    cap = cv2.VideoCapture('utils/data/tests/test_1.mp4')
    frames_processed = 0
    total_time = 0
    
    while frames_processed < 100:
        ret, frame = cap.read()
        if not ret:
            break
            
        start_time = time.time()
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()
        end_time = time.time()
        
        total_time += (end_time - start_time)
        frames_processed += 1
        
        if frames_processed % 20 == 0:
            avg_time = total_time / frames_processed
            fps = 1.0 / avg_time
            print(f"Processed {frames_processed} frames, Avg FPS: {fps:.1f}")
    
    cap.release()
    avg_time = total_time / frames_processed
    fps = 1.0 / avg_time
    print(f"\n📊 Final Results:")
    print(f"   Frames processed: {frames_processed}")
    print(f"   Average FPS: {fps:.1f}")
    print(f"   Average detection time: {avg_time*1000:.1f}ms")

if __name__ == "__main__":
    benchmark()
EOF
    
    python temp_benchmark.py
    rm temp_benchmark.py
}

# Function to run enhanced counter
run_enhanced() {
    echo -e "\n${GREEN}🔍 Chạy enhanced people counter...${NC}"
    if [ -f "enhanced_people_counter.py" ]; then
        python enhanced_people_counter.py \
            --prototxt detector/MobileNetSSD_deploy.prototxt \
            --model detector/MobileNetSSD_deploy.caffemodel \
            --input utils/data/tests/test_1.mp4
    else
        echo -e "${RED}❌ enhanced_people_counter.py not found${NC}"
    fi
}

# Function to run YOLO integration
run_yolo() {
    echo -e "\n${GREEN}🤖 Chạy YOLO integration...${NC}"
    if [ -f "yolo_integration.py" ]; then
        python yolo_integration.py
    else
        echo -e "${RED}❌ yolo_integration.py not found${NC}"
    fi
}

# Function to show help
show_help() {
    echo -e "\n${BLUE}📖 HƯỚNG DẪN SỬ DỤNG${NC}"
    echo -e "${BLUE}===================${NC}"
    echo ""
    echo -e "${GREEN}People Counter: people_counter_complete.py${NC}"
    echo "✅ All features from original version"
    echo "✅ Email alerts, logging, scheduler, timer, threading"
    echo "✅ Improved tracking with skip-frames=3"
    echo "✅ Better counting logic"
    echo "✅ Optimized parameters"
    echo ""
    echo -e "${GREEN}Cách chạy manual:${NC}"
    echo "python people_counter_complete.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel [OPTIONS]"
    echo ""
    echo -e "${GREEN}Options:${NC}"
    echo "  --input PATH          Video file path hoặc webcam (0)"
    echo "  --output PATH         Output video file"
    echo "  --confidence FLOAT    Confidence threshold (0.1-0.9, default 0.3)"
    echo "  --skip-frames INT     Số frames skip (1-10, default 3)"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  Webcam: python people_counter_complete.py --prototxt ... --model ..."
    echo "  Video:  python people_counter_complete.py --prototxt ... --model ... --input video.mp4"
    echo "  Output: python people_counter_complete.py --prototxt ... --model ... --output result.mp4"
    echo ""
    echo -e "${GREEN}Output files:${NC}"
    echo "  output/ - Directory for video outputs"
    echo "  utils/data/logs/counting_data.csv - Counting results"
}

# Main menu loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            run_test_video
            ;;
        2)
            run_webcam
            ;;
        3)
            run_with_output
            ;;
        4)
            run_custom
            ;;
        5)
            run_benchmark
            ;;
        6)
            run_enhanced
            ;;
        7)
            run_yolo
            ;;
        8)
            show_help
            ;;
        9)
            echo -e "\n${GREEN}👋 Tạm biệt!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Lựa chọn không hợp lệ. Vui lòng chọn 1-9.${NC}"
            ;;
    esac
    
    echo -e "\n${YELLOW}Nhấn Enter để tiếp tục...${NC}"
    read
done 