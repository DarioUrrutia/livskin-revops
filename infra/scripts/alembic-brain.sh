#!/usr/bin/env bash
# alembic-brain.sh — wrapper para correr Alembic contra livskin_brain.
#
# Uso:
#   ./alembic-brain.sh current
#   ./alembic-brain.sh upgrade head
#   ./alembic-brain.sh revision -m "mensaje"
#   ./alembic-brain.sh downgrade -1
#   ./alembic-brain.sh history
#
# Ver infra/docker/alembic-brain/README.md para mas detalles.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/../docker/alembic-brain"

cd "$COMPOSE_DIR"
docker compose run --rm alembic-brain "$@"
