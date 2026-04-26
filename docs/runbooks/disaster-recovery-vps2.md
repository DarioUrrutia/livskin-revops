---
runbook: disaster-recovery-vps2
severity: critical
auto_executable: false
trigger:
  - "VPS 2 (livskin-vps-operations) corrupto o destruido"
required_secrets:
  - DO_API_TOKEN
  - vtiger-db root password
  - postgres-analytics password
  - n8n credentials (en sqlite del backup)
time_target: "<90 minutos con backups recientes"
related_skills:
  - livskin-ops
---

# Disaster Recovery — VPS 2 (livskin-vps-operations)

## Pre-requisitos

- ✅ DO API token + SSH keys
- ✅ Backups recientes en `/srv/backups/vps2/` en VPS 3
- ✅ Cloudflare Origin Cert wildcard

## Procedimiento

### Paso 1: Crear droplet nuevo

```bash
doctl compute droplet create livskin-vps-operations-new \
  --region fra1 \
  --image ubuntu-24-04-x64 \
  --size s-2vcpu-4gb \
  --vpc-uuid <vpc-id> \
  --ssh-keys <key-id> \
  --tag livskin,vps2,ops \
  --wait
```

### Paso 2: Bootstrap

```bash
ssh root@<new-ip>
apt-get update && apt-get install -y docker.io docker-compose-plugin git ufw fail2ban

# User livskin + SSH
useradd -m -s /bin/bash -G docker,sudo livskin
echo 'livskin ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/livskin
mkdir -p /home/livskin/.ssh
cp ~/.ssh/authorized_keys /home/livskin/.ssh/
chown -R livskin:livskin /home/livskin/.ssh

# Hardening
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw allow from 10.114.0.0/20 to any port 9100  # sensor
ufw allow from 10.114.0.0/20 to any port 5432  # postgres-analytics cross-VPS query
ufw --force enable
systemctl enable fail2ban unattended-upgrades --now
```

### Paso 3: Clonar repo + restaurar configs

```bash
sudo -u livskin bash <<'EOF'
cd /srv
sudo mkdir -p /srv && sudo chown livskin:livskin /srv
git clone https://github.com/DarioUrrutia/livskin-revops.git
cd livskin-revops

# Network compartida + aislada
docker network create revops_net
# vtiger_internal se crea automáticamente al levantar vtiger compose

# Para cada servicio, crear .env real desde Bitwarden
cd infra/docker/vps2-ops
for svc in postgres-analytics vtiger metabase n8n nginx; do
  cd $svc
  cp .env.example .env
  # EDITAR .env CON VALORES REALES (Bitwarden)
  cd ..
done
EOF
```

### Paso 4: Restore data

```bash
# Copiar backups desde VPS 3
ssh livskin@<new-vps2-ip> bash <<EOF
mkdir -p /tmp/restore
EOF

scp livskin@<vps3-ip>:/srv/backups/vps2/analytics-*.sql.gz /tmp/restore/ -r
scp livskin@<vps3-ip>:/srv/backups/vps2/metabase-*.sql.gz /tmp/restore/
scp livskin@<vps3-ip>:/srv/backups/vps2/livskin_db-*.sql.gz /tmp/restore/
scp livskin@<vps3-ip>:/srv/backups/vps2/n8n-data-*.tar.gz /tmp/restore/

# Levantar postgres-analytics + restore
ssh livskin@<new-vps2-ip> bash <<'EOF'
cd /srv/livskin-revops/infra/docker/vps2-ops/postgres-analytics
docker compose up -d
sleep 15

# Restore analytics
docker exec -i postgres-analytics psql -U analytics_user -d analytics < <(gunzip -c /tmp/restore/analytics-*.sql.gz | tail -1)
docker exec -i postgres-analytics psql -U analytics_user -d metabase < <(gunzip -c /tmp/restore/metabase-*.sql.gz | tail -1)

# Levantar vtiger-db + restore
cd ../vtiger
docker compose up -d
sleep 15
docker exec -i vtiger-db mariadb -u root -p$VTIGER_DB_ROOT_PASSWORD livskin_db < <(gunzip -c /tmp/restore/livskin_db-*.sql.gz | tail -1)

# Levantar metabase + vtiger app
docker compose up -d
cd ../metabase
docker compose up -d

# n8n: extract data tarball ANTES de levantar
mkdir -p ../n8n
cd ../n8n
tar -xzf /tmp/restore/n8n-data-*.tar.gz -C ./
docker compose up -d

# Nginx final
cd ../nginx
docker compose up -d
EOF
```

### Paso 5: DNS cutover

```bash
# Cloudflare:
# - flow.livskin.site → A → <new-public-ip>
# - crm.livskin.site  → A → <new-public-ip>
# - dash.livskin.site → A → <new-public-ip>
```

### Paso 6: Validación

```bash
curl -sI https://flow.livskin.site
curl -sI https://crm.livskin.site
curl -sI https://dash.livskin.site

# n8n workflows aparecen en UI
# vtiger login funciona
# metabase muestra dashboards
```

### Paso 7: Cleanup + update Secrets

```bash
doctl compute droplet delete <old-vps2-id>

# Update GitHub Secrets:
# - VPS2_HOST → nueva IP
# - actualizar BACKUP_REMOTE_HOST en backup-vps3.sh
```

## Time targets

| Paso | Target |
|---|---|
| Crear droplet | 5 min |
| Bootstrap | 15 min |
| Configs | 10 min |
| Restore data (4 backups) | 35 min |
| DNS cutover | 5 min |
| Validación | 15 min |
| **Total** | **~85 min** |

## Post-recovery

- Snapshot DO baseline del nuevo droplet
- Documentar en `docs/audits/`
- Update sistema-mapa.md con IP nueva
- Notificar a usuarios de Vtiger sobre downtime
