-- People Counter Database Schema
-- PostgreSQL Production-Ready Schema for Real-time Dashboard and Analytics
-- Version: 1.0
-- Created: 2025-09-04

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create custom types
CREATE TYPE session_status AS ENUM ('active', 'completed', 'error', 'cancelled');
CREATE TYPE detection_status AS ENUM ('detecting', 'tracking', 'waiting');
CREATE TYPE movement_direction AS ENUM ('in', 'out');

-- =============================================
-- CORE TABLES
-- =============================================

-- Sessions table: Track each video processing session
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(255) NOT NULL,
    input_source VARCHAR(500), -- Path to input video or camera URL
    output_path VARCHAR(500), -- Path to output video
    start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds DECIMAL(10,2),
    status session_status NOT NULL DEFAULT 'active',
    fps DECIMAL(8,2), -- Frames per second achieved
    total_frames INTEGER,
    resolution_width INTEGER,
    resolution_height INTEGER,
    confidence_threshold DECIMAL(3,2) DEFAULT 0.3,
    skip_frames INTEGER DEFAULT 3,
    max_disappeared INTEGER DEFAULT 15,
    max_distance INTEGER DEFAULT 80,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT sessions_duration_check CHECK (duration_seconds >= 0),
    CONSTRAINT sessions_fps_check CHECK (fps > 0),
    CONSTRAINT sessions_confidence_check CHECK (confidence_threshold BETWEEN 0 AND 1)
);

-- People movements table: Track individual person movements
CREATE TABLE people_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL, -- Object ID from tracking
    movement_direction movement_direction NOT NULL,
    movement_time TIMESTAMP WITH TIME ZONE NOT NULL,
    centroid_x DECIMAL(8,2),
    centroid_y DECIMAL(8,2),
    bounding_box_x1 DECIMAL(8,2),
    bounding_box_y1 DECIMAL(8,2),
    bounding_box_x2 DECIMAL(8,2),
    bounding_box_y2 DECIMAL(8,2),
    confidence_score DECIMAL(3,2),
    frame_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT people_movements_confidence_check CHECK (confidence_score BETWEEN 0 AND 1)
);

-- Session statistics table: Aggregated statistics per session
CREATE TABLE session_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    total_people_entered INTEGER NOT NULL DEFAULT 0,
    total_people_exited INTEGER NOT NULL DEFAULT 0,
    current_people_inside INTEGER NOT NULL DEFAULT 0,
    peak_people_count INTEGER NOT NULL DEFAULT 0,
    average_people_count DECIMAL(8,2) DEFAULT 0,
    detection_frames INTEGER DEFAULT 0,
    tracking_frames INTEGER DEFAULT 0,
    waiting_frames INTEGER DEFAULT 0,
    total_detections INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    false_negatives INTEGER DEFAULT 0,
    accuracy_percentage DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT session_stats_entered_check CHECK (total_people_entered >= 0),
    CONSTRAINT session_stats_exited_check CHECK (total_people_exited >= 0),
    CONSTRAINT session_stats_inside_check CHECK (current_people_inside >= 0),
    CONSTRAINT session_stats_peak_check CHECK (peak_people_count >= 0),
    CONSTRAINT session_stats_accuracy_check CHECK (accuracy_percentage BETWEEN 0 AND 100)
);

-- Real-time metrics table: For dashboard real-time updates
CREATE TABLE realtime_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    current_people_count INTEGER NOT NULL DEFAULT 0,
    people_entered_last_minute INTEGER DEFAULT 0,
    people_exited_last_minute INTEGER DEFAULT 0,
    detection_status detection_status NOT NULL DEFAULT 'waiting',
    fps_current DECIMAL(8,2),
    cpu_usage_percentage DECIMAL(5,2),
    memory_usage_mb DECIMAL(10,2),
    processing_latency_ms DECIMAL(8,2),
    
    -- Constraints
    CONSTRAINT realtime_people_count_check CHECK (current_people_count >= 0),
    CONSTRAINT realtime_fps_check CHECK (fps_current > 0),
    CONSTRAINT realtime_cpu_check CHECK (cpu_usage_percentage BETWEEN 0 AND 100),
    CONSTRAINT realtime_memory_check CHECK (memory_usage_mb >= 0)
);

-- =============================================
-- ANALYTICS TABLES
-- =============================================

-- Hourly statistics for analytics
CREATE TABLE hourly_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    hour_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    people_entered INTEGER NOT NULL DEFAULT 0,
    people_exited INTEGER NOT NULL DEFAULT 0,
    peak_people_count INTEGER NOT NULL DEFAULT 0,
    average_people_count DECIMAL(8,2) DEFAULT 0,
    total_detections INTEGER DEFAULT 0,
    detection_accuracy DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Unique constraint for hourly data
    CONSTRAINT hourly_stats_unique UNIQUE (session_id, hour_timestamp)
);

