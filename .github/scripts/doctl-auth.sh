#!/bin/bash
# doctl-auth.sh — wrapper de `doctl auth init` con strip defensivo de whitespace.
#
# Defensa contra paste-from-clipboard que agrega \n o \r al final de tokens.
#
# Uso:
#   bash .github/scripts/doctl-auth.sh "$DO_API_TOKEN"
#
# Falla con exit 1 si el token (después del strip) queda vacío.

set -euo pipefail

RAW_TOKEN="${1:-}"
[ -z "$RAW_TOKEN" ] && { echo "ERROR: DO_API_TOKEN no recibido como arg"; exit 1; }

# Strip cualquier whitespace (incluye \n, \r, espacios, tabs)
TOKEN=$(printf '%s' "$RAW_TOKEN" | tr -d '[:space:]')

[ -z "$TOKEN" ] && { echo "ERROR: token vacio tras strip whitespace"; exit 1; }

doctl auth init --access-token "$TOKEN"
