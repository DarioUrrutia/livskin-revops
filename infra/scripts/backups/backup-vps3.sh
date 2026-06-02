#!/bin/bash
# backup-vps3.sh — corre en VPS 3, respalda livskin_erp + livskin_brain
# y los transfiere cross-VPS a livskin-ops:/srv/backups/vps3/.
#
# Cron sugerido (ya en /etc/cron.d/livskin-backups):
#   0 2 * * * livskin /srv/livskin-revops/infra/scripts/backups/backup-vps3.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

LOCAL_BACKUP_DIR="/srv/backups/local"
REMOTE_USER="${BACKUP_REMOTE_USER:-backup}"
REMOTE_HOST="${BACKUP_REMOTE_HOST:-10.114.0.2}"  # VPS 2 via VPC
REMOTE_PATH="${BACKUP_REMOTE_PATH:-/srv/backups/vps3}"

mkdir -p "$LOCAL_BACKUP_DIR"

log "=== backup-vps3.sh start ==="
audit_event "infra.backup_started" '{"vps":"vps3","source":"livskin-erp"}'

# 1. livskin_erp
ERP_FILE=$(pg_backup postgres-data livskin_erp postgres "$LOCAL_BACKUP_DIR/livskin_erp-$DATE_TAG.sql")
cross_vps_transfer "$ERP_FILE" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 2. livskin_brain (segundo cerebro)
BRAIN_FILE=$(pg_backup postgres-data livskin_brain postgres "$LOCAL_BACKUP_DIR/livskin_brain-$DATE_TAG.sql")
cross_vps_transfer "$BRAIN_FILE" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 3. Cleanup local (>30 días)
cleanup_local "$LOCAL_BACKUP_DIR" 30

log "=== backup-vps3.sh complete ==="
audit_event "infra.backup_completed" "{\"vps\":\"vps3\",\"files\":[\"$(basename "$ERP_FILE")\",\"$(basename "$BRAIN_FILE")\"]}"
