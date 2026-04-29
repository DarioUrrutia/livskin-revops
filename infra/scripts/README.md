# infra/scripts/ — Scripts de operación VPS-side

Scripts shell que corren **dentro de los VPS** (1/2/3) para tareas de ops internos. Distintos de `/scripts/` (root) que son scripts Python locales de la laptop de Dario para auditar APIs externas.

## Inventario

| Script | VPS | Propósito |
|---|---|---|
| `alembic-erp.sh` | VPS 3 | Wrapper para migrations Alembic ERP. `migrate`, `current`, `history`, `revision -m "msg"` |
| `alembic-brain.sh` | VPS 3 | Wrapper para migrations Alembic Brain (livskin_brain) |
| `brain-index.sh` | VPS 3 | Re-indexa Layer 2 (`project_knowledge` pgvector). Idempotente. ~9 min para ~1.700 chunks |
| `brain-query.sh` | VPS 3 | Query semántica al brain. Uso: `brain-query.sh "pregunta" [limit=5]` |
| `backup.sh` (legacy) | VPS 3 | DEPRECATED — usar `backups/backup-vps3.sh` en su lugar |
| `restore.sh` (legacy) | VPS 3 | DEPRECATED — restore puntual desde un .sql.gz |
| `backups/` | VPS 1/2/3 | Sistema de backups cross-VPS (ver `backups/README.md`) |

## Subfolder `backups/`

Detalle en [`backups/README.md`](backups/README.md). Incluye:
- `backup-vps1.sh` (WordPress + DB MariaDB)
- `backup-vps2.sh` (n8n DB + vtiger DB + metabase volumes)
- `backup-vps3.sh` (Postgres livskin_erp + livskin_brain)
- `verify-backup.sh` (integridad backup)
- `verify-vps2-backups.sh` (corre en VPS 3 verificando backups que VPS 2 envió)
- `install-cron-vps3.sh` (instala cron orchestration en VPS 3)
- `common.sh` (funciones compartidas: log, audit_event, pg_backup, mariadb_backup, cross_vps_transfer)

## Cuándo correrlos manualmente

| Script | Trigger |
|---|---|
| `alembic-*.sh` | Después de crear nueva migration (post desarrollo de feature ERP) |
| `brain-index.sh` | Después de cambios sustanciales a docs/ (semanal recommended), o manualmente cuando se note query results stale |
| `brain-query.sh` | Antes de mini-bloques cross-system (preflight checklist), o para debug |
| `backup-vps*.sh` | Manual (ej. antes de migration riesgosa). El cron lo ejecuta diariamente automatic |

## Comparación con `/scripts/` (laptop)

| | `infra/scripts/` (VPS) | `scripts/` (laptop) |
|---|---|---|
| **Lenguaje** | Shell (Bash) | Python |
| **Naming** | `kebab-case.sh` | `snake_case.py` (PEP 8) |
| **Corre en** | VPS 1/2/3 (deploy via git pull) | Laptop Dario |
| **Propósito** | Ops internos: migrations, backups, brain | Audit + setup APIs externas (Google/Meta) |
| **Auth** | SSH keys cross-VPS + audit_internal_token | Tokens Google/Meta locales |
| **Trigger típico** | Cron daily / manual via SSH | Manual desde laptop |

## Ejemplos

```bash
# Re-indexar brain Layer 2 (después de varios docs nuevos)
ssh livskin-erp 'bash /srv/livskin-revops/infra/scripts/brain-index.sh'

# Query brain antes de cross-system task (preflight)
ssh livskin-erp 'bash /srv/livskin-revops/infra/scripts/brain-query.sh "lead vtiger n8n flujo"'

# Migration ERP (after coding new feature)
ssh livskin-erp 'bash /srv/livskin-revops/infra/scripts/alembic-erp.sh revision -m "add_appointments"'
ssh livskin-erp 'bash /srv/livskin-revops/infra/scripts/alembic-erp.sh migrate'

# Backup manual (antes de algo riesgoso)
ssh livskin-erp 'AUDIT_INTERNAL_TOKEN=$(sudo cat /srv/livskin-revops/keys/.audit-internal-token) bash /srv/livskin-revops/infra/scripts/backups/backup-vps3.sh'
```
