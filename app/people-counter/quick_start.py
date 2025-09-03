#!/usr/bin/env python3
"""
⚡ Quick Start Script for People Counting
=========================================
Chạy nhanh các demo phổ biến nhất

Usage: 
  python quick_start.py                    # Demo với video test
  python quick_start.py --webcam           # Demo với webcam  
  python quick_start.py --output result.mp4  # Demo với output
  python quick_start.py --benchmark        # Performance test
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime

def run_cmd(cmd_list, description):
    """Chạy command và in kết quả"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd_list)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd_list, check=True)
        print(f"✅ Hoàn thành!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Bị dừng bởi user")
        return False

def check_files():
    """Kiểm tra files cần thiết"""
    required = [
        "people_counter.py",
        "detector/MobileNetSSD_deploy.prototxt", 
        "detector/MobileNetSSD_deploy.caffemodel"
    ]
    
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"   - {f}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Quick start People Counting demos')
    parser.add_argument('--webcam', action='store_true', help='Chạy với webcam')
    parser.add_argument('--output', type=str, help='Lưu output video')
    parser.add_argument('--benchmark', action='store_true', help='Chạy performance test')
    parser.add_argument('--confidence', type=float, default=0.4, help='Confidence threshold')
    parser.add_argument('--input', type=str, help='Input video file')
    
    args = parser.parse_args()
    
    print("⚡ Quick Start - People Counting")
    print("=" * 35)
    
    # Check requirements
    check_files()
    
    # Base command
    base_cmd = [
        "python", "people_counter.py",
        "--prototxt", "detector/MobileNetSSD_deploy.prototxt",
        "--model", "detector/MobileNetSSD_deploy.caffemodel",
        "--confidence", str(args.confidence)
    ]
    
    if args.benchmark:
        # Performance benchmark
        benchmark_code = '''
import cv2, time, numpy as np
net = cv2.dnn.readNetFromCaffe("detector/MobileNetSSD_deploy.prototxt", "detector/MobileNetSSD_deploy.caffemodel")
cap = cv2.VideoCapture("utils/data/tests/test_1.mp4")
times = []
for i in range(50):
    ret, frame = cap.read()
    if not ret: break
    start = time.time()
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    net.forward()
    times.append(time.time() - start)
    if i % 10 == 0: print(f"Frame {i}/50, FPS: {1/np.mean(times):.1f}")
cap.release()
print(f"\\nAverage FPS: {1/np.mean(times):.1f}")
print(f"Average time: {np.mean(times)*1000:.1f}ms")
'''
        with open("temp_bench.py", "w") as f:
            f.write(benchmark_code)
        
        success = run_cmd(["python", "temp_bench.py"], "Performance benchmark")
        os.remove("temp_bench.py")
        
    elif args.webcam:
        # Webcam demo
        print("📹 Nhấn 'q' để thoát webcam")
        success = run_cmd(base_cmd, "Webcam demo")
        
    elif args.output:
        # Video với output
        if not args.input:
            args.input = "utils/data/tests/test_1.mp4"
        
        cmd = base_cmd + ["--input", args.input, "--output", args.output]
        success = run_cmd(cmd, f"Video processing với output: {args.output}")
        
        if success:
            print(f"📁 Video đã lưu: {args.output}")
            
    else:
        # Default: video test
        input_file = args.input or "utils/data/tests/test_1.mp4"
        
        if not os.path.exists(input_file):
            print(f"❌ Video file không tồn tại: {input_file}")
            sys.exit(1)
            
        cmd = base_cmd + ["--input", input_file]
        success = run_cmd(cmd, f"Demo với video: {input_file}")
    
    if success:
        print(f"\n🎉 Demo hoàn thành!")
        print(f"📊 Check log: utils/data/logs/counting_data.csv")
    else:
        print(f"\n❌ Demo thất bại!")

if __name__ == "__main__":
    main() 