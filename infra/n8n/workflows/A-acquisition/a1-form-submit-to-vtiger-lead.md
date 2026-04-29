# [A1] Capturar Form Submit → Vtiger Lead

**Categoría:** acquisition
**Fase:** 3 (Mini-bloque 3.3 REWRITE)
**Criticidad:** critical
**Estado:** staging (en validación al 2026-04-29)
**Webhook URL:** `POST https://flow.livskin.site/webhook/acquisition/form-submit`

---

## Qué hace

Recibe cada submit del form 1569 (WordPress mu-plugin), normaliza phone a E.164, dedup contra Vtiger via phone match, y crea o actualiza Lead en Vtiger con los 12 custom fields de attribution (UTMs + click_ids + cookies + event_id + landing_url + tratamiento_interes).

Emite audit event `lead.captured_via_form` al ERP (non-blocking).

---

## Trigger

Webhook POST en `/webhook/acquisition/form-submit`.

---

## Input expected (del mu-plugin WordPress)

```json
{
  "nombre": "string (required)",
  "phone": "string (required, cualquier formato — se normaliza a E.164)",
  "email": "string (optional)",
  "tratamiento_interes": "string (optional, picklist value)",
  "consent_marketing": "boolean",
  "utm_source": "string (optional)",
  "utm_medium": "string (optional)",
  "utm_campaign": "string (optional)",
  "utm_content": "string (optional)",
  "utm_term": "string (optional)",
  "fbclid": "string (optional, Meta click ID)",
  "gclid": "string (optional, Google click ID)",
  "fbc": "string (optional, _fbc cookie)",
  "ga": "string (optional, _ga cookie)",
  "event_id": "string (optional, UUID del GTM Tracking Engine)",
  "landing_url": "string (optional, URL completa)",
  "referer": "string (optional)",
  "ip_at_submit": "string (optional, capturado server-side por mu-plugin)",
  "ua_at_submit": "string (optional)"
}
```

---

## Output (al mu-plugin)

**Caso éxito (200):**
```json
{
  "ok": true,
  "vtiger_lead_id": "12x123",
  "is_new": true,
  "event_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

`is_new` = `true` si se creó lead nuevo, `false` si fue UPDATE de lead existente (dedup match).

**Errores:**

| HTTP code | Body | Causa |
|---|---|---|
| 400 | `{"ok": false, "error": "phone_invalid", "phone_raw": "..."}` | Phone no se pudo normalizar a E.164 |
| 502 | `{"ok": false, "error": "vtiger_unreachable"}` | Vtiger getchallenge/login falló (container down o timeout) |
| 500 | `{"ok": false, "error": "internal", "execution_id": "..."}` | Bug en workflow — revisar n8n execution log |

---

## Sistemas tocados

| Sistema | Acceso |
|---|---|
| Webhook input | read (recibe POST) |
| Vtiger via REST API | read (query Leads) + write (create/update Lead) |
| ERP audit endpoint `/api/internal/audit-event` | write (POST audit event, non-blocking) |
| n8n SQLite (execution log) | write automático |

---

## Flujo (11 nodos)

```
[1] Webhook Trigger (POST /webhook/acquisition/form-submit)
        ↓
[2] Validate & Normalize Phone (Code)
    ↓ (if phone invalid → [Respond 400])
[3] Vtiger getchallenge (HTTP GET)
        ↓
[4] Compute MD5(token + accesskey) (Code)
        ↓
[5] Vtiger login (HTTP POST) → sessionName
        ↓
[6] Vtiger query Leads WHERE phone (HTTP GET)
        ↓
[7] IF: ¿lead existe?
    ├─ TRUE → [8a] Vtiger update Lead (HTTP POST)
    └─ FALSE → [8b] Vtiger create Lead (HTTP POST)
        ↓
[9] Merge branches (Merge node mode=passThrough)
        ↓
[10] Build Response Payload (Code)
        ↓
[11] Respond to Webhook (200 OK)
        ↓
