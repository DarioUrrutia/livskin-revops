#!/bin/bash
# do-snapshot.sh — crea/restaura/lista snapshots DO via doctl.
#
# Usage:
#   do-snapshot.sh create <droplet-name> <tag>
#   do-snapshot.sh restore <droplet-name> <snapshot-id>
#   do-snapshot.sh latest <droplet-name> --tag <tag>  # imprime ID del último
#
# Requiere: DO_API_TOKEN env var (con scope read+write para snapshots).
# Requiere: doctl instalado (lo instala el workflow vía apt o curl).

set -euo pipefail

CMD="${1:-help}"
shift || true

case "$CMD" in
  create)
    DROPLET="$1"
    TAG="$2"
    TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
    SNAPSHOT_NAME="${DROPLET}-${TAG}-${TIMESTAMP}"
    echo "[do-snapshot] Creating snapshot ${SNAPSHOT_NAME} for ${DROPLET}..."
    DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep -E "\\s${DROPLET}\$" | awk '{print $1}')
    [ -z "$DROPLET_ID" ] && { echo "ERROR: no droplet found named ${DROPLET}"; exit 1; }
    doctl compute droplet-action snapshot "$DROPLET_ID" --snapshot-name "$SNAPSHOT_NAME" --wait
    SNAP_ID=$(doctl compute snapshot list --format ID,Name --no-header | grep "$SNAPSHOT_NAME" | awk '{print $1}')
    echo "$SNAP_ID"
    ;;

  latest)
    DROPLET="$1"
    TAG="${2:-pre-deploy}"
    SNAP_ID=$(doctl compute snapshot list --format ID,Name,CreatedAt --no-header \
      | grep -E "${DROPLET}-${TAG}-" \
      | sort -k 3 -r \
      | head -1 \
      | awk '{print $1}')
    [ -z "$SNAP_ID" ] && { echo "ERROR: no snapshot found for ${DROPLET}-${TAG}"; exit 1; }
    echo "$SNAP_ID"
    ;;

  restore)
    DROPLET="$1"
    SNAPSHOT_ID="$2"
    echo "[do-snapshot] DESTRUCTIVE: restoring ${DROPLET} from snapshot ${SNAPSHOT_ID}..."
    DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep -E "\\s${DROPLET}\$" | awk '{print $1}')
    [ -z "$DROPLET_ID" ] && { echo "ERROR: no droplet found"; exit 1; }
    doctl compute droplet-action restore "$DROPLET_ID" --image-id "$SNAPSHOT_ID" --wait
    ;;

  cleanup)
    # Borra snapshots viejos (>7 días) para ahorrar costos
    DROPLET="$1"
    TAG="${2:-pre-deploy}"
    CUTOFF=$(date -u -d '7 days ago' +%Y-%m-%d)
    echo "[do-snapshot] Cleaning up snapshots ${DROPLET}-${TAG}-* older than ${CUTOFF}..."
    doctl compute snapshot list --format ID,Name,CreatedAt --no-header \
      | grep -E "${DROPLET}-${TAG}-" \
      | while read id name created; do
          [ "${created:0:10}" \< "$CUTOFF" ] && {
            echo "  deleting $id ($name)"
            doctl compute snapshot delete "$id" -f
          }
        done
    ;;

  *)
    echo "Usage: $0 {create|latest|restore|cleanup} <droplet> [tag|snapshot-id]"
    exit 1
    ;;
esac
