#!/bin/bash
# Backup script - livskin RevOps
# Usage: ./backup.sh

BACKUP_DIR=~/backups/$(date +%Y-%m-%d)
mkdir -p $BACKUP_DIR

echo "=== Starting backup $(date) ==="

# PostgreSQL analytics
echo "Backing up PostgreSQL analytics..."
docker exec postgres-analytics pg_dump -U analytics_user analytics > $BACKUP_DIR/analytics.sql

# Vtiger DB
echo "Backing up Vtiger DB..."
docker exec vtiger-db mysqldump -u livskin -plivskin livskin_db > $BACKUP_DIR/vtiger.sql

# n8n data
echo "Backing up n8n data..."
tar -czf $BACKUP_DIR/n8n-data.tar.gz -C ~/apps/n8n data/

# Metabase (internal DB is in PostgreSQL, already backed up)

echo "=== Backup complete: $BACKUP_DIR ==="
ls -lh $BACKUP_DIR
