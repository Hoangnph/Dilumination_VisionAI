#!/usr/bin/env python3
"""
🚀 People Counting Demo Script
==============================
Interactive demo runner cho People Counting project

Usage: python run_demo.py
"""

import os
import sys
import subprocess
import time
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class DemoRunner:
    def __init__(self):
        self.base_cmd = [
            "python", "people_counter.py",
            "--prototxt", "detector/MobileNetSSD_deploy.prototxt",
            "--model", "detector/MobileNetSSD_deploy.caffemodel"
        ]
        self.check_requirements()
    
    def check_requirements(self):
        """Kiểm tra các file cần thiết"""
        required_files = [
            "people_counter.py",
            "detector/MobileNetSSD_deploy.prototxt",
            "detector/MobileNetSSD_deploy.caffemodel",
            "utils/data/tests/test_1.mp4"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"{Colors.RED}❌ Missing required files:{Colors.NC}")
            for file in missing_files:
                print(f"   - {file}")
            sys.exit(1)
    
    def print_header(self):
        """In header của chương trình"""
        print(f"{Colors.BLUE}🚀 People Counting Demo Script{Colors.NC}")
        print(f"{Colors.BLUE}================================{Colors.NC}")
        print(f"{Colors.CYAN}📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.NC}")
        print()
    
    def show_menu(self):
        """Hiển thị menu chính"""
        print(f"\n{Colors.GREEN}📋 MENU CHÍNH - Chọn demo để chạy:{Colors.NC}")
        print(f"{Colors.WHITE}=" * 45 + f"{Colors.NC}")
        print(f"1. 📹 Chạy với video test có sẵn")
        print(f"2. 🎥 Chạy với webcam real-time")
        print(f"3. 📊 Chạy với video + lưu output")
        print(f"4. ⚙️  Chạy với tùy chỉnh parameters")
        print(f"5. 📈 Performance benchmark")
        print(f"6. 🔍 Enhanced people counter")
        print(f"7. 🤖 YOLO integration demo")
        print(f"8. 🧪 Training demo (new objects)")
        print(f"9. 📖 Hiển thị hướng dẫn")
        print(f"0. 🚪 Thoát")
        print(f"{Colors.WHITE}=" * 45 + f"{Colors.NC}")
    
    def get_user_input(self, prompt, default=None):
        """Lấy input từ user với default value"""
        if default:
            user_input = input(f"{Colors.YELLOW}{prompt} (default: {default}): {Colors.NC}")
            return user_input if user_input.strip() else default
        else:
            return input(f"{Colors.YELLOW}{prompt}: {Colors.NC}")
    
    def run_command(self, cmd, description):
        """Chạy command với logging"""
        print(f"\n{Colors.BLUE}🔄 {description}...{Colors.NC}")
        print(f"{Colors.CYAN}Command: {' '.join(cmd)}{Colors.NC}")
        print(f"{Colors.WHITE}-" * 50 + f"{Colors.NC}")
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, check=True)
            end_time = time.time()
            
            print(f"{Colors.GREEN}✅ Hoàn thành trong {end_time - start_time:.2f}s{Colors.NC}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Lỗi khi chạy command: {e}{Colors.NC}")
            return False
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Bị dừng bởi user{Colors.NC}")
            return False
    
    def demo_test_video(self):
        """Demo 1: Chạy với video test"""
        cmd = self.base_cmd + ["--input", "utils/data/tests/test_1.mp4"]
        return self.run_command(cmd, "Chạy people counting với video test")
    
    def demo_webcam(self):
        """Demo 2: Chạy với webcam"""
        print(f"{Colors.YELLOW}⌨️  Nhấn 'q' trong video window để thoát{Colors.NC}")
        cmd = self.base_cmd.copy()
        return self.run_command(cmd, "Chạy people counting với webcam")
    
    def demo_with_output(self):
        """Demo 3: Chạy với output video"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output_{timestamp}.mp4"
        
        cmd = self.base_cmd + [
            "--input", "utils/data/tests/test_1.mp4",
            "--output", output_file
        ]
        
        success = self.run_command(cmd, "Chạy với output video")
        if success:
            print(f"{Colors.GREEN}📁 Output saved to: {output_file}{Colors.NC}")
        return success
    
    def demo_custom_params(self):
        """Demo 4: Chạy với custom parameters"""
        print(f"\n{Colors.GREEN}⚙️  Tùy chỉnh parameters:{Colors.NC}")
        
        confidence = self.get_user_input("Confidence threshold (0.1-0.9)", "0.4")
        skip_frames = self.get_user_input("Skip frames (10-50)", "30")
        input_source = self.get_user_input("Input source (file path, 0 for webcam)", "utils/data/tests/test_1.mp4")
        output_file = self.get_user_input("Output file (optional, Enter to skip)", "")
        
        cmd = self.base_cmd + [
            "--confidence", confidence,
            "--skip-frames", skip_frames
        ]
        
        if input_source and input_source != "utils/data/tests/test_1.mp4":
            cmd.extend(["--input", input_source])
        else:
            cmd.extend(["--input", "utils/data/tests/test_1.mp4"])
        
        if output_file.strip():
            cmd.extend(["--output", output_file])
        
        return self.run_command(cmd, "Chạy với custom parameters")
    
    def demo_benchmark(self):
        """Demo 5: Performance benchmark"""
        benchmark_script = """
