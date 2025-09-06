-- =====================================================
-- SSE Database Triggers for Real-time Notifications
-- =====================================================

-- Enable pg_notify extension if not already enabled
-- CREATE EXTENSION IF NOT EXISTS pg_notify;

-- =====================================================
-- 1. SESSION CHANGES TRIGGER
-- =====================================================

-- Function to notify session changes
CREATE OR REPLACE FUNCTION notify_session_change()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    -- Create payload with change type and data
    payload = json_build_object(
        'table', 'sessions',
        'action', TG_OP,
        'data', row_to_json(NEW),
        'old_data', CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        'timestamp', extract(epoch from now())
    );
    
    -- Send notification
    PERFORM pg_notify('session_changes', payload::text);
    
    -- Return appropriate row
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for sessions table
DROP TRIGGER IF EXISTS session_change_trigger ON sessions;
CREATE TRIGGER session_change_trigger
    AFTER INSERT OR UPDATE OR DELETE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION notify_session_change();

-- =====================================================
-- 2. PEOPLE MOVEMENTS TRIGGER
-- =====================================================

-- Function to notify movement changes
CREATE OR REPLACE FUNCTION notify_movement_change()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    -- Create payload with change type and data
    payload = json_build_object(
        'table', 'people_movements',
        'action', TG_OP,
        'data', row_to_json(NEW),
        'old_data', CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        'timestamp', extract(epoch from now())
    );
    
    -- Send notification
    PERFORM pg_notify('movement_changes', payload::text);
    
    -- Return appropriate row
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for people_movements table
DROP TRIGGER IF EXISTS movement_change_trigger ON people_movements;
CREATE TRIGGER movement_change_trigger
    AFTER INSERT OR UPDATE OR DELETE ON people_movements
    FOR EACH ROW
    EXECUTE FUNCTION notify_movement_change();

-- =====================================================
-- 3. ALERT LOGS TRIGGER
-- =====================================================

-- Function to notify alert changes
CREATE OR REPLACE FUNCTION notify_alert_change()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    -- Create payload with change type and data
    payload = json_build_object(
        'table', 'alert_logs',
        'action', TG_OP,
        'data', row_to_json(NEW),
        'old_data', CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        'timestamp', extract(epoch from now())
    );
    
    -- Send notification
    PERFORM pg_notify('alert_changes', payload::text);
    
    -- Return appropriate row
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for alert_logs table
DROP TRIGGER IF EXISTS alert_change_trigger ON alert_logs;
CREATE TRIGGER alert_change_trigger
    AFTER INSERT OR UPDATE OR DELETE ON alert_logs
    FOR EACH ROW
    EXECUTE FUNCTION notify_alert_change();

-- =====================================================
-- 4. REALTIME METRICS TRIGGER
-- =====================================================

-- Function to notify metrics changes
CREATE OR REPLACE FUNCTION notify_metrics_change()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    -- Create payload with change type and data
    payload = json_build_object(
        'table', 'realtime_metrics',
        'action', TG_OP,
        'data', row_to_json(NEW),
        'old_data', CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        'timestamp', extract(epoch from now())
    );
    
    -- Send notification
    PERFORM pg_notify('metrics_changes', payload::text);
    
    -- Return appropriate row
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for realtime_metrics table
DROP TRIGGER IF EXISTS metrics_change_trigger ON realtime_metrics;
CREATE TRIGGER metrics_change_trigger
    AFTER INSERT OR UPDATE OR DELETE ON realtime_metrics
    FOR EACH ROW
    EXECUTE FUNCTION notify_metrics_change();

-- =====================================================
-- 5. TEST TRIGGERS FUNCTION
-- =====================================================

-- Function to test triggers manually
CREATE OR REPLACE FUNCTION test_sse_triggers()
RETURNS VOID AS $$
BEGIN
    -- Test session trigger
    PERFORM pg_notify('session_changes', json_build_object(
        'table', 'sessions',
        'action', 'TEST',
        'data', json_build_object('id', 'test-session', 'status', 'active'),
        'timestamp', extract(epoch from now())
    )::text);
    
    -- Test movement trigger
    PERFORM pg_notify('movement_changes', json_build_object(
        'table', 'people_movements',
        'action', 'TEST',
        'data', json_build_object('id', 'test-movement', 'direction', 'in'),
        'timestamp', extract(epoch from now())
    )::text);
    
    RAISE NOTICE 'SSE triggers test completed';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. CLEANUP FUNCTION
-- =====================================================

-- Function to remove all SSE triggers
CREATE OR REPLACE FUNCTION cleanup_sse_triggers()
RETURNS VOID AS $$
BEGIN
    DROP TRIGGER IF EXISTS session_change_trigger ON sessions;
    DROP TRIGGER IF EXISTS movement_change_trigger ON people_movements;
    DROP TRIGGER IF EXISTS alert_change_trigger ON alert_logs;
    DROP TRIGGER IF EXISTS metrics_change_trigger ON realtime_metrics;
    
    DROP FUNCTION IF EXISTS notify_session_change();
    DROP FUNCTION IF EXISTS notify_movement_change();
    DROP FUNCTION IF EXISTS notify_alert_change();
    DROP FUNCTION IF EXISTS notify_metrics_change();
    DROP FUNCTION IF EXISTS test_sse_triggers();
    DROP FUNCTION IF EXISTS cleanup_sse_triggers();
    
    RAISE NOTICE 'All SSE triggers and functions cleaned up';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if triggers exist
-- SELECT trigger_name, event_object_table, action_timing, event_manipulation 
-- FROM information_schema.triggers 
-- WHERE trigger_name LIKE '%_trigger';

-- Check if functions exist
-- SELECT routine_name, routine_type 
-- FROM information_schema.routines 
-- WHERE routine_name LIKE 'notify_%';

-- Test notifications
-- SELECT test_sse_triggers();
