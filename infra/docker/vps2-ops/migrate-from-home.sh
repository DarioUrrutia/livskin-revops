#!/bin/bash
# migrate-from-home.sh — mueve los servicios de VPS 2 desde
# /home/livskin/apps/<svc>/ hacia /srv/livskin-revops/infra/docker/vps2-ops/<svc>/
#
# Estrategia zero-downtime: copia volumes (NO mueve), valida config, reinicia
# uno por uno. Cada servicio es independiente; si uno falla, los demás siguen
# corriendo desde el path nuevo.
#
# Pre-condición: estar en VPS 2 con repo clonado en /srv/livskin-revops y este
# script ejecutándose desde /srv/livskin-revops/infra/docker/vps2-ops/.
#
# Uso:
#   sudo bash migrate-from-home.sh [--dry-run] [--service NAME]
#
# Idempotente: detecta servicios ya migrados y los salta.

set -euo pipefail

REPO_DIR="/srv/livskin-revops"
NEW_BASE="${REPO_DIR}/infra/docker/vps2-ops"
OLD_BASE="/home/livskin/apps"
DRY_RUN="${1:-}"
SERVICES=(n8n vtiger metabase postgres-analytics nginx)

# Mapeo OLD_BASE service name -> NEW_BASE service name
declare -A OLD_TO_NEW=(
    ["n8n"]="n8n"
    ["vtiger"]="vtiger"
    ["metabase"]="metabase"
    ["postgres"]="postgres-analytics"
    ["nginx"]="nginx"
)

log()  { echo "[$(date +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

run() {
    if [ "$DRY_RUN" = "--dry-run" ]; then
        echo "DRY: $*"
    else
        eval "$@"
    fi
}

# Verificación pre-flight
preflight() {
    [ -d "$REPO_DIR" ] || fail "$REPO_DIR no existe — clonar el repo primero"
    [ -d "$NEW_BASE" ] || fail "$NEW_BASE no existe — repo desactualizado?"
    docker network inspect revops_net >/dev/null 2>&1 || \
        fail "network revops_net no existe (docker network create revops_net)"
    log "Preflight OK"
}

# Migración de un servicio individual
migrate_service() {
    local old_name="$1"
    local new_name="${OLD_TO_NEW[$old_name]}"
    local old_dir="${OLD_BASE}/${old_name}"
    local new_dir="${NEW_BASE}/${new_name}"

    log "=== Migrando $old_name -> $new_name ==="

    [ -d "$old_dir" ] || { log "SKIP $old_name: no existe en $old_dir"; return 0; }

    # Detectar si ya está migrado (volúmenes en new_dir y compose corriendo desde ahí)
    local current_path=$(docker inspect "$old_name" 2>/dev/null \
        | jq -r '.[0].Mounts[] | select(.Type=="bind") | .Source' \
        | head -1 || echo "")
    if [[ "$current_path" == "$new_dir"* ]]; then
        log "$old_name ya está corriendo desde $new_dir — skip"
        return 0
    fi

    # Copiar volúmenes (NO mover — backup implícito)
    if [ -d "$old_dir/data" ] && [ ! -d "$new_dir/data" ]; then
        log "Copiando data volume..."
        run "cp -a $old_dir/data $new_dir/data"
    fi
    if [ -d "$old_dir/db" ] && [ ! -d "$new_dir/db" ]; then
        log "Copiando db volume..."
        run "cp -a $old_dir/db $new_dir/db"
    fi
    # Para nginx: certs + logs
    if [ "$old_name" = "nginx" ]; then
        if [ -d "$old_dir/certs" ] && [ ! -d "$new_dir/certs" ]; then
            log "Copiando certs..."
            run "cp -a $old_dir/certs $new_dir/certs"
        fi
        if [ ! -d "$new_dir/logs" ]; then
            run "mkdir -p $new_dir/logs"
        fi
    fi

    # Copiar .env si existe (con valores reales, no .env.example)
    if [ -f "$old_dir/.env" ] && [ ! -f "$new_dir/.env" ]; then
        log "Copiando .env (valores reales)..."
        run "cp $old_dir/.env $new_dir/.env"
        run "chmod 600 $new_dir/.env"
    fi

    # Validar compose nuevo
    log "Validando compose nuevo..."
    run "cd $new_dir && docker compose config -q"

    # Stop old + start new (mismo container_name → docker exige stop primero)
    log "Stopping $old_name desde $old_dir..."
    run "cd $old_dir && docker compose down"

    log "Starting $new_name desde $new_dir..."
    run "cd $new_dir && docker compose up -d"

    # Healthcheck
    sleep 3
    if [ "$DRY_RUN" != "--dry-run" ]; then
        if ! docker ps --format '{{.Names}}' | grep -qE "^${old_name}$"; then
            fail "$old_name no está corriendo tras migrar"
        fi
        log "$old_name running desde $new_dir ✓"
    fi
}

# Main
main() {
    preflight
    for svc in "${SERVICES[@]}"; do
        migrate_service "$svc"
    done
    log "=== Migration completa ==="
    log ""
    log "Verificar manualmente:"
    log "  - https://flow.livskin.site responde"
    log "  - https://crm.livskin.site responde"
    log "  - https://dash.livskin.site responde"
    log ""
    log "Si todo OK, los directorios viejos en $OLD_BASE/ pueden borrarse"
    log "tras 24-48h de operación estable."
}

main "$@"