import cv2
import numpy as np
import time

def benchmark():
    print("🔄 Starting performance benchmark...")
    
    net = cv2.dnn.readNetFromCaffe(
        'detector/MobileNetSSD_deploy.prototxt',
        'detector/MobileNetSSD_deploy.caffemodel'
    )
    
    cap = cv2.VideoCapture('utils/data/tests/test_1.mp4')
    frames_processed = 0
    detection_times = []
    
    print("📊 Processing frames...")
    while frames_processed < 100:
        ret, frame = cap.read()
        if not ret:
            break
            
        start_time = time.time()
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()
        end_time = time.time()
        
        detection_times.append(end_time - start_time)
        frames_processed += 1
        
        if frames_processed % 25 == 0:
            avg_time = np.mean(detection_times)
            fps = 1.0 / avg_time
            print(f"   Processed {frames_processed}/100 frames, Current FPS: {fps:.1f}")
    
    cap.release()
    
    # Results
    avg_time = np.mean(detection_times)
    fps = 1.0 / avg_time
    min_time = np.min(detection_times)
    max_time = np.max(detection_times)
    
    print(f"\\n📈 BENCHMARK RESULTS:")
    print(f"   Frames processed: {frames_processed}")
    print(f"   Average FPS: {fps:.1f}")
    print(f"   Average detection time: {avg_time*1000:.1f}ms")
    print(f"   Min detection time: {min_time*1000:.1f}ms")
    print(f"   Max detection time: {max_time*1000:.1f}ms")

if __name__ == "__main__":
    benchmark()
"""
        
        # Write and run benchmark
        with open("temp_benchmark.py", "w") as f:
            f.write(benchmark_script)
        
        success = self.run_command(["python", "temp_benchmark.py"], "Performance benchmark")
        
        # Cleanup
        if os.path.exists("temp_benchmark.py"):
            os.remove("temp_benchmark.py")
        
        return success
    
    def demo_enhanced(self):
        """Demo 6: Enhanced people counter"""
        if os.path.exists("enhanced_people_counter.py"):
            cmd = [
                "python", "enhanced_people_counter.py",
                "--prototxt", "detector/MobileNetSSD_deploy.prototxt",
                "--model", "detector/MobileNetSSD_deploy.caffemodel",
                "--input", "utils/data/tests/test_1.mp4"
            ]
            return self.run_command(cmd, "Enhanced people counter")
        else:
            print(f"{Colors.RED}❌ enhanced_people_counter.py not found{Colors.NC}")
            return False
    
    def demo_yolo(self):
        """Demo 7: YOLO integration"""
        if os.path.exists("yolo_integration.py"):
            cmd = ["python", "yolo_integration.py"]
            return self.run_command(cmd, "YOLO integration demo")
        else:
            print(f"{Colors.RED}❌ yolo_integration.py not found{Colors.NC}")
            return False
    
    def demo_training(self):
        """Demo 8: Training demo"""
        if os.path.exists("train_new_object.py"):
            cmd = ["python", "train_new_object.py"]
            return self.run_command(cmd, "Training demo")
        else:
            print(f"{Colors.RED}❌ train_new_object.py not found{Colors.NC}")
            return False
    
    def show_help(self):
        """Demo 9: Hiển thị help"""
        help_text = f"""
{Colors.BLUE}📖 HƯỚNG DẪN SỬ DỤNG PEOPLE COUNTING{Colors.NC}
{Colors.BLUE}==================================={Colors.NC}

