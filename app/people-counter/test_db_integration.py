#!/usr/bin/env python3
"""
Test script for People Counter Database Integration
Tests the database connection and logging functionality
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


def test_database_connection():
    """Test database connection"""
    logger.info("Testing database connection...")
    
    try:
        db = PeopleCounterDB()
        if db.test_connection():
            logger.info("✓ Database connection successful")
            return True
        else:
            logger.error("✗ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"✗ Database connection error: {e}")
        return False


def test_session_management():
    """Test session management functionality"""
    logger.info("Testing session management...")
    
    try:
        db = PeopleCounterDB()
        if not db.test_connection():
            logger.error("✗ Cannot test session management - no database connection")
            return False
        
        # Start session
        session_data = {
            'session_name': 'Test Session',
            'input_source': 'test_video.mp4'
        }
        
        session_id = db.start_session(session_data)
        if session_id:
            logger.info(f"✓ Session started: {session_id}")
            
            # End session
            if db.end_session('completed'):
                logger.info("✓ Session ended successfully")
                return True
            else:
                logger.error("✗ Failed to end session")
                return False
        else:
            logger.error("✗ Failed to start session")
            return False
            
    except Exception as e:
        logger.error(f"✗ Session management error: {e}")
        return False


def test_movement_logging():
    """Test movement logging functionality"""
    logger.info("Testing movement logging...")
    
    try:
        db = PeopleCounterDB()
        if not db.test_connection():
            logger.error("✗ Cannot test movement logging - no database connection")
            return False
        
        # Start session
        session_data = {
            'session_name': 'Movement Test Session',
            'input_source': 'test_video.mp4'
        }
        
        session_id = db.start_session(session_data)
        if not session_id:
            logger.error("✗ Failed to start session for movement test")
            return False
        
        # Log test movements
        test_movements = [
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
                'direction': 'out',
                'movement_time': datetime.now(),
                'centroid': (300, 150),
                'bounding_box': (280, 130, 320, 170),
                'confidence': 0.92,
                'frame_number': 2
            }
        ]
        
        success = True
        for movement in test_movements:
            if db.log_movement(movement):
                logger.info(f"✓ Movement logged: Person {movement['person_id']} {movement['direction']}")
            else:
                logger.error(f"✗ Failed to log movement: Person {movement['person_id']}")
                success = False
        
        # End session
        db.end_session('completed')
        
        return success
        
    except Exception as e:
        logger.error(f"✗ Movement logging error: {e}")
        return False


def test_logger_integration():
    """Test the PeopleCounterLogger integration"""
    logger.info("Testing logger integration...")
    
    try:
        db = PeopleCounterDB()
        if not db.test_connection():
            logger.error("✗ Cannot test logger integration - no database connection")
            return False
        
        # Create logger with database integration
        logger_instance = PeopleCounterLogger(db, enable_csv=True, enable_db=True)
        
        # Start session
        session_name = f"Logger Test Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        session_id = logger_instance.start_session(session_name, "test_video.mp4")
        
        if session_id:
            logger.info(f"✓ Logger session started: {session_id}")
            
            # Test single movement logging
            if logger_instance.log_single_movement(
                person_id=1,
                direction='in',
                centroid=(150, 250),
                bounding_box=(130, 230, 170, 270),
                confidence=0.88,
                frame_number=10
            ):
                logger.info("✓ Single movement logged successfully")
            else:
                logger.error("✗ Failed to log single movement")
                return False
            
            # Test real-time metrics
            if logger_instance.log_realtime_metrics(5, 10, 5):
                logger.info("✓ Real-time metrics logged successfully")
            else:
                logger.error("✗ Failed to log real-time metrics")
                return False
            
            # Test alert logging
            if logger_instance.check_and_log_alert(15, 10):
                logger.info("✓ Alert logged successfully")
            else:
                logger.info("ℹ No alert needed (threshold not exceeded)")
            
            # End session
            if logger_instance.end_session('completed'):
                logger.info("✓ Logger session ended successfully")
                return True
            else:
                logger.error("✗ Failed to end logger session")
                return False
        else:
            logger.error("✗ Failed to start logger session")
            return False
            
    except Exception as e:
        logger.error(f"✗ Logger integration error: {e}")
        return False


def test_csv_fallback():
    """Test CSV logging fallback when database is not available"""
    logger.info("Testing CSV logging fallback...")
    
    try:
        # Create logger without database
        logger_instance = PeopleCounterLogger(enable_csv=True, enable_db=False)
        
        # Test CSV logging
        move_in = [1, 2, 3]
        in_time = ["2025-01-01 10:00", "2025-01-01 10:05", "2025-01-01 10:10"]
        move_out = [1, 2]
        out_time = ["2025-01-01 10:15", "2025-01-01 10:20"]
        
        if logger_instance.log_movement_data(move_in, in_time, move_out, out_time):
            logger.info("✓ CSV logging fallback successful")
            return True
        else:
            logger.error("✗ CSV logging fallback failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ CSV fallback error: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Starting People Counter Database Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Session Management", test_session_management),
        ("Movement Logging", test_movement_logging),
        ("Logger Integration", test_logger_integration),
        ("CSV Fallback", test_csv_fallback)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Database integration is working correctly.")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed. Please check the database setup.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
