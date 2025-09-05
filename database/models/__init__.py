# People Counter Database Models
# SQLAlchemy models for the people counter system

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    Text, ForeignKey, Enum, DECIMAL, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

class SessionStatus(enum.Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class DetectionStatus(enum.Enum):
    """Detection status enumeration"""
    DETECTING = "detecting"
    TRACKING = "tracking"
    WAITING = "waiting"

class MovementDirection(enum.Enum):
    """Movement direction enumeration"""
    IN = "in"
    OUT = "out"

class Session(Base):
    """Sessions table: Track each video processing session"""
    __tablename__ = 'sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_name = Column(String(255), nullable=False)
    input_source = Column(String(500))  # Path to input video or camera URL
    output_path = Column(String(500))   # Path to output video
    start_time = Column(DateTime(timezone=True), nullable=False, default=func.now())
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(DECIMAL(10, 2))
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.ACTIVE)
    fps = Column(DECIMAL(8, 2))  # Frames per second achieved
    total_frames = Column(Integer)
    resolution_width = Column(Integer)
    resolution_height = Column(Integer)
    confidence_threshold = Column(DECIMAL(3, 2), default=0.3)
    skip_frames = Column(Integer, default=3)
    max_disappeared = Column(Integer, default=15)
    max_distance = Column(Integer, default=80)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    people_movements = relationship("PeopleMovement", back_populates="session", cascade="all, delete-orphan")
    session_statistics = relationship("SessionStatistics", back_populates="session", uselist=False, cascade="all, delete-orphan")
    realtime_metrics = relationship("RealtimeMetrics", back_populates="session", cascade="all, delete-orphan")
    hourly_statistics = relationship("HourlyStatistics", back_populates="session", cascade="all, delete-orphan")
    daily_statistics = relationship("DailyStatistics", back_populates="session", cascade="all, delete-orphan")
    alert_logs = relationship("AlertLog", back_populates="session", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('duration_seconds >= 0', name='sessions_duration_check'),
        CheckConstraint('fps > 0', name='sessions_fps_check'),
        CheckConstraint('confidence_threshold BETWEEN 0 AND 1', name='sessions_confidence_check'),
        Index('idx_sessions_start_time', 'start_time'),
        Index('idx_sessions_status', 'status'),
        Index('idx_sessions_created_at', 'created_at'),
    )

class PeopleMovement(Base):
    """People movements table: Track individual person movements"""
    __tablename__ = 'people_movements'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    person_id = Column(Integer, nullable=False)  # Object ID from tracking
    movement_direction = Column(Enum(MovementDirection), nullable=False)
    movement_time = Column(DateTime(timezone=True), nullable=False)
    centroid_x = Column(DECIMAL(8, 2))
    centroid_y = Column(DECIMAL(8, 2))
    bounding_box_x1 = Column(DECIMAL(8, 2))
    bounding_box_y1 = Column(DECIMAL(8, 2))
    bounding_box_x2 = Column(DECIMAL(8, 2))
    bounding_box_y2 = Column(DECIMAL(8, 2))
    confidence_score = Column(DECIMAL(3, 2))
    frame_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="people_movements")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('confidence_score BETWEEN 0 AND 1', name='people_movements_confidence_check'),
        Index('idx_people_movements_session_id', 'session_id'),
        Index('idx_people_movements_time', 'movement_time'),
        Index('idx_people_movements_direction', 'movement_direction'),
        Index('idx_people_movements_person_id', 'person_id'),
    )

class SessionStatistics(Base):
    """Session statistics table: Aggregated statistics per session"""
    __tablename__ = 'session_statistics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, unique=True)
    total_people_entered = Column(Integer, nullable=False, default=0)
    total_people_exited = Column(Integer, nullable=False, default=0)
    current_people_inside = Column(Integer, nullable=False, default=0)
    peak_people_count = Column(Integer, nullable=False, default=0)
    average_people_count = Column(DECIMAL(8, 2), default=0)
    detection_frames = Column(Integer, default=0)
    tracking_frames = Column(Integer, default=0)
    waiting_frames = Column(Integer, default=0)
    total_detections = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    false_negatives = Column(Integer, default=0)
    accuracy_percentage = Column(DECIMAL(5, 2))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="session_statistics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_people_entered >= 0', name='session_stats_entered_check'),
        CheckConstraint('total_people_exited >= 0', name='session_stats_exited_check'),
        CheckConstraint('current_people_inside >= 0', name='session_stats_inside_check'),
        CheckConstraint('peak_people_count >= 0', name='session_stats_peak_check'),
        CheckConstraint('accuracy_percentage BETWEEN 0 AND 100', name='session_stats_accuracy_check'),
        Index('idx_session_stats_session_id', 'session_id'),
        Index('idx_session_stats_created_at', 'created_at'),
    )

