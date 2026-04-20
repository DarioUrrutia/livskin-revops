#!/usr/bin/env bash
# brain-query.sh — busca semanticamente en Layer 2 del cerebro.
#
# Uso:
#   ./brain-query.sh "pregunta"
#   ./brain-query.sh "pregunta" 10     # top 10 resultados (default 5)

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Uso: $0 '<texto>' [limit]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/../docker/brain-tools"

cd "$COMPOSE_DIR"
docker compose run --rm brain-tools query "$@"
