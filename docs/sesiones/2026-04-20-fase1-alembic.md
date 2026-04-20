# Sesión 2026-04-20 (parte 2) — Alembic + decisión sobre mantenimiento post-MVP

**Duración:** ~1.5-2 horas
**Tipo:** ejecución directa por Claude Code + 1 conversación estratégica (sobre mantenimiento)
**Participantes:** Dario + Claude Code
**Fase del roadmap:** Fase 1 (Semana 2) — plumbing infra

---

## Decisión estratégica: operación post-MVP y mantenimiento

Dario planteó una preocupación fundamental:
> "Estas cosas cómo serán mantenidas cuando yo esté dirigiendo la empresa y use esto como herramienta de RevOps, porque no puedo pasar mi vida manteniendo el programa."

**Respuesta acordada:**

1. El sistema se diseña explícitamente para **<5 h/mes de mantenimiento** post-Fase 6.
2. Operación diaria = automática (agentes). Mantenimiento rutinario = automatizado (cron + alertas). Evolución y incidentes = intervenciones esporádicas.
3. 3 rutas de operación disponibles post-MVP:
   - **Ruta A** (recomendada meses 0-6): Dario + Claude Code, $0 extra, flexible
   - **Ruta B**: Fractional DevOps $300-800/mes
   - **Ruta C**: Managed services (DO Managed Postgres etc.) $+30-100/mes

**Formalizado en:**
- [docs/master-plan-mvp-livskin.md § 18](../master-plan-mvp-livskin.md) "Operación post-MVP y mantenimiento" (sección nueva)
- [docs/backlog.md](../backlog.md) item 🟡 "Capa de auto-mantenimiento — Fase 6" con lista concreta (Watchtower, UptimeRobot, n8n alertas, monthly audit auto-ejecutado, runbooks)

Cumple el **principio 6** del proyecto: "respeto al equipo humano — si Dario se siente atada en vez de liberada, se rediseña".

---

## Alembic — schema migrations versionadas

### Qué se implementó

Dos setups de Alembic independientes (ADR-0010 pasa a "implementada"):

| Setup | DB objetivo | Estado |
|---|---|---|
| `alembic-brain` | `livskin_brain` | Baseline `0001` stamped — schema creado por init scripts de Postgres se marca como "aplicado" |
| `alembic-erp` | `livskin_erp` | Vacío — primera migration llegará en Fase 2 con el refactor del ERP |

Ambos:
- Containers one-shot con profile `oneshot` (no se levantan con `docker compose up -d`)
- Invocados con `docker compose run --rm alembic-X <comando>`
- Usan usuario `postgres` (superuser) para DDL amplio
- Password leído de `../postgres-data/.env` (gitignored)
- Imagen Python 3.11-slim + alembic 1.14.0 + psycopg2-binary 2.9.10 + sqlalchemy 2.0.35
- env.py dinámico: construye DATABASE_URL desde env vars (DB configurable)

Wrappers shell en `infra/scripts/`:
- `alembic-brain.sh`
- `alembic-erp.sh`

### Test realizado

**Brain:**
```
stamp head → INFO Running stamp_revision  -> 0001
current    → 0001 (head)
history    → <base> -> 0001 (head), Baseline — schema livskin_brain creado
             por init scripts de Postgres.
```

En DB verificado:
```sql
SELECT * FROM alembic_version;
 version_num
-------------
 0001
(1 row)
```

**ERP:**
```
current → (vacío — no hay migrations)
history → (vacío — no hay migrations)
```

Correcto, ya que `livskin_erp` no tiene tablas aún.

### Cómo se usa para cambios futuros

Ejemplo: "agregar columna `duration_minutes` a `clinic_knowledge`".

