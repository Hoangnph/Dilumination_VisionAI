# People Counter Database Client
# Client library for integrating people counter with database

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import aiohttp
import asyncpg

# Configure logging
logger = logging.getLogger(__name__)

class PeopleCounterDBClient:
    """Client for people counter database operations"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_session_id: Optional[str] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize HTTP client session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'Content-Type': 'application/json'}
            )
            logger.info("Database client initialized")
    
    async def close(self):
        """Close HTTP client session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Database client closed")
    
    async def health_check(self) -> bool:
        """Check API health"""
        try:
            async with self.session.get(f"{self.api_base_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def start_session(self, session_data: Dict[str, Any]) -> str:
        """Start a new counting session"""
        try:
            async with self.session.post(
                f"{self.api_base_url}/sessions",
                json=session_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.current_session_id = result["session_id"]
                    logger.info(f"Started session: {self.current_session_id}")
                    return self.current_session_id
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to start session: {error_text}")
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise
    
    async def end_session(self, session_stats: Dict[str, Any]) -> bool:
        """End the current session"""
        if not self.current_session_id:
            logger.warning("No active session to end")
            return False
        
        try:
            async with self.session.put(
                f"{self.api_base_url}/sessions/{self.current_session_id}",
                json=session_stats
            ) as response:
                if response.status == 200:
                    logger.info(f"Ended session: {self.current_session_id}")
                    self.current_session_id = None
                    return True
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to end session: {error_text}")
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    async def record_movement(self, movement_data: Dict[str, Any]) -> bool:
        """Record a people movement"""
        if not self.current_session_id:
            logger.warning("No active session for movement recording")
            return False
        
        try:
            async with self.session.post(
                f"{self.api_base_url}/sessions/{self.current_session_id}/movements",
                json=movement_data
            ) as response:
                if response.status == 200:
                    return True
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed to record movement: {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to record movement: {e}")
            return False
    
    async def record_metrics(self, metrics_data: Dict[str, Any]) -> bool:
        """Record real-time metrics"""
        if not self.current_session_id:
            logger.warning("No active session for metrics recording")
            return False
        
        try:
            async with self.session.post(
                f"{self.api_base_url}/sessions/{self.current_session_id}/metrics",
                json=metrics_data
            ) as response:
                if response.status == 200:
                    return True
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed to record metrics: {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
            return False
    
    async def get_session_info(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session information"""
        target_session_id = session_id or self.current_session_id
        if not target_session_id:
            return {}
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/sessions/{target_session_id}"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed to get session info: {error_text}")
                    return {}
        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            return {}
    
    async def get_recent_movements(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get recent movements"""
        if not self.current_session_id:
            return []
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/sessions/{self.current_session_id}/movements",
                params={"limit": 100}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("movements", [])
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed to get recent movements: {error_text}")
                    return []
        except Exception as e:
            logger.error(f"Failed to get recent movements: {e}")
            return []
    
    async def get_recent_metrics(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get recent metrics"""
        if not self.current_session_id:
            return []
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/sessions/{self.current_session_id}/metrics/recent",
                params={"minutes": minutes}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("metrics", [])
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed to get recent metrics: {error_text}")
                    return []
        except Exception as e:
            logger.error(f"Failed to get recent metrics: {e}")
            return []
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary"""
        try:
            async with self.session.get(
                f"{self.api_base_url}/dashboard/summary"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed to get dashboard summary: {error_text}")
                    return {}
        except Exception as e:
            logger.error(f"Failed to get dashboard summary: {e}")
            return {}

# Integration wrapper for people counter
class PeopleCounterIntegration:
    """Integration wrapper for people counter with database"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.db_client = PeopleCounterDBClient(api_base_url)
        self.movement_buffer: List[Dict] = []
        self.metrics_buffer: List[Dict] = []
        self.buffer_size = 5  # Smaller buffer for real-time
        self.last_flush_time = datetime.now()
        self.flush_interval = 10  # Flush every 10 seconds
    
    async def initialize(self):
        """Initialize integration"""
        await self.db_client.initialize()
        
        # Check API health
        is_healthy = await self.db_client.health_check()
        if not is_healthy:
            logger.warning("Database API is not healthy")
        
        logger.info("People counter integration initialized")
    
    async def start_counting_session(self, session_data: Dict[str, Any]) -> str:
        """Start a counting session"""
        return await self.db_client.start_session(session_data)
    
    async def end_counting_session(self, session_stats: Dict[str, Any]) -> bool:
        """End a counting session"""
        # Flush any remaining data
        await self.flush_buffers()
        
        return await self.db_client.end_session(session_stats)
    
    async def record_people_movement(self, person_id: int, direction: str, 
                                   centroid: tuple, bounding_box: tuple,
                                   confidence: float, frame_number: int) -> bool:
        """Record a people movement"""
        movement_data = {
            "person_id": person_id,
            "movement_direction": direction,
            "movement_time": datetime.now().isoformat(),
            "centroid_x": centroid[0] if centroid else None,
            "centroid_y": centroid[1] if centroid else None,
            "bounding_box_x1": bounding_box[0] if bounding_box else None,
            "bounding_box_y1": bounding_box[1] if bounding_box else None,
            "bounding_box_x2": bounding_box[2] if bounding_box else None,
            "bounding_box_y2": bounding_box[3] if bounding_box else None,
            "confidence_score": confidence,
            "frame_number": frame_number
        }
        
        # Add to buffer
        self.movement_buffer.append(movement_data)
        
        # Check if buffer needs flushing
        if len(self.movement_buffer) >= self.buffer_size:
            await self.flush_movement_buffer()
        
        return True
    
    async def record_system_metrics(self, people_count: int, detection_status: str,
                                  fps: float, cpu_usage: float, memory_usage: float) -> bool:
        """Record system metrics"""
        metrics_data = {
            "current_people_count": people_count,
            "detection_status": detection_status,
            "fps_current": fps,
            "cpu_usage_percentage": cpu_usage,
            "memory_usage_mb": memory_usage,
            "processing_latency_ms": None  # Could be calculated if needed
        }
        
        # Add to buffer
        self.metrics_buffer.append(metrics_data)
        
        # Check if buffer needs flushing
        if len(self.metrics_buffer) >= self.buffer_size:
            await self.flush_metrics_buffer()
        
        return True
    
    async def flush_movement_buffer(self):
        """Flush movement buffer"""
        if not self.movement_buffer:
            return
        
        try:
            for movement_data in self.movement_buffer:
                await self.db_client.record_movement(movement_data)
            
            logger.info(f"Flushed {len(self.movement_buffer)} movements")
            self.movement_buffer.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush movement buffer: {e}")
    
    async def flush_metrics_buffer(self):
        """Flush metrics buffer"""
        if not self.metrics_buffer:
            return
        
        try:
            for metrics_data in self.metrics_buffer:
                await self.db_client.record_metrics(metrics_data)
            
            logger.info(f"Flushed {len(self.metrics_buffer)} metrics")
            self.metrics_buffer.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush metrics buffer: {e}")
    
    async def flush_buffers(self):
        """Flush all buffers"""
        await self.flush_movement_buffer()
        await self.flush_metrics_buffer()
        self.last_flush_time = datetime.now()
    
    async def auto_flush_check(self):
        """Check if buffers need auto-flushing"""
        if datetime.now() - self.last_flush_time > self.flush_interval:
            await self.flush_buffers()
    
    async def get_current_statistics(self) -> Dict[str, Any]:
        """Get current session statistics"""
        session_info = await self.db_client.get_session_info()
        return session_info.get("statistics", {})
    
    async def get_recent_activity(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity"""
        return await self.db_client.get_recent_movements(minutes)
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return await self.db_client.get_dashboard_summary()
    
    async def close(self):
        """Close integration"""
        await self.flush_buffers()
        await self.db_client.close()
        logger.info("People counter integration closed")

# Global integration instance
integration = PeopleCounterIntegration()

# Convenience functions
async def start_session(session_data: Dict[str, Any]) -> str:
    """Start a counting session"""
    return await integration.start_counting_session(session_data)

async def end_session(session_stats: Dict[str, Any]) -> bool:
    """End a counting session"""
    return await integration.end_counting_session(session_stats)

async def record_movement(person_id: int, direction: str, centroid: tuple, 
                        bounding_box: tuple, confidence: float, frame_number: int) -> bool:
    """Record a people movement"""
    return await integration.record_people_movement(
        person_id, direction, centroid, bounding_box, confidence, frame_number
    )

async def record_metrics(people_count: int, detection_status: str,
                        fps: float, cpu_usage: float, memory_usage: float) -> bool:
    """Record system metrics"""
    return await integration.record_system_metrics(
        people_count, detection_status, fps, cpu_usage, memory_usage
    )

async def get_statistics() -> Dict[str, Any]:
    """Get current statistics"""
    return await integration.get_current_statistics()

async def get_activity(minutes: int = 10) -> List[Dict[str, Any]]:
    """Get recent activity"""
    return await integration.get_recent_activity(minutes)

async def get_dashboard() -> Dict[str, Any]:
    """Get dashboard data"""
    return await integration.get_dashboard_data()

# Export
__all__ = [
    'PeopleCounterDBClient',
    'PeopleCounterIntegration',
    'integration',
    'start_session',
    'end_session',
    'record_movement',
    'record_metrics',
    'get_statistics',
    'get_activity',
    'get_dashboard'
]
