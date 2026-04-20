#!/usr/bin/env bash
# alembic-erp.sh — wrapper para correr Alembic contra livskin_erp.
#
# Uso idéntico a alembic-brain.sh pero apunta a la DB del ERP.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/../docker/alembic-erp"

cd "$COMPOSE_DIR"
docker compose run --rm alembic-erp "$@"
