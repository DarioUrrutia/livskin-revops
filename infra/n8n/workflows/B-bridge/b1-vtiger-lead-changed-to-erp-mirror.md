# [B1] Espejar Vtiger Lead Changed → ERP Mirror

**Categoría:** bridge
**Fase:** 3 (Mini-bloque 3.3 REWRITE)
**Criticidad:** critical
**Estado:** staging (en validación al 2026-04-29)
**Webhook URL:** `POST https://flow.livskin.site/webhook/bridge/vtiger-lead-changed`

---

## Qué hace

Recibe webhook de Vtiger cuando un Lead cambia (CREATE o UPDATE). Pulla data fresca via REST `retrieve`, mapea custom fields `cf_NNN` → ERP column names, y POSTea al endpoint `/api/leads/sync-from-vtiger` del ERP (Paso 5) que persiste/actualiza la fila en `livskin_erp.leads`.

Sync **unidireccional** Vtiger → ERP. ERP NUNCA escribe a Vtiger desde este workflow (eso lo hace [B2] cuando lead convierte a cliente, futuro F6).

---

## Trigger

Webhook POST en `/webhook/bridge/vtiger-lead-changed`.

**Configurable de 2 formas:**

1. **Vtiger Workflow + Workflow Tasks → "Invoke Custom Function" / "Send To URL"** (preferido en Vtiger 8.2 community)
2. **Cron pull en n8n** que cada N minutos query Vtiger y procesa cambios (fallback si webhook on-change Vtiger no funciona — diferido)

Para Mini-bloque 3.3 usamos opción 1, configurada en sub-paso 6.5.

---

## Input expected (de Vtiger)

Vtiger Workflow puede enviar tres formatos según config:
- **Mínimo:** solo `{"id": "10x123"}` — workflow [B1] hará retrieve para llenar el resto
- **Parcial:** algunos fields (firstname, phone, leadstatus) — usable pero incompleto
- **Full:** todos los fields incluyendo cf_NNN — ideal pero depende de config Vtiger

`[B1]` está diseñado para tolerar los 3 — siempre hace retrieve fresh para garantizar consistency.

```json
{
  "id": "10x123"  // mínimo requerido
  // resto opcional, será sobrescrito por retrieve
}
```

---

## Output

200 OK con confirmación:
```json
{
  "ok": true,
  "vtiger_id": "10x123",
  "erp_response": {
    "operation": "created" | "updated",
    "lead_id": 3,
    "cod_lead": "LIVLEAD0001"
  }
}
```

Errores (raros, casi todos defensive):
| HTTP | Body | Causa |
|---|---|---|
| 400 | `{"ok": false, "error": "id_missing"}` | Vtiger no mandó `id` en payload |
| 502 | `{"ok": false, "error": "vtiger_unreachable"}` | retrieve falló |
| 502 | `{"ok": false, "error": "erp_unreachable"}` | POST al ERP falló |

---

## Sistemas tocados

| Sistema | Acceso |
|---|---|
| Webhook input | read (recibe POST de Vtiger) |
| Vtiger via REST API | read (login + retrieve Lead by id) |
| ERP `/api/leads/sync-from-vtiger` | write (POST con X-Internal-Token) |
| n8n SQLite (execution log) | write automático |

---

## Flujo (10 nodos)

```
[1] Webhook Trigger (POST /webhook/bridge/vtiger-lead-changed)
        ↓
[2] Extract vtiger_id (Code)
    ↓ (if id missing → Respond 400)
[3] Vtiger getchallenge (HTTP GET)
        ↓
[4] Compute MD5 Hash (Code)
        ↓
[5] Vtiger Login (HTTP POST → sessionName)
        ↓
[6] Vtiger Retrieve Lead (HTTP GET ?operation=retrieve&id=...)
        ↓
[7] Map cf_NNN → ERP fields (Code)
        ↓
[8] HTTP POST ERP /api/leads/sync-from-vtiger
        ↓
[9] Build Response (Code)
        ↓
[10] Respond to Webhook (200)
```

---

## Mapeo cf_NNN → ERP (en nodo [7])

Ver autoritativo `integrations/vtiger/fields-mapping.md`. Snippet en JS:

```javascript
const v = $input.first().json.result;  // retrieve response
const erpPayload = {
  vtiger_id: v.id,
  nombre: ((v.firstname || '') + ' ' + (v.lastname || '')).trim(),
  phone_e164: v.phone || '',
  email: v.email || '',
  leadstatus: v.leadstatus || '',
  leadsource: v.leadsource || '',

  // cf_NNN → ERP (12 custom fields)
  utm_source: v.cf_853 || '',
  utm_medium: v.cf_855 || '',
  utm_campaign: v.cf_857 || '',
  utm_content: v.cf_859 || '',
  utm_term: v.cf_861 || '',
  fbclid: v.cf_863 || '',
  gclid: v.cf_865 || '',
  fbc: v.cf_867 || '',
  ga: v.cf_869 || '',
  event_id: v.cf_871 || '',
  landing_url: v.cf_873 || '',
  tratamiento_interes: v.cf_875 || '',
};
```

---

## Credenciales necesarias (env vars en n8n container — ya seteadas en [A1])

```bash
VTIGER_URL=https://crm.livskin.site
VTIGER_API_USER=admin
VTIGER_API_ACCESSKEY=<keys/.env.integrations>
ERP_SYNC_URL=https://erp.livskin.site/api/leads/sync-from-vtiger
AUDIT_INTERNAL_TOKEN=<keys/.audit-internal-token VPS 3>
```

**Nuevo:** `ERP_SYNC_URL`. Hay que agregar a `/home/livskin/apps/n8n/.env` antes de importar workflow (sub-paso 6.2).

---

## Errores conocidos / edge cases

| Caso | Comportamiento |
|---|---|
| Vtiger payload sin `id` | 400 inmediato |
| Vtiger retrieve devuelve `success: false` | 502 vtiger_unreachable + log error |
| ERP responde 4xx (validación schema) | 502 + log con detalles del error response del ERP |
| ERP responde 5xx | 502 erp_unreachable + log |
| Race condition (Vtiger UPDATE rapido) | Idempotencia del endpoint /sync-from-vtiger garantiza no duplicar |
| Vtiger phone sin formato E.164 | Pasa as-is al ERP (que valida y rechaza si inválido) — backlog F6: normalizar acá |
| Custom field nuevo agregado a Vtiger sin estar en mapping | Se ignora silenciosamente — actualizar fields-mapping.md cuando se agregue |

---

## Tags n8n (post-import)

```
bridge · fase-3 · critical · staging  (cambia a production tras smoke test)
```

---

## Cómo testar manualmente

```bash
# Mínimo: solo id de un lead que existe en Vtiger
curl -X POST https://flow.livskin.site/webhook/bridge/vtiger-lead-changed \
  -H "Content-Type: application/json" \
  -d '{"id": "10xN"}'  # reemplazar 10xN con un id real

# Expected:
# 200 + { ok: true, vtiger_id: "10xN", erp_response: { operation: "created", lead_id: ..., cod_lead: "LIVLEAD####" } }

# Verificar en ERP DB
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp \
  -c "SELECT id, cod_lead, vtiger_id, nombre, phone_e164, utm_source_at_capture FROM leads WHERE vtiger_id = '\''10xN'\'';"'

# Ver execution log en n8n UI:
# https://flow.livskin.site → Workflows → [B1] → Executions
```

---

## Cambios

- 2026-04-29 v1.0 — diseño inicial Mini-bloque 3.3 REWRITE