class RealtimeMetrics(Base):
    """Real-time metrics table: For dashboard real-time updates"""
    __tablename__ = 'realtime_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    current_people_count = Column(Integer, nullable=False, default=0)
    people_entered_last_minute = Column(Integer, default=0)
    people_exited_last_minute = Column(Integer, default=0)
    detection_status = Column(Enum(DetectionStatus), nullable=False, default=DetectionStatus.WAITING)
    fps_current = Column(DECIMAL(8, 2))
    cpu_usage_percentage = Column(DECIMAL(5, 2))
    memory_usage_mb = Column(DECIMAL(10, 2))
    processing_latency_ms = Column(DECIMAL(8, 2))
    
    # Relationships
    session = relationship("Session", back_populates="realtime_metrics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('current_people_count >= 0', name='realtime_people_count_check'),
        CheckConstraint('fps_current > 0', name='realtime_fps_check'),
        CheckConstraint('cpu_usage_percentage BETWEEN 0 AND 100', name='realtime_cpu_check'),
        CheckConstraint('memory_usage_mb >= 0', name='realtime_memory_check'),
        Index('idx_realtime_session_id', 'session_id'),
        Index('idx_realtime_timestamp', 'timestamp'),
        Index('idx_realtime_session_timestamp', 'session_id', 'timestamp'),
    )

class HourlyStatistics(Base):
    """Hourly statistics for analytics"""
    __tablename__ = 'hourly_statistics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    hour_timestamp = Column(DateTime(timezone=True), nullable=False)
    people_entered = Column(Integer, nullable=False, default=0)
    people_exited = Column(Integer, nullable=False, default=0)
    peak_people_count = Column(Integer, nullable=False, default=0)
    average_people_count = Column(DECIMAL(8, 2), default=0)
    total_detections = Column(Integer, default=0)
    detection_accuracy = Column(DECIMAL(5, 2))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="hourly_statistics")
    
    # Constraints
    __table_args__ = (
        Index('idx_hourly_session_hour', 'session_id', 'hour_timestamp', unique=True),
    )

class DailyStatistics(Base):
    """Daily statistics for analytics"""
    __tablename__ = 'daily_statistics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    date_timestamp = Column(DateTime(timezone=True), nullable=False)
    total_people_entered = Column(Integer, nullable=False, default=0)
    total_people_exited = Column(Integer, nullable=False, default=0)
    peak_people_count = Column(Integer, nullable=False, default=0)
    average_people_count = Column(DECIMAL(8, 2), default=0)
    total_detections = Column(Integer, default=0)
    total_session_duration = Column(DECIMAL(10, 2))
    detection_accuracy = Column(DECIMAL(5, 2))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="daily_statistics")
    
    # Constraints
    __table_args__ = (
        Index('idx_daily_session_date', 'session_id', 'date_timestamp', unique=True),
    )

class SystemConfig(Base):
    """System configuration table"""
    __tablename__ = 'system_config'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False, default='string')
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

class AlertThreshold(Base):
    """Alert thresholds table"""
    __tablename__ = 'alert_thresholds'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'))
    threshold_name = Column(String(100), nullable=False)
    threshold_value = Column(Integer, nullable=False)
    alert_message = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    session = relationship("Session")
    alert_logs = relationship("AlertLog", back_populates="threshold")

class AlertLog(Base):
    """Alert logs table"""
    __tablename__ = 'alert_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    threshold_id = Column(UUID(as_uuid=True), ForeignKey('alert_thresholds.id', ondelete='SET NULL'))
    alert_type = Column(String(50), nullable=False)
    alert_message = Column(Text, nullable=False)
    current_value = Column(Integer, nullable=False)
    threshold_value = Column(Integer, nullable=False)
    triggered_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    is_resolved = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    session = relationship("Session", back_populates="alert_logs")
    threshold = relationship("AlertThreshold", back_populates="alert_logs")
    
    # Constraints
    __table_args__ = (
        Index('idx_alert_logs_session_id', 'session_id'),
        Index('idx_alert_logs_triggered_at', 'triggered_at'),
        Index('idx_alert_logs_resolved', 'is_resolved'),
    )

# Export all models
__all__ = [
    'Base',
    'SessionStatus',
    'DetectionStatus', 
    'MovementDirection',
    'Session',
    'PeopleMovement',
    'SessionStatistics',
    'RealtimeMetrics',
    'HourlyStatistics',
    'DailyStatistics',
    'SystemConfig',
    'AlertThreshold',
    'AlertLog'
]
