---
runbook: disaster-recovery-vps1
severity: critical
auto_executable: false
trigger:
  - "VPS 1 (livskin-wp) corrupto o destruido"
  - "WordPress completo perdido"
required_secrets:
  - DO_API_TOKEN
  - WP_DB_PASS (Bitwarden)
  - LETSENCRYPT_EMAIL
time_target: "<45 minutos con backups recientes"
related_skills:
  - livskin-ops
---

# Disaster Recovery — VPS 1 (livskin-wp)

## Pre-requisitos

- ✅ DO API token + SSH keys
- ✅ Backups en `/srv/backups/vps1/` en VPS 2:
  - `livskin_wp-<fecha>.sql.gz` (DB)
  - `wordpress-files-<fecha>.tar.gz` (filesystem)
- ✅ DNS Cloudflare control

## Procedimiento

### Paso 1: Crear droplet

```bash
doctl compute droplet create Livskin-WP-01-new \
  --region fra1 \
  --image ubuntu-24-04-x64 \
  --size s-1vcpu-1gb \
  --vpc-uuid <vpc-id> \
  --ssh-keys <key-id> \
  --tag livskin,vps1,wordpress \
  --wait
```

### Paso 2: Bootstrap automatizado via install.sh

```bash
ssh root@<new-ip> bash <<'EOF'
# Clonar repo
apt-get update && apt-get install -y git
mkdir -p /srv && cd /srv
git clone https://github.com/DarioUrrutia/livskin-revops.git

# Ejecutar install.sh
cd /srv/livskin-revops/infra/docker/vps1-wp
export WP_DB_PASS="<from-bitwarden>"
export WP_ADMIN_EMAIL="daizurma@gmail.com"
export RESTORE_FROM=""  # primero install fresca, después restore
sudo bash install.sh
EOF
```

`install.sh` se encarga de:
- Update + hardening (UFW + fail2ban + unattended-upgrades)
- Stack: nginx + PHP 8.1 + MariaDB
- DB + user creados
- WP core descargado
- nginx config aplicada
- mu-plugins sincronizados
- Cert TLS Let's Encrypt

### Paso 3: Restore de backups

```bash
# Copiar backups desde VPS 2
scp livskin@<vps2-ip>:/srv/backups/vps1/livskin_wp-*.sql.gz /tmp/
scp livskin@<vps2-ip>:/srv/backups/vps1/wordpress-files-*.tar.gz /tmp/

ssh root@<new-ip> bash <<'EOF'
# Restore DB
gunzip -c /tmp/livskin_wp-*.sql.gz | mariadb livskin_wp

# Restore filesystem (sobrescribe el WP fresca de install.sh)
cd /var/www
tar -xzf /tmp/wordpress-files-*.tar.gz
chown -R www-data:www-data livskin/

# Restart php-fpm para tomar la DB restaurada
systemctl restart php8.1-fpm nginx
EOF
```

### Paso 4: DNS cutover

```bash
# Cloudflare:
# - livskin.site → A → <new-public-ip>
# - www.livskin.site → CNAME → livskin.site
# TTL 60s temporalmente
```

### Paso 5: Validación

```bash
# 1. Site responde
curl -sI https://livskin.site

# 2. WP admin accesible
# https://livskin.site/wp-admin/ login con cuenta de Dario

# 3. Plugins activos
curl -s https://livskin.site/wp-json/ | jq '.routes' | head

# 4. SureForms aún manda webhooks correctamente (test desde flow.livskin.site)
```

### Paso 6: Cleanup

```bash
doctl compute droplet delete <old-vps1-id>

# Update GitHub Secrets:
# - VPS1_HOST → nueva IP
# - WP_DB_PASS si rotaste

# Update sistema-mapa.md con IP nueva
```

## Time targets

| Paso | Target |
|---|---|
| Crear droplet | 5 min |
| Bootstrap install.sh | 15 min |
| Restore data | 15 min |
| DNS cutover | 3 min |
| Validación | 5 min |
| **Total** | **~43 min** |

## Caveats

- WordPress 6.9.4: si la versión de WP en el backup está obsoleta, post-recovery
  hacer `wp core update` desde admin
- Plugins activos pueden perder licencias (LatePoint, Astra Pro): renovar
- Certbot va a pedir nueva validación al cambiar IP (HTTP-01 challenge)

## Post-recovery

- Snapshot DO baseline
- Documentar en `docs/audits/`
- Verificar próximo backup automático
