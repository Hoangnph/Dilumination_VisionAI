# People Counter Database API
# FastAPI endpoints for database operations

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging

from .config.settings import app_config
from .utils.database import get_db, get_async_db, db_manager
from .models import (
    Session as DBSession, PeopleMovement, SessionStatistics, 
    RealtimeMetrics, HourlyStatistics, DailyStatistics,
    AlertThreshold, AlertLog, SystemConfig,
    SessionStatus, MovementDirection, DetectionStatus
)

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="People Counter Database API",
    description="API for managing people counter database operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    is_healthy = await db_manager.health_check()
    if is_healthy:
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    else:
        raise HTTPException(status_code=503, detail="Database unhealthy")

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with connection info"""
    is_healthy = await db_manager.health_check()
    conn_info = await db_manager.get_connection_info()
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.utcnow(),
        "database": conn_info
    }

# Session management endpoints
@app.post("/sessions")
async def create_session(
    session_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a new session"""
    try:
        db_session = DBSession(
            session_name=session_data.get("session_name", f"Session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            input_source=session_data.get("input_source"),
            output_path=session_data.get("output_path"),
            confidence_threshold=session_data.get("confidence_threshold", 0.3),
            skip_frames=session_data.get("skip_frames", 3),
            max_disappeared=session_data.get("max_disappeared", 15),
            max_distance=session_data.get("max_distance", 80),
            status=SessionStatus.ACTIVE
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Created session: {db_session.id}")
        return {"session_id": str(db_session.id), "status": "created"}
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def get_sessions(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get sessions with pagination and filtering"""
    try:
        query = db.query(DBSession)
        
        if status:
            query = query.filter(DBSession.status == SessionStatus(status))
        
        sessions = query.order_by(desc(DBSession.start_time)).offset(offset).limit(limit).all()
        
        return {
            "sessions": [
                {
                    "id": str(session.id),
                    "session_name": session.session_name,
                    "status": session.status.value,
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                    "duration_seconds": float(session.duration_seconds) if session.duration_seconds else None,
                    "fps": float(session.fps) if session.fps else None,
                    "total_frames": session.total_frames,
                    "resolution": f"{session.resolution_width}x{session.resolution_height}" if session.resolution_width else None
                }
                for session in sessions
            ],
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get specific session details"""
    try:
        session_uuid = uuid.UUID(session_id)
        session = db.query(DBSession).filter(DBSession.id == session_uuid).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get session statistics
        stats = db.query(SessionStatistics).filter(SessionStatistics.session_id == session_uuid).first()
        
        return {
            "id": str(session.id),
            "session_name": session.session_name,
            "input_source": session.input_source,
            "output_path": session.output_path,
            "status": session.status.value,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration_seconds": float(session.duration_seconds) if session.duration_seconds else None,
            "fps": float(session.fps) if session.fps else None,
            "total_frames": session.total_frames,
            "resolution_width": session.resolution_width,
            "resolution_height": session.resolution_height,
            "confidence_threshold": float(session.confidence_threshold),
            "skip_frames": session.skip_frames,
            "max_disappeared": session.max_disappeared,
            "max_distance": session.max_distance,
            "statistics": {
                "total_people_entered": stats.total_people_entered if stats else 0,
                "total_people_exited": stats.total_people_exited if stats else 0,
                "current_people_inside": stats.current_people_inside if stats else 0,
                "peak_people_count": stats.peak_people_count if stats else 0,
                "accuracy_percentage": float(stats.accuracy_percentage) if stats and stats.accuracy_percentage else None
            } if stats else None
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update session information"""
    try:
        session_uuid = uuid.UUID(session_id)
        session = db.query(DBSession).filter(DBSession.id == session_uuid).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update allowed fields
        allowed_fields = [
            "session_name", "output_path", "end_time", "duration_seconds",
            "fps", "total_frames", "resolution_width", "resolution_height",
            "status"
        ]
        
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(session, field):
                if field == "status" and isinstance(value, str):
                    setattr(session, field, SessionStatus(value))
                else:
                    setattr(session, field, value)
        
        session.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Updated session: {session_id}")
        return {"status": "updated", "session_id": session_id}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to update session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# People movement endpoints
@app.post("/sessions/{session_id}/movements")
async def record_movement(
    session_id: str,
    movement_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Record a people movement"""
    try:
        session_uuid = uuid.UUID(session_id)
        
        # Verify session exists
        session = db.query(DBSession).filter(DBSession.id == session_uuid).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        movement = PeopleMovement(
            session_id=session_uuid,
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
        
        db.add(movement)
        db.commit()
        db.refresh(movement)
        
        logger.info(f"Recorded movement for session {session_id}: {movement_data['movement_direction']}")
        return {"movement_id": str(movement.id), "status": "recorded"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {e}")
    except Exception as e:
        logger.error(f"Failed to record movement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/movements")
async def get_movements(
    session_id: str,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    direction: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get movements for a session"""
    try:
        session_uuid = uuid.UUID(session_id)
        
        query = db.query(PeopleMovement).filter(PeopleMovement.session_id == session_uuid)
        
        if direction:
            query = query.filter(PeopleMovement.movement_direction == MovementDirection(direction))
        
        movements = query.order_by(desc(PeopleMovement.movement_time)).offset(offset).limit(limit).all()
        
        return {
            "movements": [
                {
                    "id": str(movement.id),
                    "person_id": movement.person_id,
                    "movement_direction": movement.movement_direction.value,
                    "movement_time": movement.movement_time,
                    "centroid": {
                        "x": float(movement.centroid_x) if movement.centroid_x else None,
                        "y": float(movement.centroid_y) if movement.centroid_y else None
                    },
                    "bounding_box": {
                        "x1": float(movement.bounding_box_x1) if movement.bounding_box_x1 else None,
                        "y1": float(movement.bounding_box_y1) if movement.bounding_box_y1 else None,
                        "x2": float(movement.bounding_box_x2) if movement.bounding_box_x2 else None,
                        "y2": float(movement.bounding_box_y2) if movement.bounding_box_y2 else None
                    },
                    "confidence_score": float(movement.confidence_score) if movement.confidence_score else None,
                    "frame_number": movement.frame_number
                }
                for movement in movements
            ],
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get movements for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Real-time metrics endpoints
@app.post("/sessions/{session_id}/metrics")
async def record_realtime_metrics(
    session_id: str,
    metrics_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Record real-time metrics"""
    try:
        session_uuid = uuid.UUID(session_id)
        
        # Verify session exists
        session = db.query(DBSession).filter(DBSession.id == session_uuid).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        metrics = RealtimeMetrics(
            session_id=session_uuid,
            current_people_count=metrics_data["current_people_count"],
            people_entered_last_minute=metrics_data.get("people_entered_last_minute", 0),
            people_exited_last_minute=metrics_data.get("people_exited_last_minute", 0),
            detection_status=DetectionStatus(metrics_data.get("detection_status", "waiting")),
            fps_current=metrics_data.get("fps_current"),
            cpu_usage_percentage=metrics_data.get("cpu_usage_percentage"),
            memory_usage_mb=metrics_data.get("memory_usage_mb"),
            processing_latency_ms=metrics_data.get("processing_latency_ms")
        )
        
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        
        return {"metrics_id": str(metrics.id), "status": "recorded"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {e}")
    except Exception as e:
        logger.error(f"Failed to record metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/metrics/recent")
async def get_recent_metrics(
    session_id: str,
    minutes: int = Query(10, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get recent metrics for a session"""
    try:
        session_uuid = uuid.UUID(session_id)
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        metrics = db.query(RealtimeMetrics).filter(
            and_(
                RealtimeMetrics.session_id == session_uuid,
                RealtimeMetrics.timestamp >= since
            )
        ).order_by(desc(RealtimeMetrics.timestamp)).limit(100).all()
        
        return {
            "metrics": [
                {
                    "timestamp": metric.timestamp,
                    "current_people_count": metric.current_people_count,
                    "people_entered_last_minute": metric.people_entered_last_minute,
                    "people_exited_last_minute": metric.people_exited_last_minute,
                    "detection_status": metric.detection_status.value,
                    "fps_current": float(metric.fps_current) if metric.fps_current else None,
                    "cpu_usage_percentage": float(metric.cpu_usage_percentage) if metric.cpu_usage_percentage else None,
                    "memory_usage_mb": float(metric.memory_usage_mb) if metric.memory_usage_mb else None,
                    "processing_latency_ms": float(metric.processing_latency_ms) if metric.processing_latency_ms else None
                }
                for metric in metrics
            ],
            "period_minutes": minutes
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get recent metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/analytics/hourly")
async def get_hourly_analytics(
    session_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    db: Session = Depends(get_db)
):
    """Get hourly analytics"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(HourlyStatistics).filter(HourlyStatistics.hour_timestamp >= since)
        
        if session_id:
            session_uuid = uuid.UUID(session_id)
            query = query.filter(HourlyStatistics.session_id == session_uuid)
        
        analytics = query.order_by(desc(HourlyStatistics.hour_timestamp)).all()
        
        return {
            "analytics": [
                {
                    "session_id": str(analytic.session_id),
                    "hour_timestamp": analytic.hour_timestamp,
                    "people_entered": analytic.people_entered,
                    "people_exited": analytic.people_exited,
                    "peak_people_count": analytic.peak_people_count,
                    "average_people_count": float(analytic.average_people_count) if analytic.average_people_count else None,
                    "total_detections": analytic.total_detections,
                    "detection_accuracy": float(analytic.detection_accuracy) if analytic.detection_accuracy else None
                }
                for analytic in analytics
            ],
            "period_hours": hours
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get hourly analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/daily")
async def get_daily_analytics(
    session_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),  # Max 1 year
    db: Session = Depends(get_db)
):
    """Get daily analytics"""
    try:
        since = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(DailyStatistics).filter(DailyStatistics.date_timestamp >= since)
        
        if session_id:
            session_uuid = uuid.UUID(session_id)
            query = query.filter(DailyStatistics.session_id == session_uuid)
        
        analytics = query.order_by(desc(DailyStatistics.date_timestamp)).all()
        
        return {
            "analytics": [
                {
                    "session_id": str(analytic.session_id),
                    "date_timestamp": analytic.date_timestamp,
                    "total_people_entered": analytic.total_people_entered,
                    "total_people_exited": analytic.total_people_exited,
                    "peak_people_count": analytic.peak_people_count,
                    "average_people_count": float(analytic.average_people_count) if analytic.average_people_count else None,
                    "total_detections": analytic.total_detections,
                    "total_session_duration": float(analytic.total_session_duration) if analytic.total_session_duration else None,
                    "detection_accuracy": float(analytic.detection_accuracy) if analytic.detection_accuracy else None
                }
                for analytic in analytics
            ],
            "period_days": days
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get daily analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard summary endpoint
@app.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary data"""
    try:
        # Get active sessions
        active_sessions = db.query(DBSession).filter(DBSession.status == SessionStatus.ACTIVE).count()
        
        # Get total sessions today
        today = datetime.utcnow().date()
        sessions_today = db.query(DBSession).filter(
            func.date(DBSession.start_time) == today
        ).count()
        
        # Get total people entered today
        people_entered_today = db.query(func.sum(SessionStatistics.total_people_entered)).join(
            DBSession, SessionStatistics.session_id == DBSession.id
        ).filter(func.date(DBSession.start_time) == today).scalar() or 0
        
        # Get total people exited today
        people_exited_today = db.query(func.sum(SessionStatistics.total_people_exited)).join(
            DBSession, SessionStatistics.session_id == DBSession.id
        ).filter(func.date(DBSession.start_time) == today).scalar() or 0
        
        # Get recent movements (last hour)
        recent_movements = db.query(PeopleMovement).filter(
            PeopleMovement.movement_time >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        return {
            "active_sessions": active_sessions,
            "sessions_today": sessions_today,
            "people_entered_today": people_entered_today,
            "people_exited_today": people_exited_today,
            "recent_movements": recent_movements,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.utcnow()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow()}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await db_manager.initialize()
        logger.info("Database API started successfully")
    except Exception as e:
        logger.error(f"Failed to start database API: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        db_manager.close()
        logger.info("Database API shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
