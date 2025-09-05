"""
Simplified Async Database Logger for People Counter
Only logs confirmed in/out events, not real-time metrics
"""

import queue
import threading
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from dbConnect.db_connection import PeopleCounterDB

logger = logging.getLogger(__name__)

@dataclass
class EventEntry:
    """Data structure for event entries (in/out only)"""
    event_type: str  # 'in' or 'out'
    person_id: int
    timestamp: datetime
    centroid: tuple
    bounding_box: tuple
    confidence: float
    frame_number: int
    
    def __lt__(self, other):
        """Support for PriorityQueue ordering"""
        return self.timestamp < other.timestamp
    
    def __eq__(self, other):
        """Support for PriorityQueue ordering"""
        return self.timestamp == other.timestamp

class SimpleAsyncLogger:
    """
    Simplified async logger that only logs confirmed in/out events
    Matches CSV logging behavior - no real-time metrics
    """
    
    def __init__(self, db_instance: Optional[PeopleCounterDB] = None, 
                 max_queue_size: int = 100):
        """
        Initialize simple async logger
        
        Args:
            db_instance: Database instance
            max_queue_size: Maximum queue size before dropping entries
        """
        self.db = db_instance
        self.max_queue_size = max_queue_size
        
        # Queue for event entries
        self.event_queue = queue.PriorityQueue(maxsize=max_queue_size)
        
        # Background thread
        self.worker_thread = None
        self.running = False
        self.session_id = None
        
        # Statistics
        self.stats = {
            'total_logged': 0,
            'queue_drops': 0,
            'errors': 0,
            'last_flush': None
        }
    
    def start(self, session_id: str) -> bool:
        """
        Start the async logger
        
        Args:
            session_id: Database session ID
            
        Returns:
            True if started successfully
        """
        if self.running:
            logger.warning("Simple async logger already running")
            return True
            
        if not self.db or not self.db.test_connection():
            logger.error("Database not available for async logging")
            return False
            
        self.session_id = session_id
        self.running = True
        
        # Start background worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        logger.info(f"Simple async logger started for session {session_id}")
        return True
    
    def stop(self) -> bool:
        """
        Stop the async logger and flush remaining entries
        
        Returns:
            True if stopped successfully
        """
        if not self.running:
            return True
            
        logger.info("Stopping simple async logger...")
        self.running = False
        
        # Wait for worker thread to finish
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        
        # Flush remaining entries
        self._flush_queue()
        
        logger.info(f"Simple async logger stopped. Stats: {self.stats}")
        return True
    
    def log_event_async(self, event_type: str, person_id: int, 
                        centroid: tuple, bounding_box: tuple, 
                        confidence: float, frame_number: int) -> bool:
        """
        Log confirmed in/out event asynchronously (non-blocking)
        
        Args:
            event_type: 'in' or 'out'
            person_id: Person ID
            centroid: Centroid coordinates
            bounding_box: Bounding box coordinates
            confidence: Detection confidence
            frame_number: Frame number
            
        Returns:
            True if queued successfully, False if queue full
        """
        if not self.running:
            return False
            
        event_entry = EventEntry(
            event_type=event_type,
            person_id=int(person_id),
            timestamp=datetime.now(),
            centroid=centroid,
            bounding_box=bounding_box,
            confidence=float(confidence),
            frame_number=int(frame_number)
        )
        
        try:
            self.event_queue.put_nowait(event_entry)
            logger.debug(f"Queued {event_type} event for person {person_id}")
            return True
        except queue.Full:
            self.stats['queue_drops'] += 1
            logger.warning(f"Event queue full, dropping {event_type} event for person {person_id}")
            return False
    
    def _worker_loop(self):
        """Background worker thread loop"""
        logger.info("Simple async logger worker thread started")
        
        while self.running:
            try:
                # Try to get entry from queue with timeout
                try:
                    entry = self.event_queue.get(timeout=0.1)
                    self._process_event(entry)
                    self.stats['total_logged'] += 1
                    self.stats['last_flush'] = datetime.now()
                except queue.Empty:
                    pass
                
            except Exception as e:
                logger.error(f"Error in simple async logger worker: {e}")
                self.stats['errors'] += 1
                time.sleep(0.1)  # Prevent tight error loop
        
        logger.info("Simple async logger worker thread stopped")
    
    def _flush_queue(self):
        """Flush all remaining entries in queue"""
        count = 0
        while not self.event_queue.empty():
            try:
                entry = self.event_queue.get_nowait()
                self._process_event(entry)
                count += 1
            except queue.Empty:
                break
        
        if count > 0:
            logger.info(f"Flushed {count} remaining events")
    
    def _process_event(self, entry: EventEntry):
        """Process a single event entry"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO people_movements (
                            session_id, person_id, movement_direction,
                            movement_time, centroid_x, centroid_y,
                            bounding_box_x1, bounding_box_y1,
                            bounding_box_x2, bounding_box_y2,
                            confidence_score, frame_number, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        self.session_id,
                        entry.person_id,
                        entry.event_type,
                        entry.timestamp,
                        float(entry.centroid[0]),
                        float(entry.centroid[1]),
                        float(entry.bounding_box[0]),
                        float(entry.bounding_box[1]),
                        float(entry.bounding_box[2]),
                        float(entry.bounding_box[3]),
                        entry.confidence,
                        entry.frame_number,
                        datetime.now()
                    ))
                    
                    logger.debug(f"Logged {entry.event_type} event for person {entry.person_id}")
                    
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics"""
        return {
            **self.stats,
            'queue_size': self.event_queue.qsize(),
            'running': self.running
        }
