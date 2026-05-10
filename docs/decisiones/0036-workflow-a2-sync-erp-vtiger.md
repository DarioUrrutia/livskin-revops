# ADR-0036 — Workflow [A2] sync ERP→Vtiger (cierra bidireccional del lead lifecycle)

**Estado:** ✅ Aprobada
**Fecha:** 2026-05-10
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** 4A.3 (Bot-broker bidireccional, sub-componente independiente)
**Workstream:** Datos · Infra

---

## 1. Contexto

### Problema

El sync entre Vtiger (CRM, master del lead lifecycle) y ERP (Postgres, master del cliente + transacciones) hoy es **unidireccional**:

```
✅ Vtiger → ERP (cron B3 cada 2 min, espeja leads modificados)
❌ ERP → Vtiger (NO existe — la doctora marca cita, ERP cambia lead.estado_lead, pero Vtiger queda stale)
```

Esto rompe la integridad del lead lifecycle cuando la doctora opera en ERP:
- Doctora marca cita "Asistió" → ERP `leads.estado_lead = "cliente"` ← OK
- Vtiger sigue mostrando el lead como `Nuevo` o `Contactado` ← WRONG (lead.estado_lead desincronizado)

Esto impacta:
- Marketing automation en Vtiger (workflows que dependen de leadstatus se disparan incorrectamente)
- Reports de funnel (queries cruzando leads + clientes ven números inconsistentes)
- Doctrina rectora `feedback_doctora_solo_erp_vtiger_automatico.md` ("doctora SOLO opera ERP, sync a Vtiger es automático") no se cumple sin este workflow

### Trigger

Backlog item Fase 4A.3 (subcomponente "Workflow [A2] sync ERP→Vtiger"). Se construye AHORA, separado del bot-broker (Fase 4A.3 main), porque:
- NO depende de WhatsApp Cloud API (bloqueado por Business Verification — días)
- Resuelve gap operacional inmediato
- Trabajo durable que avanza el proyecto sin tocar campañas

### Pre-requisitos resueltos

- ADR-0035 — Módulo Agenda Mínima ERP (origen de eventos `appointment.marked_attended` / `appointment.marked_no_show`)
- ADR-0027 — Audit log inmutable (los eventos viajan por audit_log)
- Picklist `vtiger_leadstatus` alineado con ERP `lead.estado_lead` (cleanup 2026-05-10, ver `integrations/vtiger/fields-mapping.md`)
- Doctrina `feedback_congruencia_nombres_cross_system.md` (mapping 1:1 case-insensitive)

---

## 2. Opciones consideradas

### Opción A — Cron pull desde n8n (similar a [B3])

n8n cron cada N minutos consulta endpoint ERP `/api/internal/leads/pending-vtiger-sync?since=<cursor>`. ERP devuelve eventos audit pendientes de propagar. n8n procesa cada uno: extrae `cod_appointment` → resuelve `lead.vtiger_id` → PATCH Vtiger REST API. n8n mantiene cursor en credentials.

### Opción B — Webhook push desde ERP

Cuando ERP emite audit event de tipo relevante, también dispara HTTP POST a `https://flow.livskin.site/webhook/erp/lead-state-changed`. n8n recibe + procesa async.

### Opción C — Trigger SQL Postgres + LISTEN/NOTIFY

Trigger PL/pgSQL en `audit_log` INSERT que invoca `pg_notify`. Un proceso Python listener (sidecar al ERP) capta el notify y dispara HTTP a n8n.

### Opción D — Tabla queue dedicada `vtiger_sync_queue`

Insert en queue table cuando audit event relevante. Worker n8n cron consume queue. State machine (pending/processing/synced/failed).

---

## 3. Análisis de tradeoffs

