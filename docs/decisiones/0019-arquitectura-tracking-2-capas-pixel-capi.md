# ADR-0019 — Arquitectura tracking 2-capas (Pixel client-side + CAPI server-side via n8n)

**Estado:** ✅ Aprobada
**Fecha:** 2026-05-01
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 3 (Mini-bloque 3.4)
**Workstream:** Tracking

---

## 1. Contexto

Hasta hoy (2026-05-01), Livskin tiene capa **client-side** de tracking funcionando (Pixel via GTM Tracking Engine — Mini-bloque 3.2 + ADR-0021). Esto cubre eventos browser-side (PageView, ViewContent, form_submit, whatsapp_click) pero deja gaps significativos:

- **iOS 14.5+ Tracking Transparency** rechaza ~30% de los Pixel events
- **AdBlockers** bloquean ~10-20% adicionales
- **Browser cookies degradadas** (Safari ITP, Chrome 3rd party deprecation)
- **Resultado:** Meta solo ve 60-70% de las conversiones reales → optimización mediocre, CPM/CPA reportados peor que real, CAC sobreestimado

Para resolver esto, Meta provee **Conversions API (CAPI)** — emisión server-side directamente al Graph API. Combinado con Pixel client-side via `event_id` deduplicado, cubre 95%+ de conversiones reales.

**Pre-requisitos cumplidos al iniciar este ADR:**
- ✅ ERP refactorizado en producción (Mini-bloque 2 — completado 2026-04-26)
- ✅ Pipeline form WP → Vtiger → ERP `leads` con first-touch attribution preservada (Mini-bloque 3.3 REWRITE — completado 2026-05-01)
- ✅ event_id UUID coherente client+server propagándose end-to-end (Mini-bloques 3.2 + 3.3)
- ✅ Pixel `4410809639201712` activo en Business Manager Livskin Perú
- ✅ Token CAPI generado + validado API + validado visual UI Meta (2026-05-01)
- ✅ n8n como capa orquestadora cross-system establecida (memoria `project_n8n_orchestration_layer`)

**Referencias:**
- Plan maestro § 11.5 (Fase 3 — Tracking)
- Blueprint § 7 (Marketing & Acquisition)
- ADR-0021 (UTMs persistence + Tracking Engine client-side)
- ADR-0011 v1.1 (modelo de datos — schema soporta CAPI fields)
- ADR-0015 (Source of Truth — ERP master de transacciones es fuente de Purchase events)
- Memoria `project_capi_match_quality.md` — click_ids supremos para attribution
- Memoria `project_n8n_orchestration_layer.md` — n8n como capa visible
- Memoria `project_tracking_architecture.md` — superseded en parte por este ADR

---

## 2. Opciones consideradas

### Opción A — CAPI emit directo desde ERP a Meta (sin n8n)

ERP Flask llama directamente al Graph API de Meta cuando se crea lead/cita/venta. Mínimo hops, control total en Python.

**Pros:**
- Match quality alta (PII en ERP)
- Audit log directamente en ERP
- Latencia baja (~100ms)
- Sin dependencia de n8n para emit

**Contras:**
- Sin visualidad para Dario (debugging requiere logs Python)
- Si Meta cambia API, hay que tocar Python y redeployar ERP
- Vendor lock-in: agregar Google CAPI / TikTok / Snap requiere reimplementar
- Pierde coherencia con principio "n8n = capa visual orquestadora"

### Opción B — CAPI emit vía n8n (ERP → n8n → Meta)

ERP llama a un webhook interno de n8n cuando se crea lead/cita/venta. n8n hace el hashing + POST a Meta. Mismo evento de Pixel client-side dispara con `event_id` coherente para deduplicación.

**Pros:**
- Visualidad total: Dario ve cada evento en `flow.livskin.site` execution log
- Centralización outbound a Meta + futuros canales (Google CAPI, TikTok, Snap) en n8n
- Edit nodo n8n si Meta cambia API (sin redeploy ERP)
- Coherente con memoria `project_n8n_orchestration_layer`
- Pause/restart con un click si Meta tiene incidente

