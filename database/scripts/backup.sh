#!/bin/bash

# Database Backup Script
# Automated backup with compression and rotation

set -e

# Configuration
DB_NAME="people_counter"
DB_USER="people_counter_user"
BACKUP_DIR="/backups"
RETENTION_DAYS=30
COMPRESS=true

# Create backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/people_counter_backup_$(date +%Y%m%d_%H%M%S).sql"

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Starting database backup..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform backup
log "Creating backup: $BACKUP_FILE"
pg_dump -h postgres -U $DB_USER -d $DB_NAME --verbose --no-password > $BACKUP_FILE

if [ $? -eq 0 ]; then
    log "Backup completed successfully"
    
    # Compress backup if enabled
    if [ "$COMPRESS" = true ]; then
        log "Compressing backup..."
        gzip $BACKUP_FILE
        BACKUP_FILE="${BACKUP_FILE}.gz"
        log "Backup compressed: $BACKUP_FILE"
    fi
    
    # Clean up old backups
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    find $BACKUP_DIR -name "people_counter_backup_*.sql*" -type f -mtime +$RETENTION_DAYS -delete
    
    log "Backup process completed successfully"
else
    log "Backup failed!"
    exit 1
fi
