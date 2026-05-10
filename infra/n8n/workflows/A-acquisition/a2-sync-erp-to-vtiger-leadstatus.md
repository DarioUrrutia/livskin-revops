# [A2] Sync ERP estado_lead → Vtiger leadstatus (cierre bidireccional)

**Categoría:** acquisition
**Fase:** 4A.3 sub-componente (independiente del bot-broker bidireccional)
**Criticidad:** high
**Estado:** ✅ producción 2026-05-10
**Trigger:** cron (cada 2 minutos)
**Schedule:** `*/2 * * * *`
**ADR:** [0036](../../../../docs/decisiones/0036-workflow-a2-sync-erp-vtiger.md)

---

## Qué hace

Cada 2 minutos, consulta endpoint ERP `/api/internal/leads/pending-vtiger-sync?since=<cursor>` para obtener eventos audit_log donde la doctora marcó asistencia/no_show en el módulo Agenda. Para cada evento:

1. Auth Vtiger (getchallenge + MD5 + login → sessionName)
2. PATCH Vtiger lead `revise` con `leadstatus` actualizado
3. Emit audit event `tracking.vtiger_leadstatus_synced` (success) o `tracking.vtiger_leadstatus_sync_failed` (error)
4. Avanza cursor en static data al max audit_log_id procesado

**Cierra el loop bidireccional ERP↔Vtiger del lead lifecycle**:

```
┌─ Form WP → n8n[A1] → Vtiger Lead (leadstatus=Nuevo)
│
│  cron[B3] cada 2min sync Vtiger → ERP (estado_lead=nuevo)
│  ↓
│  Doctora opera ERP (módulo Agenda - Fase 4A.1)
│  ↓
│  Marca cita "Asistió" → audit_log appointment.marked_attended
│  ↓
└─ cron[A2] cada 2min ← endpoint ERP → Vtiger (leadstatus=Cliente) ← cerrado HOY
```

**Doctrina rectora**: `feedback_doctora_solo_erp_vtiger_automatico.md` (la doctora opera SOLO el ERP, sync a Vtiger es automático) + `feedback_congruencia_nombres_cross_system.md` (nombres congruentes 1:1 case-insensitive).

---

## Eventos en scope (solo 2 de los 7 emitidos por appointment_service)

| Audit event | ERP `lead.estado_lead` | Vtiger `leadstatus` (post-sync) |
|---|---|---|
| `appointment.marked_attended` | → `cliente` | → `Cliente` |
| `appointment.marked_no_show` | → `contactado` | → `Contactado` |

**NO sync**: `cancelled`, `rescheduled`, `confirmed`, `created`, `updated` (no afectan estado lead per memoria).

**Picklist Vtiger** (cleanup ejecutado 2026-05-10): 11 valores legacy default (Hot, Cold, Warm, Qualified, etc.) reemplazados por 6 valores en español congruentes con ERP — `Nuevo, Contactado, Agendado, Asistió, Cliente, Perdido`. Ver `integrations/vtiger/fields-mapping.md` § Picklist `leadstatus`.

---

## Trigger

**Schedule Trigger** — cron `*/2 * * * *` (cada 2 minutos UTC).

Mismo cadencia que B3 (alineación de patrones cron).

---

## Cursor en static data

n8n persiste `lastAuditLogId` en `$workflow.staticData.global` para tracking del cursor entre ejecuciones. Cursor avanza al max audit_log_id de items SUCCESSFULLY synced (items failed quedan en queue para retry en próximos crons).

---

## Filtros del endpoint ERP

`GET /api/internal/leads/pending-vtiger-sync?since=<id>&limit=50`:
- `audit_log.action IN ('appointment.marked_attended', 'appointment.marked_no_show')`
- `audit_log.id > since_cursor`
- JOIN appointments + leads
- WHERE `Lead.vtiger_id IS NOT NULL` (skip leads creados manualmente en ERP sin contraparte Vtiger — walk-ins / referidos directos)

---

## Idempotencia

Cursor estricto `>` (not `>=`) garantiza que un evento se procesa exactamente una vez. Si Vtiger update falla, el cursor NO avanza — próximo cron retoma desde mismo punto.

Si la auth Vtiger falla globalmente (network, credentials), el batch entero falla; cursor no avanza; próximo cron reintenta desde mismo cursor.

---

## Audit events emitidos

| Event | When | After state |
|---|---|---|
| `tracking.vtiger_leadstatus_synced` | Vtiger update exitoso | `{cod_lead, vtiger_id, old_leadstatus, new_leadstatus, source_audit_log_id}` |
| `tracking.vtiger_leadstatus_sync_failed` | Vtiger update fail (después de retry interno) | `{cod_lead, vtiger_id, attempted_leadstatus, error_message, source_audit_log_id}` |

Categoría `tracking.*` (60 eventos canónicos total al 2026-05-10).

---

## Smoke test E2E (ejecutado 2026-05-10)

Test data:
- Lead Vtiger creado: `id=10x69, leadstatus=Nuevo` (LEA68, SMOKE_A2)
- ERP insert directo: `cod_lead=SMOKE_A2_LEAD, vtiger_id=10x69`
- Audit event simulado: `appointment.marked_attended` (id 238)

Resultado:
- ✅ Endpoint ERP devuelve item correcto
- ✅ Workflow A2 cron disparado
- ✅ Vtiger update exitoso: leadstatus `Nuevo → Cliente`
- ✅ Audit event downstream: `tracking.vtiger_leadstatus_synced` (id 239)
- ✅ Latencia E2E: ~2 min cron + ~3 sec API calls

Smoke data limpiada post-validación.

---

## Cross-references

- ADR-0036 — Workflow [A2] sync ERP→Vtiger (decisión arquitectónica + 4 opciones consideradas)
- ADR-0035 — Módulo Agenda Mínima ERP (origen de eventos appointment.marked_*)
- ADR-0027 — Audit log inmutable (bus de eventos)
- Memoria `feedback_doctora_solo_erp_vtiger_automatico.md` — doctrina operacional
- Memoria `feedback_congruencia_nombres_cross_system.md` — picklist congruente
- `integrations/vtiger/fields-mapping.md` § Picklist `leadstatus`
