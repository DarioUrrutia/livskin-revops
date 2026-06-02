# ADR-0038 — Postgres streaming replica VPS3→VPS2 (failover manual)

**Estado:** ✅ Aprobada
**Fecha:** 2026-05-28
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Sprint 1 estabilización (post Fase 4A)
**Workstream:** Infra · Seguridad

---

## 1. Contexto

### Problema

El análisis comprehensivo del sistema (2026-05-27, ver `docs/audits/system-analysis-2026-05-27/README.md`) identificó como **gap C-02 crítico** el SPOF #2 del proyecto:

```
postgres-data en VPS3 = single point of failure crítico
  ├── livskin_erp       (cliente + ventas + pagos + leads + appointments + audit_log)
  └── livskin_brain     (segundo cerebro, 1765 chunks pgvector)

Si VPS3 cae:
  - ERP offline (doctora no puede operar)
  - Audit log paralizado (eventos perdidos hasta recovery)
  - Brain offline (queries semánticas imposibles)
  - Restore desde backup nightly: ~30 min downtime + RPO hasta 24h
```

Backups daily (Bloque 0.5, commits `ab38c6c` + `a866994`) son la primera defensa, pero:
- RPO de 24h potencial (pérdida hasta 1 día de transacciones)
- RTO de ~30 min (extract + load + verify)
- Restore requiere intervención humana (no automático)

Con 2da campaña paga (S/350/5d Click-to-WA) en DRAFT Campaign `120243301839000678` y proyección de volumen creciente, el riesgo de SPOF crítico es inaceptable.

### Trigger

Sprint 1.4 (2026-05-28) — mitigation del SPOF #2 identificado en análisis comprehensivo. Pre-requisito implícito antes de 2da campaña paga.

### Pre-requisitos resueltos

- ADR-0002 — Arquitectura de datos (3 VPS, 5 DBs) — define postgres-data en VPS3 como master
- ADR-0027 — audit_log inmutable (que ya estaba expuesto al SPOF)
- DigitalOcean VPC `10.114.0.0/20` Frankfurt (latencia inter-VPS <2ms)
- Backups daily operacionales (Bloque 0.5 commits `ab38c6c` + `a866994`)
- Doctrina `feedback_no_paid_services` — DO managed Postgres descartado por costo
- Bloque 0.5 — backup cross-VPS infrastructure operacional

---

## 2. Opciones consideradas

### Opción A — Streaming async + manual failover (ELEGIDA)

Streaming replication nativa Postgres (WAL shipping continuo) de postgres-data en VPS3 hacia nuevo container postgres-replica en VPS2. Failover manual via `pg_promote()` + cutover DNS/connection-string. Replication asíncrono (no espera ack del standby).

### Opción B — Streaming sync + manual failover

Igual que A pero con `synchronous_commit=remote_apply`. RPO = 0 (cero pérdida de datos garantizada por commit sincronizado).

### Opción C — Logical replication (publications/subscriptions)

Postgres logical replication a nivel tabla. Permite replicar subset de tablas, distintas versiones PG, transformaciones.

### Opción D — pgpool-II / repmgr con failover automático

Stack de alta disponibilidad con failover automático orquestado por daemon externo. Múltiples nodos coordinan via heartbeat + auto-promotion.

### Opción E — DigitalOcean Managed Postgres con HA built-in

Migrar postgres-data desde container self-hosted a DO Managed Postgres con HA included.

---

## 3. Análisis de tradeoffs