{Colors.GREEN}🔧 Cách chạy manual:{Colors.NC}
python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel [OPTIONS]

{Colors.GREEN}📋 Available Options:{Colors.NC}
  --input PATH          Input video file hoặc webcam (0 = default webcam)
  --output PATH         Output video file path
  --confidence FLOAT    Confidence threshold (0.1-0.9, default: 0.4)
  --skip-frames INT     Số frames skip để tăng tốc (10-50, default: 30)

{Colors.GREEN}💡 Examples:{Colors.NC}
  # Webcam
  python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel

  # Video file
  python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel --input video.mp4

  # Với output
  python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel --input video.mp4 --output result.mp4

  # Custom confidence
  python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel --confidence 0.3

{Colors.GREEN}📁 Output Files:{Colors.NC}
  - utils/data/logs/counting_data.csv    → Counting results
  - output_TIMESTAMP.mp4                 → Processed video (if --output used)

{Colors.GREEN}⌨️  Controls:{Colors.NC}
  - 'q' key: Quit the application
  - 'p' key: Pause/Resume (in some modes)

{Colors.GREEN}🧠 Model Info:{Colors.NC}
  - Framework: MobileNet SSD with Caffe backend
  - Input size: 300x300 pixels
  - Classes: 21 object classes (focus on 'person')
  - Performance: ~50+ FPS on modern hardware
        """
        print(help_text)
    
    def run(self):
        """Main program loop"""
        self.print_header()
        
        while True:
            self.show_menu()
            
            try:
                choice = input(f"\n{Colors.YELLOW}Nhập lựa chọn (0-9): {Colors.NC}")
                
                if choice == '1':
                    self.demo_test_video()
                elif choice == '2':
                    self.demo_webcam()
                elif choice == '3':
                    self.demo_with_output()
                elif choice == '4':
                    self.demo_custom_params()
                elif choice == '5':
                    self.demo_benchmark()
                elif choice == '6':
                    self.demo_enhanced()
                elif choice == '7':
                    self.demo_yolo()
                elif choice == '8':
                    self.demo_training()
                elif choice == '9':
                    self.show_help()
                elif choice == '0':
                    print(f"\n{Colors.GREEN}👋 Cảm ơn bạn đã sử dụng! Tạm biệt!{Colors.NC}")
                    break
                else:
                    print(f"{Colors.RED}❌ Lựa chọn không hợp lệ. Vui lòng chọn 0-9.{Colors.NC}")
                    continue
                
                # Pause after each demo
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    input(f"\n{Colors.YELLOW}Nhấn Enter để trở về menu chính...{Colors.NC}")
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}⚠️  Thoát chương trình bằng Ctrl+C{Colors.NC}")
                break
            except EOFError:
                print(f"\n\n{Colors.YELLOW}⚠️  Thoát chương trình (EOF){Colors.NC}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Lỗi: {e}{Colors.NC}")
                break

def main():
    """Entry point"""
    try:
        demo = DemoRunner()
        demo.run()
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error: {e}{Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    main() 