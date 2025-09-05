# People Counter Database - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Prerequisites
```bash
# Check if Docker is installed
docker --version
docker-compose --version

# Check if Python is installed
python --version  # Should be 3.9+
```

### 2. Clone and Setup
```bash
# Navigate to database directory
cd Dilumination_VisionAI/database

# Copy environment configuration
cp env.example .env

# Start database services
./manage_db.sh start

# Run migrations
python migrate.py migrate

# Start API server
python run_api.py
```

### 3. Verify Installation
```bash
# Check database health
curl http://localhost:8000/health

# Check database status
./manage_db.sh status
```

## 📊 Basic Usage

### Start a Counting Session
```python
from database.client import PeopleCounterIntegration

# Initialize
integration = PeopleCounterIntegration()
await integration.initialize()

# Start session
session_id = await integration.start_counting_session({
    "session_name": "My Session",
    "input_source": "video.mp4"
})

# Record movement
await integration.record_people_movement(
    person_id=1,
    direction="in",
    centroid=(320, 240),
    bounding_box=(300, 200, 340, 280),
    confidence=0.95,
    frame_number=100
)

# End session
await integration.end_counting_session({
    "status": "completed"
})
```

### API Usage
```bash
# Start session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_name": "Test Session", "input_source": "video.mp4"}'

# Record movement
curl -X POST http://localhost:8000/sessions/{session_id}/movements \
  -H "Content-Type: application/json" \
  -d '{"person_id": 1, "movement_direction": "in", "movement_time": "2025-09-05T12:00:00Z"}'

# Get dashboard data
curl http://localhost:8000/dashboard/summary
```

## 🔧 Common Commands

### Database Management
```bash
# Start services
./manage_db.sh start

# Stop services
./manage_db.sh stop

# Restart services
./manage_db.sh restart

# Check status
./manage_db.sh status

# Create backup
./manage_db.sh backup

# View logs
./manage_db.sh logs
```

### Migration Management
```bash
# Run migrations
python migrate.py migrate

# Check migration status
python migrate.py status

# Run without seeds
python migrate.py migrate --no-seeds
```

### Testing
```bash
# Run test suite
python test_database.py

# Run example integration
python example_integration.py
```

## 🆘 Troubleshooting

### Database Won't Start
```bash
# Check Docker status
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart services
./manage_db.sh restart
```

### Migration Errors
```bash
# Check migration status
python migrate.py status

# Reset and re-run migrations
python migrate.py migrate
```

### API Not Responding
```bash
# Check if API is running
curl http://localhost:8000/health

# Check API logs
tail -f logs/api.log

# Restart API
python run_api.py
```

## 📈 Next Steps

1. **Configure Environment**: Edit `.env` file with your settings
2. **Set Up Monitoring**: Configure alert thresholds in database
3. **Integrate with People Counter**: Use the integration examples
4. **Set Up Dashboard**: Connect to your web application
5. **Configure Backups**: Enable automated backups

## 📚 Documentation

- **Full Documentation**: [DATABASE_DOCUMENTATION.md](DATABASE_DOCUMENTATION.md)
- **API Reference**: http://localhost:8000/docs (when API is running)
- **Schema Reference**: [schemas/people_counter_schema.sql](schemas/people_counter_schema.sql)

## 🆘 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check docs/ directory
- **Examples**: See example_integration.py