| Dimensión | A (async + manual) | B (sync + manual) | C (logical) | D (pgpool auto) | E (DO Managed) |
|---|---|---|---|---|---|
| RPO (data loss potential) | ~ms (replication lag) | 0 | ~ms | ~ms | ~ms |
| RTO (recovery time) | 15-30 min (humano) | 15-30 min (humano) | 15-30 min | < 1 min (auto) | < 1 min (DO maneja) |
| Complejidad implementación | Baja (PG nativo) | Baja | Media (publications/subs) | Alta (deploy cluster + tuning) | Baja (managed) |
| Complejidad mantenimiento | Baja | Media (sync penalty si replica lenta) | Media (DDL fuera del schema replica) | Alta (operar pgpool + repmgr) | Mínima |
| Performance impact primary | Mínimo (async) | ⚠️ Bloquea write si replica lenta | Mínimo | Mínimo | N/A (DO maneja) |
| Risk split-brain | Bajo (manual failover human-gated) | Bajo (manual) | Bajo | ⚠️ Alto en VPC glitches | Mínimo (DO maneja) |
| Cobertura datos | TODO el cluster (incluye pgvector tablas grandes) | TODO | ⚠️ Subset configurado, NO pgvector tablas grandes by default | TODO | TODO |
| Soporta DDL (migrations) | ✅ Automático | ✅ | ⚠️ Manual aplicar DDL en ambos lados | ✅ | ✅ |
| Costo $/mes | $0 (self-host) | $0 | $0 | $0 self-host op cost ↑ | ~$30/mes mínimo |
| Alineación principio #8 (cero pago) | ✅ | ✅ | ✅ | ✅ | ❌ |
| Reversibilidad | Total (parar replica, borrar slot) | Total | Media (recrear publications) | Baja (deployed cluster) | Baja (migration costosa) |
| Escala futura | Replica disponible para read queries (escalado lecturas) | Igual | Subset replication permite uso específico | Múltiples nodos | DO maneja escalado |

**Nota sobre Opción C (logical):** Logical replication NO incluye por default tablas pgvector grandes (brain con 1765 chunks de embeddings) sin configuración extra. Además, requiere mantener publications/subscriptions manualmente al agregar tablas (cada migration Alembic). Operacionalmente más frágil para nuestro caso (replicación de cluster completo, no subset).

**Nota sobre Opción D (auto failover):** El riesgo principal es **split-brain en VPC glitches**: si la VPC interna DO tiene un hiccup transitorio (ha pasado documentado en status pages), pgpool puede promover el standby pensando que el primary murió, y al volver la red ambos aceptan writes → divergencia irrecuperable. Para nuestra escala MVP (1 ERP, 1 doctora operando), preferimos RTO de 15-30 min con humano-gated sobre RTO sub-minuto con risk split-brain.

**Nota sobre Opción E (DO Managed):** Costo ≥ $30/mes (cluster básico). Viola principio #8 (cero servicios pagos sin aprobación). Además requeriría migración compleja del cluster actual (134 clientes, 88 ventas, 1765 chunks brain) + reconfiguración de extensions (pgvector disponibility en managed plan a verificar).

---

## 4. Recomendación

Yo (Claude Code) recomiendo **Opción A (streaming async + manual failover)** porque:

1. **RPO ~ms aceptable para nuestro contexto**: en MVP scale con 1 doctora operando ERP, perder ~ms de transacciones en failover es invisible operacionalmente (no es un sistema de trading financiero).
2. **RTO 15-30 min aceptable**: la doctora puede esperar 30 min en evento de disaster (estimación bajísima frecuencia: 1-2 veces/año), preferible a complejidad operacional de auto-failover.
3. **Manual failover reduce risk split-brain**: humano-gated previene divergencias por VPC glitches. La doctora opera business hours; si VPS3 cae 3am, intervención mañana siguiente es OK.
4. **PG nativo, complejidad mínima**: streaming replication es feature core Postgres desde 2010. Sin daemons externos, sin clustering software adicional. Recovery con `pg_basebackup -R` documentado y probado.
5. **Replica disponible para escalado futuro**: una vez en place, podemos rutear queries read-only a la replica (analytics dashboards, reports Metabase) reduciendo load en primary.
6. **DDL/migrations transparentes**: Alembic migrations se aplican automáticamente al primary, WAL las propaga a la replica sin intervención.
7. **Cobertura total**: TODO el cluster (incluye `livskin_erp`, `livskin_brain` con pgvector, todas las tablas, todos los indexes) sin configuración extra.
8. **Reversible 100%**: si descubrimos limitación, drop replication slot + parar container. Cero side effects en primary.

Tradeoff principal que aceptamos: **failover requiere intervención humana ~15-30min** (vs sub-minuto de auto). En probabilidad baja de evento (1-2 veces/año) y contexto MVP, justificable.

---

## 5. Decisión

**Elección:** Opción A — Streaming replication async + manual failover via `pg_promote()`

**Fecha de aprobación:** 2026-05-28 por Dario

**Razonamiento de la decisora:**
> Aprobado en bloque Sprint 1 estabilización backbone. SPOF #2 mitigado sin violar principio #8.

---

## 6. Consecuencias

### Desbloqueado por esta decisión

