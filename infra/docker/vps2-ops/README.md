# VPS 2 — Operaciones (livskin-vps-operations)

**IP pública:** 167.172.97.197
**IP privada VPC:** 10.114.0.2
**Hostname:** `livskin-vps-operations`

## Rol

Stack de orquestación + analítica + CRM. Punto central de:
- **n8n** — workflows (form webhooks, agent dispatch, ETL)
- **Vtiger** — CRM (master del lead digital, ADR-0015)
- **Metabase** — dashboards de analítica
- **Postgres-analytics** — warehouse OLAP (analytics + metabase databases)
- **Nginx** — reverse proxy (TLS termination, 3 subdominios públicos)

## Containers

| Container | Image | Network | URL pública |
|---|---|---|---|
| `n8n` | `n8nio/n8n:latest` | `revops_net` | https://flow.livskin.site |
| `vtiger` | `vtigercrm/vtigercrm-8.2.0:latest` | `revops_net` + `vtiger_internal` | https://crm.livskin.site |
| `vtiger-db` | `mariadb:10.6` | `vtiger_internal` (aislada) | (interno) |
| `metabase` | `metabase/metabase:latest` | `revops_net` | https://dash.livskin.site |
| `postgres-analytics` | `postgres:16` | `revops_net` | (interno) |
| `nginx` | `nginx:stable` | `revops_net` | proxy externo |

## Networks

- **`revops_net`** — bridge compartido entre todos los containers públicos. External (creada manualmente con `docker network create revops_net`).
- **`vtiger_internal`** — aislada (defensa-en-profundidad ADR-0003) — solo vtiger ↔ vtiger-db hablan acá. La DB nunca expuesta al revops_net.

## Estructura de directorios

```
vps2-ops/
├── README.md                           # este archivo
├── n8n/
│   ├── docker-compose.yml
│   └── .env.example                    # config de host/protocol
├── vtiger/
│   ├── docker-compose.yml
│   └── .env.example                    # passwords mariadb
├── metabase/
│   ├── docker-compose.yml
│   └── .env.example                    # password postgres
├── postgres-analytics/
│   ├── docker-compose.yml
│   └── .env.example                    # password postgres
└── nginx/
    ├── docker-compose.yml
    ├── conf/
    │   └── nginx.conf                  # nginx core config
    └── sites/
        ├── crm.conf                    # crm.livskin.site → vtiger:80
        ├── dash.conf                   # dash.livskin.site → metabase:3000
        └── n8n.conf                    # flow.livskin.site → n8n:5678
```

## Path en el VPS

**Histórico:** `/home/livskin/apps/<servicio>/`
**Objetivo (post-Bloque 0):** `/srv/livskin-revops/infra/docker/vps2-ops/<servicio>/`

La migración se hace con `infra/docker/vps2-ops/migrate-from-home.sh` (script idempotente, zero-downtime).

## Volumes persistentes

| Servicio | Volumen host | Contenido |
|---|---|---|
| n8n | `./n8n/data/` | workflows + DB SQLite + logs |
| vtiger | `./vtiger/data/` | files de WP-style (uploads + storage) |
| vtiger-db | `./vtiger/db/` | datos MariaDB |
| metabase | (en postgres-analytics:metabase DB) | configs y dashboards |
| postgres-analytics | `./postgres-analytics/data/` | tablas analytics |

## Backups

Ver `docs/sistema-mapa.md § backups` y `infra/scripts/backup-vps2.sh`.

## TLS

Certificados Cloudflare Origin Cert wildcard `*.livskin.site` en `nginx/certs/` (gitignored).

## Setup desde cero

1. Crear droplet Ubuntu 24.04 en DO (Frankfurt, VPC `10.114.0.0/20`)
2. Hardening (Lynis baseline + UFW + Fail2Ban — ver `docs/seguridad/`)
3. Instalar Docker (`apt install docker.io docker-compose-plugin`)
4. `git clone` el repo a `/srv/livskin-revops`
5. `docker network create revops_net`
6. Para cada servicio:
   - `cp .env.example .env` y rellenar valores reales (Bitwarden)
   - `docker compose up -d`
7. Restore de backups si reconstrucción
8. Verificar URLs públicas en Cloudflare DNS
