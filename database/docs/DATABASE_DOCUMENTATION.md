# People Counter Database System
## Tài liệu kỹ thuật và hướng dẫn sử dụng

### 📋 Mục lục
1. [Tổng quan hệ thống](#tổng-quan-hệ-thống)
2. [Cấu trúc database](#cấu-trúc-database)
3. [Cài đặt và triển khai](#cài-đặt-và-triển-khai)
4. [API Documentation](#api-documentation)
5. [Integration Guide](#integration-guide)
6. [Monitoring và Maintenance](#monitoring-và-maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)

---

## 🎯 Tổng quan hệ thống

### Mục đích
Hệ thống database PostgreSQL được thiết kế để lưu trữ và quản lý dữ liệu từ hệ thống People Counter, cung cấp:
- **Real-time Dashboard**: Hiển thị dữ liệu đếm người theo thời gian thực
- **Analytics**: Phân tích xu hướng và báo cáo chi tiết
- **Alert System**: Cảnh báo khi vượt ngưỡng
- **Data Storage**: Lưu trữ lịch sử đếm người và metadata

### Kiến trúc hệ thống
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   People        │    │   Database      │    │   Dashboard     │
│   Counter       │───▶│   PostgreSQL    │───▶│   Web App       │
│   Application   │    │   + Redis       │    │   + Analytics   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Tính năng chính
- ✅ **Real-time Data Collection**: Thu thập dữ liệu đếm người theo thời gian thực
- ✅ **Session Management**: Quản lý các phiên đếm người
- ✅ **Movement Tracking**: Theo dõi chuyển động của từng người
- ✅ **Statistics Aggregation**: Tổng hợp thống kê theo giờ/ngày
- ✅ **Alert System**: Hệ thống cảnh báo thông minh
- ✅ **API RESTful**: API đầy đủ cho tích hợp
- ✅ **Docker Support**: Triển khai dễ dàng với Docker
- ✅ **Production Ready**: Tối ưu cho môi trường production

---

## 🗄️ Cấu trúc Database

### Schema Overview
Database được thiết kế với 9 bảng chính và 4 views:

#### Core Tables
1. **sessions** - Quản lý các phiên đếm người
2. **people_movements** - Lưu trữ chuyển động của từng người
3. **session_statistics** - Thống kê tổng hợp theo phiên
4. **realtime_metrics** - Metrics thời gian thực
5. **hourly_statistics** - Thống kê theo giờ
6. **daily_statistics** - Thống kê theo ngày

#### System Tables
7. **system_config** - Cấu hình hệ thống
8. **alert_thresholds** - Ngưỡng cảnh báo
9. **alert_logs** - Lịch sử cảnh báo

#### Views
- **current_session_overview** - Tổng quan phiên hiện tại
- **recent_movements** - Chuyển động gần đây
- **hourly_analytics** - Phân tích theo giờ
- **daily_analytics** - Phân tích theo ngày

### Data Types
```sql
-- Custom Enums
session_status: 'active', 'completed', 'error', 'cancelled'
detection_status: 'detecting', 'tracking', 'waiting'
movement_direction: 'in', 'out'
```

### Relationships
```
sessions (1) ──→ (N) people_movements
sessions (1) ──→ (1) session_statistics
sessions (1) ──→ (N) realtime_metrics
sessions (1) ──→ (N) hourly_statistics
sessions (1) ──→ (N) daily_statistics
sessions (1) ──→ (N) alert_logs
alert_thresholds (1) ──→ (N) alert_logs
```

---

## 🚀 Cài đặt và triển khai

### Yêu cầu hệ thống
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.9+
- **PostgreSQL**: 15+
- **Redis**: 7+

### Cài đặt nhanh
```bash
# 1. Clone repository
git clone <repository-url>
cd Dilumination_VisionAI/database

# 2. Cấu hình environment
cp env.example .env
# Chỉnh sửa .env với thông tin của bạn

# 3. Khởi động database
./manage_db.sh start

# 4. Chạy migration
python migrate.py migrate

# 5. Khởi động API server
python run_api.py
```

### Cấu hình chi tiết

#### Environment Variables (.env)
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=people_counter
DB_USER=people_counter_user
DB_PASSWORD=secure_password_123

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
API_RATE_LIMIT=1000
API_TIMEOUT=30

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

#### Docker Compose Services
```yaml
services:
  postgres:     # PostgreSQL database
  redis:        # Redis cache
  pgadmin:      # Database admin (optional)
  postgres-backup: # Backup service (optional)
```

### Production Deployment

#### 1. Security Configuration
```bash
# Thay đổi password mặc định
DB_PASSWORD=your_secure_password_here

# Cấu hình SSL
POSTGRES_SSL_MODE=require
POSTGRES_SSL_CERT=/path/to/cert.pem
POSTGRES_SSL_KEY=/path/to/key.pem
```

#### 2. Performance Tuning
```bash
# PostgreSQL Performance
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
POSTGRES_WORK_MEM=4MB
POSTGRES_MAINTENANCE_WORK_MEM=64MB
```

#### 3. Backup Configuration
```bash
# Automated Backups
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Hiện tại API không yêu cầu authentication. Trong production, nên thêm JWT hoặc API key authentication.

### Endpoints

#### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-05T11:56:20.054Z"
}
```

#### Sessions Management

##### Tạo session mới
```http
POST /sessions
Content-Type: application/json

{
  "session_name": "My Counting Session",
  "input_source": "path/to/video.mp4",
  "output_path": "path/to/output.mp4",
  "confidence_threshold": 0.3,
  "skip_frames": 3,
  "max_disappeared": 15,
  "max_distance": 80
}
```

##### Lấy danh sách sessions
```http
GET /sessions?limit=50&offset=0&status=active
```

##### Lấy thông tin session
```http
GET /sessions/{session_id}
```

##### Cập nhật session
```http
PUT /sessions/{session_id}
Content-Type: application/json

{
  "status": "completed",
  "fps": 30.5,
  "total_frames": 1200
}
```

#### People Movements

##### Ghi nhận chuyển động
```http
POST /sessions/{session_id}/movements
Content-Type: application/json

{
  "person_id": 1,
  "movement_direction": "in",
  "movement_time": "2025-09-05T11:56:20.054Z",
  "centroid_x": 320,
  "centroid_y": 240,
  "bounding_box_x1": 300,
  "bounding_box_y1": 200,
  "bounding_box_x2": 340,
  "bounding_box_y2": 280,
  "confidence_score": 0.95,
  "frame_number": 100
}
```

##### Lấy chuyển động gần đây
```http
GET /sessions/{session_id}/movements?limit=100&direction=in
```

#### Real-time Metrics

##### Ghi nhận metrics
```http
POST /sessions/{session_id}/metrics
Content-Type: application/json

{
  "current_people_count": 5,
  "people_entered_last_minute": 2,
  "people_exited_last_minute": 1,
  "detection_status": "tracking",
  "fps_current": 30.2,
  "cpu_usage_percentage": 45.5,
  "memory_usage_mb": 256.8,
  "processing_latency_ms": 12.3
}
```

##### Lấy metrics gần đây
```http
GET /sessions/{session_id}/metrics/recent?minutes=10
```

#### Analytics

##### Thống kê theo giờ
```http
GET /analytics/hourly?session_id={id}&hours=24
```

##### Thống kê theo ngày
```http
GET /analytics/daily?session_id={id}&days=30
```

#### Dashboard

##### Tổng quan dashboard
```http
GET /dashboard/summary
```

**Response:**
```json
{
  "active_sessions": 2,
  "sessions_today": 5,
  "people_entered_today": 150,
  "people_exited_today": 145,
  "recent_movements": 25,
  "timestamp": "2025-09-05T11:56:20.054Z"
}
```

### Error Handling
```json
{
  "detail": "Error message",
  "timestamp": "2025-09-05T11:56:20.054Z"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## 🔗 Integration Guide

### Python Integration

#### 1. Basic Usage
```python
from database.client import PeopleCounterIntegration

# Initialize integration
integration = PeopleCounterIntegration()
await integration.initialize()

# Start counting session
session_data = {
    "session_name": "My Session",
    "input_source": "video.mp4"
}
session_id = await integration.start_counting_session(session_data)

# Record movement
await integration.record_people_movement(
    person_id=1,
    direction="in",
    centroid=(320, 240),
    bounding_box=(300, 200, 340, 280),
    confidence=0.95,
    frame_number=100
)

# Record metrics
await integration.record_system_metrics(
    people_count=5,
    detection_status="tracking",
    fps=30.0,
    cpu_usage=45.5,
    memory_usage=256.8
)

# End session
await integration.end_counting_session({
    "fps": 30.0,
    "total_frames": 1000,
    "status": "completed"
})
```

#### 2. Advanced Integration
```python
import asyncio
from database.client import PeopleCounterIntegration

class PeopleCounterWithDB:
    def __init__(self):
        self.integration = PeopleCounterIntegration()
        self.session_id = None
    
    async def start(self, video_path):
        await self.integration.initialize()
        
        session_data = {
            "session_name": f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "input_source": video_path,
            "confidence_threshold": 0.3,
            "skip_frames": 3
        }
        
        self.session_id = await self.integration.start_counting_session(session_data)
        return self.session_id
    
    async def process_frame(self, frame_data):
        # Process frame and detect people
        for person in frame_data.detections:
            await self.integration.record_people_movement(
                person_id=person.id,
                direction=person.direction,
                centroid=person.centroid,
                bounding_box=person.bbox,
                confidence=person.confidence,
                frame_number=frame_data.frame_number
            )
        
        # Record system metrics
        await self.integration.record_system_metrics(
            people_count=len(frame_data.detections),
            detection_status="tracking",
            fps=frame_data.fps,
            cpu_usage=frame_data.cpu_usage,
            memory_usage=frame_data.memory_usage
        )
        
        # Auto-flush buffers
        await self.integration.auto_flush_check()
    
    async def stop(self):
        if self.session_id:
            await self.integration.end_counting_session({
                "status": "completed"
            })
        await self.integration.close()
```

### HTTP Client Integration

#### JavaScript/Node.js
```javascript
const axios = require('axios');

class PeopleCounterDBClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.client = axios.create({ baseURL });
    }
    
    async startSession(sessionData) {
        const response = await this.client.post('/sessions', sessionData);
        return response.data.session_id;
    }
    
    async recordMovement(sessionId, movementData) {
        await this.client.post(`/sessions/${sessionId}/movements`, movementData);
    }
    
    async recordMetrics(sessionId, metricsData) {
        await this.client.post(`/sessions/${sessionId}/metrics`, metricsData);
    }
    
    async getDashboard() {
        const response = await this.client.get('/dashboard/summary');
        return response.data;
    }
}

// Usage
const client = new PeopleCounterDBClient();
const sessionId = await client.startSession({
    session_name: 'My Session',
    input_source: 'video.mp4'
});
```

### Real-time Integration

#### WebSocket (Future Enhancement)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'movement') {
        updateDashboard(data);
    } else if (data.type === 'alert') {
        showAlert(data.message);
    }
};
```

---

## 📊 Monitoring và Maintenance

### Health Monitoring

#### Database Health Check
```bash
# Check database status
./manage_db.sh status

# Detailed health check
curl http://localhost:8000/health/detailed
```

#### Performance Monitoring
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Check database size
SELECT pg_size_pretty(pg_database_size('people_counter'));

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### Backup và Restore

#### Automated Backup
```bash
# Enable automated backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM

# Manual backup
./manage_db.sh backup
```

#### Manual Backup
```bash
# Create backup
pg_dump -h localhost -U people_counter_user people_counter > backup.sql

# Restore backup
./manage_db.sh restore backup.sql
```

### Log Management

#### Log Files
- `logs/migrations.log` - Migration logs
- `logs/api.log` - API server logs
- `logs/database.log` - Database operation logs

#### Log Rotation
```bash
# Configure log rotation
logrotate /etc/logrotate.d/people-counter-db
```

### Maintenance Tasks

#### Daily Maintenance
```sql
-- Update statistics
ANALYZE;

-- Vacuum tables
VACUUM ANALYZE sessions;
VACUUM ANALYZE people_movements;
VACUUM ANALYZE realtime_metrics;
```

#### Weekly Maintenance
```sql
-- Full vacuum
VACUUM FULL;

-- Reindex
REINDEX DATABASE people_counter;
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
**Symptoms:**
- `Connection refused` errors
- API returns 503 status

**Solutions:**
```bash
# Check if database is running
docker-compose ps

# Restart database
./manage_db.sh restart

# Check logs
docker-compose logs postgres
```

#### 2. Migration Failed
**Symptoms:**
- Migration errors during setup
- Schema inconsistencies

**Solutions:**
```bash
# Check migration status
python migrate.py status

# Reset migrations (CAUTION: Data loss)
python migrate.py migrate --reset

# Manual schema fix
psql -h localhost -U people_counter_user -d people_counter -f schemas/people_counter_schema.sql
```

#### 3. Performance Issues
**Symptoms:**
- Slow API responses
- High CPU usage
- Memory leaks

**Solutions:**
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
WHERE mean_time > 1000;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### 4. Data Inconsistency
**Symptoms:**
- Incorrect people counts
- Missing movements
- Statistics mismatch

**Solutions:**
```sql
-- Recalculate statistics
SELECT calculate_current_people_inside('session-uuid-here');

-- Check data integrity
SELECT 
    s.id,
    s.session_name,
    COUNT(pm_in.id) as movements_in,
    COUNT(pm_out.id) as movements_out,
    ss.current_people_inside
FROM sessions s
LEFT JOIN people_movements pm_in ON s.id = pm_in.session_id AND pm_in.movement_direction = 'in'
LEFT JOIN people_movements pm_out ON s.id = pm_out.session_id AND pm_out.movement_direction = 'out'
LEFT JOIN session_statistics ss ON s.id = ss.session_id
GROUP BY s.id, s.session_name, ss.current_people_inside;
```

### Debug Mode

#### Enable Debug Logging
```bash
# Set debug level
LOG_LEVEL=DEBUG

# Restart services
./manage_db.sh restart
python run_api.py
```

#### API Debug
```bash
# Enable SQL logging
export SQLALCHEMY_ECHO=true
python run_api.py
```

---

## ⚡ Performance Optimization

### Database Optimization

#### Index Optimization
```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_people_movements_session_time 
ON people_movements(session_id, movement_time);
```

#### Query Optimization
```sql
-- Optimize slow queries
EXPLAIN ANALYZE SELECT * FROM people_movements 
WHERE session_id = 'uuid' AND movement_time > NOW() - INTERVAL '1 hour';

-- Use prepared statements
PREPARE get_recent_movements(UUID, TIMESTAMP) AS
SELECT * FROM people_movements 
WHERE session_id = $1 AND movement_time > $2;
```

### Application Optimization

#### Connection Pooling
```python
# Optimize connection pool
db_config.pool_min = 10
db_config.pool_max = 50
db_config.pool_timeout = 30
```

#### Caching Strategy
```python
# Redis caching
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Cache session data
def get_session_cached(session_id):
    cache_key = f"session:{session_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    session_data = fetch_session_from_db(session_id)
    r.setex(cache_key, 300, json.dumps(session_data))  # 5 min cache
    return session_data
```

### Monitoring Performance

#### Key Metrics
- **Response Time**: < 100ms for API calls
- **Throughput**: > 1000 requests/second
- **Database Connections**: < 80% of pool size
- **Memory Usage**: < 80% of available RAM
- **CPU Usage**: < 70% average

#### Performance Monitoring
```python
# Add performance monitoring
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        if duration > 1.0:  # Log slow operations
            logger.warning(f"Slow operation: {func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper
```

---

## 📚 Additional Resources

### Documentation Links
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)

### Support Contacts
- **Technical Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)
- **Email Support**: support@yourcompany.com

### Version History
- **v1.0.0** (2025-09-05): Initial release
  - Basic database schema
  - API endpoints
  - Docker support
  - Migration system

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Last Updated**: 2025-09-05  
**Version**: 1.0.0  
**Author**: Development Team
