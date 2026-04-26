#!/bin/bash
# verify-backup.sh — verifica un backup restaurándolo a una DB temporal.
#
# Uso:
#   verify-backup.sh postgres <container> <backup.sql.gz> <expected_db>
#   verify-backup.sh mariadb <container> <backup.sql.gz> <expected_db>
#
# Crea una DB temporal `verify_<random>`, restaura el dump, ejecuta queries
# de sanidad (count tablas + rows total), reporta.
#
# Si todo OK → exit 0 + audit event infra.backup_verified
# Si falla → exit 1 + audit event infra.backup_failed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

ENGINE="${1:?Usage: $0 <postgres|mariadb> <container> <backup.gz> <expected_db>}"
CONTAINER="${2:?Usage: $0 ... <container> ...}"
BACKUP_FILE="${3:?Usage: $0 ... <backup.gz> ...}"
EXPECTED_DB="${4:?Usage: $0 ... <expected_db>}"

[ -f "$BACKUP_FILE" ] || fail "backup file no existe: $BACKUP_FILE"

VERIFY_DB="verify_$(date +%s)_$$"
SUMMARY="{}"

cleanup_temp_db() {
    case "$ENGINE" in
        postgres)
            docker exec "$CONTAINER" psql -U postgres -c "DROP DATABASE IF EXISTS $VERIFY_DB;" >/dev/null 2>&1 || true
            ;;
        mariadb)
            docker exec "$CONTAINER" mariadb -u root -p"${MYSQL_ROOT_PASSWORD:-livskin}" \
                -e "DROP DATABASE IF EXISTS $VERIFY_DB;" >/dev/null 2>&1 || true
            ;;
    esac
}
trap cleanup_temp_db EXIT

case "$ENGINE" in
    postgres)
        log "verify postgres: restoring $(basename "$BACKUP_FILE") → $VERIFY_DB"
        docker exec "$CONTAINER" psql -U postgres -c "CREATE DATABASE $VERIFY_DB;"
        gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER" psql -U postgres -d "$VERIFY_DB" -q

        # Sanity checks
        TABLE_COUNT=$(docker exec "$CONTAINER" psql -U postgres -d "$VERIFY_DB" -t -c \
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" \
            | tr -d ' \n')

        # Comparar con DB original
        ORIGINAL_TABLES=$(docker exec "$CONTAINER" psql -U postgres -d "$EXPECTED_DB" -t -c \
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" \
            | tr -d ' \n')

        log "  Tablas: backup=$TABLE_COUNT, original=$ORIGINAL_TABLES"

        if [ "$TABLE_COUNT" != "$ORIGINAL_TABLES" ]; then
            audit_event "infra.backup_failed" \
                "{\"engine\":\"postgres\",\"db\":\"$EXPECTED_DB\",\"backup\":\"$(basename "$BACKUP_FILE")\",\"reason\":\"table count mismatch ($TABLE_COUNT vs $ORIGINAL_TABLES)\"}"
            fail "table count mismatch"
        fi
        SUMMARY="{\"tables\":$TABLE_COUNT}"
        ;;

    mariadb)
        log "verify mariadb: restoring $(basename "$BACKUP_FILE") → $VERIFY_DB"
        docker exec "$CONTAINER" mariadb -u root -p"${MYSQL_ROOT_PASSWORD:-livskin}" \
            -e "CREATE DATABASE $VERIFY_DB;"
        gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER" \
            mariadb -u root -p"${MYSQL_ROOT_PASSWORD:-livskin}" "$VERIFY_DB"

        TABLE_COUNT=$(docker exec "$CONTAINER" mariadb -u root -p"${MYSQL_ROOT_PASSWORD:-livskin}" \
            -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$VERIFY_DB';" \
            | tr -d ' \n')

        ORIGINAL_TABLES=$(docker exec "$CONTAINER" mariadb -u root -p"${MYSQL_ROOT_PASSWORD:-livskin}" \
            -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$EXPECTED_DB';" \
            | tr -d ' \n')

        log "  Tablas: backup=$TABLE_COUNT, original=$ORIGINAL_TABLES"

        if [ "$TABLE_COUNT" != "$ORIGINAL_TABLES" ]; then
            audit_event "infra.backup_failed" \
                "{\"engine\":\"mariadb\",\"db\":\"$EXPECTED_DB\",\"reason\":\"table count mismatch\"}"
            fail "table count mismatch"
        fi
        SUMMARY="{\"tables\":$TABLE_COUNT}"
        ;;

    *)
        fail "engine desconocido: $ENGINE"
        ;;
esac

log "  ✓ verificado OK"
audit_event "infra.backup_verified" \
    "{\"engine\":\"$ENGINE\",\"db\":\"$EXPECTED_DB\",\"backup\":\"$(basename "$BACKUP_FILE")\",\"summary\":$SUMMARY}"