| Dimensión | A (cron pull) | B (webhook push) | C (LISTEN/NOTIFY) | D (queue table) |
|---|---|---|---|---|
| Complejidad implementación | Baja (patrón B3 existente) | Media (cambios en ERP service layer) | Alta (sidecar listener nuevo) | Media-alta (migration + worker) |
| Complejidad mantenimiento | Baja | Media (acopla ERP y n8n) | Alta (debug listener) | Media |
| Latencia ERP→Vtiger | 2-5 min (cadencia cron) | < 1 seg | < 1 seg | 2-5 min |
| Robustez a fallos n8n | Alta (cursor retry) | Baja (eventos perdidos) | Baja (eventos perdidos) | Alta (queue persistente) |
| Robustez a fallos Vtiger | Alta (reintenta en próximo cron) | Media (reintento manual) | Media | Alta (rows pending) |
| Acoplamiento sistemas | Mínimo (ERP no sabe de Vtiger) | Alto (ERP llama a n8n) | Alto (ERP dispara notify) | Medio (queue compartida) |
| Reversibilidad | Total (eliminar workflow) | Media (también remover hook) | Baja (sidecar deployed) | Baja (datos en queue) |
| Alineación con `n8n_orchestration_layer` | ✅ Total | ⚠️ ERP toma rol orquestador | ⚠️ ERP toma rol orquestador | ⚠️ Queue separada |
| Alineación con `feedback_surgical_precision_erp` | ✅ ERP solo expone endpoint read-only | ❌ ERP service layer cambia | ❌ Trigger DB nuevo | ❌ Migration nueva |
| Latencia aceptable en este caso | ✅ (la doctora marca asistencia, propagación a Vtiger no es crítica en segundos) | — | — | — |

---

## 4. Recomendación

Yo (Claude Code) recomiendo **Opción A (cron pull)** porque:

1. **Patrón existente conocido**: el workflow [B3] hace exactamente esto en sentido inverso. Reutilizamos arquitectura validada en producción 2 meses + lecciones aprendidas (race condition fix HOTFIX 2026-05-02 documentada).
2. **Acoplamiento mínimo**: el ERP solo expone un endpoint read-only. No sabe de Vtiger. n8n es el único orquestador cross-system (alineado con memoria 🔥 `project_n8n_orchestration_layer`).
3. **Robusto a fallos**: si n8n cae, el cursor no avanza, los eventos se procesan en próximo cron. Si Vtiger cae, mismo principio. Eventos no se pierden silenciosamente (auditables vía `audit_log`).
4. **Latencia 2-5 min es aceptable** para este caso de uso. La doctora marca asistencia → Vtiger se actualiza dentro de 5 min. Esto NO afecta workflows time-critical (no hay ninguno hoy en módulo Leads de Vtiger).
5. **Reversible 100%**: si descubrimos limitación, deshabilitar workflow en n8n. Cero side effects en datos.

Tradeoff principal que aceptamos: **latencia de 2-5 min** (vs sub-segundo de B/C). Aceptable porque el use case no es realtime crítico.

---

## 5. Decisión

**Elección:** Opción A — Cron pull desde n8n + endpoint ERP read-only

**Fecha de aprobación:** 2026-05-10 por Dario

**Razonamiento de la decisora:**
> *"OK"* (tras presentación del plan completo + 3 opciones de mapping picklist tomadas con disciplina de pre-flight cross-system runbook)

---

## 6. Consecuencias

### Desbloqueado por esta decisión

- Bidireccional ERP↔Vtiger lead lifecycle completo
- Doctrina `feedback_doctora_solo_erp_vtiger_automatico` operacionalmente cumplida
- Path crítico para Fase 4A.3 (bot-broker) — D2 workflow puede consumir leads sincronizados
- Reports cross-system (Metabase) ven números consistentes en lead funnel

### Bloqueado / descartado

- Opciones B, C, D descartadas para esta iteración. Ver "Cuándo reabrir" abajo.
- NO se sincronizan eventos `appointment.cancelled` / `appointment.rescheduled` / `appointment.confirmed` / `appointment.created` / `appointment.updated` — porque NO afectan `lead.estado_lead` (per memoria `feedback_doctora_solo_erp_vtiger_automatico` § "Estados del lead que transicionan").

### Eventos en scope (solo 2 de los 7 emitidos por appointment_service)

| Audit event | ERP `lead.estado_lead` | Vtiger `leadstatus` (post-sync) |
|---|---|---|
| `appointment.marked_attended` | → `cliente` | → `Cliente` |
| `appointment.marked_no_show` | → `contactado` | → `Contactado` |

Mapping ERP→Vtiger derivado de `integrations/vtiger/fields-mapping.md` § Picklist `leadstatus`. Diferencia: lowercase ASCII (ERP) ↔ Title Case con tildes (Vtiger).

### Implementación derivada

