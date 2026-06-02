#!/bin/bash
# backup-vps1.sh — corre en VPS 1, respalda:
# - livskin_wp (MariaDB host)
# - /var/www/livskin/ (filesystem)
# Transfiere cross-VPS a livskin-ops:/srv/backups/vps1/.
#
# Cron sugerido (en /etc/cron.d/livskin-backups en VPS 1):
#   0 2 * * * root /srv/livskin-revops/infra/scripts/backups/backup-vps1.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

LOCAL_BACKUP_DIR="/srv/backups/local"
REMOTE_USER="${BACKUP_REMOTE_USER:-backup}"
REMOTE_HOST="${BACKUP_REMOTE_HOST:-10.114.0.2}"  # VPS 2 via VPC
REMOTE_PATH="${BACKUP_REMOTE_PATH:-/srv/backups/vps1}"

WP_DB_NAME="${WP_DB_NAME:-livskin_wp}"
WP_DB_USER="${WP_DB_USER:-livskin_user}"
WP_DB_PASS="${WP_DB_PASS:-}"  # leer desde wp-config.php si vacío

mkdir -p "$LOCAL_BACKUP_DIR"

log "=== backup-vps1.sh start ==="
audit_event "infra.backup_started" '{"vps":"vps1","source":"livskin-wp"}'

# 1. WP DB (host MariaDB, no docker — usar mariadb-dump directo)
DB_FILE="$LOCAL_BACKUP_DIR/livskin_wp-$DATE_TAG.sql"
log "mariadb-dump $WP_DB_NAME → $DB_FILE.gz"
if [ -n "$WP_DB_PASS" ]; then
    MYSQL_PWD="$WP_DB_PASS" mariadb-dump -u "$WP_DB_USER" --single-transaction --quick "$WP_DB_NAME" \
        | gzip -9 > "$DB_FILE.gz"
else
    # Sin password: usar /etc/mysql/debian.cnf (root local en Ubuntu)
    sudo mariadb-dump --defaults-file=/etc/mysql/debian.cnf --single-transaction --quick "$WP_DB_NAME" \
        | gzip -9 > "$DB_FILE.gz"
fi
log "  ✓ $(du -h "$DB_FILE.gz" | cut -f1)"
cross_vps_transfer "$DB_FILE.gz" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 2. /var/www/livskin/ — filesystem
WP_FILE=$(tar_backup "/var/www/livskin" "$LOCAL_BACKUP_DIR/wordpress-files-$DATE_TAG")
cross_vps_transfer "$WP_FILE" "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PATH"

# 3. Cleanup local
cleanup_local "$LOCAL_BACKUP_DIR" 30

log "=== backup-vps1.sh complete ==="
audit_event "infra.backup_completed" \
    "{\"vps\":\"vps1\",\"files\":[\"$(basename "$DB_FILE.gz")\",\"$(basename "$WP_FILE")\"]}"
