-- Seed Data for People Counter Database
-- Initial configuration and test data

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('default_confidence_threshold', '0.3', 'decimal', 'Default detection confidence threshold'),
('default_skip_frames', '3', 'integer', 'Default number of frames to skip between detections'),
('default_max_disappeared', '15', 'integer', 'Default max frames before object considered disappeared'),
('default_max_distance', '80', 'integer', 'Default max distance for object tracking'),
('email_alerts_enabled', 'true', 'boolean', 'Enable email alerts for threshold breaches'),
('dashboard_refresh_interval', '5000', 'integer', 'Dashboard refresh interval in milliseconds'),
('realtime_enabled', 'true', 'boolean', 'Enable real-time metrics collection'),
('backup_enabled', 'true', 'boolean', 'Enable automatic database backups'),
('backup_retention_days', '30', 'integer', 'Number of days to retain backups'),
('max_sessions_display', '50', 'integer', 'Maximum number of sessions to display in dashboard'),
('alert_email_smtp_host', 'smtp.gmail.com', 'string', 'SMTP host for email alerts'),
('alert_email_smtp_port', '587', 'integer', 'SMTP port for email alerts'),
('alert_email_from', 'noreply@peoplecounter.com', 'string', 'From email address for alerts'),
('video_storage_path', '/data/videos', 'string', 'Path for storing input videos'),
('output_storage_path', '/data/outputs', 'string', 'Path for storing output videos'),
('log_level', 'INFO', 'string', 'Application log level'),
('api_rate_limit', '1000', 'integer', 'API rate limit per hour'),
('health_check_interval', '30', 'integer', 'Health check interval in seconds');

-- Insert default alert thresholds
INSERT INTO alert_thresholds (threshold_name, threshold_value, alert_message, is_active) VALUES
('max_people_count', 50, 'Maximum people count exceeded', true),
('min_people_count', 0, 'Minimum people count threshold', true),
('detection_accuracy_low', 80, 'Detection accuracy below threshold', true),
('fps_low', 15, 'FPS below threshold', true),
('cpu_usage_high', 90, 'CPU usage above threshold', true),
('memory_usage_high', 80, 'Memory usage above threshold', true);

-- Create test session for demonstration
INSERT INTO sessions (
    session_name,
    input_source,
    output_path,
    status,
    fps,
    total_frames,
    resolution_width,
    resolution_height,
    confidence_threshold,
    skip_frames,
    max_disappeared,
    max_distance
) VALUES (
    'Test Session - Demo',
    'utils/data/tests/test_1.mp4',
    'output/test_demo.mp4',
    'completed',
    30.5,
    1200,
    640,
    480,
    0.3,
    3,
    15,
    80
);

-- Log seed data completion
INSERT INTO system_config (config_key, config_value, config_type, description) 
VALUES ('seed_data_completed', 'true', 'boolean', 'Initial seed data inserted');