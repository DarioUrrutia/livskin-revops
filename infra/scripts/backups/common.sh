#!/bin/bash
# common.sh — funciones compartidas por backup-vps{1,2,3}.sh.
# Source este archivo desde los demás scripts.
#
# Variables esperadas en environment:
# - AUDIT_INTERNAL_TOKEN: shared secret para POST a /api/internal/audit-event
# - ERP_AUDIT_URL: default https://erp.livskin.site/api/internal/audit-event

set -euo pipefail

ERP_AUDIT_URL="${ERP_AUDIT_URL:-https://erp.livskin.site/api/internal/audit-event}"
DATE_TAG=$(date -u +%Y-%m-%d)
LOG_FILE="${LOG_FILE:-/var/log/livskin-backup.log}"

log() {
    local msg="[$(date -u +%H:%M:%SZ)] $*"
    # tee con redirect a stderr (>&2): evita que log lines contaminen
    # el stdout que el caller usa para capturar output (ej. ERP_FILE=$(pg_backup ...)).
    echo "$msg" | tee -a "$LOG_FILE" >&2
}

fail() {
    log "ERROR: $*"
    audit_event "infra.backup_failed" "{\"error\":\"$*\"}"
    exit 1
}

audit_event() {
    local action="$1"
    local metadata_json="${2:-{}}"
    if [ -z "${AUDIT_INTERNAL_TOKEN:-}" ]; then
        log "WARNING: AUDIT_INTERNAL_TOKEN no seteado — skip audit"
        return 0
    fi
    curl -s -X POST "$ERP_AUDIT_URL" \
        -H "X-Internal-Token: $AUDIT_INTERNAL_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"action\":\"$action\",\"metadata\":$metadata_json}" \
        --max-time 10 \
        > /dev/null \
        || log "WARNING: audit endpoint no respondio"
}

# pg_dump wrapper con compresión gzip
pg_backup() {
    local container="$1"   # nombre del container postgres
    local db="$2"          # database a respaldar
    local user="$3"        # user de la DB
    local out_file="$4"    # path destino (sin .gz, se agrega)

    log "pg_dump $db (container=$container) → $out_file.gz"
    docker exec "$container" pg_dump -U "$user" "$db" \
        | gzip -9 > "$out_file.gz"

    local size=$(du -h "$out_file.gz" | cut -f1)
    log "  ✓ tamaño: $size"
    echo "$out_file.gz"
}

# mariadb-dump wrapper
mariadb_backup() {
    local container="$1"
    local db="$2"
    local user="$3"
    local password="$4"
    local out_file="$5"

    log "mariadb-dump $db (container=$container) → $out_file.gz"
    docker exec -e MYSQL_PWD="$password" "$container" \
        mariadb-dump -u "$user" --single-transaction --quick "$db" \
        | gzip -9 > "$out_file.gz"

    local size=$(du -h "$out_file.gz" | cut -f1)
    log "  ✓ tamaño: $size"
    echo "$out_file.gz"
}

# tar wrapper (filesystem backup)
tar_backup() {
    local source_dir="$1"
    local out_file="$2"

    log "tar $source_dir → $out_file.tar.gz"
    tar -czf "$out_file.tar.gz" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"

    local size=$(du -h "$out_file.tar.gz" | cut -f1)
    log "  ✓ tamaño: $size"
    echo "$out_file.tar.gz"
}

# rsync cross-VPS via SSH key dedicada
cross_vps_transfer() {
    local local_file="$1"
    local remote_user="$2"
    local remote_host="$3"
    local remote_path="$4"
    # SSH key default: ~/.ssh/backup-target del user que ejecuta (livskin via cron).
    # Se eligió este path (no /root/.ssh/) para que livskin pueda leerla sin sudo.
    local ssh_key="${5:-${HOME}/.ssh/backup-target}"

    log "rsync $local_file → ${remote_user}@${remote_host}:${remote_path}"
    rsync -az --partial --inplace \
        -e "ssh -i $ssh_key -o BatchMode=yes -o StrictHostKeyChecking=accept-new" \
        "$local_file" \
        "${remote_user}@${remote_host}:${remote_path}/"
    log "  ✓ transferido"
}

# Cleanup local files older than N days
cleanup_local() {
    local dir="$1"
    local days="${2:-30}"

    log "cleanup $dir/ (>$days días)"
    find "$dir" -maxdepth 1 -type f -mtime +"$days" -print -delete 2>/dev/null \
        | while read f; do log "  borrado: $f"; done || true
}
