#!/bin/bash
# verify-vps2-backups.sh — corre en VPS 3, verifica backups recibidos de VPS 2.
# Toma el último backup de cada DB y lo restaura a una temp DB en
# postgres-data (o vtiger-db si fuera mariadb — pero VPS 2 envia postgres
# analytics + mariadb vtiger-db dump, los verificamos contra postgres-data
# y vtiger-db respectivamente).
#
# NOTA: para mariadb backups (vtiger-db) hay que verificar en VPS 2 mismo,
# este script solo verifica los postgres analytics.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

BACKUPS_DIR="/srv/backups/vps2"

log "=== verify-vps2-backups.sh start ==="

verify_latest() {
    local prefix="$1"
    local engine="$2"
    local container="$3"
    local original_db="$4"

    local latest=$(ls -t "$BACKUPS_DIR/${prefix}-"*.sql.gz 2>/dev/null | head -1 || true)
    if [ -z "$latest" ]; then
        log "WARN: no hay backup de $prefix"
        audit_event "infra.backup_failed" \
            "{\"vps\":\"vps2\",\"reason\":\"no backup found for $prefix\"}"
        return
    fi

    log "Verificando $latest..."
    bash "$SCRIPT_DIR/verify-backup.sh" "$engine" "$container" "$latest" "$original_db" || \
        log "FAIL: verificación de $prefix falló"
}

# Solo verificamos los Postgres acá. Los mariadb se verifican en VPS 2.
verify_latest "analytics" postgres postgres-analytics analytics
verify_latest "metabase" postgres postgres-analytics metabase

log "=== verify-vps2-backups.sh complete ==="
