#!/bin/bash
# Restore script - livskin RevOps
# Usage: ./restore.sh <backup-date>
# Example: ./restore.sh 2026-04-16

BACKUP_DIR=~/backups/$1

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup-date>"
    echo "Example: ./restore.sh 2026-04-16"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "=== Restoring from $BACKUP_DIR ==="

# PostgreSQL analytics
if [ -f "$BACKUP_DIR/analytics.sql" ]; then
    echo "Restoring PostgreSQL analytics..."
    cat $BACKUP_DIR/analytics.sql | docker exec -i postgres-analytics psql -U analytics_user analytics
fi

# Vtiger DB
if [ -f "$BACKUP_DIR/vtiger.sql" ]; then
    echo "Restoring Vtiger DB..."
    cat $BACKUP_DIR/vtiger.sql | docker exec -i vtiger-db mysql -u livskin -plivskin livskin_db
fi

# n8n data
if [ -f "$BACKUP_DIR/n8n-data.tar.gz" ]; then
    echo "Restoring n8n data..."
    tar -xzf $BACKUP_DIR/n8n-data.tar.gz -C ~/apps/n8n/
fi

echo "=== Restore complete ==="
