# Estructura `infra/docker/`

Source of truth de **todo el infra Docker** de los 3 VPS de Livskin.

## Layout

```
infra/docker/
│
├── README.md                       # este archivo
│
├── vps1-wp/                        # VPS 1: WordPress (host, no docker)
│   ├── README.md
│   ├── nginx/livskin.conf          # /etc/nginx/sites-available/livskin
│   ├── wp-mu-plugins/              # mu-plugins versionados
│   └── install.sh                  # bootstrap idempotente DR
│
├── vps2-ops/                       # VPS 2: Orquestación + analítica
│   ├── README.md
│   ├── n8n/                        # workflows
│   ├── vtiger/                     # CRM (master del lead digital)
│   ├── metabase/                   # dashboards
│   ├── postgres-analytics/         # warehouse OLAP
│   ├── nginx/                      # reverse proxy 3 subdomains
│   └── migrate-from-home.sh        # migra de /home/livskin/apps/* → /srv/...
│
├── erp-flask/                      # VPS 3: ERP refactorizado ⚠️ legacy path
├── postgres-data/                  # VPS 3: Postgres + pgvector (brain) ⚠️ legacy
├── embeddings-service/             # VPS 3: ⚠️ legacy
├── nginx-vps3/                     # VPS 3: ⚠️ legacy
├── alembic-erp/                    # VPS 3: on-demand ⚠️ legacy
├── alembic-brain/                  # VPS 3: on-demand ⚠️ legacy
└── brain-tools/                    # VPS 3: on-demand ⚠️ legacy
```

## Asimetría intencional VPS 3

**Decisión 2026-04-26**: VPS 3 mantiene paths planos `infra/docker/<servicio>/`
en lugar del prefix `vps3-erp/<servicio>/`.

**Razón:** los volumes son `./data` (relativos al compose file). Mover el compose
file requiere mover también el directorio data — operación destructiva sobre
postgres-data (~1GB de data real backfilleada: 134 clientes, 88 ventas, 84 pagos).
Riesgo no justificado por consistencia cosmética.

**Cuándo se reorganiza:** Fase 6, durante el cutover Render→VPS 3 cuando ya hay
backups verificados + procedure DR ensayado. Ahí el `mv` se hace en el contexto
del cutover (que ya reinicia containers).

**Por ahora:** documentar la deuda en `docs/backlog.md` (item 🟡).

## Convenciones por VPS

| VPS | Tech | Versionado | CI/CD workflow |
|---|---|---|---|
| VPS 1 (WP) | host nginx + php-fpm + MariaDB (NO docker) | `vps1-wp/` | `deploy-vps1.yml` (rsync) |
| VPS 2 (ops) | docker compose por servicio | `vps2-ops/` | `deploy-vps2.yml` (compose up) |
| VPS 3 (erp) | docker compose por servicio | (paths legacy) | `deploy-vps3.yml` (compose up) |

## Networks Docker

- **VPS 2 — `revops_net`** (bridge externa, manual): n8n, vtiger, metabase, postgres-analytics, nginx
- **VPS 2 — `vtiger_internal`** (bridge aislada): vtiger ↔ vtiger-db (defensa-en-profundidad)
- **VPS 3 — `data_net`** (bridge externa, manual): postgres-data, embeddings, erp-flask, nginx-vps3, brain-tools

## Cross-VPS connectivity

DigitalOcean VPC `10.114.0.0/20` (Frankfurt) — latencia inter-VPS <2ms.

| Origen | Destino | Puerto | Protocolo | Propósito |
|---|---|---|---|---|
| VPS 1 (WP, SureForms) | VPS 2 (n8n) | 443 | HTTPS público | Webhook form-submit |
| VPS 2 (n8n workflow) | VPS 3 (erp-flask) | 443 | HTTPS público | Cross-VPS sync |
| VPS 3 (recolector cron) | VPS 1, VPS 2 (sensors) | 9100 | HTTP via VPC | system-state pull |
| VPS 2 (metabase) | VPS 3 (postgres-data) | 5432 | postgres via VPC | queries cross-VPS |

(Detalle exhaustivo en `docs/sistema-mapa.md`.)

## Cómo agregar un servicio nuevo

### En VPS 2 (futuro Langfuse en Fase 3)
```bash
mkdir -p infra/docker/vps2-ops/langfuse
cp infra/docker/vps2-ops/_template/* infra/docker/vps2-ops/langfuse/
# editar docker-compose.yml + .env.example + README.md
git commit -m "feat(vps2): agregar container <servicio>"
git push  # deploy-vps2.yml se encarga
```

### En VPS 3 (sigue paths legacy hasta Fase 6)
```bash
mkdir -p infra/docker/<servicio>
# compose + README
git push  # deploy-vps3.yml
```

### En VPS 1 (host config)
```bash
# editar infra/docker/vps1-wp/nginx/livskin.conf o agregar mu-plugin
git push  # deploy-vps1.yml hace rsync + reload
```
