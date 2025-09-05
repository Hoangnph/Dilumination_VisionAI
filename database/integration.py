# People Counter Database Integration
# Integration layer between people counter and database

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import aiohttp
import asyncpg
from sqlalchemy.orm import Session

# Add database directory to path
import sys
sys.path.append(str(Path(__file__).parent))

from config.settings import db_config, app_config
from utils.database import db_manager
from models import (
    Session as DBSession, PeopleMovement, SessionStatistics, 
    RealtimeMetrics, HourlyStatistics, DailyStatistics,
    SessionStatus, MovementDirection, DetectionStatus
)

# Configure logging
logger = logging.getLogger(__name__)

class PeopleCounterDBIntegration:
    """Integration class for people counter and database"""
    
    def __init__(self):
        self.current_session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self.movement_buffer: List[Dict] = []
        self.metrics_buffer: List[Dict] = []
        self.buffer_size = 10  # Flush buffer when it reaches this size
        self.last_flush_time = datetime.now()
        self.flush_interval = 30  # Flush every 30 seconds
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            await db_manager.initialize()
            logger.info("Database integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database integration: {e}")
            raise
    
    async def start_session(self, session_data: Dict[str, Any]) -> str:
        """Start a new counting session"""
        try:
            async with db_manager.async_session_scope() as session:
                db_session = DBSession(
                    session_name=session_data.get("session_name", f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    input_source=session_data.get("input_source"),
                    output_path=session_data.get("output_path"),
                    confidence_threshold=session_data.get("confidence_threshold", 0.3),
                    skip_frames=session_data.get("skip_frames", 3),
                    max_disappeared=session_data.get("max_disappeared", 15),
                    max_distance=session_data.get("max_distance", 80),
                    status=SessionStatus.ACTIVE
                )
                
                session.add(db_session)
                await session.commit()
                await session.refresh(db_session)
                
                self.current_session_id = str(db_session.id)
                self.session_start_time = datetime.now()
                
                logger.info(f"Started session: {self.current_session_id}")
                return self.current_session_id
                
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise
    
    async def end_session(self, session_stats: Dict[str, Any]) -> bool:
        """End the current session"""
        if not self.current_session_id:
            logger.warning("No active session to end")
            return False
        
        try:
            # Flush any remaining data
            await self.flush_buffers()
            
            async with db_manager.async_session_scope() as session:
                session_uuid = self.current_session_id
                
                # Update session with end time and stats
                db_session = await session.get(DBSession, session_uuid)
                if db_session:
                    db_session.end_time = datetime.now()
                    db_session.duration_seconds = (datetime.now() - self.session_start_time).total_seconds()
                    db_session.fps = session_stats.get("fps")
                    db_session.total_frames = session_stats.get("total_frames")
                    db_session.resolution_width = session_stats.get("resolution_width")
                    db_session.resolution_height = session_stats.get("resolution_height")
                    db_session.status = SessionStatus.COMPLETED
                    
                    await session.commit()
                
                logger.info(f"Ended session: {self.current_session_id}")
                
                # Reset session state
                self.current_session_id = None
                self.session_start_time = None
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    async def record_movement(self, movement_data: Dict[str, Any]) -> bool:
        """Record a people movement"""
        if not self.current_session_id:
            logger.warning("No active session for movement recording")
            return False
        
        try:
            # Add to buffer
            movement_data["session_id"] = self.current_session_id
            self.movement_buffer.append(movement_data)
            
            # Check if buffer needs flushing
            if len(self.movement_buffer) >= self.buffer_size:
                await self.flush_movement_buffer()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record movement: {e}")
            return False
    
    async def record_realtime_metrics(self, metrics_data: Dict[str, Any]) -> bool:
        """Record real-time metrics"""
        if not self.current_session_id:
            logger.warning("No active session for metrics recording")
            return False
        
        try:
            # Add to buffer
            metrics_data["session_id"] = self.current_session_id
            self.metrics_buffer.append(metrics_data)
            
            # Check if buffer needs flushing
            if len(self.metrics_buffer) >= self.buffer_size:
                await self.flush_metrics_buffer()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
            return False
    
    async def flush_movement_buffer(self):
        """Flush movement buffer to database"""
        if not self.movement_buffer:
            return
        
        try:
            async with db_manager.async_session_scope() as session:
                for movement_data in self.movement_buffer:
                    movement = PeopleMovement(
                        session_id=movement_data["session_id"],
                        person_id=movement_data["person_id"],
                        movement_direction=MovementDirection(movement_data["movement_direction"]),
                        movement_time=datetime.fromisoformat(movement_data["movement_time"].replace('Z', '+00:00')),
                        centroid_x=movement_data.get("centroid_x"),
                        centroid_y=movement_data.get("centroid_y"),
                        bounding_box_x1=movement_data.get("bounding_box_x1"),
                        bounding_box_y1=movement_data.get("bounding_box_y1"),
                        bounding_box_x2=movement_data.get("bounding_box_x2"),
                        bounding_box_y2=movement_data.get("bounding_box_y2"),
                        confidence_score=movement_data.get("confidence_score"),
                        frame_number=movement_data.get("frame_number")
                    )
                    session.add(movement)
                
                await session.commit()
                logger.info(f"Flushed {len(self.movement_buffer)} movements to database")
                
        except Exception as e:
            logger.error(f"Failed to flush movement buffer: {e}")
        finally:
            self.movement_buffer.clear()
    
    async def flush_metrics_buffer(self):
        """Flush metrics buffer to database"""
        if not self.metrics_buffer:
            return
        
        try:
            async with db_manager.async_session_scope() as session:
                for metrics_data in self.metrics_buffer:
                    metrics = RealtimeMetrics(
                        session_id=metrics_data["session_id"],
                        current_people_count=metrics_data["current_people_count"],
                        people_entered_last_minute=metrics_data.get("people_entered_last_minute", 0),
                        people_exited_last_minute=metrics_data.get("people_exited_last_minute", 0),
                        detection_status=DetectionStatus(metrics_data.get("detection_status", "waiting")),
                        fps_current=metrics_data.get("fps_current"),
                        cpu_usage_percentage=metrics_data.get("cpu_usage_percentage"),
                        memory_usage_mb=metrics_data.get("memory_usage_mb"),
                        processing_latency_ms=metrics_data.get("processing_latency_ms")
                    )
                    session.add(metrics)
                
                await session.commit()
                logger.info(f"Flushed {len(self.metrics_buffer)} metrics to database")
                
        except Exception as e:
            logger.error(f"Failed to flush metrics buffer: {e}")
        finally:
            self.metrics_buffer.clear()
    
    async def flush_buffers(self):
        """Flush all buffers"""
        await self.flush_movement_buffer()
        await self.flush_metrics_buffer()
        self.last_flush_time = datetime.now()
    
    async def auto_flush_check(self):
        """Check if buffers need auto-flushing based on time"""
        if datetime.now() - self.last_flush_time > timedelta(seconds=self.flush_interval):
            await self.flush_buffers()
    
    async def get_session_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session statistics"""
        target_session_id = session_id or self.current_session_id
        if not target_session_id:
            return {}
        
        try:
            async with db_manager.async_session_scope() as session:
                # Get session statistics
                stats = await session.get(SessionStatistics, target_session_id)
                
                if stats:
                    return {
                        "total_people_entered": stats.total_people_entered,
                        "total_people_exited": stats.total_people_exited,
                        "current_people_inside": stats.current_people_inside,
                        "peak_people_count": stats.peak_people_count,
                        "average_people_count": float(stats.average_people_count) if stats.average_people_count else None,
                        "accuracy_percentage": float(stats.accuracy_percentage) if stats.accuracy_percentage else None
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {}
    
    async def get_recent_movements(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get recent movements"""
        if not self.current_session_id:
            return []
        
        try:
            async with db_manager.async_session_scope() as session:
                since = datetime.now() - timedelta(minutes=minutes)
                
                result = await session.execute(
                    text("""
                        SELECT person_id, movement_direction, movement_time, 
                               centroid_x, centroid_y, confidence_score
                        FROM people_movements 
                        WHERE session_id = :session_id AND movement_time >= :since
                        ORDER BY movement_time DESC
                        LIMIT 100
                    """),
                    {"session_id": self.current_session_id, "since": since}
                )
                
                movements = []
                for row in result.fetchall():
                    movements.append({
                        "person_id": row[0],
                        "movement_direction": row[1],
                        "movement_time": row[2],
                        "centroid": {"x": float(row[3]) if row[3] else None, "y": float(row[4]) if row[4] else None},
                        "confidence_score": float(row[5]) if row[5] else None
                    })
                
                return movements
                
        except Exception as e:
            logger.error(f"Failed to get recent movements: {e}")
            return []
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        if not self.current_session_id:
            return []
        
        try:
            # Get current session statistics
            stats = await self.get_session_statistics()
            
            alerts = []
            
            # Check people count threshold
            if stats.get("current_people_inside", 0) > 50:  # Default threshold
                alerts.append({
                    "type": "high_people_count",
                    "message": f"People count ({stats['current_people_inside']}) exceeded threshold",
                    "current_value": stats["current_people_inside"],
                    "threshold_value": 50
                })
            
            # Check accuracy threshold
            if stats.get("accuracy_percentage", 100) < 80:  # Default threshold
                alerts.append({
                    "type": "low_accuracy",
                    "message": f"Detection accuracy ({stats['accuracy_percentage']:.1f}%) below threshold",
                    "current_value": stats["accuracy_percentage"],
                    "threshold_value": 80
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
            return []
    
    async def close(self):
        """Close database integration"""
        try:
            # Flush any remaining data
            await self.flush_buffers()
            
            # End current session if active
            if self.current_session_id:
                await self.end_session({})
            
            logger.info("Database integration closed")
            
        except Exception as e:
            logger.error(f"Error during database integration close: {e}")

# Global integration instance
db_integration = PeopleCounterDBIntegration()

# Convenience functions for people counter integration
async def start_counting_session(session_data: Dict[str, Any]) -> str:
    """Start a counting session"""
    return await db_integration.start_session(session_data)

async def end_counting_session(session_stats: Dict[str, Any]) -> bool:
    """End a counting session"""
    return await db_integration.end_session(session_stats)

async def record_people_movement(movement_data: Dict[str, Any]) -> bool:
    """Record a people movement"""
    return await db_integration.record_movement(movement_data)

async def record_system_metrics(metrics_data: Dict[str, Any]) -> bool:
    """Record system metrics"""
    return await db_integration.record_realtime_metrics(metrics_data)

async def get_current_statistics() -> Dict[str, Any]:
    """Get current session statistics"""
    return await db_integration.get_session_statistics()

async def get_recent_activity(minutes: int = 10) -> List[Dict[str, Any]]:
    """Get recent activity"""
    return await db_integration.get_recent_movements(minutes)

async def check_system_alerts() -> List[Dict[str, Any]]:
    """Check for system alerts"""
    return await db_integration.check_alerts()

# Export
__all__ = [
    'PeopleCounterDBIntegration',
    'db_integration',
    'start_counting_session',
    'end_counting_session', 
    'record_people_movement',
    'record_system_metrics',
    'get_current_statistics',
    'get_recent_activity',
    'check_system_alerts'
]