```bash
# 1. Crear migration vacía
cd /srv/livskin-revops/infra/docker/alembic-brain
docker compose run --rm alembic-brain revision -m "add duration to clinic_knowledge"
# Genera migrations/versions/<fecha>-<rev>_add_duration_to_clinic_knowledge.py

# 2. Editar el archivo generado localmente (Dario + Claude Code):
#    def upgrade():
#        op.add_column('clinic_knowledge',
#            sa.Column('duration_minutes', sa.Integer(), nullable=True))
#    def downgrade():
#        op.drop_column('clinic_knowledge', 'duration_minutes')

# 3. git commit + push

# 4. Aplicar en VPS 3 (hoy manual, futuro CI/CD)
docker compose run --rm alembic-brain upgrade head
```

### Pendientes relacionados

- **Wire Alembic al workflow CI/CD** — agregar step al workflow que corra `alembic upgrade head` tras `git pull` (antes de `docker compose up -d` de otros services). Pendiente para sesión posterior.
- **Primer uso real** en Fase 2 al refactorizar ERP — la primera migration de `alembic-erp` creará el schema completo.

---

## Estructura del repo al cierre

```
infra/
├── docker/
│   ├── postgres-data/        ← Postgres 16 + pgvector
│   ├── embeddings-service/   ← multilingual-e5-small self-hosted
│   ├── nginx-vps3/           ← reverse proxy + TLS público
│   ├── alembic-brain/        ← NUEVO: migrations para livskin_brain
│   └── alembic-erp/          ← NUEVO: migrations para livskin_erp (vacío)
└── scripts/
    ├── backup.sh
    ├── restore.sh
    ├── alembic-brain.sh      ← NUEVO: wrapper invocación
    └── alembic-erp.sh        ← NUEVO: wrapper invocación
```

---

## Containers activos en VPS 3 al cierre

```
postgres-data       (healthy) — 3 DBs operativas
embeddings-service  (healthy) — multilingual-e5-small
nginx-vps3          (healthy) — puerta pública con TLS
alembic-brain       (image built, no permanent container)
alembic-erp         (image built, no permanent container)
```

---

## Commits del día

1. `6961f61` — VPS 3 + hardening (ayer)
2. `f791689` — data layer (ayer)
3. `a0a436b` — nginx público (ayer)
4. `fc37811` → `774d0ef` — CI/CD workflow (5 iteraciones hasta pasar)
5. `4bde4bf` — test end-to-end CI/CD
6. `5567de2` — session log CI/CD
7. `704884d` — Alembic brain + erp
8. (por venir) — session log Alembic + mantenimiento

---

## Estado de Fase 1

```
✅ VPS 3 provisionado + hardening + Docker
✅ DO VPC entre los 3 VPS
✅ Postgres 16 + pgvector + 6 tablas del cerebro
✅ Embeddings service (multilingual-e5-small self-hosted)
✅ Nginx + TLS público (erp.livskin.site + staging)
✅ CI/CD GitHub Actions funcionando end-to-end
✅ Alembic skeleton (brain stamped, erp listo para Fase 2)
⏳ MCP server del cerebro
⏳ Indexer repo → Layer 2 del cerebro
```

Quedan **2 piezas de plumbing** para cerrar Fase 1. Después ya es Fase 2 (ERP refactor con data sintética).

---

## Aprendizajes

**Sobre Alembic:**
- Baseline migration con `stamp head` es el patrón correcto para DBs que ya tienen schema creado por otros medios (init scripts, backfill manual, etc.). No intentar usar `upgrade` para reinventar lo que ya existe.
- Separar alembic por DB (un container + compose por DB) es más limpio que un env unificado — cada DB tiene su propio historial auditable.
- Usar env vars para `DATABASE_URL` en `env.py` permite el mismo código para brain y erp, sin duplicación real.

**Sobre comunicación con Dario:**
- La pregunta sobre mantenimiento post-MVP es la correcta y merece documentación formal. Lo que parece "técnico" (Alembic, CI/CD) es en realidad "cómo reduce tu carga operativa cuando esto esté en producción".
- Cada vez que se introduce una herramienta nueva (Alembic, GitHub Actions, etc.), explicar **cuánto mantenimiento agrega vs cuánto mantenimiento evita**. El ROI casi siempre es positivo pero hay que mostrarlo.

---

**Firma del log:** Claude Code + Dario · 2026-04-20 (parte 2)
