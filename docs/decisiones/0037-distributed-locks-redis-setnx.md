# ADR-0037 — Distributed locks Redis SETNX para crons n8n

**Estado:** ✅ Aprobada
**Fecha:** 2026-05-28
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Sprint 1 estabilización (post Fase 4A)
**Workstream:** Infra · Datos

---

## 1. Contexto

### Problema

El análisis comprehensivo del sistema (2026-05-27, ver `docs/audits/system-analysis-2026-05-27/README.md`) identificó como **gap C-05 crítico de escalabilidad** que los workflows n8n con cron trigger no tenían protección contra **overlap de ejecuciones concurrentes**:

```
Workflow          Cron cadencia    Riesgo si overlap
─────────────────────────────────────────────────────────
[F1] re-engagement 4h    */15 min   Doble-send template Meta al mismo lead
[F2] auto-close cold      0 4 * * * Doble-update lead.estado_lead = 'cerrado'
[F3] GDPR data deletion   0 3 * * * Doble-delete races, errores de FK
[B3] Vtiger modified pull */2 min   Race condition (HOTFIX 2026-05-02 mitigó parcialmente)
```

Cuando una ejecución tarda más que el intervalo del cron (carga puntual, latencia Vtiger REST API, lag postgres), n8n **dispara nueva ejecución sin esperar** a que la anterior termine. Las dos ejecuciones leen el mismo cursor, procesan los mismos items, escriben el mismo destino → **data corruption silenciosa**.

Síntomas observados en producción pre-Sprint 1:
- B3 HOTFIX 2026-05-02 (race condition cron Vtiger) fue parche localizado, NO patrón general
- F1 nunca llegó a estresarse en Bridge Episode (6 leads), pero el riesgo escalaba con campaña paga 2da (S/350/5d)
- Sin protección, **escalabilidad horizontal n8n imposible** (n+1 réplicas multiplicarían el problema)

### Trigger

Sprint 1.3 (2026-05-28) — implementación parte del análisis comprehensivo del sistema (2026-05-27) que identificó "F1/F2/F3 + B3 cron sin distributed lock" como gap crítico de escalabilidad. Fix obligatorio antes de 2da campaña paga (FB Ads S/350/5d Click-to-WA en DRAFT Campaign `120243301839000678`).

### Pre-requisitos resueltos

- Sprint 1.1 — Redis 7-alpine container deployed en VPS2 (commit `fc91c97`, 200MB AOF, VPC 10.114.0.2:6379, password-protected)
- Doctrina #11 (deterministic backbone first) — locks son determinísticos, no IA
- ADR-0027 — audit_log inmutable (eventos de lock acquire/release auditables)
- Doctrina `feedback_no_paid_services` — Redis self-hosted ($0/mes), no SaaS

---

## 2. Opciones consideradas

### Opción A — n8n native Redis node

n8n tiene un nodo Redis built-in. Usarlo directamente desde los workflows F1/F2/F3/B3 para SETNX + GET + DEL via UI nodes encadenados.

### Opción B — ERP HTTP endpoint wrapper (ELEGIDA)

Centralizar la lógica de locking en el ERP Flask como `services/distributed_lock_service.py` exposed via HTTP endpoints `/api/internal/lock/acquire|release|ping`. Los workflows n8n inyectan al inicio: try-acquire-lock → si held, skip; si OK, continuar. TTL libera tras crash.

### Opción C — Postgres advisory locks

Usar `pg_advisory_lock(key)` desde n8n via Postgres node. Los locks son cross-process automáticamente (ya tenemos Postgres como dependency).

### Opción D — etcd / Zookeeper

Sistema de coordinación distribuida estándar industria (Kubernetes, Vault, etc).

---

## 3. Análisis de tradeoffs

