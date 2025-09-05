#!/bin/bash

# People Counter Database Management Script
# Production-ready database operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_FILE="./logs/database.log"

# Create necessary directories
mkdir -p $BACKUP_DIR
mkdir -p logs

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Error handling
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✓ $1${NC}"
    log "SUCCESS: $1"
}

# Warning message
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    log "WARNING: $1"
}

# Info message
info() {
    echo -e "${BLUE}ℹ $1${NC}"
    log "INFO: $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error_exit "Docker is not running. Please start Docker first."
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        warning ".env file not found. Creating from env.example..."
        cp env.example $ENV_FILE
        warning "Please edit $ENV_FILE with your configuration before proceeding."
        exit 1
    fi
}

# Start database services
start_db() {
    info "Starting People Counter Database services..."
    check_docker
    check_env
    
    docker-compose -f $COMPOSE_FILE up -d postgres redis
    
    # Wait for services to be healthy
    info "Waiting for services to be healthy..."
    timeout 60 bash -c 'until docker-compose -f '$COMPOSE_FILE' ps postgres | grep -q "healthy"; do sleep 2; done'
    timeout 60 bash -c 'until docker-compose -f '$COMPOSE_FILE' ps redis | grep -q "Up"; do sleep 2; done'
    
    success "Database services started successfully!"
}

# Stop database services
stop_db() {
    info "Stopping People Counter Database services..."
    docker-compose -f $COMPOSE_FILE down
    success "Database services stopped successfully!"
}

# Restart database services
restart_db() {
    info "Restarting People Counter Database services..."
    stop_db
    sleep 5
    start_db
}

# Show database status
status_db() {
    info "Database services status:"
    docker-compose -f $COMPOSE_FILE ps
}

# Create database backup
backup_db() {
    info "Creating database backup..."
    check_docker
    
    BACKUP_FILE="$BACKUP_DIR/people_counter_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U people_counter_user people_counter > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        success "Backup created: $BACKUP_FILE"
        log "Backup created: $BACKUP_FILE"
    else
        error_exit "Backup failed!"
    fi
}

# Restore database from backup
restore_db() {
    if [ -z "$1" ]; then
        error_exit "Please provide backup file path: ./manage_db.sh restore /path/to/backup.sql"
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        error_exit "Backup file not found: $BACKUP_FILE"
    fi
    
    info "Restoring database from: $BACKUP_FILE"
    warning "This will overwrite existing data. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        info "Restore cancelled."
        exit 0
    fi
    
    check_docker
    
    # Stop services
    stop_db
    
    # Start only postgres
    docker-compose -f $COMPOSE_FILE up -d postgres
    
    # Wait for postgres to be ready
    timeout 60 bash -c 'until docker-compose -f '$COMPOSE_FILE' ps postgres | grep -q "healthy"; do sleep 2; done'
    
    # Restore database
    docker-compose -f $COMPOSE_FILE exec -T postgres psql -U people_counter_user -d people_counter -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    docker-compose -f $COMPOSE_FILE exec -T postgres psql -U people_counter_user -d people_counter < $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        success "Database restored successfully!"
        log "Database restored from: $BACKUP_FILE"
    else
        error_exit "Restore failed!"
    fi
}

# Run database migrations
migrate_db() {
    info "Running database migrations..."
    check_docker
    
    # Check if postgres is healthy
    if ! docker-compose -f $COMPOSE_FILE ps postgres | grep -q "healthy"; then
        error_exit "PostgreSQL is not healthy. Please start the database first."
    fi
    
    # Run schema
    docker-compose -f $COMPOSE_FILE exec -T postgres psql -U people_counter_user -d people_counter -f /docker-entrypoint-initdb.d/schemas/people_counter_schema.sql
    
    if [ $? -eq 0 ]; then
        success "Database migrations completed successfully!"
        log "Database migrations completed"
    else
        error_exit "Migration failed!"
    fi
}

# Show database logs
logs_db() {
    info "Showing database logs..."
    docker-compose -f $COMPOSE_FILE logs -f postgres
}

# Connect to database
connect_db() {
    info "Connecting to database..."
    check_docker
    
    if ! docker-compose -f $COMPOSE_FILE ps postgres | grep -q "healthy"; then
        error_exit "PostgreSQL is not healthy. Please start the database first."
    fi
    
    docker-compose -f $COMPOSE_FILE exec postgres psql -U people_counter_user -d people_counter
}

# Clean up old backups
cleanup_backups() {
    info "Cleaning up old backups (keeping last 30 days)..."
    
    find $BACKUP_DIR -name "people_counter_backup_*.sql" -type f -mtime +30 -delete
    
    success "Old backups cleaned up!"
    log "Old backups cleaned up"
}

# Show help
show_help() {
    echo "People Counter Database Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start database services"
    echo "  stop        Stop database services"
    echo "  restart     Restart database services"
    echo "  status      Show services status"
    echo "  backup      Create database backup"
    echo "  restore     Restore database from backup"
    echo "  migrate     Run database migrations"
    echo "  logs        Show database logs"
    echo "  connect     Connect to database"
    echo "  cleanup     Clean up old backups"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 backup"
    echo "  $0 restore ./backups/backup.sql"
    echo "  $0 migrate"
}

# Main script logic
case "${1:-help}" in
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        restart_db
        ;;
    status)
        status_db
        ;;
    backup)
        backup_db
        ;;
    restore)
        restore_db "$2"
        ;;
    migrate)
        migrate_db
        ;;
    logs)
        logs_db
        ;;
    connect)
        connect_db
        ;;
    cleanup)
        cleanup_backups
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error_exit "Unknown command: $1. Use '$0 help' for usage information."
        ;;
esac