**Contras:**
- 1 hop más (~+300ms latencia total) — no crítico para CAPI
- 1 workflow más a mantener
- Si n8n cae, eventos no llegan (mitigación: ERP audit_log mantiene record para retry)

### Opción C — Meta-enabled CAPI (cloud-based hosted by Meta)

Meta hostea la infraestructura. One-click setup en Events Manager. Lanzado Apr 15 2026.

**Pros:**
- Cero código + cero mantenimiento
- Setup en minutos

**Contras (descalificadores para Livskin):**
- ⚠️ **Restricciones para "special ad categories"** — health/medicina estética casi seguro restringido
- ⚠️ **No documenta integración con ERP/CRM custom** — no claro cómo Meta-hosted cobnnects con Vtiger + Postgres
- ⚠️ **No menciona custom event_id support** → rompería deduplicación con Pixel client-side existente (Mini-bloque 3.2)
- ⚠️ **AI pixel enrichment NO disponible para health** — pierdes la feature principal
- ⚠️ Vendor lock-in alto (Meta-only, futuro Google/TikTok requiere reimplementar)
- ⚠️ Producto NUEVO sin docs técnicas detalladas

---

## 3. Análisis de tradeoffs

| Dimensión | A: ERP directo | **B: vía n8n** | C: Meta-enabled |
|---|---|---|---|
| Costo monetario | $0 | $0 | $0 |
| Costo implementación | 1-2 sesiones | 2-3 sesiones | ~10 min (button) |
| Complejidad mantenimiento | Media | Media | Cero |
| Visualidad para Dario | ❌ Logs Python only | ✅ flow.livskin.site UI | UI Meta only |
| Match quality control | Total | Total | Limited |
| Custom event_id deduplicación | ✅ | ✅ | ❌ No mencionado |
| Health/medical category | ✅ Sin restricciones | ✅ Sin restricciones | ⚠️ Restricciones casi seguras |
| Backend integration ERP custom | ✅ | ✅ | ❌ No claro |
| Vendor lock-in | Bajo | **Bajo** (extensible) | Alto |
| Risk si Meta cambia API | Edit + redeploy | Edit nodo n8n | ⚠️ Perdés todo overnight |
| Portfolio value RevOps | Medio | **Alto** | Bajo |
| Reversibilidad | Alta | Alta | Baja |
| Alineación con `project_n8n_orchestration_layer` | ❌ Bypassa n8n | ✅ Coherente | ❌ Bypassa todo |

---

## 4. Recomendación

Yo (Claude Code) recomiendo **Opción B (CAPI emit vía n8n)** porque:

1. **Coherente con principio operativo de n8n como capa visible** — toda integración cross-system pasa por n8n. Dario gobierna desde `flow.livskin.site`.
2. **Match quality igual a Opción A** — porque el origen del evento sigue siendo el ERP (PII real), n8n solo orquesta el outbound.
3. **Extensibilidad cross-platform** — el mismo workflow [G3] se extiende para Google CAPI / TikTok / Snap cambiando solo el destination URL + payload mapping.
4. **Bajo vendor lock-in** — si en F4-F5 se agrega un nuevo canal (TikTok), reusamos el workflow base.
5. **Opción C descalificada** por restricciones health + sin custom event_id support → rompería nuestro Pixel client-side existente.

**Tradeoff principal que aceptamos:** ~+300ms latencia adicional por el hop ERP → n8n. No crítico para CAPI (no es real-time con UI). El beneficio de visualidad + extensibilidad supera ampliamente.

---

## 5. Decisión

**Elección:** Opción B — CAPI emit vía n8n.

**Fecha de aprobación:** 2026-05-01 por Dario.

**Razonamiento de la decisora:**
> "n8n es la capa visual de las automatizaciones que tú haces, pero que yo gestiono desde aquí y puedo ver su estructura en n8n, o para hacer algunos debugs." (Dario, 2026-04-29 → reafirmado 2026-05-01).

---

## 6. Arquitectura completa (cross-reference de capas)

### Capa 1 — Client-side (Pixel via GTM)

