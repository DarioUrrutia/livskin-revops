# [G3] Despachar ERP CAPI Event → Meta Graph API

**Categoría:** growth
**Fase:** 3 (Mini-bloque 3.4)
**Criticidad:** critical
**Estado:** staging
**Webhook URL:** `POST https://flow.livskin.site/webhook/growth/capi-emit`

---

## Qué hace

Recibe events del ERP (`capi_emitter_service.emit_event()`), hashea PII con SHA-256, construye payload Meta CAPI, y POSTea al Graph API del Pixel `4410809639201712`. Returns response del Graph API.

**Eventos canónicos soportados:** `Lead`, `Schedule`, `Purchase` (per ADR-0019).

---

## Trigger

Webhook POST en `/webhook/growth/capi-emit` (interno — auth via X-Internal-Token gestionada por ERP cuando llama).

---

## Input expected (del ERP capi_emitter_service)

```json
{
  "event_name": "Lead | Schedule | Purchase",
  "event_id": "uuid-coherente-con-pixel-client",
  "event_time": <unix_timestamp>,
  "event_source_url": "https://livskin.site/...",
  "action_source": "website",
  "user_data": {
    "email": "raw@example.com",
    "phone_e164": "+51999000111",
    "fbc": "fb.1.xxx.IwAR...",
    "fbp": "fb.1.xxx",
    "external_id": "LIVLEAD0001",
    "client_ip_address": "78.213.23.237",
    "client_user_agent": "Mozilla/5.0..."
  },
  "custom_data": {
    "currency": "PEN",
    "value": "250.00",
    "content_name": "Botox",
    "content_category": "lead_acquisition"
  }
}
```

---

## Flujo (10 nodos)

```
[1] Webhook trigger /webhook/growth/capi-emit
       ↓
[2] Code: hash PII + build Meta CAPI payload
       ↓ (SHA-256 lowercase + trim para email/phone/external_id)
[3] HTTP POST → https://graph.facebook.com/{version}/{pixel_id}/events
       ↓
[4] Code: build response al ERP (incluye fbtrace_id de Meta)
       ↓
[5] Respond to webhook 200
```

---

## Hashing (regla Meta)

Per [Meta Conversions API docs](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/customer-information-parameters):

| Campo | Pre-hashing transform | Hash |
|---|---|---|
| `email` | lowercase + trim | SHA-256 |
| `phone` | strip non-digits, NO leading + (E.164 sin +) | SHA-256 |
| `external_id` | trim (NO lowercase si es UUID o cod_lead) | SHA-256 |
| `fbc`, `fbp`, `client_ip_address`, `client_user_agent` | NO hashing — pasan raw | — |

---

## Credenciales necesarias (env vars n8n)

```bash
META_PIXEL_ID=4410809639201712
META_CAPI_ACCESS_TOKEN=EAA...
META_GRAPH_API_VERSION=v21.0
META_TEST_EVENT_CODE=  # vacío en producción
```

---

## Output al ERP

```json
{
  "ok": true,
  "events_received": 1,
  "fbtrace_id": "AKj6SWLywcDijSo-lh_xH7P",
  "event_id": "<echo>"
}
```

Errores:
| HTTP | Causa |
|---|---|
| 400 | payload inválido (event_name desconocido, event_id missing) |
| 502 | Meta Graph API unreachable o 5xx |
| 200 con `ok: false` | Meta rechazó el evento (fbtrace_id provee debug info) |

---

## Tags n8n (post-import)

```
growth · fase-3 · critical · staging
```

---

## Cómo testar manualmente

```bash
TOKEN=$(ssh livskin-erp 'sudo cat /srv/livskin-revops/keys/.audit-internal-token')
# (este endpoint NO valida X-Internal-Token, depende de protección de red interna VPC)

curl -X POST https://flow.livskin.site/webhook/growth/capi-emit \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "Lead",
    "event_id": "test-g3-validation",
    "event_time": 1777625085,
    "event_source_url": "https://livskin.site/?utm_source=test",
    "action_source": "website",
    "user_data": {
      "email": "test@example.com",
      "phone_e164": "+51999000111",
      "fbc": "fb.1.1777.IwAR_test",
      "client_ip_address": "78.213.23.237",
      "client_user_agent": "Mozilla/5.0 (Test)"
    },
    "custom_data": {
      "currency": "PEN",
      "content_name": "Test Lead",
      "content_category": "test"
    }
  }'

# Expected: 200 con events_received=1
```

Verificar en Meta Events Manager → Probar eventos tab.

---

## Cambios

- 2026-05-01 v1.0 — diseño inicial Mini-bloque 3.4
