#!/bin/bash
# backup-vps2.sh — corre en VPS 2, respalda:
# - livskin_db (Vtiger MariaDB)
# - analytics + metabase (Postgres analytics)
# - n8n data (workflows + sqlite)
# Transfiere cross-VPS a livskin-erp:/srv/backups/vps2/.
#
# Cron sugerido (en /etc/cron.d/livskin-backups en VPS 2):
#   0 2 * * * livskin /srv/livskin-revops/infra/scripts/backups/backup-vps2.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

LOCAL_BACKUP_DIR="/srv/backups/local"
REMOTE_USER="${BACKUP_REMOTE_USER:-backup}"
REMOTE_HOST="${BACKUP_REMOTE_HOST:-10.114.0.4}"  # VPS 3 via VPC
REMOTE_PATH="${BACKUP_REMOTE_PATH:-/srv/backups/vps2}"

# DB credentials desde .env de cada servicio
VTIGER_DB_PASSWORD="${VTIGER_DB_PASSWORD:-livskin}"  # TODO rotar
ANALYTICS_DB_PASSWORD="${ANALYTICS_DB_PASSWORD:-livskin}"  # TODO rotar

mkdir -p "$LOCAL_BACKUP_DIR"

log "=== backup-vps2.sh start ==="
audit_event "infra.backup_started" '{"vps":"vps2","source":"livskin-ops"}'

# 1. Vtiger DB (mariadb)
VTIGER_FILE=$(mariadb_backup vtiger-db livskin_db livskin "$VTIGER_DB_PASSWORD" \
    "$LOCAL_BACKUP_DIR/livskin_db-$DATE_TAG.sql")
cross_vps_transfer "$VTIGER_FILE" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 2. analytics (postgres)
ANALYTICS_FILE=$(pg_backup postgres-analytics analytics analytics_user \
    "$LOCAL_BACKUP_DIR/analytics-$DATE_TAG.sql")
cross_vps_transfer "$ANALYTICS_FILE" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 3. metabase backend (postgres) — configs + dashboards
METABASE_FILE=$(pg_backup postgres-analytics metabase analytics_user \
    "$LOCAL_BACKUP_DIR/metabase-$DATE_TAG.sql")
cross_vps_transfer "$METABASE_FILE" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 4. n8n data (sqlite + workflows + credentials)
# CRITICAL: si esto se pierde, los workflows hay que recrearlos manualmente
N8N_FILE=$(tar_backup "/home/livskin/apps/n8n/data" \
    "$LOCAL_BACKUP_DIR/n8n-data-$DATE_TAG")
cross_vps_transfer "$N8N_FILE" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 5. Cleanup local
cleanup_local "$LOCAL_BACKUP_DIR" 30

log "=== backup-vps2.sh complete ==="
audit_event "infra.backup_completed" \
    "{\"vps\":\"vps2\",\"files\":[\"$(basename "$VTIGER_FILE")\",\"$(basename "$ANALYTICS_FILE")\",\"$(basename "$METABASE_FILE")\",\"$(basename "$N8N_FILE")\"]}"
