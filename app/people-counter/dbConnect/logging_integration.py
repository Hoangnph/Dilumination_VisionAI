"""
Logging Integration Module for People Counter
Handles integration between CSV logging and database logging
"""

import os
import csv
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from itertools import zip_longest

from .db_connection import PeopleCounterDB

logger = logging.getLogger(__name__)


class PeopleCounterLogger:
    """
    Clean logging integration class that handles both CSV and database logging
    Follows Single Responsibility Principle
    """
    
    def __init__(self, db_instance: Optional[PeopleCounterDB] = None, 
                 enable_csv: bool = True, enable_db: bool = True):
        """
        Initialize logger with database and CSV options
        
        Args:
            db_instance: Database connection instance
            enable_csv: Enable CSV logging
            enable_db: Enable database logging
        """
        self.db = db_instance
        self.enable_csv = enable_csv
        self.enable_db = enable_db
        self.csv_file_path = 'utils/data/logs/counting_data.csv'
        
        # Ensure logs directory exists
        if self.enable_csv:
            os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
    
    def log_movement_data(self, move_in: List[int], in_time: List[str], 
                         move_out: List[int], out_time: List[str]) -> bool:
        """
        Log movement data to both CSV and database
        
        Args:
            move_in: List of people entering
            in_time: List of entry times
            move_out: List of people exiting
            out_time: List of exit times
            
        Returns:
            True if logging successful, False otherwise
        """
        success = True
        
        # Log to CSV if enabled
        if self.enable_csv:
            success &= self._log_to_csv(move_in, in_time, move_out, out_time)
        
        # Log to database if enabled and database is available
        if self.enable_db and self.db:
            success &= self._log_to_database(move_in, in_time, move_out, out_time)
        
        return success
    
    def _log_to_csv(self, move_in: List[int], in_time: List[str], 
                   move_out: List[int], out_time: List[str]) -> bool:
        """
        Log data to CSV file (original functionality)
        
        Args:
            move_in: List of people entering
            in_time: List of entry times
            move_out: List of people exiting
            out_time: List of exit times
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = [move_in, in_time, move_out, out_time]
            export_data = zip_longest(*data, fillvalue='')
            
            with open(self.csv_file_path, 'w', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                if myfile.tell() == 0:  # Check if header rows are already existing
                    wr.writerow(("Move In", "In Time", "Move Out", "Out Time"))
                    wr.writerows(export_data)
            
            logger.debug(f"Data logged to CSV: {self.csv_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log to CSV: {e}")
            return False
    
    def _log_to_database(self, move_in: List[int], in_time: List[str], 
                        move_out: List[int], out_time: List[str]) -> bool:
        """
        Log data to database
        
        Args:
            move_in: List of people entering
            in_time: List of entry times
            move_out: List of people exiting
            out_time: List of exit times
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Log individual movements
            for i, (person_id, timestamp) in enumerate(zip(move_in, in_time)):
                movement_data = {
                    'person_id': person_id,
                    'direction': 'in',
                    'movement_time': self._parse_timestamp(timestamp),
                    'centroid': (0, 0),  # Default values
                    'bounding_box': (0, 0, 0, 0),
                    'confidence': 1.0,
                    'frame_number': i
                }
                self.db.log_movement(movement_data)
            
            for i, (person_id, timestamp) in enumerate(zip(move_out, out_time)):
                movement_data = {
                    'person_id': person_id,
                    'direction': 'out',
                    'movement_time': self._parse_timestamp(timestamp),
                    'centroid': (0, 0),  # Default values
                    'bounding_box': (0, 0, 0, 0),
                    'confidence': 1.0,
                    'frame_number': i
                }
                self.db.log_movement(movement_data)
            
            # Log real-time metrics
            current_count = len(move_in) - len(move_out)
            metrics_data = {
                'current_count': current_count,
                'entered_count': len(move_in),
                'exited_count': len(move_out),
                'timestamp': datetime.now()
            }
            self.db.log_realtime_metrics(metrics_data)
            
            logger.debug("Data logged to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log to database: {e}")
            return False
    
    def log_single_movement(self, person_id: int, direction: str, 
                          centroid: tuple, bounding_box: tuple, 
                          confidence: float, frame_number: int) -> bool:
        """
        Log a single movement event
        
        Args:
            person_id: ID of the person
            direction: Movement direction ('in' or 'out')
            centroid: Centroid coordinates (x, y)
            bounding_box: Bounding box coordinates (x1, y1, x2, y2)
            confidence: Detection confidence score
            frame_number: Frame number
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enable_db or not self.db:
            return True
        
        try:
            movement_data = {
                'person_id': person_id,
                'direction': direction,
                'movement_time': datetime.now(),
                'centroid': centroid,
                'bounding_box': bounding_box,
                'confidence': confidence,
                'frame_number': frame_number
            }
            
            return self.db.log_movement(movement_data)
            
        except Exception as e:
            logger.error(f"Failed to log single movement: {e}")
            return False
    
    def log_realtime_metrics(self, current_count: int, entered_count: int, 
                           exited_count: int) -> bool:
        """
        Log real-time metrics
        
        Args:
            current_count: Current number of people inside
            entered_count: Total people entered
            exited_count: Total people exited
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enable_db or not self.db:
            return True
        
        try:
            metrics_data = {
                'current_count': current_count,
                'entered_count': entered_count,
                'exited_count': exited_count,
                'timestamp': datetime.now()
            }
            
            return self.db.log_realtime_metrics(metrics_data)
            
        except Exception as e:
            logger.error(f"Failed to log realtime metrics: {e}")
            return False
    
    def check_and_log_alert(self, current_count: int, threshold: int) -> bool:
        """
        Check threshold and log alert if exceeded
        
        Args:
            current_count: Current number of people inside
            threshold: Alert threshold
            
        Returns:
            True if alert logged or not needed, False if failed
        """
        if not self.enable_db or not self.db:
            return True
        
        try:
            if self.db.check_alert_threshold(current_count):
                alert_data = {
                    'alert_type': 'threshold_exceeded',
                    'message': f'People count ({current_count}) exceeded threshold ({threshold})',
                    'level': 'warning',
                    'people_count': current_count,
                    'threshold_value': threshold,
                    'alert_time': datetime.now()
                }
                
                return self.db.log_alert(alert_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check and log alert: {e}")
            return False
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse timestamp string to datetime object
        
        Args:
            timestamp_str: Timestamp string
            
        Returns:
            Datetime object
        """
        try:
            # Try different timestamp formats
            formats = [
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            logger.warning(f"Could not parse timestamp: {timestamp_str}")
            return datetime.now()
            
        except Exception as e:
            logger.error(f"Error parsing timestamp: {e}")
            return datetime.now()
    
    def get_session_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get current session statistics from database
        
        Returns:
            Session statistics dictionary or None if not available
        """
        if not self.enable_db or not self.db:
            return None
        
        try:
            return self.db.get_session_stats()
        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return None
    
    def start_session(self, session_name: str, input_source: str) -> Optional[str]:
        """
        Start a new counting session
        
        Args:
            session_name: Name of the session
            input_source: Input source (video file, webcam, etc.)
            
        Returns:
            Session ID if successful, None otherwise
        """
        if not self.enable_db or not self.db:
            return None
        
        try:
            session_data = {
                'session_name': session_name,
                'input_source': input_source
            }
            return self.db.start_session(session_data)
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return None
    
    def end_session(self, status: str = 'completed') -> bool:
        """
        End the current counting session
        
        Args:
            status: Session end status
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enable_db or not self.db:
            return True
        
        try:
            return self.db.end_session(status)
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False


# Factory function for creating logger instance
def create_logger(db_instance: Optional[PeopleCounterDB] = None, 
                 enable_csv: bool = True, enable_db: bool = True) -> PeopleCounterLogger:
    """
    Factory function to create logger instance
    
    Args:
        db_instance: Database connection instance
        enable_csv: Enable CSV logging
        enable_db: Enable database logging
        
    Returns:
        PeopleCounterLogger instance
    """
    return PeopleCounterLogger(db_instance, enable_csv, enable_db)
