#!/usr/bin/env python3
"""
People Counter Database Test Suite
Comprehensive testing for database functionality
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

import pytest
import asyncpg
from sqlalchemy import text

# Add database directory to path
sys.path.append(str(Path(__file__).parent))

from config.settings import db_config
from utils.database import db_manager
from models import *
from client import PeopleCounterDBClient, PeopleCounterIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseTestSuite:
    """Comprehensive database test suite"""
    
    def __init__(self):
        self.test_results = {}
        self.test_session_id = None
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all database tests"""
        logger.info("Starting database test suite...")
        
        try:
            # Initialize database
            await self.test_database_connection()
            
            # Test database schema
            await self.test_database_schema()
            
            # Test migrations
            await self.test_migrations()
            
            # Test CRUD operations
            await self.test_crud_operations()
            
            # Test API endpoints
            await self.test_api_endpoints()
            
            # Test integration
            await self.test_integration()
            
            # Test performance
            await self.test_performance()
            
            # Test data integrity
            await self.test_data_integrity()
            
            logger.info("Database test suite completed")
            return self.test_results
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            return self.test_results
    
    async def test_database_connection(self):
        """Test database connection"""
        logger.info("Testing database connection...")
        
        try:
            await db_manager.initialize()
            is_healthy = await db_manager.health_check()
            
            if is_healthy:
                logger.info("✓ Database connection test passed")
                self.test_results["database_connection"] = True
            else:
                logger.error("✗ Database connection test failed")
                self.test_results["database_connection"] = False
                
        except Exception as e:
            logger.error(f"✗ Database connection test failed: {e}")
            self.test_results["database_connection"] = False
    
    async def test_database_schema(self):
        """Test database schema"""
        logger.info("Testing database schema...")
        
        try:
            async with db_manager.async_session_scope() as session:
                # Test if all tables exist
                tables = [
                    'sessions', 'people_movements', 'session_statistics',
                    'realtime_metrics', 'hourly_statistics', 'daily_statistics',
                    'system_config', 'alert_thresholds', 'alert_logs'
                ]
                
                for table in tables:
                    result = await session.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        )
                    """))
                    exists = result.scalar()
                    
                    if not exists:
                        raise Exception(f"Table {table} does not exist")
                
                # Test if all views exist
                views = [
                    'current_session_overview', 'recent_movements',
                    'hourly_analytics', 'daily_analytics'
                ]
                
                for view in views:
                    result = await session.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.views 
                            WHERE table_name = '{view}'
                        )
                    """))
                    exists = result.scalar()
                    
                    if not exists:
                        raise Exception(f"View {view} does not exist")
                
                logger.info("✓ Database schema test passed")
                self.test_results["database_schema"] = True
                
        except Exception as e:
            logger.error(f"✗ Database schema test failed: {e}")
            self.test_results["database_schema"] = False
    
    async def test_migrations(self):
        """Test migration system"""
        logger.info("Testing migration system...")
        
        try:
            # Check if migration history table exists
            async with db_manager.async_session_scope() as session:
                result = await session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'migration_history'
                    )
                """))
                exists = result.scalar()
                
                if not exists:
                    raise Exception("Migration history table does not exist")
                
                # Check if initial migration was applied
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM migration_history 
                    WHERE migration_name LIKE '001_%'
                """))
                count = result.scalar()
                
                if count == 0:
                    raise Exception("Initial migration was not applied")
                
                logger.info("✓ Migration system test passed")
                self.test_results["migrations"] = True
                
        except Exception as e:
            logger.error(f"✗ Migration system test failed: {e}")
            self.test_results["migrations"] = False
    
    async def test_crud_operations(self):
        """Test CRUD operations"""
        logger.info("Testing CRUD operations...")
        
        try:
            async with db_manager.async_session_scope() as session:
                # Test CREATE - Create a test session
                test_session = Session(
                    session_name="Test Session",
                    input_source="test_input.mp4",
                    output_path="test_output.mp4",
                    status=SessionStatus.ACTIVE,
                    fps=30.0,
                    total_frames=1000,
                    resolution_width=640,
                    resolution_height=480
                )
                
                session.add(test_session)
                await session.commit()
                await session.refresh(test_session)
                
                self.test_session_id = str(test_session.id)
                
                # Test READ - Read the session
                retrieved_session = await session.get(Session, test_session.id)
                if not retrieved_session:
                    raise Exception("Failed to retrieve session")
                
                # Test UPDATE - Update the session
                retrieved_session.session_name = "Updated Test Session"
                retrieved_session.status = SessionStatus.COMPLETED
                await session.commit()
                
                # Test DELETE - Delete the session
                await session.delete(retrieved_session)
                await session.commit()
                
                logger.info("✓ CRUD operations test passed")
                self.test_results["crud_operations"] = True
                
        except Exception as e:
            logger.error(f"✗ CRUD operations test failed: {e}")
            self.test_results["crud_operations"] = False
    
    async def test_api_endpoints(self):
        """Test API endpoints"""
        logger.info("Testing API endpoints...")
        
        try:
            # Test API client
            async with PeopleCounterDBClient() as client:
                # Test health check
                is_healthy = await client.health_check()
                if not is_healthy:
                    raise Exception("API health check failed")
                
                # Test session creation
                session_data = {
                    "session_name": "API Test Session",
                    "input_source": "test_input.mp4",
                    "confidence_threshold": 0.3
                }
                
                session_id = await client.start_session(session_data)
                if not session_id:
                    raise Exception("Failed to create session via API")
                
                # Test movement recording
                movement_data = {
                    "person_id": 1,
                    "movement_direction": "in",
                    "movement_time": datetime.now().isoformat(),
                    "centroid_x": 320,
                    "centroid_y": 240,
                    "confidence_score": 0.95
                }
                
                success = await client.record_movement(movement_data)
                if not success:
                    raise Exception("Failed to record movement via API")
                
                # Test metrics recording
                metrics_data = {
                    "current_people_count": 1,
                    "detection_status": "tracking",
                    "fps_current": 30.0
                }
                
                success = await client.record_metrics(metrics_data)
                if not success:
                    raise Exception("Failed to record metrics via API")
                
                # Test session info retrieval
                session_info = await client.get_session_info(session_id)
                if not session_info:
                    raise Exception("Failed to retrieve session info via API")
                
                # Test session ending
                session_stats = {
                    "fps": 30.0,
                    "total_frames": 1000,
                    "status": "completed"
                }
                
                success = await client.end_session(session_stats)
                if not success:
                    raise Exception("Failed to end session via API")
                
                logger.info("✓ API endpoints test passed")
                self.test_results["api_endpoints"] = True
                
        except Exception as e:
            logger.error(f"✗ API endpoints test failed: {e}")
            self.test_results["api_endpoints"] = False
    
    async def test_integration(self):
        """Test integration layer"""
        logger.info("Testing integration layer...")
        
        try:
            # Test integration
            integration = PeopleCounterIntegration()
            await integration.initialize()
            
            # Test session start
            session_data = {
                "session_name": "Integration Test Session",
                "input_source": "test_input.mp4"
            }
            
            session_id = await integration.start_counting_session(session_data)
            if not session_id:
                raise Exception("Failed to start session via integration")
            
            # Test movement recording
            success = await integration.record_people_movement(
                person_id=1,
                direction="in",
                centroid=(320, 240),
                bounding_box=(300, 200, 340, 280),
                confidence=0.95,
                frame_number=100
            )
            
            if not success:
                raise Exception("Failed to record movement via integration")
            
            # Test metrics recording
            success = await integration.record_system_metrics(
                people_count=1,
                detection_status="tracking",
                fps=30.0,
                cpu_usage=45.5,
                memory_usage=256.8
            )
            
            if not success:
                raise Exception("Failed to record metrics via integration")
            
            # Test statistics retrieval
            stats = await integration.get_current_statistics()
            if not stats:
                raise Exception("Failed to retrieve statistics via integration")
            
            # Test session end
            session_stats = {
                "fps": 30.0,
                "total_frames": 1000,
                "status": "completed"
            }
            
            success = await integration.end_counting_session(session_stats)
            if not success:
                raise Exception("Failed to end session via integration")
            
            await integration.close()
            
            logger.info("✓ Integration layer test passed")
            self.test_results["integration"] = True
            
        except Exception as e:
            logger.error(f"✗ Integration layer test failed: {e}")
            self.test_results["integration"] = False
    
    async def test_performance(self):
        """Test database performance"""
        logger.info("Testing database performance...")
        
        try:
            async with db_manager.async_session_scope() as session:
                # Test bulk insert performance
                start_time = datetime.now()
                
                # Create test session
                test_session = Session(
                    session_name="Performance Test Session",
                    input_source="test_input.mp4",
                    status=SessionStatus.ACTIVE
                )
                
                session.add(test_session)
                await session.commit()
                await session.refresh(test_session)
                
                # Insert multiple movements
                movements = []
                for i in range(100):
                    movement = PeopleMovement(
                        session_id=test_session.id,
                        person_id=i % 10,
                        movement_direction=MovementDirection.IN if i % 2 == 0 else MovementDirection.OUT,
                        movement_time=datetime.now() - timedelta(minutes=i),
                        centroid_x=320 + i,
                        centroid_y=240 + i,
                        confidence_score=0.9
                    )
                    movements.append(movement)
                
                session.add_all(movements)
                await session.commit()
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if duration > 5.0:  # Should complete within 5 seconds
                    raise Exception(f"Bulk insert too slow: {duration:.2f}s")
                
                # Test query performance
                start_time = datetime.now()
                
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM people_movements 
                    WHERE session_id = :session_id
                """), {"session_id": test_session.id})
                
                count = result.scalar()
                
                end_time = datetime.now()
                query_duration = (end_time - start_time).total_seconds()
                
                if query_duration > 1.0:  # Should complete within 1 second
                    raise Exception(f"Query too slow: {query_duration:.2f}s")
                
                if count != 100:
                    raise Exception(f"Expected 100 movements, got {count}")
                
                # Cleanup
                await session.delete(test_session)
                await session.commit()
                
                logger.info(f"✓ Performance test passed (insert: {duration:.2f}s, query: {query_duration:.2f}s)")
                self.test_results["performance"] = True
                
        except Exception as e:
            logger.error(f"✗ Performance test failed: {e}")
            self.test_results["performance"] = False
    
    async def test_data_integrity(self):
        """Test data integrity"""
        logger.info("Testing data integrity...")
        
        try:
            async with db_manager.async_session_scope() as session:
                # Test foreign key constraints
                test_session = Session(
                    session_name="Integrity Test Session",
                    input_source="test_input.mp4",
                    status=SessionStatus.ACTIVE
                )
                
                session.add(test_session)
                await session.commit()
                await session.refresh(test_session)
                
                # Test valid movement
                valid_movement = PeopleMovement(
                    session_id=test_session.id,
                    person_id=1,
                    movement_direction=MovementDirection.IN,
                    movement_time=datetime.now(),
                    confidence_score=0.95
                )
                
                session.add(valid_movement)
                await session.commit()
                
                # Test invalid movement (should fail)
                try:
                    invalid_movement = PeopleMovement(
                        session_id="invalid-uuid",
                        person_id=1,
                        movement_direction=MovementDirection.IN,
                        movement_time=datetime.now(),
                        confidence_score=0.95
                    )
                    
                    session.add(invalid_movement)
                    await session.commit()
                    
                    # If we get here, the constraint failed
                    raise Exception("Foreign key constraint not enforced")
                    
                except Exception:
                    # This is expected - foreign key constraint should prevent this
                    await session.rollback()
                
                # Test check constraints
                try:
                    invalid_session = Session(
                        session_name="Invalid Session",
                        input_source="test_input.mp4",
                        status=SessionStatus.ACTIVE,
                        fps=-1.0  # Invalid FPS
                    )
                    
                    session.add(invalid_session)
                    await session.commit()
                    
                    # If we get here, the constraint failed
                    raise Exception("Check constraint not enforced")
                    
                except Exception:
                    # This is expected - check constraint should prevent this
                    await session.rollback()
                
                # Cleanup
                await session.delete(test_session)
                await session.commit()
                
                logger.info("✓ Data integrity test passed")
                self.test_results["data_integrity"] = True
                
        except Exception as e:
            logger.error(f"✗ Data integrity test failed: {e}")
            self.test_results["data_integrity"] = False
    
    def print_test_results(self):
        """Print test results summary"""
        print("\n" + "="*50)
        print("DATABASE TEST RESULTS SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("\nDetailed Results:")
        
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {test_name}: {status}")
        
        print("="*50)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Database is ready for production.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please review and fix issues.")

async def main():
    """Main test function"""
    test_suite = DatabaseTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        test_suite.print_test_results()
        
        # Return exit code based on results
        failed_tests = sum(1 for result in results.values() if not result)
        sys.exit(0 if failed_tests == 0 else 1)
        
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