- [ ] Endpoint Flask `/api/internal/leads/pending-vtiger-sync?since=<audit_log_id>` (`infra/docker/erp-flask/routes/api_internal_leads.py`)
  - Auth: `X-Internal-Token` header (`AUDIT_INTERNAL_TOKEN`)
  - Returns: lista de items `{audit_log_id, cod_appointment, cod_lead, vtiger_id, target_vtiger_leadstatus, audit_action, audit_after_state}`
  - Filtros aplicados:
    - `audit_log.action IN ('appointment.marked_attended', 'appointment.marked_no_show')`
    - `audit_log.id > since_cursor`
    - JOIN appointments ON entity_id → JOIN leads ON appointment.lead_id → WHERE leads.vtiger_id IS NOT NULL
  - Limit configurable (default 50)
  - Tests pytest cubriendo: happy path, leads sin vtiger_id (skip), eventos no relevantes (excluidos), cursor avanza correctamente

- [ ] Workflow n8n `[A2] Sync ERP estado_lead → Vtiger leadstatus` (`infra/n8n/workflows/A-acquisition/a2-sync-erp-to-vtiger-leadstatus.json` + `.md`)
  - Trigger: cron `*/2 * * * *` (matches B3)
  - Nodes:
    1. Cron trigger
    2. HTTP GET endpoint ERP con cursor (almacenado en n8n credentials o static data)
    3. SplitInBatches (loop por items)
    4. HTTP PATCH Vtiger REST `/webservice.php?operation=update` con leadstatus actualizado
    5. Continue on fail + retry (per HOTFIX B3 race condition)
    6. Update cursor (max audit_log_id procesado)
  - Tests smoke: enviar 1 evento appointment.marked_attended → verificar Vtiger lead actualizado

- [ ] Documentación operativa
  - [ ] Update `infra/n8n/README.md` con [A2] en lista de workflows activos
  - [ ] Update `docs/sistema-mapa.md` § n8n_workflows con [A2]
  - [ ] Update `integrations/vtiger/fields-mapping.md` cross-link a este ADR

- [ ] Smoke E2E completo
  - Crear lead test en Vtiger via REST API → cron B3 espeja a ERP
  - Crear appointment en ERP UI con ese lead → marcar "Asistió"
  - Esperar ≤5 min cron A2
  - Verificar Vtiger `leadstatus = "Cliente"`
  - Verificar audit_log: `appointment.marked_attended` + downstream `vtiger.leadstatus_synced` (nuevo evento canónico)

### Eventos audit nuevos

Agregar a `docs/audit-events-schema.md`:

| Evento | When | After state |
|---|---|---|
| `vtiger.leadstatus_synced` | Workflow A2 actualiza Vtiger exitosamente | `{vtiger_id, old_leadstatus, new_leadstatus, source_audit_log_id}` |
| `vtiger.leadstatus_sync_failed` | Workflow A2 reintenta y falla | `{vtiger_id, attempted_leadstatus, error_message, source_audit_log_id}` |

(Estos eventos los emite el workflow n8n via POST a `/api/internal/audit-event` — endpoint ya existente.)

### Cuándo reabrir esta decisión

- **Trigger 1 — Volumen alto**: si > 1000 eventos/día se sincronizan, latencia 2-5 min puede ser limitante. Migrar a Opción B (webhook push).
- **Trigger 2 — Vtiger se reemplaza**: si Vtiger se descontinúa (improbable Año 1, posible Año 2 si Conversation Agent cubre marketing automation), todo este workflow se elimina.
- **Trigger 3 — Race conditions reales**: si múltiples ejecuciones concurrentes del cron causan duplicados o eventos perdidos, evaluar Opción D (queue table con state machine).
- **Revisión obligatoria**: a los 3 meses de operación, post-cierre Fase 4A.3 completa.

---

## 7. Changelog de esta ADR

- 2026-05-10 — v1.0 — Creada y aprobada en sesión 2026-05-10 tras pre-flight cross-system + cleanup picklist Vtiger + alignment workflow A1.

---

**Notas:**
- Esta ADR cierra el gap detectado en Fase 4A.1 (módulo Agenda) donde la doctora opera ERP pero Vtiger queda stale.
- La implementación SE PUEDE hacer sin esperar Business Verification de Meta (no toca WhatsApp).
- Esta ADR NO supersede ninguna previa — es trabajo nuevo derivado de ADR-0035.