-- Daily statistics for analytics
CREATE TABLE daily_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    date_timestamp DATE NOT NULL,
    total_people_entered INTEGER NOT NULL DEFAULT 0,
    total_people_exited INTEGER NOT NULL DEFAULT 0,
    peak_people_count INTEGER NOT NULL DEFAULT 0,
    average_people_count DECIMAL(8,2) DEFAULT 0,
    total_detections INTEGER DEFAULT 0,
    total_session_duration DECIMAL(10,2),
    detection_accuracy DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Unique constraint for daily data
    CONSTRAINT daily_stats_unique UNIQUE (session_id, date_timestamp)
);

-- =============================================
-- SYSTEM TABLES
-- =============================================

-- System configuration table
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) NOT NULL DEFAULT 'string',
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Alert thresholds table
CREATE TABLE alert_thresholds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    threshold_name VARCHAR(100) NOT NULL,
    threshold_value INTEGER NOT NULL,
    alert_message TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Alert logs table
CREATE TABLE alert_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    threshold_id UUID REFERENCES alert_thresholds(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_message TEXT NOT NULL,
    current_value INTEGER NOT NULL,
    threshold_value INTEGER NOT NULL,
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    is_resolved BOOLEAN NOT NULL DEFAULT false
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Sessions indexes
CREATE INDEX idx_sessions_start_time ON sessions(start_time);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);

-- People movements indexes
CREATE INDEX idx_people_movements_session_id ON people_movements(session_id);
CREATE INDEX idx_people_movements_time ON people_movements(movement_time);
CREATE INDEX idx_people_movements_direction ON people_movements(movement_direction);
CREATE INDEX idx_people_movements_person_id ON people_movements(person_id);

-- Session statistics indexes
CREATE INDEX idx_session_stats_session_id ON session_statistics(session_id);
CREATE INDEX idx_session_stats_created_at ON session_statistics(created_at);

-- Real-time metrics indexes
CREATE INDEX idx_realtime_session_id ON realtime_metrics(session_id);
CREATE INDEX idx_realtime_timestamp ON realtime_metrics(timestamp);
CREATE INDEX idx_realtime_session_timestamp ON realtime_metrics(session_id, timestamp);

-- Analytics indexes
CREATE INDEX idx_hourly_session_hour ON hourly_statistics(session_id, hour_timestamp);
CREATE INDEX idx_daily_session_date ON daily_statistics(session_id, date_timestamp);

-- Alert indexes
CREATE INDEX idx_alert_logs_session_id ON alert_logs(session_id);
CREATE INDEX idx_alert_logs_triggered_at ON alert_logs(triggered_at);
CREATE INDEX idx_alert_logs_resolved ON alert_logs(is_resolved);

