-- Migration: 002_fix_trigger.sql
-- Description: Fix trigger function to remove ON CONFLICT
-- Version: 1.1
-- Created: 2025-09-05

-- Drop and recreate the trigger function
DROP TRIGGER IF EXISTS update_stats_on_movement ON people_movements;
DROP FUNCTION IF EXISTS update_session_statistics() CASCADE;

-- Create function to update session statistics
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
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Recreate trigger
CREATE TRIGGER update_stats_on_movement 
    AFTER INSERT ON people_movements
    FOR EACH ROW EXECUTE FUNCTION update_session_statistics();
INSERT INTO system_config (config_key, config_value, config_type, description) 
VALUES ('migration_002_completed', 'true', 'boolean', 'Trigger fix migration completed')
ON CONFLICT (config_key) DO UPDATE SET config_value = 'true', updated_at = NOW();
