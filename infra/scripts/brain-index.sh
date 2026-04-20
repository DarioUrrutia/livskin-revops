#!/usr/bin/env bash
# brain-index.sh — re-indexa todos los .md del repo en Layer 2 del cerebro.
#
# Uso:
#   ./brain-index.sh
#
# Ver infra/docker/brain-tools/README.md para detalles.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/../docker/brain-tools"

cd "$COMPOSE_DIR"
docker compose run --rm brain-tools index
