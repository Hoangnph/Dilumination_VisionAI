"""
Asynchronous Database Logger for People Counter
Optimized for real-time video processing without frame drops
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
class LogEntry:
    """Data structure for log entries"""
    entry_type: str  # 'movement', 'metrics', 'alert'
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=high, 2=medium, 3=low
    
    def __lt__(self, other):
        """Support for PriorityQueue ordering"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp
    
    def __eq__(self, other):
        """Support for PriorityQueue ordering"""
        return (self.priority == other.priority and 
                self.timestamp == other.timestamp)

class AsyncDatabaseLogger:
    """
    Asynchronous database logger that processes logs in background
    Prevents video frame drops during database operations
    """
    
    def __init__(self, db_instance: Optional[PeopleCounterDB] = None, 
                 max_queue_size: int = 1000, 
                 batch_size: int = 10,
                 flush_interval: float = 1.0):
        """
        Initialize async logger
        
        Args:
            db_instance: Database instance
            max_queue_size: Maximum queue size before dropping entries
            batch_size: Number of entries to process in one batch
            flush_interval: Time interval to flush queue (seconds)
        """
        self.db = db_instance
        self.max_queue_size = max_queue_size
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Queue for log entries
        self.log_queue = queue.PriorityQueue(maxsize=max_queue_size)
        
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
            logger.warning("Async logger already running")
            return True
            
        if not self.db or not self.db.test_connection():
            logger.error("Database not available for async logging")
            return False
            
        self.session_id = session_id
        self.running = True
        
        # Start background worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        logger.info(f"Async database logger started for session {session_id}")
        return True
    
    def stop(self) -> bool:
        """
        Stop the async logger and flush remaining entries
        
        Returns:
            True if stopped successfully
        """
        if not self.running:
            return True
            
        logger.info("Stopping async database logger...")
        self.running = False
        
        # Wait for worker thread to finish
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        
        # Flush remaining entries
        self._flush_queue()
        
        logger.info(f"Async logger stopped. Stats: {self.stats}")
        return True
    
    def log_movement_async(self, person_id: int, direction: str, 
                          centroid: tuple, bounding_box: tuple, 
                          confidence: float, frame_number: int) -> bool:
        """
        Log movement asynchronously (non-blocking)
        
        Args:
            person_id: Person ID
            direction: Movement direction ('in' or 'out')
            centroid: Centroid coordinates
            bounding_box: Bounding box coordinates
            confidence: Detection confidence
            frame_number: Frame number
            
        Returns:
            True if queued successfully, False if queue full
        """
        if not self.running:
            return False
            
        log_entry = LogEntry(
            entry_type='movement',
            data={
                'person_id': int(person_id),
                'direction': direction,
                'movement_time': datetime.now(),
                'centroid': centroid,
                'bounding_box': bounding_box,
                'confidence': float(confidence),
                'frame_number': int(frame_number)
            },
            timestamp=datetime.now(),
            priority=1  # High priority for movements
        )
        
        try:
            self.log_queue.put_nowait(log_entry)
            return True
        except queue.Full:
            self.stats['queue_drops'] += 1
            logger.warning(f"Log queue full, dropping movement log for person {person_id}")
            return False
    
    def log_metrics_async(self, current_count: int, entered_count: int, 
                         exited_count: int) -> bool:
        """
        Log real-time metrics asynchronously
        
        Args:
            current_count: Current people count
            entered_count: People entered count
            exited_count: People exited count
            
        Returns:
            True if queued successfully
        """
        if not self.running:
            return False
            
        log_entry = LogEntry(
            entry_type='metrics',
            data={
                'current_count': current_count,
                'entered_count': entered_count,
                'exited_count': exited_count,
                'timestamp': datetime.now()
            },
            timestamp=datetime.now(),
            priority=2  # Medium priority for metrics
        )
        
        try:
            self.log_queue.put_nowait(log_entry)
            return True
        except queue.Full:
            self.stats['queue_drops'] += 1
            logger.warning("Log queue full, dropping metrics log")
            return False
    
    def log_alert_async(self, alert_type: str, message: str, 
                       current_value: Any, threshold_value: Any) -> bool:
        """
        Log alert asynchronously
        
        Args:
            alert_type: Type of alert
            message: Alert message
            current_value: Current value that triggered alert
            threshold_value: Threshold value
            
        Returns:
            True if queued successfully
        """
        if not self.running:
            return False
            
        log_entry = LogEntry(
            entry_type='alert',
            data={
                'alert_type': alert_type,
                'alert_message': message,
                'current_value': current_value,
                'threshold_value': threshold_value,
                'triggered_at': datetime.now()
            },
            timestamp=datetime.now(),
            priority=1  # High priority for alerts
        )
        
        try:
            self.log_queue.put_nowait(log_entry)
            return True
        except queue.Full:
            self.stats['queue_drops'] += 1
            logger.warning("Log queue full, dropping alert log")
            return False
    
    def _worker_loop(self):
        """Background worker thread loop"""
        logger.info("Async logger worker thread started")
        
        batch = []
        last_flush = time.time()
        
        while self.running:
            try:
                # Try to get entry from queue with timeout
                try:
                    entry = self.log_queue.get(timeout=0.1)
                    batch.append(entry)
                except queue.Empty:
                    entry = None
                
                # Check if we should flush batch
                current_time = time.time()
                should_flush = (
                    len(batch) >= self.batch_size or
                    (batch and current_time - last_flush >= self.flush_interval)
                )
                
                if should_flush:
                    self._process_batch(batch)
                    batch = []
                    last_flush = current_time
                    self.stats['last_flush'] = datetime.now()
                
            except Exception as e:
                logger.error(f"Error in async logger worker: {e}")
                self.stats['errors'] += 1
                time.sleep(0.1)  # Prevent tight error loop
        
        # Process remaining entries
        if batch:
            self._process_batch(batch)
        
        logger.info("Async logger worker thread stopped")
    
    def _flush_queue(self):
        """Flush all remaining entries in queue"""
        batch = []
        while not self.log_queue.empty():
            try:
                entry = self.log_queue.get_nowait()
                batch.append(entry)
            except queue.Empty:
                break
        
        if batch:
            self._process_batch(batch)
            logger.info(f"Flushed {len(batch)} remaining entries")
    
    def _process_batch(self, batch: List[LogEntry]):
        """Process a batch of log entries"""
        if not batch:
            return
            
        logger.debug(f"Processing batch of {len(batch)} entries")
        
        # Group entries by type for efficient processing
        movements = []
        metrics = []
        alerts = []
        
        for entry in batch:
            if entry.entry_type == 'movement':
                movements.append(entry.data)
            elif entry.entry_type == 'metrics':
                metrics.append(entry.data)
            elif entry.entry_type == 'alert':
                alerts.append(entry.data)
        
        # Process each type
        try:
            if movements:
                self._batch_log_movements(movements)
            if metrics:
                self._batch_log_metrics(metrics)
            if alerts:
                self._batch_log_alerts(alerts)
                
            self.stats['total_logged'] += len(batch)
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            self.stats['errors'] += 1
    
    def _batch_log_movements(self, movements: List[Dict[str, Any]]):
        """Batch log movements for efficiency"""
        if not movements:
            return
            
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Prepare batch insert
                    values = []
                    for movement in movements:
                        values.append((
                            self.session_id,
                            movement['person_id'],
                            movement['direction'],
                            movement['movement_time'],
                            float(movement['centroid'][0]),
                            float(movement['centroid'][1]),
                            float(movement['bounding_box'][0]),
                            float(movement['bounding_box'][1]),
                            float(movement['bounding_box'][2]),
                            float(movement['bounding_box'][3]),
                            float(movement['confidence']),
                            int(movement['frame_number']),
                            datetime.now()
                        ))
                    
                    # Execute batch insert
                    cursor.executemany("""
                        INSERT INTO people_movements (
                            session_id, person_id, movement_direction,
                            movement_time, centroid_x, centroid_y,
                            bounding_box_x1, bounding_box_y1,
                            bounding_box_x2, bounding_box_y2,
                            confidence_score, frame_number, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, values)
                    
                    logger.debug(f"Batch logged {len(movements)} movements")
                    
        except Exception as e:
            logger.error(f"Error batch logging movements: {e}")
            raise
    
    def _batch_log_metrics(self, metrics: List[Dict[str, Any]]):
        """Batch log metrics"""
        if not metrics:
            return
            
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Use the latest metrics entry
                    latest_metrics = metrics[-1]
                    
                    cursor.execute("""
                        INSERT INTO realtime_metrics (
                            session_id, current_people_count,
                            people_entered_last_minute, people_exited_last_minute,
                            timestamp
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, (
                        self.session_id,
                        latest_metrics['current_count'],
                        latest_metrics['entered_count'],
                        latest_metrics['exited_count'],
                        latest_metrics['timestamp']
                    ))
                    
                    logger.debug(f"Logged metrics: {latest_metrics}")
                    
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
            raise
    
    def _batch_log_alerts(self, alerts: List[Dict[str, Any]]):
        """Batch log alerts"""
        if not alerts:
            return
            
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    for alert in alerts:
                        cursor.execute("""
                            INSERT INTO alert_logs (
                                session_id, alert_type, alert_message,
                                current_value, threshold_value, triggered_at
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            self.session_id,
                            alert['alert_type'],
                            alert['alert_message'],
                            alert['current_value'],
                            alert['threshold_value'],
                            alert['triggered_at']
                        ))
                    
                    logger.debug(f"Batch logged {len(alerts)} alerts")
                    
        except Exception as e:
            logger.error(f"Error batch logging alerts: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics"""
        return {
            **self.stats,
            'queue_size': self.log_queue.qsize(),
            'running': self.running
        }