-- =============================================
-- TRIGGERS AND FUNCTIONS
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_session_statistics_updated_at BEFORE UPDATE ON session_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_thresholds_updated_at BEFORE UPDATE ON alert_thresholds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate current people inside
CREATE OR REPLACE FUNCTION calculate_current_people_inside(session_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    people_inside INTEGER;
BEGIN
    SELECT 
        COALESCE(
            (SELECT COUNT(*) FROM people_movements 
             WHERE session_id = session_uuid AND movement_direction = 'in') -
            (SELECT COUNT(*) FROM people_movements 
             WHERE session_id = session_uuid AND movement_direction = 'out'),
            0
        ) INTO people_inside;
    
    RETURN people_inside;
END;
$$ LANGUAGE plpgsql;

-- Function to update session statistics
CREATE OR REPLACE FUNCTION update_session_statistics()
RETURNS TRIGGER AS $$
DECLARE
    session_uuid UUID;
    people_entered INTEGER;
    people_exited INTEGER;
    people_inside INTEGER;
    peak_count INTEGER;
BEGIN
    session_uuid := NEW.session_id;
    
    -- Get counts
    SELECT COUNT(*) INTO people_entered 
    FROM people_movements 
    WHERE session_id = session_uuid AND movement_direction = 'in';
    
    SELECT COUNT(*) INTO people_exited 
    FROM people_movements 
    WHERE session_id = session_uuid AND movement_direction = 'out';
    
    people_inside := people_entered - people_exited;
    
    -- Get peak count
    SELECT COALESCE(MAX(current_people_count), 0) INTO peak_count
    FROM realtime_metrics 
    WHERE session_id = session_uuid;
    
    -- Update or insert session statistics
    INSERT INTO session_statistics (
        session_id, 
        total_people_entered, 
        total_people_exited, 
        current_people_inside,
        peak_people_count
    ) VALUES (
        session_uuid, 
        people_entered, 
        people_exited, 
        people_inside,
        peak_count
    )
    ON CONFLICT (session_id) 
    DO UPDATE SET
        total_people_entered = people_entered,
        total_people_exited = people_exited,
        current_people_inside = people_inside,
        peak_people_count = GREATEST(session_statistics.peak_people_count, peak_count),
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update statistics when movement is recorded
CREATE TRIGGER update_stats_on_movement 
    AFTER INSERT ON people_movements
    FOR EACH ROW EXECUTE FUNCTION update_session_statistics();

-- =============================================
-- VIEWS FOR DASHBOARD
-- =============================================

-- Current session overview
CREATE VIEW current_session_overview AS
SELECT 
    s.id,
    s.session_name,
    s.status,
    s.start_time,
    s.duration_seconds,
    s.fps,
    ss.total_people_entered,
    ss.total_people_exited,
    ss.current_people_inside,
    ss.peak_people_count,
    ss.accuracy_percentage
FROM sessions s
LEFT JOIN session_statistics ss ON s.id = ss.session_id
WHERE s.status = 'active'
ORDER BY s.start_time DESC;

-- Recent movements for real-time dashboard
CREATE VIEW recent_movements AS
SELECT 
    pm.id,
    pm.session_id,
    s.session_name,
    pm.person_id,
    pm.movement_direction,
    pm.movement_time,
    pm.centroid_x,
    pm.centroid_y,
    pm.confidence_score
FROM people_movements pm
JOIN sessions s ON pm.session_id = s.id
WHERE pm.movement_time >= NOW() - INTERVAL '1 hour'
ORDER BY pm.movement_time DESC;

-- Hourly analytics view
CREATE VIEW hourly_analytics AS
SELECT 
    s.session_name,
    hs.hour_timestamp,
    hs.people_entered,
    hs.people_exited,
    hs.peak_people_count,
    hs.average_people_count,
    hs.detection_accuracy
FROM hourly_statistics hs
JOIN sessions s ON hs.session_id = s.id
ORDER BY hs.hour_timestamp DESC;

-- Daily analytics view
CREATE VIEW daily_analytics AS
SELECT 
    s.session_name,
    ds.date_timestamp,
    ds.total_people_entered,
    ds.total_people_exited,
    ds.peak_people_count,
    ds.average_people_count,
    ds.total_session_duration,
    ds.detection_accuracy
FROM daily_statistics ds
JOIN sessions s ON ds.session_id = s.id
ORDER BY ds.date_timestamp DESC;

-- =============================================
-- COMMENTS
-- =============================================

COMMENT ON TABLE sessions IS 'Core table storing video processing sessions';
COMMENT ON TABLE people_movements IS 'Individual person movement records with tracking data';
COMMENT ON TABLE session_statistics IS 'Aggregated statistics per session';
COMMENT ON TABLE realtime_metrics IS 'Real-time metrics for dashboard updates';
COMMENT ON TABLE hourly_statistics IS 'Hourly aggregated data for analytics';
COMMENT ON TABLE daily_statistics IS 'Daily aggregated data for analytics';
COMMENT ON TABLE system_config IS 'System configuration parameters';
COMMENT ON TABLE alert_thresholds IS 'Alert threshold configurations';
COMMENT ON TABLE alert_logs IS 'Alert trigger logs and history';

COMMENT ON COLUMN sessions.session_name IS 'Human-readable name for the session';
COMMENT ON COLUMN sessions.input_source IS 'Path to input video file or camera URL';
COMMENT ON COLUMN sessions.output_path IS 'Path to generated output video';
COMMENT ON COLUMN sessions.duration_seconds IS 'Total processing duration in seconds';
COMMENT ON COLUMN sessions.fps IS 'Average frames per second achieved';
COMMENT ON COLUMN sessions.confidence_threshold IS 'Detection confidence threshold used';
COMMENT ON COLUMN sessions.skip_frames IS 'Number of frames skipped between detections';
COMMENT ON COLUMN sessions.max_disappeared IS 'Max frames before object considered disappeared';
COMMENT ON COLUMN sessions.max_distance IS 'Max distance for object tracking';

COMMENT ON COLUMN people_movements.person_id IS 'Object ID from tracking system';
COMMENT ON COLUMN people_movements.movement_direction IS 'Direction of movement: in or out';
COMMENT ON COLUMN people_movements.movement_time IS 'Timestamp when movement occurred';
COMMENT ON COLUMN people_movements.centroid_x IS 'X coordinate of object centroid';
COMMENT ON COLUMN people_movements.centroid_y IS 'Y coordinate of object centroid';
COMMENT ON COLUMN people_movements.bounding_box_x1 IS 'Left edge of bounding box';
COMMENT ON COLUMN people_movements.bounding_box_y1 IS 'Top edge of bounding box';
COMMENT ON COLUMN people_movements.bounding_box_x2 IS 'Right edge of bounding box';
COMMENT ON COLUMN people_movements.bounding_box_y2 IS 'Bottom edge of bounding box';
COMMENT ON COLUMN people_movements.confidence_score IS 'Detection confidence score';
COMMENT ON COLUMN people_movements.frame_number IS 'Frame number when movement occurred';
