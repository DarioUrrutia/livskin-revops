# postgres-data — Postgres 16 + pgvector para VPS 3

Instancia Postgres dedicada al VPS 3 (`livskin-vps-erp`). Aloja 2 DBs:

- **`livskin_erp`** — OLTP del ERP refactorizado (Fase 2 la poblará)
- **`livskin_brain`** — segundo cerebro con 6 capas (schemas aplicados al crear)

## Roles (least privilege)

| Rol | DB | Permisos | Uso |
|---|---|---|---|
| `postgres` | todo | SUPERUSER | Admin, migrations, backups |
| `erp_user` | livskin_erp | OWNER | App Flask del ERP |
| `analytics_etl_reader` | livskin_erp | CONNECT + SELECT en public | ETL desde n8n (VPS 2) |
| `brain_user` | livskin_brain | OWNER | Agentes, MCP server, embeddings service |
| `brain_reader` | livskin_brain | CONNECT + SELECT en public | Metabase, exploración |

Ver `init/01-roles.sh` y `init/02-databases.sh` para detalles.

## Schema del brain (aplicado en init)

6 tablas de capas (ADR-0001) + 1 auditoría:

```
clinic_knowledge    L1 — catálogo tratamientos/productos/brand/protocolos
project_knowledge   L2 — docs markdown del repo indexados
conversations       L4 — mensajes WhatsApp con embeddings
creative_memory     L5 — briefs + creativos + performance
learnings           L6 — insights Growth Agent
embedding_runs      auditoría de re-embeddings
```

Capa 3 (data operativa) se define como vistas SQL cuando se conecte con livskin_erp + analytics (Fase 2).

Extensiones activadas en `livskin_brain`:
- `vector` (pgvector) — búsqueda por similitud
- `pgcrypto` — `gen_random_uuid()`

## Setup (primera vez)

1. Crear red Docker externa:
   ```bash
   docker network create data_net
   ```

2. Generar passwords y crear `.env`:
   ```bash
   cd /srv/livskin/postgres-data
   cp .env.example .env
   for var in POSTGRES_SUPERUSER_PASSWORD ERP_USER_PASSWORD ANALYTICS_ETL_READER_PASSWORD BRAIN_USER_PASSWORD BRAIN_READER_PASSWORD; do
     sed -i "s|^$var=.*|$var=$(openssl rand -base64 24)|" .env
   done
   chmod 600 .env
   ```

3. Start:
   ```bash
   docker compose up -d
   docker compose logs -f postgres-data
   ```

4. Verificar:
   ```bash
   docker exec -it postgres-data psql -U postgres -c "\l"  # lista DBs
   docker exec -it postgres-data psql -U postgres -d livskin_brain -c "\dt"  # tablas del brain
   docker exec -it postgres-data psql -U postgres -d livskin_brain -c "SELECT extname FROM pg_extension;"
   ```

## Puerto 5432

**NO expuesto al host ni a internet.** Solo accesible dentro de `data_net`.

**Acceso cross-VPS (n8n desde VPS 2):** vía DO VPC privada (10.114.0.4:5432). Requiere regla UFW específica que se agregará cuando conectemos VPS 2 → VPS 3 (Fase 2).

## Backups

- Diarios vía `pg_dump` (se configura en Fase 2)
- Retención: 14 días local + cross-VPS a VPS 2
- Ver ADR-0041 y `infra/scripts/backup-postgres-data.sh` (pendiente)

## Referencias

- [ADR-0001](../../../docs/decisiones/0001-segundo-cerebro-filosofia-y-alcance.md) — filosofía del segundo cerebro + schema completo
- [ADR-0002](../../../docs/decisiones/0002-arquitectura-de-datos-y-3-vps.md) — arquitectura 3 VPS y 5 DBs
- [ADR-0010](../../../docs/decisiones/README.md) — Alembic migrations (por configurar para cambios futuros de schema)
- [pgvector docs](https://github.com/pgvector/pgvector)