Ya implementado en Mini-bloque 3.2 + ADR-0021. Resumen:
- GTM Tracking Engine v18 dispara Pixel events (PageView, ViewContent, form_submit, whatsapp_click)
- Cookies first-party `lvk_*` 90 días persisten UTMs + click_ids cross-session
- mu-plugin (Mini-bloque 3.3) inyecta hidden inputs + populates con cookies/URL params + genera UUID `event_id` al submit

### Capa 2 — Server-side (CAPI via n8n) — esta ADR

**Disparadores en ERP** que emiten eventos server-side:

| Evento Meta | Trigger ERP | event_id source |
|---|---|---|
| **Lead** | Lead se crea via `/api/leads/sync-from-vtiger` (operation="created") | `event_id_at_capture` del lead (UUID generado por GTM al form submit) |
| **Schedule** | Cita se crea en tabla `appointments` (Bloque puente Agenda — futuro) | UUID nuevo generado al INSERT de appointment |
| **Purchase** | Pago real se registra en `pagos` (legacy_forms route) | UUID nuevo generado al INSERT de pago |

**Flow:**

```
ERP business event
   ↓ (hook auto-emit en service layer)
POST https://flow.livskin.site/webhook/growth/capi-emit
   ↓ (n8n Workflow [G3])
Code: build CAPI payload
  - hash email/phone con SHA-256 (lowercase + trim primero)
  - propagate fbc, fbp cookies (si están en lead/cliente)
  - propagate UTMs + click_ids (preserved en at_capture fields)
  - event_id = pasado por ERP (mismo que Pixel client-side fired)
  - test_event_code (env var, opcional para staging)
   ↓
HTTP POST https://graph.facebook.com/v21.0/{PIXEL_ID}/events?access_token={TOKEN}
   ↓
Meta Events Manager (recibe)
   ↓ (deduplica por event_id contra Pixel client-side)
Optimization signal mejorado para algoritmo de ads
```

### Eventos canónicos + payload schema

```json
{
  "data": [{
    "event_name": "<Lead|Schedule|Purchase>",
    "event_time": <unix_timestamp>,
    "event_id": "<UUID coherente con Pixel client-side>",
    "event_source_url": "<landing_url_at_capture o URL contextual>",
    "action_source": "website",
    "user_data": {
      "em": ["<sha256(email_lowercase_trim)>"],
      "ph": ["<sha256(phone_e164)>"],
      "fbc": "<lvk_fbc cookie value si presente>",
      "fbp": "<_fbp cookie value si presente>",
      "client_ip_address": "<ip_at_submit>",
      "client_user_agent": "<ua_at_submit>",
      "external_id": ["<sha256(cod_cliente o cod_lead)>"]
    },
    "custom_data": {
      "currency": "PEN",
      "value": <total para Purchase, omitido para Lead/Schedule>,
      "content_name": "<tratamiento_interes>",
      "content_category": "<categoria del catálogo>"
    }
  }],
  "test_event_code": "<env var TEST_EVENT_CODE — solo en staging>"
}
```

### Pixel canónico

**Único:** `4410809639201712` (Livksin Pixel 2026).
**Legacy a archivar:** `670708374433840` (Livksin Pixel) — backlog item específico tras este ADR.

### event_id deduplicación

**Regla dura:** el `event_id` que mandamos en CAPI server-side **DEBE coincidir** con el `event_id` que el Pixel client-side disparó para el mismo evento del usuario. Meta deduplica:
- Si solo recibe client-side → cuenta 1
- Si solo recibe server-side → cuenta 1
- Si recibe ambos con mismo event_id → cuenta 1 (deduplica)
- Si recibe ambos con event_ids distintos → **cuenta 2** (métricas infladas — error)

**Implementación:**
- `Lead`: ya existe `event_id_at_capture` en `leads` table (Mini-bloque 3.3) — valor pasado al CAPI emit
- `Schedule`: appointment.event_id (futuro) — generado al crear cita
- `Purchase`: pago.event_id (futuro) — generado al crear pago real, idéntico al `Pixel Purchase fbq('track', 'Purchase', { event_id: ... })` en pantalla de confirmación

---

## 7. Decisión

**Elección:** Opción B — CAPI emit vía n8n.

**Aprobada:** 2026-05-01 por Dario.

---

## 8. Consecuencias

### Desbloqueado por esta decisión

