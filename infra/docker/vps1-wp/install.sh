#!/bin/bash
# install.sh — bootstrap idempotente de VPS 1 desde Ubuntu fresca.
#
# Reconstruye el VPS WP en caso de DR (disaster recovery).
# Time target: <45 min con backups disponibles.
#
# Uso:
#   sudo bash install.sh [--restore-from=BACKUP_PATH]
#
# Pre-condición: Ubuntu 24.04, IP estática DO en VPC 10.114.0.0/20, root SSH.

set -euo pipefail

LOG_PREFIX="[install-vps1]"
log() { echo "${LOG_PREFIX} $*"; }
fail() { echo "${LOG_PREFIX} ERROR: $*" >&2; exit 1; }

# Configurable via env
WP_DOMAIN="${WP_DOMAIN:-livskin.site}"
WP_DB_NAME="${WP_DB_NAME:-livskin_wp}"
WP_DB_USER="${WP_DB_USER:-livskin_user}"
WP_DB_PASS="${WP_DB_PASS:-}"  # required, no default — Bitwarden
WP_ADMIN_EMAIL="${WP_ADMIN_EMAIL:-daizurma@gmail.com}"
RESTORE_FROM="${RESTORE_FROM:-}"

[ -z "$WP_DB_PASS" ] && fail "WP_DB_PASS requerida (export desde Bitwarden)"
[ "$EUID" -eq 0 ] || fail "ejecutar como root o sudo"

# 1. Sistema base
log "1/8 Actualizando sistema..."
apt-get update -y
apt-get upgrade -y

# 2. Hardening (Lynis baseline + UFW + Fail2Ban)
log "2/8 Instalando herramientas de seguridad..."
apt-get install -y ufw fail2ban unattended-upgrades

# Whitelist SSH + HTTP/HTTPS
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

systemctl enable fail2ban --now
systemctl enable unattended-upgrades --now

# 3. Stack web
log "3/8 Instalando nginx + PHP 8.1 + MariaDB..."
apt-get install -y nginx mariadb-server \
    php8.1-fpm php8.1-mysql php8.1-curl php8.1-gd php8.1-mbstring \
    php8.1-xml php8.1-zip php8.1-imagick php8.1-intl

systemctl enable nginx php8.1-fpm mariadb --now

# 4. MariaDB hardening + DB
log "4/8 Configurando MariaDB..."
mysql -e "CREATE DATABASE IF NOT EXISTS ${WP_DB_NAME} CHARACTER SET utf8mb4;"
mysql -e "CREATE USER IF NOT EXISTS '${WP_DB_USER}'@'localhost' IDENTIFIED BY '${WP_DB_PASS}';"
mysql -e "GRANT ALL PRIVILEGES ON ${WP_DB_NAME}.* TO '${WP_DB_USER}'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# 5. WordPress core
log "5/8 Descargando WordPress..."
mkdir -p /var/www/livskin
if [ -n "$RESTORE_FROM" ]; then
    log "5/8 Restoring desde backup $RESTORE_FROM..."
    tar -xzf "$RESTORE_FROM" -C /var/www/livskin --strip-components=1
else
    cd /tmp
    wget -q https://wordpress.org/latest.tar.gz
    tar -xzf latest.tar.gz
    cp -r wordpress/* /var/www/livskin/
    rm -rf wordpress latest.tar.gz
fi
chown -R www-data:www-data /var/www/livskin

# 6. nginx config
log "6/8 Aplicando nginx config..."
cp "$(dirname "$0")/nginx/livskin.conf" /etc/nginx/sites-available/livskin
ln -sf /etc/nginx/sites-available/livskin /etc/nginx/sites-enabled/livskin

# 7. mu-plugins
log "7/8 Sincronizando mu-plugins..."
mkdir -p /var/www/livskin/wp-content/mu-plugins
rsync -av --delete "$(dirname "$0")/wp-mu-plugins/" /var/www/livskin/wp-content/mu-plugins/
chown -R www-data:www-data /var/www/livskin/wp-content/mu-plugins

# 8. TLS (certbot)
log "8/8 Solicitando cert TLS Let's Encrypt..."
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d "${WP_DOMAIN}" -d "www.${WP_DOMAIN}" \
    --non-interactive --agree-tos --email "${WP_ADMIN_EMAIL}" \
    || log "WARNING: certbot falló — verificar DNS apuntando a este IP"

# Auto-renew cron
echo "0 2 * * * root certbot renew --quiet --post-hook 'systemctl reload nginx'" > /etc/cron.d/certbot

systemctl reload nginx
log ""
log "=== Install completo ==="
log "Verificar:"
log "  curl -sI https://${WP_DOMAIN} | head -3"
log "  Visitar https://${WP_DOMAIN} y completar setup WP si fresca"
log ""
log "Si restore desde backup, restaurar también la DB con:"
log "  mariadb ${WP_DB_NAME} < backup.sql"
