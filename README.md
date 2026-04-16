# Livskin RevOps System

Sistema RevOps self-hosted para livskin.site.

## Arquitectura

```
WordPress (livskin.site) → n8n (flow.livskin.site) → Vtiger (crm.livskin.site)
                                                          ↓
                                                    n8n (ETL/sync)
                                                          ↓
                                                  PostgreSQL analytics
                                                          ↓
                                                  Metabase (dash.livskin.site)
```

## Stack

| Servicio | Imagen | Subdominio | Funcion |
|----------|--------|------------|---------|
| Nginx | nginx:stable | - | Reverse proxy + TLS |
| n8n | n8nio/n8n:latest | flow.livskin.site | Automatizacion |
| Vtiger | vtigercrm-8.2.0 | crm.livskin.site | CRM (source of truth) |
| PostgreSQL | postgres:16 | - | Base analitica |
| Metabase | metabase/metabase | dash.livskin.site | Dashboards/BI |

## Estructura del repo

```
livskin-revops/
├── docker/           # Docker compose files por servicio
│   ├── nginx/
│   ├── n8n/
│   ├── vtiger/
│   ├── postgres/
│   └── metabase/
├── nginx/            # Configuracion Nginx
│   ├── nginx.conf
│   └── sites/
├── scripts/          # Scripts operativos
│   ├── backup.sh
│   └── restore.sh
├── n8n/workflows/    # Exports de workflows n8n
├── sql/              # Schema y queries
│   └── schema.sql
├── docs/             # Documentacion
├── .env.example
└── .gitignore
```

## Red Docker

- `revops_net` — red compartida (nginx, n8n, vtiger, postgres, metabase)
- `vtiger_internal` — red aislada (vtiger-db)

## VPS

- Ubuntu 22.04 LTS
- DigitalOcean (FRA1)
- Cloudflare DNS + SSL (Full Strict, Origin Certificate)
- UFW (22, 80, 443)
- Fail2Ban

## Setup

Ver [docs/](docs/) para guias de instalacion y configuracion.

## Backups

```bash
./scripts/backup.sh           # Crear backup
./scripts/restore.sh 2026-04-16  # Restaurar
```
