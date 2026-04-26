#!/bin/bash
# do-snapshot.sh — crea/restaura/lista snapshots DO via doctl.
#
# Usage:
#   do-snapshot.sh create <droplet-name> <tag>      # imprime SNAP_ID
#   do-snapshot.sh restore <droplet-name> <snap-id>
#   do-snapshot.sh latest <droplet-name> [tag]      # imprime ID del último
#   do-snapshot.sh cleanup <droplet-name> [tag]     # borra snapshots >7d
#
# Requiere: doctl + jq instalados, DO_API_TOKEN configurado via doctl auth init.

set -euo pipefail

CMD="${1:-help}"
shift || true

# Helper: encuentra droplet ID por name usando JSON output (mas robusto que parsing tabular)
find_droplet_id() {
    local name="$1"
    doctl compute droplet list -o json \
        | jq -r ".[] | select(.name == \"$name\") | .id"
}

# Helper: encuentra snapshot ID por nombre exacto
find_snapshot_id_by_name() {
    local snap_name="$1"
    doctl compute snapshot list --resource droplet -o json \
        | jq -r ".[] | select(.name == \"$snap_name\") | .id"
}

case "$CMD" in
  create)
    DROPLET="$1"
    TAG="$2"
    TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
    SNAPSHOT_NAME="${DROPLET}-${TAG}-${TIMESTAMP}"
    echo "[do-snapshot] Creating snapshot ${SNAPSHOT_NAME} for ${DROPLET}..." >&2

    DROPLET_ID=$(find_droplet_id "$DROPLET")
    [ -z "$DROPLET_ID" ] && { echo "ERROR: no droplet found named ${DROPLET}" >&2; exit 1; }
    echo "[do-snapshot] Droplet ID: $DROPLET_ID" >&2

    doctl compute droplet-action snapshot "$DROPLET_ID" --snapshot-name "$SNAPSHOT_NAME" --wait >&2
    SNAP_ID=$(find_snapshot_id_by_name "$SNAPSHOT_NAME")
    [ -z "$SNAP_ID" ] && { echo "ERROR: snapshot creado pero no se pudo recuperar ID" >&2; exit 1; }

    # stdout: solo el ID (consumido por workflow GHA)
    echo "$SNAP_ID"
    ;;

  latest)
    DROPLET="$1"
    TAG="${2:-pre-deploy}"
    PREFIX="${DROPLET}-${TAG}-"
    SNAP_ID=$(doctl compute snapshot list --resource droplet -o json \
      | jq -r ".[] | select(.name | startswith(\"$PREFIX\")) | [.created_at, .id] | @tsv" \
      | sort -r | head -1 | awk '{print $2}')
    [ -z "$SNAP_ID" ] && { echo "ERROR: no snapshot found for $PREFIX" >&2; exit 1; }
    echo "$SNAP_ID"
    ;;

  restore)
    DROPLET="$1"
    SNAPSHOT_ID="$2"
    echo "[do-snapshot] DESTRUCTIVE: restoring ${DROPLET} from snapshot ${SNAPSHOT_ID}..." >&2
    DROPLET_ID=$(find_droplet_id "$DROPLET")
    [ -z "$DROPLET_ID" ] && { echo "ERROR: no droplet found named ${DROPLET}" >&2; exit 1; }
    doctl compute droplet-action restore "$DROPLET_ID" --image-id "$SNAPSHOT_ID" --wait >&2
    ;;

  cleanup)
    DROPLET="$1"
    TAG="${2:-pre-deploy}"
    PREFIX="${DROPLET}-${TAG}-"
    CUTOFF_EPOCH=$(date -u -d '7 days ago' +%s)
    echo "[do-snapshot] Cleaning up snapshots ${PREFIX}* older than 7 days..." >&2

    doctl compute snapshot list --resource droplet -o json \
      | jq -r ".[] | select(.name | startswith(\"$PREFIX\")) | [.id, .name, .created_at] | @tsv" \
      | while IFS=$'\t' read -r id name created_at; do
          [ -z "$id" ] && continue
          # Convert ISO timestamp to epoch (BSD date vs GNU date — usa python como fallback)
          created_epoch=$(date -u -d "$created_at" +%s 2>/dev/null || \
                          python3 -c "from datetime import datetime; print(int(datetime.fromisoformat('$created_at'.replace('Z','+00:00')).timestamp()))" 2>/dev/null || \
                          echo "0")
          if [ "$created_epoch" -lt "$CUTOFF_EPOCH" ] && [ "$created_epoch" -gt 0 ]; then
              echo "  deleting $id ($name, created $created_at)" >&2
              doctl compute snapshot delete "$id" -f >&2 || echo "  WARN: failed to delete $id" >&2
          fi
        done
    ;;

  *)
    echo "Usage: $0 {create|latest|restore|cleanup} <droplet> [tag|snapshot-id]" >&2
    exit 1
    ;;
esac