| Dimensión | A (n8n Redis node) | B (ERP HTTP wrapper) | C (PG advisory) | D (etcd/Zookeeper) |
|---|---|---|---|---|
| Complejidad implementación | Media (3 nodos por workflow × 4 wfs = 12 nodos UI) | Baja (1 HTTP node + service Flask reusable) | Media (PG node + manejar conn pool) | Alta (deploy nuevo cluster) |
| Complejidad mantenimiento | Alta (12 nodos UI a debuggear, sin tests) | Baja (lógica centralizada + pytest) | Media (advisory locks son session-scoped, ojo conn pool) | Alta (operar cluster nuevo) |
| Acoplamiento sistemas | Bajo (n8n ↔ Redis directo) | Medio (n8n → ERP → Redis, 2-hop) | Alto (n8n VPS2 → PG primario VPS3) | Bajo |
| Audit visibility | Bajo (logs n8n) | Alta (audit_log centralizado) | Medio (PG logs) | Bajo |
| Reusable para otros casos | No (lock-specific UI nodes) | Sí (service + endpoint reusable) | Sí (PG nativo) | Sí |
| Cross-process cron coordination | Sí | Sí | ⚠️ Limitado (session-scoped, requiere conn dedicada) | Sí |
| Fail-OPEN si lock backend caído | Manual implementar en UI | Sí (centralized en service) | Difícil | Sí |
| Latencia adquisición lock | < 1ms (VPS2 local) | 1-2ms (cross-VPS via VPC) | 2-5ms (VPS3 PG) | 1-3ms |
| Alineación con `n8n_orchestration_layer` | ⚠️ n8n maneja primitiva infra | ✅ ERP centraliza, n8n consume HTTP | ⚠️ n8n acoplado a PG | ⚠️ Nuevo servicio |
| Alineación con principio #8 (self-hosted simple) | ✅ Redis ya deployed | ✅ Redis ya deployed | ✅ PG ya deployed | ❌ Overkill MVP |
| Costo $/mes | $0 (Redis ya está) | $0 | $0 | $0 self-host pero op cost ↑ |
| Reversibilidad | Alta (eliminar nodos) | Total (deshabilitar endpoint) | Alta | Baja (deployed cluster) |
| Tests unitarios | ⚠️ Difícil (UI nodes) | ✅ pytest sobre service | Medio | Difícil |

**Nota sobre Opción C (PG advisory locks):** Ya estamos usando `pg_advisory_xact_lock` para race conditions intra-transacción (UPSERT wa_state Sprint 1.15, serial counter ERP). Pero para **cross-process cron coordination** entre n8n VPS2 y workflows que escriben a PG VPS3, los advisory locks tienen limitaciones: son session-scoped, requieren conexión dedicada por la duración del lock, y si el cron crashea sin release explícito, el lock libera solo cuando la conexión cierra (timeout TCP). Para crons cortos (segundos) funciona; para crons largos (minutos, como B3 procesando 100+ leads) es frágil.

---

## 4. Recomendación

Yo (Claude Code) recomiendo **Opción B (ERP HTTP endpoint wrapper)** porque:

1. **Audit visibility centralizada**: cada acquire/release viaja por audit_log con `lock_key`, `ttl`, `holder_value`. Operacionalmente verificable en `/admin/audit-log` y vía SQL queries — alineado con ADR-0027.
2. **Reusable**: el patrón de lock distribuido lo necesitarán futuros componentes (ETL pesado, batch jobs Brand Orchestrator V0, sincronizaciones cross-VPS). Centralizar en service evita duplicar lógica en 10 lugares.
3. **Testeable**: `tests/routes/test_api_internal_lock.py` con pytest cubre happy path + race + fail-OPEN. Imposible testear igual nodos UI n8n.
4. **Alineado con `project_n8n_orchestration_layer`**: n8n orquesta cross-system, ERP centraliza primitivas. n8n NO debe conocer primitivas infra directamente (Redis es detalle de implementación del ERP).
5. **Fail-OPEN by default**: si Redis cae, el endpoint retorna `{acquired: true, fallback: true}` y los workflows continúan. Preferimos doble-run sobre miss completo (data eventualmente convergente vs gap permanente).
6. **TTL nativo Redis SETNX EX**: atómico, sin race condition de acquire+expire. Liberación automática si workflow crashea.

Tradeoff principal que aceptamos: **latencia cross-VPS de ~1-2ms por acquire** (n8n VPS2 → ERP VPS3 → Redis VPS2). Aceptable porque la cadencia de cron es minutos, no milisegundos.

---

## 5. Decisión

**Elección:** Opción B — ERP HTTP endpoint wrapper sobre Redis SETNX

**Fecha de aprobación:** 2026-05-28 por Dario

**Razonamiento de la decisora:**
> Aprobado en bloque Sprint 1 estabilización backbone tras análisis 2026-05-27. Centralización en ERP coherente con doctrina `project_n8n_orchestration_layer`.

---

## 6. Consecuencias

### Desbloqueado por esta decisión

