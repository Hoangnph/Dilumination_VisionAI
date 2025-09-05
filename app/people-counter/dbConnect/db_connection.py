"""
Database Connection Module for People Counter
Clean, production-ready database integration
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Add the database directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'database'))

try:
    from config.settings import db_config
except ImportError:
    # Fallback configuration if database module is not available
    db_config = None

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors"""
    pass


class PeopleCounterDB:
    """
    Clean database connection class for People Counter application
    Follows SOLID principles and clean code practices
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            config_path: Optional path to database configuration
        """
        self.config = self._load_config(config_path)
        self.connection = None
        self.session_id = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load database configuration
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Database configuration dictionary
        """
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Use database module config if available
        if db_config:
            return {
                'host': db_config.host,
                'port': db_config.port,
                'database': db_config.database,
                'user': db_config.username,
                'password': db_config.password
            }
        
        # Default configuration
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'people_counter',
            'user': 'postgres',
            'password': 'postgres'
        }
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Ensures proper connection cleanup
        """
        connection = None
        try:
            connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                cursor_factory=RealDictCursor
            )
            connection.autocommit = True
            yield connection
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")
        finally:
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def start_session(self, session_data: Dict[str, Any]) -> Optional[str]:
        """
        Start a new counting session
        
        Args:
            session_data: Session information dictionary
            
        Returns:
            Session ID if successful, None otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO sessions (
                            session_name, 
                            input_source, 
                            start_time, 
                            status,
                            created_at,
                            updated_at
                        ) VALUES (
                            %(session_name)s,
                            %(input_source)s,
                            %(start_time)s,
                            %(status)s,
                            NOW(),
                            NOW()
                        ) RETURNING id
                    """, {
                        'session_name': session_data.get('session_name', 'People Counter Session'),
                        'input_source': session_data.get('input_source', 'video'),
                        'start_time': datetime.now(),
                        'status': 'active'
                    })
                    
                    result = cursor.fetchone()
                    if result:
                        self.session_id = str(result['id'])
                        logger.info(f"Session started with ID: {self.session_id}")
                        return self.session_id
                        
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
        if not self.session_id:
            logger.warning("No active session to end")
            return False
            
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE sessions 
                        SET status = %s, end_time = NOW(), updated_at = NOW()
                        WHERE id = %s
                    """, (status, self.session_id))
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Session {self.session_id} ended with status: {status}")
                        self.session_id = None
                        return True
                        
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    def log_movement(self, movement_data: Dict[str, Any]) -> bool:
        """
        Log a people movement event
        
        Args:
            movement_data: Movement information dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.session_id:
            logger.warning("No active session for logging movement")
            return False
            
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO people_movements (
                            session_id,
                            person_id,
                            movement_direction,
                            movement_time,
                            centroid_x,
                            centroid_y,
                            bounding_box_x1,
                            bounding_box_y1,
                            bounding_box_x2,
                            bounding_box_y2,
                            confidence_score,
                            frame_number,
                            created_at
                        ) VALUES (
                            %(session_id)s,
                            %(person_id)s,
                            %(movement_direction)s,
                            %(movement_time)s,
                            %(centroid_x)s,
                            %(centroid_y)s,
                            %(bounding_box_x1)s,
                            %(bounding_box_y1)s,
                            %(bounding_box_x2)s,
                            %(bounding_box_y2)s,
                            %(confidence_score)s,
                            %(frame_number)s,
                            NOW()
                        )
                    """, {
                        'session_id': self.session_id,
                        'person_id': int(movement_data.get('person_id', 0)),  # Convert numpy.int64 to int
                        'movement_direction': movement_data.get('direction'),
                        'movement_time': movement_data.get('movement_time', datetime.now()),
                        'centroid_x': float(movement_data.get('centroid', (0, 0))[0]),  # Convert to float
                        'centroid_y': float(movement_data.get('centroid', (0, 0))[1]),  # Convert to float
                        'bounding_box_x1': float(movement_data.get('bounding_box', (0, 0, 0, 0))[0]),  # Convert to float
                        'bounding_box_y1': float(movement_data.get('bounding_box', (0, 0, 0, 0))[1]),  # Convert to float
                        'bounding_box_x2': float(movement_data.get('bounding_box', (0, 0, 0, 0))[2]),  # Convert to float
                        'bounding_box_y2': float(movement_data.get('bounding_box', (0, 0, 0, 0))[3]),  # Convert to float
                        'confidence_score': float(movement_data.get('confidence', 0.0)),  # Convert to float
                        'frame_number': int(movement_data.get('frame_number', 0))  # Convert numpy.int64 to int
                    })
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to log movement: {e}")
            return False
    
    def log_realtime_metrics(self, metrics_data: Dict[str, Any]) -> bool:
        """
        Log real-time metrics
        
        Args:
            metrics_data: Metrics information dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.session_id:
            logger.warning("No active session for logging metrics")
            return False
            
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO realtime_metrics (
                            session_id,
                            current_people_count,
                            people_entered_last_minute,
                            people_exited_last_minute,
                            timestamp
                        ) VALUES (
                            %(session_id)s,
                            %(current_people_count)s,
                            %(people_entered_last_minute)s,
                            %(people_exited_last_minute)s,
                            %(timestamp)s
                        )
                    """, {
                        'session_id': self.session_id,
                        'current_people_count': metrics_data.get('current_count', 0),
                        'people_entered_last_minute': metrics_data.get('entered_count', 0),
                        'people_exited_last_minute': metrics_data.get('exited_count', 0),
                        'timestamp': metrics_data.get('timestamp', datetime.now())
                    })
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to log realtime metrics: {e}")
            return False
    
    def get_session_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get current session statistics
        
        Returns:
            Session statistics dictionary or None if failed
        """
        if not self.session_id:
            logger.warning("No active session to get stats")
            return None
            
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(CASE WHEN movement_direction = 'in' THEN 1 END) as people_entered,
                            COUNT(CASE WHEN movement_direction = 'out' THEN 1 END) as people_exited,
                            COUNT(CASE WHEN movement_direction = 'in' THEN 1 END) - 
                            COUNT(CASE WHEN movement_direction = 'out' THEN 1 END) as current_inside
                        FROM people_movements 
                        WHERE session_id = %s
                    """, (self.session_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        return {
                            'people_entered': result['people_entered'],
                            'people_exited': result['people_exited'],
                            'current_inside': result['current_inside']
                        }
                        
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return None
    
    def check_alert_threshold(self, current_count: int) -> bool:
        """
        Check if current count exceeds alert threshold
        
        Args:
            current_count: Current number of people inside
            
        Returns:
            True if threshold exceeded, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT threshold_value 
                        FROM alert_thresholds 
                        WHERE threshold_name = 'people_count' 
                        AND is_active = true
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """)
                    
                    result = cursor.fetchone()
                    if result:
                        threshold = result['threshold_value']
                        return current_count >= threshold
                        
        except Exception as e:
            logger.error(f"Failed to check alert threshold: {e}")
            
        return False
    
    def log_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Log an alert event
        
        Args:
            alert_data: Alert information dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.session_id:
            logger.warning("No active session for logging alert")
            return False
            
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO alert_logs (
                            session_id,
                            alert_type,
                            alert_message,
                            alert_level,
                            people_count,
                            threshold_value,
                            alert_time,
                            created_at
                        ) VALUES (
                            %(session_id)s,
                            %(alert_type)s,
                            %(alert_message)s,
                            %(alert_level)s,
                            %(people_count)s,
                            %(threshold_value)s,
                            %(alert_time)s,
                            NOW()
                        )
                    """, {
                        'session_id': self.session_id,
                        'alert_type': alert_data.get('alert_type', 'threshold_exceeded'),
                        'alert_message': alert_data.get('message', 'People count threshold exceeded'),
                        'alert_level': alert_data.get('level', 'warning'),
                        'people_count': alert_data.get('people_count', 0),
                        'threshold_value': alert_data.get('threshold_value', 0),
                        'alert_time': alert_data.get('alert_time', datetime.now())
                    })
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
            return False


# Factory function for creating database instance
def create_db_connection(config_path: Optional[str] = None) -> PeopleCounterDB:
    """
    Factory function to create database connection instance
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        PeopleCounterDB instance
    """
    return PeopleCounterDB(config_path)


# Convenience functions for easy integration
def get_db_instance() -> PeopleCounterDB:
    """
    Get a database instance with default configuration
    
    Returns:
        PeopleCounterDB instance
    """
    return create_db_connection()
