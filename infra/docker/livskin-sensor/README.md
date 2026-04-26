# livskin-sensor

Sensor uniforme cross-VPS para recolección de estado del sistema.

## Endpoints

| Endpoint | Auth | Propósito |
|---|---|---|
| `GET /api/health` | sin auth | Liveness check |
| `GET /api/system-state` | `X-Internal-Token` | Snapshot detallado |

## Modos de despliegue

### VPS 2 (livskin-ops) — Container Docker

```bash
# En VPS 2, después del git pull:
cd /srv/livskin-revops/infra/docker/vps2-ops
mkdir -p livskin-sensor
cp -r ../../livskin-sensor/* livskin-sensor/
cd livskin-sensor

# Crear .env con VPS_ALIAS + VPS_ROLE + AUDIT_INTERNAL_TOKEN
cat > .env <<EOF
VPS_ALIAS=livskin-ops
VPS_ROLE=vps2-ops
AUDIT_INTERNAL_TOKEN=<from-bitwarden>
EOF
chmod 600 .env

docker compose up -d
```

### VPS 3 (livskin-erp) — Endpoint en erp-flask

No requiere container separado. El endpoint `/api/system-state` vive en
[`infra/docker/erp-flask/routes/api_internal.py`](../erp-flask/routes/api_internal.py).

### VPS 1 (livskin-wp) — Systemd service (sin Docker)

```bash
# En VPS 1:
sudo apt-get install -y python3-pip
sudo pip3 install -r /srv/livskin-revops/infra/docker/livskin-sensor/requirements.txt

# Copiar script
sudo cp /srv/livskin-revops/infra/docker/livskin-sensor/sensor.py /usr/local/bin/livskin-sensor

# Systemd service
sudo tee /etc/systemd/system/livskin-sensor.service <<EOF
[Unit]
Description=Livskin Sensor (system-state endpoint)
After=network.target

[Service]
Type=simple
Environment="VPS_ALIAS=livskin-wp"
Environment="VPS_ROLE=vps1-wp"
Environment="AUDIT_INTERNAL_TOKEN=<from-bitwarden>"
Environment="REPO_PATH=/srv/livskin-revops"
ExecStart=/usr/bin/gunicorn --bind 127.0.0.1:9100 --workers 1 --chdir /usr/local/bin sensor:app
Restart=always
User=www-data

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable livskin-sensor --now
```

## Firewall (UFW) — Cross-VPS access

En **cada VPS** (1, 2, 3) abrir el puerto 9100 SOLO al rango VPC:

```bash
sudo ufw allow from 10.114.0.0/20 to any port 9100 proto tcp comment 'livskin-sensor cross-VPS'
sudo ufw reload
```

NO abrir 9100 al público — el sensor expone container info que ayuda a
atacantes hacer reconnaissance.

## Verificar

Desde **otro VPS** dentro del VPC:

```bash
# Health (sin token)
curl -sf http://10.114.0.X:9100/api/health | jq

# System state (con token)
curl -sf -H "X-Internal-Token: <token>" http://10.114.0.X:9100/api/system-state | jq
```

Desde **fuera del VPC** debería timeout o connection refused (UFW bloquea).
