#!/usr/bin/env python3
"""
Example script demonstrating People Counter Database Integration
Shows how to use the database connection and logging features
"""

import sys
import os
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from dbConnect import PeopleCounterDB, PeopleCounterLogger

# Setup logging
logging.basicConfig(level=logging.INFO, format="[INFO] %(message)s")
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example of basic database usage"""
    logger.info("=== Basic Database Usage Example ===")
    
    # Create database instance
    db = PeopleCounterDB()
    
    # Test connection
    if not db.test_connection():
        logger.error("Database connection failed!")
        return False
    
    logger.info("✓ Database connection successful")
    
    # Start a session
    session_data = {
        'session_name': 'Example Session',
        'input_source': 'example_video.mp4'
    }
    
    session_id = db.start_session(session_data)
    if session_id:
        logger.info(f"✓ Session started: {session_id}")
        
        # Log some movements
        movements = [
            {
                'person_id': 1,
                'direction': 'in',
                'movement_time': datetime.now(),
                'centroid': (100, 200),
                'bounding_box': (80, 180, 120, 220),
                'confidence': 0.95,
                'frame_number': 1
            },
            {
                'person_id': 2,
                'direction': 'in',
                'movement_time': datetime.now(),
                'centroid': (200, 250),
                'bounding_box': (180, 230, 220, 270),
                'confidence': 0.92,
                'frame_number': 2
            },
            {
                'person_id': 1,
                'direction': 'out',
                'movement_time': datetime.now(),
                'centroid': (150, 100),
                'bounding_box': (130, 80, 170, 120),
                'confidence': 0.88,
                'frame_number': 3
            }
        ]
        
        for movement in movements:
            if db.log_movement(movement):
                logger.info(f"✓ Logged: Person {movement['person_id']} {movement['direction']}")
            else:
                logger.error(f"✗ Failed to log: Person {movement['person_id']}")
        
        # Log real-time metrics
        metrics_data = {
            'current_count': 1,  # 2 in - 1 out = 1 inside
            'entered_count': 2,
            'exited_count': 1,
            'timestamp': datetime.now()
        }
        
        if db.log_realtime_metrics(metrics_data):
            logger.info("✓ Real-time metrics logged")
        
        # Get session statistics
        stats = db.get_session_stats()
        if stats:
            logger.info(f"Session stats: {stats}")
        
        # End session
        if db.end_session('completed'):
            logger.info("✓ Session ended successfully")
        
        return True
    else:
        logger.error("✗ Failed to start session")
        return False


def example_logger_usage():
    """Example of using the PeopleCounterLogger"""
    logger.info("\n=== Logger Usage Example ===")
    
    # Create database instance
    db = PeopleCounterDB()
    
    if not db.test_connection():
        logger.error("Database connection failed!")
        return False
    
    # Create logger with both CSV and database logging
    logger_instance = PeopleCounterLogger(db, enable_csv=True, enable_db=True)
    
    # Start session
    session_name = f"Logger Example - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    session_id = logger_instance.start_session(session_name, "example_video.mp4")
    
    if session_id:
        logger.info(f"✓ Logger session started: {session_id}")
        
        # Simulate people counter data
        move_in = [1, 2, 3, 4, 5]
        in_time = [
            "2025-01-01 10:00",
            "2025-01-01 10:05", 
            "2025-01-01 10:10",
            "2025-01-01 10:15",
            "2025-01-01 10:20"
        ]
        move_out = [1, 2, 3]
        out_time = [
            "2025-01-01 10:25",
            "2025-01-01 10:30",
            "2025-01-01 10:35"
        ]
        
        # Log movement data (both CSV and database)
        if logger_instance.log_movement_data(move_in, in_time, move_out, out_time):
            logger.info("✓ Movement data logged to both CSV and database")
        
        # Log individual movements
        for i in range(3):
            if logger_instance.log_single_movement(
                person_id=i+1,
                direction='in',
                centroid=(100 + i*50, 200),
                bounding_box=(80 + i*50, 180, 120 + i*50, 220),
                confidence=0.9,
                frame_number=i+1
            ):
                logger.info(f"✓ Individual movement {i+1} logged")
        
        # Log real-time metrics
        current_count = len(move_in) - len(move_out)  # 5 - 3 = 2
        if logger_instance.log_realtime_metrics(current_count, len(move_in), len(move_out)):
            logger.info(f"✓ Real-time metrics logged: {current_count} people inside")
        
        # Check and log alert if threshold exceeded
        threshold = 3
        if logger_instance.check_and_log_alert(current_count, threshold):
            logger.info(f"✓ Alert checked and logged (threshold: {threshold})")
        
        # End session
        if logger_instance.end_session('completed'):
            logger.info("✓ Logger session ended successfully")
        
        return True
    else:
        logger.error("✗ Failed to start logger session")
        return False


def example_csv_only():
    """Example of CSV-only logging (fallback mode)"""
    logger.info("\n=== CSV-Only Logging Example ===")
    
    # Create logger without database (CSV only)
    logger_instance = PeopleCounterLogger(enable_csv=True, enable_db=False)
    
    # Simulate data
    move_in = [1, 2]
    in_time = ["2025-01-01 11:00", "2025-01-01 11:05"]
    move_out = [1]
    out_time = ["2025-01-01 11:10"]
    
    # Log to CSV only
    if logger_instance.log_movement_data(move_in, in_time, move_out, out_time):
        logger.info("✓ Data logged to CSV file only")
        logger.info(f"CSV file location: {logger_instance.csv_file_path}")
        return True
    else:
        logger.error("✗ Failed to log to CSV")
        return False


def main():
    """Run all examples"""
    logger.info("People Counter Database Integration Examples")
    logger.info("=" * 60)
    
    examples = [
        ("Basic Database Usage", example_basic_usage),
        ("Logger Usage", example_logger_usage),
        ("CSV-Only Logging", example_csv_only)
    ]
    
    results = []
    for example_name, example_func in examples:
        try:
            result = example_func()
            results.append((example_name, result))
        except Exception as e:
            logger.error(f"✗ Example {example_name} failed: {e}")
            results.append((example_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE SUMMARY")
    logger.info("=" * 60)
    
    for example_name, result in results:
        status = "SUCCESS" if result else "FAILED"
        logger.info(f"{example_name}: {status}")
    
    logger.info("\n🎉 Examples completed! Check the database and CSV files for logged data.")


if __name__ == "__main__":
    main()
