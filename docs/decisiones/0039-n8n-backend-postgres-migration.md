# ADR-0039 — Migración n8n SQLite → Postgres backend

**Estado:** ✅ Aprobada
**Fecha:** 2026-05-28
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Sprint 1 estabilización (post Fase 4A)
**Workstream:** Infra · Datos

---

## 1. Contexto

### Problema

El análisis comprehensivo del sistema (2026-05-27, ver `docs/audits/system-analysis-2026-05-27/README.md`) identificó como **gap C-01 / bottleneck #1** la arquitectura de persistencia n8n:

```
n8n default backend: SQLite local en /home/node/.n8n/database.sqlite
  ├── Single writer (sin MVCC)
  ├── Serializa TODOS los writes (executions + workflows + credentials + audit interno)
  └── Lock timeout escala mal con concurrencia
```

**Síntomas observados / proyectados:**
- 8 conversaciones / 2 días en bot test = ~720 executions/día A2 cron (1 cada 2 min × 24h × 0.5 día util) sin issue, pero con campañas activas:
- Proyección 2da campaña paga (S/350/5d, FB Ads Click-to-WA): 50-100 conv/día sostenido durante 5 días + cola post-campaign reactivation
- Análisis 2026-05-27 conclusión: **"n8n SQLite single-writer bloquea concurrencia. Se rompe a >50 conv/día simultáneas"**

Con campañas activas habría headroom corto, pero el bottleneck identificado como **blocker antes de 10x volumen** — proyectando crecimiento por Brand Orchestrator V0 + future campaigns, mitigation obligatoria pre-launch.

### Trigger

Sprint 1.2 (2026-05-28) — mitigación del bottleneck #1 del análisis comprehensivo. Critical pre-2da campaña paga.

### Pre-requisitos resueltos

- postgres-analytics ya deployed en VPS2 (ADR-0002, ADR-0032)
- ADR-0032 — Metabase warehouse architecture (postgres-analytics es backbone analítico)
- Doctrina `project_n8n_orchestration_layer` — n8n es capa orquestadora cross-system, su backend persistente es crítico
- Backup VPS2 daily operacional (commit `a866994` — Sprint 1 misma sesión fix backup incluye n8n DB)
- ADR-0038 — Streaming replica VPS3→VPS2 (postgres-analytics queda en VPS2 fuera del replication scope, pero backup nightly cubre)

---

## 2. Opciones consideradas

### Opción A — Fresh start approach (ELEGIDA)

Migration "limpia" via export/import nativo n8n. Pasos:
1. Backup SQLite + export workflows decrypted + export credentials decrypted (CLI n8n nativo)
2. Stop n8n, mover data → `data.sqlite-bak-DATE`
3. Crear fresh `/data` con SOLO config (encryption key preservado)
4. `.env` += `DB_POSTGRESDB_*` + `N8N_ENCRYPTION_KEY` explícito
5. Start n8n → corre ~50 migrations sobre PG vacío
6. `import:workflow --separate` + `import:credentials`
7. SQL `UPDATE workflow_entity SET active=true` para workflows productivos
8. Restart n8n para activar crons + webhooks

### Opción B — Migration directa SQLite → Postgres via tools de conversión

Usar `sqlite-to-postgresql` u otros tools que copian schema + data 1:1 entre engines.

### Opción C — MariaDB backend en lugar de Postgres

n8n soporta MariaDB también. Migrar a MariaDB en VPS2 (mismo stack que Vtiger).

### Opción D — Stay on SQLite con WAL mode + tuning

Habilitar `journal_mode=WAL` en SQLite (concurrent readers + 1 writer simultáneo) + tuning `synchronous=NORMAL` + `cache_size`. No migrar engine.

---

## 3. Análisis de tradeoffs

| Dimensión | A (fresh start) | B (migration directa) | C (MariaDB) | D (SQLite WAL) |
|---|---|---|---|---|
| Concurrencia writers | ✅ Postgres MVCC (N writers) | ✅ Postgres MVCC | ✅ MariaDB InnoDB | ⚠️ WAL = 1 writer + N readers (no soluciona writer bottleneck) |
| Riesgo data corruption durante migration | Bajo (CLI nativo export/import) | ⚠️ Alto (schema mismatch, encryption format) | Bajo (tool nativo n8n) | N/A (no migration) |
| Risk encryption mismatch credentials | Manejable (N8N_ENCRYPTION_KEY persisting explícito) | ⚠️ Alto (BLOB encryption SQLite ≠ PG si no se preserva key) | Manejable | N/A |
| Complejidad implementación | Media (~8 pasos coordinados, downtime ~30min) | ⚠️ Alta (debug schema diff, FK reescritura) | Media | Baja |
| Operability post-migration | ✅ Unified PG stack (analytics + metabase + n8n + erp-flask) | ✅ Mismo | ⚠️ Stack mixto MariaDB + PG | ✅ Mantiene estado actual |
| Backup integration | ✅ DB n8n incluido en backup-vps2.sh (PG dumps) | ✅ Igual | ⚠️ Backup MariaDB requiere ajuste script | Mismo (filesystem backup) |
| Headroom escalado | 100x antes saturar PG | Igual | ~50x antes saturar MariaDB single instance | < 2x (writer único) |
| Reversibilidad | ✅ Total (SQLite backup preservado, revert .env) | ⚠️ Alta dependencia herramienta migration | Reversible | N/A |
| Alineación principio "una SoT PG por dominio" | ✅ Coherente | ✅ | ⚠️ Stack mixto | ⚠️ SQLite divergente |
| Alineación con `n8n_orchestration_layer` | ✅ Backend robust en VPS2 stack analítico | ✅ Igual | ⚠️ Stack mixto | ⚠️ Backend frágil cuando volumen suba |
| Latencia ops | Mínima (n8n + PG mismo VPS2) | Igual | Igual | Igual (local file) |