- Construcción endpoint ERP `/api/internal/capi-emit` (interno, X-Internal-Token auth)
- Construcción n8n Workflow [G3] CAPI emit (hash + POST Meta)
- Hooks en ERP services para auto-emit (`lead_sync_service`, `pago_service`)
- Backlog Bloque puente Agenda: hook auto-emit Schedule al crear `appointment`
- Subir 134 clientes existentes a Meta como Custom Audience (script Python — bonus de este mini-bloque)
- Métricas reales de attribution + LTV + CAC en Metabase dashboards (Mini-bloque 3.5)

### Bloqueado / descartado

- **Opción C (Meta-enabled CAPI)** descartada por restricciones health + sin custom event_id support
- **Opción A (ERP directo a Meta)** descartada por contradecir principio de visualidad n8n
- **Marketing API tokens (ads_management)** sigue diferido — se trataría en F5 si se construye Acquisition Agent productivo

### Implementación derivada

**Mini-bloque 3.4 (este bloque):**
- [ ] Endpoint `/api/internal/capi-emit` en ERP Flask (Pydantic schema + service + tests TDD)
- [ ] n8n Workflow [G3] CAPI emit (12-15 nodes esperados)
- [ ] Hook en `lead_sync_service.upsert_lead()` — auto-emit Lead event al CREATE
- [ ] Hook en `pago_service.create_pago()` — auto-emit Purchase event (cuando exista)
- [ ] Smoke test E2E con `test_event_code` → Meta Events Manager Test Events tab
- [ ] Verificación match quality ≥7/10 con datos reales (post-cleanup test data)
- [ ] Update `infra/docker/vps2-ops/n8n/.env.example` + VPS 2 .env con `META_PIXEL_ID`, `META_CAPI_ACCESS_TOKEN`, `META_GRAPH_API_VERSION`
- [ ] Update `services/audit_service.py` KNOWN_ACTIONS: agregar `tracking.capi_event_emitted`, `tracking.capi_event_failed`
- [ ] Bonus: script Python `scripts/meta_custom_audience_upload.py` para subir 134 clientes existentes

**Bloque puente Agenda (futuro):**
- [ ] Tabla `appointments` con columna `event_id` (UUID, generado al INSERT)
- [ ] Hook auto-emit Schedule en service layer

**Mini-bloque 3.5 (Observabilidad):**
- [ ] Metabase dashboard "CAPI events emitted" — count por día + match quality avg
- [ ] Alert si `capi_event_failed` >5 en 1h (workflow [G3] failures)

### Cuándo reabrir esta decisión

- **Volumen >10K events/día:** evaluar si latencia n8n se vuelve issue → posible move a queue (Redis/RabbitMQ) entre ERP y n8n
- **Meta launches mejor producto que Meta-enabled CAPI** que SÍ soporta health + custom event_id
- **Aparición de Google CAPI equivalent** (gtag.js Server-side ya disponible 2026) — extender o consolidar workflow [G3] a multi-platform
- **Token rotation issues** post-60-días → automation de rotación necesaria
- **Match quality consistente <6/10** post-launch — investigar qué identifiers faltan

---

## 9. Changelog

- 2026-05-01 — v1.0 — Creada y aprobada (Mini-bloque 3.4)

---

## 10. Cross-references

- ADR-0021 — UTMs persistence + Tracking Engine client-side (capa 1, complementaria)
- ADR-0011 v1.1 — modelo de datos (provee schema soportado para CAPI emission)
- ADR-0015 — Source of Truth (ERP es source de Purchase events autoritative)
- Memoria `project_capi_match_quality.md` — taxonomía identifiers Meta + Google
- Memoria `project_n8n_orchestration_layer.md` — n8n capa visual cross-system
- Memoria `project_tracking_architecture.md` — superseded en parte (capa server-side ahora cerrada acá)
- Backlog: subir 134 clientes Custom Audience + alinear picklist Vtiger cf_875 + Pixel legacy archivar

**Notas:**
- Este ADR es inmutable salvo cambios de status.
- Para cambiar la decisión (ej: mover CAPI emit a Redis queue vs n8n directo) → crear nueva ADR que la `superseda`.
