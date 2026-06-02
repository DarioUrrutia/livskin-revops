#!/bin/bash
# install-cron-vps3.sh — instala cron de backups en VPS 3.
# Verificación de backups recibidos también va aquí (VPS 3 verifica los
# backups de VPS 2 que llegan a /srv/backups/vps2/).

set -euo pipefail

CRON_FILE="/etc/cron.d/livskin-backups"
BACKUP_SCRIPT="/srv/livskin-revops/infra/scripts/backups/backup-vps3.sh"
VERIFY_SCRIPT="/srv/livskin-revops/infra/scripts/backups/verify-backup.sh"

[ -x "$BACKUP_SCRIPT" ] || { echo "ERROR: $BACKUP_SCRIPT no es ejecutable"; exit 1; }

sudo mkdir -p /var/log /srv/backups/local /srv/backups/vps2

# Para que VPS 2 pueda transferir aca, necesitamos un user 'backup' con
# directorio escribible
sudo useradd -r -s /bin/bash -d /srv/backups -m backup 2>/dev/null || true
sudo chown -R backup:backup /srv/backups

sudo tee "$CRON_FILE" > /dev/null <<'EOF'
# /etc/cron.d/livskin-backups — cross-VPS backup orchestration en VPS 3
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
AUDIT_INTERNAL_TOKEN=loaded-from-systemd-environment

# 02:00 UTC — backup VPS 3 (transfer a VPS 2)
0 2 * * * livskin AUDIT_INTERNAL_TOKEN="$(cat /srv/livskin-revops/keys/.audit-internal-token 2>/dev/null)" /srv/livskin-revops/infra/scripts/backups/backup-vps3.sh >> /var/log/livskin-backup.log 2>&1

# 04:00 UTC — verify backups de VPS 2 que llegaron a /srv/backups/vps2/
0 4 * * * livskin AUDIT_INTERNAL_TOKEN="$(cat /srv/livskin-revops/keys/.audit-internal-token 2>/dev/null)" /srv/livskin-revops/infra/scripts/backups/verify-vps2-backups.sh >> /var/log/livskin-backup.log 2>&1

# 05:00 UTC — cleanup local (>30 dias en /srv/backups/local + /srv/backups/vps2)
0 5 * * * livskin find /srv/backups/local /srv/backups/vps2 -maxdepth 1 -type f -mtime +30 -delete >> /var/log/livskin-backup.log 2>&1
EOF

sudo chmod 644 "$CRON_FILE"
echo "Cron de backups instalado en $CRON_FILE"
echo "Logs: /var/log/livskin-backup.log"
echo ""
echo "Pendiente:"
echo "  1. Crear /srv/livskin-revops/keys/.audit-internal-token con el token"
echo "  2. Generar SSH key /root/.ssh/backup-target en VPS 3"
echo "  3. Copiar pública del VPS 2 al VPS 3 user backup"
echo "  4. Test: sudo -u livskin /srv/livskin-revops/infra/scripts/backups/backup-vps3.sh"