[12] (parallel non-blocking) HTTP POST ERP audit-event
```

---

## Credenciales necesarias

Como **environment variables** en el container n8n (ver `infra/n8n/conventions.md` § 9):

```bash
VTIGER_URL=https://crm.livskin.site
VTIGER_API_USER=admin
VTIGER_API_ACCESSKEY=<ver keys/.env.integrations>
AUDIT_INTERNAL_TOKEN=<ver keys/.env.integrations o /srv/livskin-revops/keys/.audit-internal-token en VPS>
ERP_AUDIT_URL=https://erp.livskin.site/api/internal/audit-event
```

---

## Lógica de dedup

**Algoritmo (paso [6] + [7]):**

1. Normalizar phone del form a E.164 con código país Perú default (`+51`)
2. Query Vtiger: `SELECT id FROM Leads WHERE phone='<E.164>' LIMIT 1`
3. Si retorna 0 filas → CREATE nuevo Lead
4. Si retorna ≥1 fila → UPDATE el primero (el más reciente típicamente)

**Reglas de UPDATE (paso [8a]) — qué se preserva inmutable vs qué se sobreescribe:**

| Campo | Acción en UPDATE |
|---|---|
| `firstname`, `lastname` | Preservar (no actualizar — el original tiene priority) |
| `email` | Sobreescribir si el nuevo está más completo (no vacío) |
| `phone` | Preservar (es el match key, no cambia) |
| `cf_853` (UTM Source) ... `cf_865` (GCLID) | **Preservar** — first-touch attribution es inmutable conceptualmente |
| `cf_867` (FBC) ... `cf_871` (Event ID) | Preservar (mismo razón) |
| `cf_873` (Landing URL) | Preservar (first-touch) |
| `cf_875` (Tratamiento de Interés) | Sobreescribir si el nuevo es más específico que "Otro / No especificado" |
| `description` | Append: `\n[2026-04-29] Re-submitted form` |

**Razón:** los campos at_capture son first-touch attribution que NO debe cambiar. El siguiente touchpoint (re-submit del mismo lead) se registra en `lead_touchpoints` (tabla ERP) via Workflow B1 cuando Vtiger emita su webhook on-change.

---

## Errores conocidos / edge cases

| Caso | Comportamiento |
|---|---|
| Phone empty | 400 + log warning |
| Phone con caracteres no-numéricos (espacios, +, paréntesis) | Normalizar quitándolos antes de validar |
| Phone con prefijo distinto a `+51` | Aceptado tal cual si ya en E.164 (ej. `+34`, `+1`) |
| Phone 9 dígitos sin prefijo | Asumir Perú: prepend `+51` |
| Phone <8 dígitos o >15 dígitos | 400 phone_invalid |
| Email vacío | Aceptado (campo opcional) |
| Email duplicado (otro lead lo tiene) | NO bloqueamos — phone es el dedup key, email es secundario |
| Vtiger session expirada mid-workflow | Re-autenticar (re-correr nodos 3-5) |
| Vtiger create devuelve "Field cf_XXX does not exist" | 500 internal — significa fields no creados en Vtiger (verificar runbook `vtiger-custom-fields.md`) |
| ERP audit-event endpoint 5xx | Log warning, NO falla workflow (audit non-blocking) |
| `event_id` vacío (form sin GTM Tracking Engine activo) | Aceptado, log warning porque empeora CAPI dedup |
| `consent_marketing=false` | Aceptado — lead se crea pero `nurture_state='inactivo'` (no entra a drip) |

---

## Tags n8n (post-import)

```
acquisition · fase-3 · critical · staging  (cambia a production tras smoke test)
```

---

## Cómo testar manualmente

```bash
# Test mínimo (solo phone + nombre)
curl -X POST https://flow.livskin.site/webhook/acquisition/form-submit \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Lead Manual",
    "phone": "+51999000001",
    "consent_marketing": true
  }'
# Expected: 200 + { ok: true, vtiger_lead_id: "...", is_new: true, event_id: null }

# Test full payload con todos los campos
curl -X POST https://flow.livskin.site/webhook/acquisition/form-submit \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Full Lead",
    "phone": "+51999000002",
    "email": "test-full@example.com",
    "tratamiento_interes": "Botox",
    "consent_marketing": true,
    "utm_source": "facebook",
    "utm_medium": "cpc",
    "utm_campaign": "test-campaign-2026-04-29",
    "utm_content": "test-creative-001",
    "fbclid": "IwAR1Test123abc",
    "gclid": "",
    "fbc": "fb.1.1714398432.IwAR1Test123abc",
    "ga": "GA1.2.1234567890.1714398432",
    "event_id": "550e8400-e29b-41d4-a716-446655440000",
    "landing_url": "https://livskin.site/botox?utm_source=facebook&...",
    "referer": "https://www.facebook.com/",
    "ip_at_submit": "190.236.1.2",
    "ua_at_submit": "Mozilla/5.0 (Test)"
  }'

# Test phone invalid (debería 400)
curl -X POST https://flow.livskin.site/webhook/acquisition/form-submit \
  -H "Content-Type: application/json" \
  -d '{ "nombre": "Test Bad Phone", "phone": "abc", "consent_marketing": true }'
# Expected: 400 + { ok: false, error: "phone_invalid" }

# Test dedup (re-enviar mismo phone debería retornar is_new=false)
# Re-correr el primer test: vtiger_lead_id mismo + is_new: false
```

Después de cada test, verificar en n8n UI execution log:
- Logueado en https://flow.livskin.site
- Workflows → [A1] → Executions → ver el execution más reciente
- Confirmar que cada nodo ejecutó exitosamente
- Si algún nodo falló: click en él para ver el error y debugar

Verificar lead creado en Vtiger UI:
- https://crm.livskin.site → Leads → buscar por phone

Verificar audit event en ERP:
```bash
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp \
  -c "SELECT timestamp, action, metadata FROM audit_log \
      WHERE action = '\''lead.captured_via_form'\'' \
      ORDER BY timestamp DESC LIMIT 5;"'
```

---

## Cambios

- 2026-04-29 v1.0 — diseño inicial Mini-bloque 3.3 REWRITE
