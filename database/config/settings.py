# People Counter Database Configuration
# Centralized configuration management

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    database: str = os.getenv('DB_NAME', 'people_counter')
    username: str = os.getenv('DB_USER', 'people_counter_user')
    password: str = os.getenv('DB_PASSWORD', 'secure_password_123')
    
    # Connection pool settings
    pool_min: int = int(os.getenv('DB_POOL_MIN', '5'))
    pool_max: int = int(os.getenv('DB_POOL_MAX', '20'))
    pool_timeout: int = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    
    # Performance settings
    shared_buffers: str = os.getenv('POSTGRES_SHARED_BUFFERS', '256MB')
    effective_cache_size: str = os.getenv('POSTGRES_EFFECTIVE_CACHE_SIZE', '1GB')
    work_mem: str = os.getenv('POSTGRES_WORK_MEM', '4MB')
    
    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_connection_string(self) -> str:
        """Get async PostgreSQL connection string"""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    password: Optional[str] = os.getenv('REDIS_PASSWORD')
    db: int = int(os.getenv('REDIS_DB', '0'))
    
    @property
    def connection_string(self) -> str:
        """Get Redis connection string"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"

@dataclass
class AppConfig:
    """Application configuration settings"""
    environment: str = os.getenv('APP_ENV', 'production')
    debug: bool = os.getenv('APP_DEBUG', 'false').lower() == 'true'
    log_level: str = os.getenv('APP_LOG_LEVEL', 'info')
    
    # Security
    jwt_secret: str = os.getenv('JWT_SECRET', 'your_jwt_secret_key_here')
    encryption_key: str = os.getenv('ENCRYPTION_KEY', 'your_encryption_key_here')
    
    # API settings
    api_rate_limit: int = int(os.getenv('API_RATE_LIMIT', '1000'))
    api_timeout: int = int(os.getenv('API_TIMEOUT', '30'))
    cors_origins: str = os.getenv('API_CORS_ORIGINS', 'http://localhost:3000')
    
    # Dashboard settings
    dashboard_refresh_interval: int = int(os.getenv('DASHBOARD_REFRESH_INTERVAL', '5000'))
    dashboard_max_sessions: int = int(os.getenv('DASHBOARD_MAX_SESSIONS_DISPLAY', '50'))
    realtime_enabled: bool = os.getenv('DASHBOARD_REALTIME_ENABLED', 'true').lower() == 'true'
    
    # File storage
    upload_max_size: str = os.getenv('UPLOAD_MAX_SIZE', '100MB')
    video_storage_path: str = os.getenv('VIDEO_STORAGE_PATH', '/data/videos')
    output_storage_path: str = os.getenv('OUTPUT_STORAGE_PATH', '/data/outputs')
    
    # Monitoring
    enable_metrics: bool = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    metrics_port: int = int(os.getenv('METRICS_PORT', '9090'))
    
    # Health check
    health_check_interval: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
    health_check_timeout: int = int(os.getenv('HEALTH_CHECK_TIMEOUT', '10'))
    health_check_retries: int = int(os.getenv('HEALTH_CHECK_RETRIES', '3'))

@dataclass
class AlertConfig:
    """Alert configuration settings"""
    email_enabled: bool = os.getenv('ALERT_EMAIL_ENABLED', 'true').lower() == 'true'
    smtp_host: str = os.getenv('ALERT_EMAIL_SMTP_HOST', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('ALERT_EMAIL_SMTP_PORT', '587'))
    smtp_user: str = os.getenv('ALERT_EMAIL_USER', 'your_email@gmail.com')
    smtp_password: str = os.getenv('ALERT_EMAIL_PASSWORD', 'your_app_password')
    smtp_from: str = os.getenv('ALERT_EMAIL_FROM', 'noreply@peoplecounter.com')

@dataclass
class BackupConfig:
    """Backup configuration settings"""
    enabled: bool = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
    schedule: str = os.getenv('BACKUP_SCHEDULE', '0 2 * * *')  # Daily at 2 AM
    retention_days: int = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    backup_path: str = os.getenv('BACKUP_PATH', './database/backups')

# Global configuration instances
db_config = DatabaseConfig()
redis_config = RedisConfig()
app_config = AppConfig()
alert_config = AlertConfig()
backup_config = BackupConfig()

# Configuration validation
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Database validation
    if not db_config.host:
        errors.append("DB_HOST is required")
    if not db_config.database:
        errors.append("DB_NAME is required")
    if not db_config.username:
        errors.append("DB_USER is required")
    if not db_config.password:
        errors.append("DB_PASSWORD is required")
    
    # Security validation
    if app_config.jwt_secret == 'your_jwt_secret_key_here':
        errors.append("JWT_SECRET must be changed from default value")
    if app_config.encryption_key == 'your_encryption_key_here':
        errors.append("ENCRYPTION_KEY must be changed from default value")
    
    # Email validation
    if alert_config.email_enabled:
        if not alert_config.smtp_user or alert_config.smtp_user == 'your_email@gmail.com':
            errors.append("ALERT_EMAIL_USER must be configured for email alerts")
        if not alert_config.smtp_password or alert_config.smtp_password == 'your_app_password':
            errors.append("ALERT_EMAIL_PASSWORD must be configured for email alerts")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    return True

# Export configurations
__all__ = [
    'DatabaseConfig',
    'RedisConfig', 
    'AppConfig',
    'AlertConfig',
    'BackupConfig',
    'db_config',
    'redis_config',
    'app_config',
    'alert_config',
    'backup_config',
    'validate_config'
]
