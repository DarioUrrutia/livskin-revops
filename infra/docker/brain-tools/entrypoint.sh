#!/bin/bash
# Entrypoint — despacha a indexer o query segun subcomando.
set -euo pipefail

cmd="${1:-help}"
shift || true

case "$cmd" in
  index)
    exec python /app/index.py "$@"
    ;;
  query)
    if [ $# -lt 1 ]; then
      echo "Uso: brain-tools query '<texto>' [limit]" >&2
      exit 1
    fi
    exec python /app/query.py "$@"
    ;;
  help|--help|-h)
    cat <<EOF
brain-tools — CLI para el segundo cerebro de Livskin

Comandos:
  index               Indexa todos los .md del repo en project_knowledge (L2)
  query "<pregunta>"  Busca chunks similares semanticamente (coseno)
  help                Este mensaje

Ejemplos:
  docker compose run --rm brain-tools index
  docker compose run --rm brain-tools query "como se hace CI CD"
  docker compose run --rm brain-tools query "arquitectura VPS" 3
EOF
    ;;
  *)
    echo "Subcomando desconocido: $cmd" >&2
    echo "Usa 'help' para ver los disponibles." >&2
    exit 1
    ;;
esac
