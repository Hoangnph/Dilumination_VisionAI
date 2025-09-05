# People Counter Database Integration Example
# Example of how to integrate people counter with database

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database integration
from database.client import integration

class PeopleCounterWithDB:
    """Example people counter with database integration"""
    
    def __init__(self):
        self.session_id: str = None
        self.is_running = False
    
    async def initialize(self):
        """Initialize database integration"""
        await integration.initialize()
        logger.info("People counter with database initialized")
    
    async def start_counting(self, input_source: str, output_path: str = None):
        """Start people counting with database logging"""
        try:
            # Start database session
            session_data = {
                "session_name": f"Counting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "input_source": input_source,
                "output_path": output_path,
                "confidence_threshold": 0.3,
                "skip_frames": 3,
                "max_disappeared": 15,
                "max_distance": 80
            }
            
            self.session_id = await integration.start_session(session_data)
            self.is_running = True
            
            logger.info(f"Started counting session: {self.session_id}")
            
            # Simulate people counting process
            await self.simulate_counting_process()
            
        except Exception as e:
            logger.error(f"Failed to start counting: {e}")
            raise
    
    async def simulate_counting_process(self):
        """Simulate the people counting process"""
        logger.info("Simulating people counting process...")
        
        # Simulate some movements
        movements = [
            (1, "in", (320, 240), (300, 200, 340, 280), 0.95, 100),
            (2, "in", (350, 250), (330, 210, 370, 290), 0.92, 150),
            (3, "in", (280, 220), (260, 180, 300, 260), 0.88, 200),
            (1, "out", (320, 200), (300, 160, 340, 240), 0.94, 250),
            (4, "in", (400, 280), (380, 240, 420, 320), 0.91, 300),
        ]
        
        for i, (person_id, direction, centroid, bbox, confidence, frame) in enumerate(movements):
            # Record movement
            await integration.record_movement(
                person_id, direction, centroid, bbox, confidence, frame
            )
            
            # Record metrics
            people_count = len([m for m in movements[:i+1] if m[1] == "in"]) - \
                          len([m for m in movements[:i+1] if m[1] == "out"])
            
            await integration.record_metrics(
                people_count=people_count,
                detection_status="tracking",
                fps=30.0,
                cpu_usage=45.5,
                memory_usage=256.8
            )
            
            # Auto-flush check
            await integration.auto_flush_check()
            
            logger.info(f"Recorded movement: Person {person_id} {direction}")
            
            # Simulate processing time
            await asyncio.sleep(0.1)
        
        # Get final statistics
        stats = await integration.get_statistics()
        logger.info(f"Final statistics: {stats}")
        
        # Get recent activity
        activity = await integration.get_activity(minutes=10)
        logger.info(f"Recent activity: {len(activity)} movements")
    
    async def stop_counting(self):
        """Stop people counting"""
        if not self.is_running:
            logger.warning("Counting is not running")
            return
        
        try:
            # End database session
            session_stats = {
                "fps": 30.0,
                "total_frames": 500,
                "resolution_width": 640,
                "resolution_height": 480,
                "status": "completed"
            }
            
            await integration.end_session(session_stats)
            self.is_running = False
            
            logger.info("Stopped counting session")
            
        except Exception as e:
            logger.error(f"Failed to stop counting: {e}")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        try:
            dashboard_data = await integration.get_dashboard()
            return dashboard_data
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {}
    
    async def close(self):
        """Close integration"""
        if self.is_running:
            await self.stop_counting()
        
        await integration.close()
        logger.info("People counter with database closed")

async def main():
    """Main example function"""
    counter = PeopleCounterWithDB()
    
    try:
        # Initialize
        await counter.initialize()
        
        # Start counting
        await counter.start_counting(
            input_source="utils/data/tests/test_1.mp4",
            output_path="output/test_with_db.mp4"
        )
        
        # Get dashboard data
        dashboard = await counter.get_dashboard_data()
        logger.info(f"Dashboard data: {dashboard}")
        
        # Stop counting
        await counter.stop_counting()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
    
    finally:
        # Close
        await counter.close()

if __name__ == "__main__":
    asyncio.run(main())
