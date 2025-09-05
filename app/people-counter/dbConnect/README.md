# People Counter Database Integration

Clean, production-ready database integration for the People Counter application.

## 🚀 Quick Start

### 1. Prerequisites
- PostgreSQL database running (see `../../database/` for setup)
- Python dependencies installed

### 2. Basic Usage

```python
from dbConnect import PeopleCounterDB, PeopleCounterLogger

# Create database connection
db = PeopleCounterDB()

# Test connection
if db.test_connection():
    print("Database connected successfully!")
    
    # Start session
    session_id = db.start_session({
        'session_name': 'My Session',
        'input_source': 'video.mp4'
    })
    
    # Log movement
    db.log_movement({
        'person_id': 1,
        'direction': 'in',
        'centroid': (100, 200),
        'bounding_box': (80, 180, 120, 220),
        'confidence': 0.95,
        'frame_number': 1
    })
    
    # End session
    db.end_session('completed')
```

### 3. Using the Logger

```python
# Create logger with database integration
logger = PeopleCounterLogger(db, enable_csv=True, enable_db=True)

# Start session
session_id = logger.start_session("My Session", "video.mp4")

# Log movement data
move_in = [1, 2, 3]
in_time = ["2025-01-01 10:00", "2025-01-01 10:05", "2025-01-01 10:10"]
move_out = [1, 2]
out_time = ["2025-01-01 10:15", "2025-01-01 10:20"]

logger.log_movement_data(move_in, in_time, move_out, out_time)

# Log real-time metrics
logger.log_realtime_metrics(1, 3, 2)  # 1 inside, 3 entered, 2 exited

# End session
logger.end_session('completed')
```

## 📁 File Structure

```
dbConnect/
├── __init__.py              # Module exports
├── db_connection.py         # Core database connection class
├── logging_integration.py   # CSV + Database logging integration
└── config.json             # Configuration file
```

## 🔧 Configuration

Edit `config.json` to customize database settings:

```json
{
    "database": {
        "host": "localhost",
        "port": 5432,
        "database": "people_counter",
        "user": "postgres",
        "password": "postgres"
    },
    "logging": {
        "enable_csv": true,
        "enable_database": true,
        "csv_file_path": "utils/data/logs/counting_data.csv"
    }
}
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_db_integration.py
```

Run examples to see usage patterns:

```bash
python example_db_usage.py
```

## 🔄 Integration with People Counter

The `people_counter_complete.py` has been updated to automatically use database logging when available:

1. **Automatic Detection**: Database connection is tested on startup
2. **Fallback Mode**: If database fails, falls back to CSV-only logging
3. **Session Management**: Automatically starts/ends database sessions
4. **Real-time Logging**: Logs movements and metrics in real-time
5. **Alert Integration**: Logs alerts to database when thresholds exceeded

## 📊 Database Schema

The integration works with the PostgreSQL schema in `../../database/schemas/`:

- **sessions**: Session information
- **people_movements**: Individual movement events
- **realtime_metrics**: Real-time counting metrics
- **alert_logs**: Alert events
- **session_statistics**: Session summaries

## 🛡️ Error Handling

The integration includes robust error handling:

- **Connection Failures**: Graceful fallback to CSV logging
- **Database Errors**: Logged but don't crash the application
- **Missing Data**: Default values provided for optional fields
- **Schema Mismatches**: Handled with appropriate error messages

## 🎯 Features

### PeopleCounterDB Class
- ✅ Database connection management
- ✅ Session lifecycle management
- ✅ Movement event logging
- ✅ Real-time metrics logging
- ✅ Alert threshold checking
- ✅ Session statistics retrieval

### PeopleCounterLogger Class
- ✅ Dual CSV + Database logging
- ✅ CSV-only fallback mode
- ✅ Individual movement logging
- ✅ Batch movement data logging
- ✅ Real-time metrics logging
- ✅ Alert checking and logging
- ✅ Session management integration

## 🔍 Monitoring

Check database logs and CSV files to monitor the integration:

```bash
# Check CSV logs
cat utils/data/logs/counting_data.csv

# Check database sessions
psql -d people_counter -c "SELECT * FROM sessions ORDER BY created_at DESC LIMIT 5;"

# Check recent movements
psql -d people_counter -c "SELECT * FROM people_movements ORDER BY created_at DESC LIMIT 10;"
```

## 🚨 Troubleshooting

### Database Connection Issues
```python
# Test connection
db = PeopleCounterDB()
if not db.test_connection():
    print("Check database is running and credentials are correct")
```

### Schema Issues
- Ensure database migrations are applied
- Check column names match the schema
- Verify data types are correct

### Performance Issues
- Use connection pooling for high-volume applications
- Consider batch logging for better performance
- Monitor database performance metrics

## 📝 Clean Code Principles

This integration follows clean code principles:

- **Single Responsibility**: Each class has one clear purpose
- **Dependency Injection**: Database instance can be injected
- **Error Handling**: Comprehensive error handling without crashes
- **Configuration**: Externalized configuration
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear documentation and examples
- **Fallback**: Graceful degradation when database unavailable
