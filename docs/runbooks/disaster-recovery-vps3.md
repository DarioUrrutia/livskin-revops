---
runbook: disaster-recovery-vps3
severity: critical
auto_executable: false
trigger:
  - "VPS 3 (livskin-vps-erp) corrupto o destruido"
  - "Pérdida total del droplet sin posibilidad de recovery por snapshot"
required_secrets:
  - DO_API_TOKEN
  - postgres-data password
  - AUDIT_INTERNAL_TOKEN
time_target: "<90 minutos con backups recientes verificados"
related_skills:
  - livskin-ops
---

# Disaster Recovery — VPS 3 (livskin-vps-erp)

## Pre-requisitos

- ✅ DO API token con permisos de droplet creation
- ✅ Backups recientes (<24h) verificados en `/srv/backups/vps3/` en VPS 2
- ✅ SSH key en `keys/claude-livskin` (public + private)
- ✅ Cloudflare Origin Cert wildcard (en Bitwarden)

## Procedimiento

### Paso 1: Crear droplet nuevo en DO

```bash
# 1.1 Crear droplet (CLI)
doctl compute droplet create livskin-vps-erp-new \
  --region fra1 \
  --image ubuntu-24-04-x64 \
  --size s-2vcpu-2gb \
  --vpc-uuid <vpc-id-livskin> \
  --ssh-keys <ssh-key-id> \
  --tag livskin,vps3,erp \
  --wait

# 1.2 Anotar IPs (pública + privada VPC)
doctl compute droplet list livskin-vps-erp-new --format Name,PublicIPv4,PrivateIPv4
```

### Paso 2: Bootstrap (Ubuntu fresca → containers)

```bash
# 2.1 SSH como root inicialmente
ssh root@<new-public-ip>

# 2.2 Instalar Docker + create user 'livskin'
apt-get update && apt-get install -y docker.io docker-compose-plugin git
useradd -m -s /bin/bash -G docker,sudo livskin
echo 'livskin ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/livskin
mkdir -p /home/livskin/.ssh
cp ~/.ssh/authorized_keys /home/livskin/.ssh/
chown -R livskin:livskin /home/livskin/.ssh
chmod 700 /home/livskin/.ssh
chmod 600 /home/livskin/.ssh/authorized_keys

# 2.3 Hardening (Lynis baseline)
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw allow from 10.114.0.0/20 to any port 9100
ufw --force enable

apt-get install -y fail2ban unattended-upgrades
systemctl enable fail2ban unattended-upgrades --now

# 2.4 Clonar repo + setup
sudo -u livskin bash <<'EOF'
cd /srv
sudo mkdir -p /srv && sudo chown livskin:livskin /srv
git clone https://github.com/DarioUrrutia/livskin-revops.git
cd livskin-revops

# Crear network data_net
docker network create data_net

# Levantar postgres-data con datos vacíos (preparado para restore)
cd infra/docker/postgres-data
cp .env.example .env
# RELLENAR .env con password real (Bitwarden)
docker compose up -d

# Esperar postgres listo
sleep 15
EOF
```

### Paso 3: Restore de backups

```bash
# 3.1 Copiar backups desde VPS 2 (que actúa como off-site)
ssh livskin@<vps2-ip> "ls /srv/backups/vps3/livskin_erp-*.sql.gz" | tail -1
scp livskin@<vps2-ip>:/srv/backups/vps3/livskin_erp-<fecha>.sql.gz /tmp/
scp livskin@<vps2-ip>:/srv/backups/vps3/livskin_brain-<fecha>.sql.gz /tmp/

# 3.2 Crear DBs vacías + restore
ssh livskin@<new-public-ip> 'docker exec -i postgres-data psql -U postgres -c "
  CREATE DATABASE livskin_erp;
  CREATE DATABASE livskin_brain;
"'

ssh livskin@<new-public-ip> 'gunzip -c /tmp/livskin_erp-*.sql.gz | docker exec -i postgres-data psql -U postgres livskin_erp'
ssh livskin@<new-public-ip> 'gunzip -c /tmp/livskin_brain-*.sql.gz | docker exec -i postgres-data psql -U postgres livskin_brain'

# 3.3 Verificar counts coinciden con backup
ssh livskin@<new-public-ip> 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  SELECT
    (SELECT count(*) FROM clientes) as clientes,
    (SELECT count(*) FROM ventas) as ventas,
    (SELECT count(*) FROM pagos) as pagos,
    (SELECT count(*) FROM users) as users;
"'
# Debe dar: clientes=134, ventas=88, pagos=84, users=2 (o lo que esté en backup)
```

### Paso 4: Levantar el resto del stack

```bash
ssh livskin@<new-public-ip> bash <<'EOF'
cd /srv/livskin-revops

# Embeddings + nginx + erp-flask
for svc in embeddings-service nginx-vps3 erp-flask; do
  cd infra/docker/$svc
  cp .env.example .env 2>/dev/null || true
  # Editar .env con valores reales
  docker compose up -d --build
  cd /srv/livskin-revops
done

# Smoke tests
curl -sI https://localhost/ping  # via nginx
docker exec erp-flask pytest /app/tests/ --no-cov -x --tb=short
EOF
```

### Paso 5: DNS cutover

```bash
# Vía Cloudflare API o panel:
# - erp.livskin.site → A record → <new-public-ip>
# - TTL bajo (60s) por si necesitamos cambiar de nuevo
```

### Paso 6: Validación final

```bash
# 6.1 URL pública responde
curl -sI https://erp.livskin.site/ping

# 6.2 Login funciona (Dario debe poder loguear)
# 6.3 Audit log captura nuevo evento
# 6.4 Sensor cross-VPS reachable desde VPS 2
ssh livskin@<vps2-ip> 'curl -sI http://10.114.0.X:9100/api/health'  # nueva IP privada
```

### Paso 7: Cleanup

```bash
# Borrar droplet viejo (si todavía existe)
doctl compute droplet delete <old-droplet-id>

# Update GitHub Secrets si IP cambió
# - VPS3_HOST → nueva IP pública
# - actualizar también en infra/scripts/backups/backup-vps2.sh BACKUP_REMOTE_HOST
```

## Time targets

| Paso | Target |
|---|---|
| 1. Crear droplet | 5 min |
| 2. Bootstrap | 20 min |
| 3. Restore DBs | 30 min |
| 4. Levantar stack | 15 min |
| 5. DNS cutover | 5 min |
| 6. Validación | 10 min |
| **Total** | **~85 min** |

## Post-recovery

- Documentar incidente en `docs/audits/dr-vps3-<fecha>.md`
- Snapshot DO del nuevo droplet (baseline)
- Verificar próximo backup automático corre OK
- Ajustar `docs/sistema-mapa.md` con nueva IP

## Validación drill

Este runbook se ejecuta como drill cada 6 meses (cron en calendar). Crear
droplet temporal `dr-test-vps3`, ejecutar todos los pasos, validar, y
borrar. Documentar findings + tiempos reales.