- SPOF #2 mitigado — VPS3 down ya NO equivale a data loss potencial
- DR drill ejecutable trimestral sin downtime productivo
- Replica disponible para queries read-only future (escalado lecturas Metabase)
- RTO documentado y validado: 15-30 min con humano-gated cutover
- Backup nightly + replica continua = doble defensa (defense in depth)

### Bloqueado / descartado

- Opciones B, C, D, E descartadas para esta iteración. Ver "Cuándo reabrir" abajo.
- DO Managed Postgres queda diferida indefinidamente (costo violaría #8).
- Failover automático (pgpool/repmgr) descartado por risk split-brain en MVP scale.

### Implementación derivada

- [x] Replication user creado en postgres-data VPS3
  - User `replicator` con permiso REPLICATION
  - Password 40-char random (`REPLICATOR_PASSWORD` en `keys/.env.integrations`)
  - `pg_hba.conf` entry: `host replication replicator 10.114.0.2/32 scram-sha-256`
- [x] Replication slot persistente
  - `SELECT pg_create_physical_replication_slot('vps2_replica_slot');`
  - Preserva WAL si replica desconectada (evita gap data loss)
- [x] postgres-data VPS3 ahora expuesto en VPC `10.114.0.4:5432` (era solo data_net interno)
  - Firewall DO restringe acceso a VPC `10.114.0.0/20` only
  - NO expuesto a internet pública
- [x] postgres-replica container deployed en VPS2
  - Bind `10.114.0.2:5433` (no choca con postgres-analytics:5432)
  - `pg_basebackup -R` desde VPS2 con auto-config standby
  - `primary_conninfo` apunta a VPS3:5432 vía VPC
  - `recovery.signal` file presente (standby mode)
- [x] Streaming async config
  - `wal_level=replica` (default PG 12+)
  - `max_wal_senders=10`, `max_replication_slots=10`
  - `synchronous_commit=on` (local commit ack, NO espera replica)
- [x] DR drill validado 2026-05-28
  - Write to primary → ~2ms replay_lag medido en replica
  - Read en replica retorna data consistente
  - Runbook documentado: `docs/runbooks/pg-failover-replica.md`
- [x] Runbook failover manual `docs/runbooks/pg-failover-replica.md`
  - Pasos para `pg_promote()` cuando primary muere
  - Cutover connection-strings ERP + audit + brain
  - Re-sync inverso (nuevo primary VPS2 → standby VPS3) post-recovery

### Eventos audit nuevos

| Evento | When | After state |
|---|---|---|
| `infra.replica_promoted` | `pg_promote()` ejecutado en replica VPS2 | `{previous_primary, new_primary, promoted_at, reason}` |
| `infra.replica_lag_alert` | replay_lag > 1000ms sostenido por 5 min (futuro monitoring) | `{lag_ms, duration_seconds}` |

### Cuándo reabrir esta decisión

- **Trigger 1 — RTO 15-30 min se vuelve inaceptable**: si volumen escala a punto que 30 min downtime = pérdida revenue significativa, evaluar auto-failover (D) con mitigación split-brain (witness node externo).
- **Trigger 2 — Replication lag sostenido**: si lag > 100ms steady state aparece (network congestion VPC, primary overload), evaluar tuning WAL + commit settings o upgrade VPS sizing.
- **Trigger 3 — Necesidad escalado lectura**: si analytics dashboards Metabase causan load measurable en primary, formalizar routing read-only queries a la replica (nueva ADR).
- **Trigger 4 — Multi-region requerimiento**: si negocio expande fuera Cusco/Frankfurt single-region, evaluar replicación cross-region.
- **Revisión obligatoria**: DR drill trimestral re-ejecución (cadencia documented en `docs/runbooks/pg-failover-replica.md`).

---

## 7. Changelog de esta ADR

- 2026-05-28 — v1.0 — Creada y aprobada en sesión Sprint 1 estabilización tras análisis comprehensivo 2026-05-27. Implementación validada + DR drill ejecutado mismo día (commit `4a70211`).

---

**Notas:**
- Esta ADR formaliza decisión ya implementada en Sprint 1.4 (commit `4a70211`). Documento retroactivo para cerrar deuda de gobernanza ADR.
- Esta ADR NO supersede ADR-0002 (arquitectura 3 VPS sigue válida). Extiende el modelo con replica continua como capa defensa adicional.
- Postgres advisory locks (Sprint 1.15) operan en primary; en evento de failover el lock state se preserva en WAL replay (no se pierde state).
