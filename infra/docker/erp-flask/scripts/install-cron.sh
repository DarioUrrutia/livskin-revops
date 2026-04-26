#!/bin/bash
# install-cron.sh — instala los crons de mantenimiento del ERP en VPS 3.
#
# Crons instalados:
# 1. infra-snapshot collect — cada 5 min, pollea sensors y persiste
# 2. infra-snapshot cleanup — diario 03:00, borra snapshots >30 días
#
# Uso (en VPS 3, como user con permiso a docker):
#   sudo bash install-cron.sh
#
# Idempotente: borra crons viejos antes de instalar.

set -euo pipefail

LOG_DIR="/var/log/livskin-cron"
sudo mkdir -p "$LOG_DIR"
sudo chmod 755 "$LOG_DIR"

CRON_FILE="/etc/cron.d/livskin-erp"

sudo tee "$CRON_FILE" > /dev/null <<'EOF'
# /etc/cron.d/livskin-erp — crons de mantenimiento del ERP (Bloque 0.4)
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Recolectar snapshots cross-VPS cada 5 min
*/5 * * * * livskin docker exec erp-flask python -m services.infra_snapshot_service collect >> /var/log/livskin-cron/snapshot-collect.log 2>&1

# Cleanup snapshots viejos diario 03:00 UTC
0 3 * * * livskin docker exec erp-flask python -m services.infra_snapshot_service cleanup >> /var/log/livskin-cron/snapshot-cleanup.log 2>&1
EOF

sudo chmod 644 "$CRON_FILE"

# Verificar sintaxis
sudo crontab -l 2>/dev/null || true
echo "Cron jobs instalados en $CRON_FILE"
echo "Logs: $LOG_DIR/"
echo ""
echo "Test manual:"
echo "  docker exec erp-flask python -m services.infra_snapshot_service collect"