- F1/F2/F3/B3 idempotent vs overlap concurrente (ningún double-send Meta, ningún double-write Vtiger)
- Patrón reusable para futuros endpoints batch (ETLs, jobs Brand Orchestrator V0)
- Audit visibility centralizada de coordinación cross-process
- Habilita pre-launch 2da campaña paga (S/350/5d) sin riesgo data corruption por overlap

### Bloqueado / descartado

- Opciones A, C, D descartadas para esta iteración. Ver "Cuándo reabrir" abajo.
- Postgres advisory locks **se mantienen** para casos intra-transacción (UPSERT wa_state Sprint 1.15, serial counter ERP) — son herramienta complementaria, no sustituible por Redis SETNX.

### Implementación derivada

- [x] Redis 7-alpine container VPS2 (Sprint 1.1, commit `fc91c97`)
  - Bind `10.114.0.2:6379`, password-protected, NO expuesto a internet
  - 200MB max memory, AOF + RDB persistence
  - Volume `/srv/livskin-revops/data/redis`
- [x] `services/distributed_lock_service.py` con connection pool reusable
  - `acquire(key, ttl_seconds, value)` → bool
  - `release(key, expected_value)` → bool (compare-and-delete vía Lua script)
  - `ping()` → dict (health Redis)
  - Fail-OPEN si Redis caído (`{acquired: true, fallback: true}`)
- [x] Endpoints HTTP internos en `routes/api_internal_lock.py`:
  - `POST /api/internal/lock/acquire` body `{key, ttl_seconds, value}` → `{acquired: bool, ttl_remaining: int}`
  - `POST /api/internal/lock/release` body `{key, value}` → `{released: bool}`
  - `GET /api/internal/lock/ping` → `{redis: "ok"|"error"}`
  - Auth: `X-Internal-Token` header (`AUDIT_INTERNAL_TOKEN`)
- [x] Tests pytest cubriendo happy path + race + fail-OPEN (`tests/routes/test_api_internal_lock.py`)
- [x] Workflows n8n F1/F2/F3/B3 patcheados con nodo HTTP try-acquire al inicio (commit `488493e`)
  - Keys patrón: `cron:f1-reengagement-4h`, `cron:f2-auto-close-cold-leads`, `cron:f3-gdpr-data-deletion`, `cron:b3-vtiger-modified-cron-pull`
  - TTL = 2 × cadencia esperada del cron (margen de seguridad)
  - Si `acquired: false` → workflow termina con log "lock held by previous run, skipping"

### Eventos audit nuevos

| Evento | When | After state |
|---|---|---|
| `lock.acquired` | Endpoint /api/internal/lock/acquire retorna acquired=true | `{key, ttl_seconds, value, fallback}` |
| `lock.acquire_skipped` | Endpoint retorna acquired=false (lock held) | `{key, holder_value, ttl_remaining}` |
| `lock.released` | Endpoint /api/internal/lock/release retorna released=true | `{key, value}` |
| `lock.redis_unavailable` | Service detecta Redis caído, fallback mode active | `{key, error_message}` |

### Cuándo reabrir esta decisión

- **Trigger 1 — Redis se vuelve SPOF crítico**: si cae Redis > N veces/mes con impacto operacional, evaluar Redis Sentinel o clustering (latencia agregada).
- **Trigger 2 — Latencia cross-VPS inaceptable**: si en algún caso de uso la latencia 1-2ms por acquire suma > 100ms total en un workflow (improbable con cadencias actuales), evaluar mover lock backend a VPS local al consumidor.
- **Trigger 3 — Múltiples instancias n8n (escalado horizontal)**: si llegamos a n+1 réplicas n8n y los locks empiezan a contender por keys altos, evaluar particionado o consistent hashing.
- **Revisión obligatoria**: a los 3 meses de operación post-Sprint 1, post-2da campaña paga cerrada.

---

## 7. Changelog de esta ADR

- 2026-05-28 — v1.0 — Creada y aprobada en sesión Sprint 1 estabilización tras análisis comprehensivo 2026-05-27. Implementación validada commits `e7a3118` (backbone) + `488493e` (workflows patcheados).

---

**Notas:**
- Esta ADR formaliza decisión ya implementada en Sprint 1.3 (commit `e7a3118`). Documento retroactivo para cerrar deuda de gobernanza ADR.
- Redis NO reemplaza Postgres advisory locks — ambos coexisten para casos distintos (cross-process vs intra-transacción).
- Esta ADR NO supersede ninguna previa. Trabajo nuevo derivado de análisis 2026-05-27.