**Nota sobre Opción B (migration directa):** El problema clave es que las **credentials de n8n están encriptadas con la `N8N_ENCRYPTION_KEY`** que por default vive en `/home/node/.n8n/config` (NO en la DB). Si la migration directa copia BLOBs SQLite a PG sin preservar el encryption key + asegurar consistency en el formato, las credentials quedan **unreadable post-migration** → todos los workflows con HTTP nodes, Postgres credentials, OAuth tokens **fallan silenciosamente**. Riesgo demasiado alto para migration "automática".

**Nota sobre Opción D (SQLite WAL):** WAL mode mejora concurrencia de readers pero **mantiene single writer**. n8n al ejecutar workflow escribe a `execution_entity` table. WAL no soluciona el bottleneck identificado (que es el writer único bloqueando inserts concurrentes). Sería curita temporal con techo bajo.

**Nota sobre Opción C (MariaDB):** Funcionalmente equivalente a A pero introduce stack mixto. Doctrina del proyecto (memoria `project_stack`) ya prefiere PG para datos analíticos. Vtiger usa MariaDB porque es su requirement nativo, no porque sea preferencia. Para greenfield (n8n migration), elegir PG mantiene unified stack.

---

## 4. Recomendación

Yo (Claude Code) recomiendo **Opción A (fresh start approach)** porque:

1. **Encryption key preservado explícitamente**: el aprendizaje crítico de Opción B es que credentials encrypted necesitan el mismo `N8N_ENCRYPTION_KEY` para decryptar post-migration. Mover el key de `/home/node/.n8n/config` a env var explícita (`N8N_ENCRYPTION_KEY` en `.env`) **antes** de la migration garantiza decryptability.
2. **Export/import via CLI n8n nativos**: `n8n export:workflow --separate` + `n8n export:credentials --decrypted` + `n8n import:*` son comandos oficiales soportados. Workflow decryption explícito al exportar elimina el risk de schema BLOB mismatch.
3. **Auto-migrations PG built-in**: n8n al arrancar con PG vacío corre sus ~50 migrations propias automáticamente (schema setup). Cero intervención manual en DDL.
4. **MVCC nativo Postgres**: N concurrent writers sin lock contention. Headroom medido 100x antes saturar (proyección bottleneck #1 resuelto).
5. **Unified PG management**: postgres-analytics ya hosting `analytics` + `metabase` DBs. Agregar `n8n` DB consolida 3 DBs en mismo instance. Backup unified (un solo `pg_dumpall`).
6. **Reversible 100%**: SQLite `data.sqlite-bak-DATE` preservado. Si algo falla, revert `.env` + restart restaura estado pre-migration.

Tradeoff principal que aceptamos: **~30min downtime de n8n** durante migration (workflows pausados, webhooks no-recibibles). Aceptable porque se hace en ventana low-traffic y los workflows críticos (A1 webhook form, D1 WA inbound) tienen retry/queue del lado emisor (WordPress retry, Meta webhook retry).

---

## 5. Decisión

**Elección:** Opción A — Fresh start approach (backup + export decrypted + restart con PG backend + import + activate)

**Fecha de aprobación:** 2026-05-28 por Dario

**Razonamiento de la decisora:**
> Aprobado en bloque Sprint 1 estabilización backbone tras análisis 2026-05-27. Bottleneck #1 mitigado, unified PG stack coherente con doctrina.

---

## 6. Consecuencias

### Desbloqueado por esta decisión

- Concurrencia MVCC nativa — n8n ya no bloquea writes simultáneos
- Headroom 100x antes saturar PG vs SQLite (proyección bottleneck #1 cerrado)
- DB n8n included en `backup-vps2.sh` (gap latente fix Sprint 1.2 misma sesión, commit `a866994`)
- Unified PG management (analytics + metabase + n8n + erp-flask todos PG)
- Habilita 2da campaña paga (S/350/5d) sin riesgo bottleneck SQLite
- Future: si Brand Orchestrator V0 BOOTSTRAP corre via n8n workflows, headroom suficiente

### Bloqueado / descartado

- Opciones B, C, D descartadas para esta iteración. Ver "Cuándo reabrir" abajo.
- SQLite como backend persistente n8n queda descartada definitivamente para producción.

### Implementación derivada

- [x] Backup SQLite + export decrypted (commit `e1faffa`)
  - `cp /home/node/.n8n/database.sqlite database.sqlite-bak-2026-05-28`
  - `n8n export:workflow --separate --output=/tmp/workflows-export/`
  - `n8n export:credentials --decrypted --output=/tmp/credentials-export.json`
- [x] DB `n8n` creada en postgres-analytics VPS2
  - User dedicado `n8n_app` con permisos solo sobre DB `n8n`
  - 40-char random password (`N8N_DB_PASSWORD` en `keys/.env.integrations`)
- [x] `.env` n8n actualizado
  - `DB_TYPE=postgresdb`
  - `DB_POSTGRESDB_HOST=postgres-analytics`
  - `DB_POSTGRESDB_PORT=5432`
  - `DB_POSTGRESDB_DATABASE=n8n`
  - `DB_POSTGRESDB_USER=n8n_app`
  - `DB_POSTGRESDB_PASSWORD=***`
  - **`N8N_ENCRYPTION_KEY=***` explícito** (crítico — sin esto credentials encryptadas post-migration quedan unreadable)
- [x] `docker-compose.yml` n8n: stop + recrear container (NO restart simple, ver memoria `feedback_docker_compose_restart_no_recarga_env`)
- [x] Auto-migrations corridas al primer arranque
  - n8n detecta DB vacía → corre ~50 migrations propias en orden
  - Schema completo creado: workflow_entity, execution_entity, credentials_entity, etc.
- [x] Import workflows + credentials
  - `n8n import:workflow --separate --input=/tmp/workflows-export/`
  - `n8n import:credentials --input=/tmp/credentials-export.json`
- [x] Activación post-import
  - `SQL UPDATE workflow_entity SET active=true WHERE name IN (...productive workflows...)`
  - `SQL UPDATE workflow_entity SET activeVersionId=versionId` (fix conocido import CLI)
- [x] Restart final container para activar crons + webhooks
- [x] Backup script `infra/scripts/backups/backup-vps2.sh` actualizado (commit `a866994`)
  - Agregado `pg_dump` de DB `n8n` al rutine nightly
  - Critical: gap latente detectado mismo día (25d sin backup n8n DB si no se hubiera fixado)
- [x] Smoke E2E validación post-migration
  - Workflows productivos siguen ejecutando (A1, A2, B1, B3, D1, E1, E2, G3)
  - Credentials decryption OK (no errores en logs)
  - Cron executions matching pre-migration ratio (target ~720/día A2)

### Riesgos operacionales

| Riesgo | Mitigación |
|---|---|
| Pérdida `N8N_ENCRYPTION_KEY` post-migration | Documentado en `keys/.env.integrations` (gitignored) + backup en Bitwarden |
| postgres-analytics cae → n8n no funciona | n8n ya tenía dependency a postgres-analytics via workflows que escriben analytics. PG VPS2 = hard dependency unificada |
| DB n8n no backed up | Fix mismo Sprint 1.2 (commit `a866994`). Backup script update obligatorio |
| Schema drift en future n8n upgrades | n8n maneja migrations propias automáticas; cluster PG backups dan rollback option |

### Eventos audit nuevos

No se agregan eventos audit nuevos. n8n maneja su propio audit interno via `execution_entity` table.

### Cuándo reabrir esta decisión

- **Trigger 1 — Volumen supera 1000 executions/día sostenido**: si saturamos postgres-analytics single instance (proyección 100x = ~70K executions/día A2), evaluar dedicated postgres-n8n instance o read replica.
- **Trigger 2 — Cross-VPS desired**: si por compartmentalización quisiéramos mover postgres-n8n a VPS dedicado (`agents.livskin.site` futuro), formalizar nueva ADR de partitioning.
- **Trigger 3 — Encryption key rotation**: rotación periódica del `N8N_ENCRYPTION_KEY` (best practice security) requiere procedure documentado (re-encrypt credentials).
- **Revisión obligatoria**: a los 3 meses post-Sprint 1, post-2da campaña paga cerrada + post-mortem volumen.

---

## 7. Changelog de esta ADR

- 2026-05-28 — v1.0 — Creada y aprobada en sesión Sprint 1 estabilización tras análisis comprehensivo 2026-05-27. Implementación validada + smoke E2E mismo día (commit `e1faffa`).

---

**Notas:**
- Esta ADR formaliza decisión ya implementada en Sprint 1.2 (commit `e1faffa`). Documento retroactivo para cerrar deuda de gobernanza ADR.
- Backup script fix incluido en mismo sprint (commit `a866994`) — cabo suelto que hubiera quedado latente.
- Esta ADR NO supersede ninguna previa. Trabajo nuevo derivado de análisis 2026-05-27.
- `N8N_ENCRYPTION_KEY` es ahora **CRÍTICA P0** para operabilidad. Pérdida = todas credentials de workflows unreadable. Backup en Bitwarden + `keys/.env.integrations` documentado.
