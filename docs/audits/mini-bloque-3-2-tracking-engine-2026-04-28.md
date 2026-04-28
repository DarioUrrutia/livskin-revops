# Mini-bloque 3.2 — GTM Tracking Engine + UTM persistence (2026-04-28)

> Segundo mini-bloque de Fase 3. Ejecutado programáticamente vía GTM API (5 scopes OAuth).

---

## Acciones ejecutadas

### 1. Pre-flight: revert del workspace draft potencialmente destructivo
El workspace tenía 1 cambio sin publicar — el tag `Pixel Meta - Config` con `firingTriggerId=None` (sin trigger). Si se hubiera publicado, **el Pixel hubiera dejado de dispararse en TODAS las páginas**.

Acción: `revert` API call → tag restaurado al estado live (`firingTriggerId=['2147479553']` All Pages). Workspace quedó con 0 cambios pendientes antes de empezar a construir.

### 2. OAuth scopes ampliados
- Antes: `analytics.readonly` + `tagmanager.readonly` (2 scopes, audit only)
- Después: + `tagmanager.edit.containers` + `tagmanager.edit.containerversions` + `tagmanager.publish` (5 scopes, full setup)
- Re-OAuth flow ejecutado, refresh token nuevo guardado en `keys/google-oauth-token.json`
- Cuando termine el setup de Fase 3 podemos opcionalmente revertir a 2 scopes (otra ronda OAuth, 3 min)

### 3. 17 variables creadas
**11 First-Party Cookie variables:**
- `Cookie - utm_source`, `Cookie - utm_medium`, `Cookie - utm_campaign`, `Cookie - utm_content`, `Cookie - utm_term`
- `Cookie - fbclid`, `Cookie - gclid`, `Cookie - ttclid`, `Cookie - msclkid`
- `Cookie - landing_url`, `Cookie - first_referrer`

**6 Data Layer variables:**
- `DLV - event_id`, `DLV - form_id`, `DLV - click_url`
- `DLV - utm_source_v`, `DLV - utm_medium_v`, `DLV - utm_campaign_v` (versiones inline para events que no leen cookies)

### 4. 3 triggers creados
| Trigger | Tipo | Configuración |
|---|---|---|
| `Trigger - form_submit_lvk` | Custom Event | event = `form_submit_lvk` |
| `Trigger - whatsapp_click` | Custom Event | event = `whatsapp_click` |
| `Trigger - scroll_75` | Scroll Depth | 75% vertical, DOM_READY |

### 5. 6 tags creados (suma 8 total con los 2 viejos)

**Tag 1 — `lvk - Tracking Engine` (Custom HTML, All Pages)**

JavaScript engine que:
- Captura URL params al cargar página → cookies `lvk_*` 30 días + SameSite=Lax + domain padre
- Captura first-touch landing URL + referrer (solo primera visita)
- Auto-populator de hidden fields para SureForms (busca `input[name="utm_*"]` o `input[name$="-utm_*"]` y los rellena con cookie value)
- Listener click delegado: si target `.closest('a[href*="api.whatsapp.com"], a[href*="wa.me"]')` → push `whatsapp_click` a dataLayer con `event_id` único + UTMs + click_url
- Listener submit delegado: si form tiene clase `srfm-form` → genera `event_id` único, lo inyecta como hidden input en el form, push `form_submit_lvk` a dataLayer con event_id + form_id + UTMs

**event_id format:** `<prefix>_<timestamp_ms>_<random_base36>` (ej. `lead_1745847123456_x7k2j8h`). Único por evento, sirve para deduplicación CAPI server-side (cuando arranque mini-bloque 3.4).

**Tag 2 — `GA4 Event - whatsapp_click`**
- Type: GA4 Event (`gaawe`)
- Trigger: form_submit_lvk → wait, esto es whatsapp_click trigger
- Event params: event_id, click_url, utm_source/medium/campaign

**Tag 3 — `GA4 Event - lead (form_submit)`**
- Type: GA4 Event
- Trigger: form_submit_lvk
- Event params: event_id, form_id, utm_source/medium/campaign + fbclid + gclid

**Tag 4 — `GA4 Event - scroll_75`**
- Type: GA4 Event
- Trigger: scroll_75
- Event params: page_url

**Tag 5 — `Meta Pixel - Lead`** (Custom HTML)
```html
<script>
if (typeof fbq === 'function') {
  fbq('track', 'Lead', {}, {eventID: {{DLV - event_id}}});
}
</script>
```
Trigger: form_submit_lvk

**Tag 6 — `Meta Pixel - Contact`** (Custom HTML)
```html
<script>
if (typeof fbq === 'function') {
  fbq('track', 'Contact', {}, {eventID: {{DLV - event_id}}});
}
</script>
```
Trigger: whatsapp_click

### 6. GTM v18 publicada
- Version creada desde workspace 18 con name "v18 - Tracking Engine + UTM persistence + events"
- Notes: descripción del mini-bloque
- Compilado: 21,026 chars de container JS
- Status post-publish: **LIVE** version 18 en `https://www.googletagmanager.com/gtm.js?id=GTM-P55KXDL6`

### 7. Decisión: hidden fields SureForms diferidos a Mini-bloque 3.3
SureForms tiene un block `srfm/hidden` pero su construcción via post_content blocks es compleja (requiere block validation correcta). Decisión:
- HOY: el Tracking Engine inyecta dinámicamente solo `event_id` al submit (suficiente para CAPI dedup)
- MINI-BLOQUE 3.3: definimos schema exacto de hidden fields (utm_*, click_ids, landing_url, first_referrer) cuando wire webhook a ERP — para que el backend reciba todo en POST body
- Mientras tanto: las cookies `lvk_*` están activas, GTM events fluyen con UTM context vía variables, GA4 + Pixel reciben datos de campaña

---

## Validación

### Server-side (verificada)
- ✅ GTM container `GTM-P55KXDL6` carga en HTML
- ✅ SureForms 1569 sigue rendering
- ✅ Turnstile sigue rendering (Mini-bloque 3.1 intacto)
- ✅ Page size 262,314 bytes (similar a antes — overhead mínimo del Engine)
- ✅ GTM live version = 18 (vía API)
- ✅ Tags live = 8 (was 2)
- ✅ Triggers live = 3 (was 0)
- ✅ Variables live = 17 (was 0)

### Browser-side (pendiente — Dario hace cuando quiera con DevTools)
1. Abrir `https://livskin.site/?utm_source=test_validation&utm_campaign=mini3_2&utm_medium=qa`
2. DevTools → Application → Cookies → ver `lvk_utm_source=test_validation` etc
3. Click WhatsApp icon → Network tab → buscar requests a `google-analytics.com/g/collect` con event_name `whatsapp_click`
4. (Después de mini-bloque 3.3) Submit form → verificar event_id en dataLayer + en GA4 Events Manager + (eventually) en Meta Events Manager con dedupe

### Validación end-to-end real (cuando lleguen visitantes orgánicos)
- GA4 Realtime → ver eventos `lead`, `whatsapp_click`, `scroll_75` apareciendo
- Meta Events Manager → ver eventos `Lead` y `Contact` con event_id (cuando lleguen)
- En 1-2 semanas: dashboard Metabase de "leads por source/medium/campaign" basado en GA4 events

---

## Reversibilidad

GTM tiene versioning nativo. Para rollback completo a v17 (estado pre-mini-bloque 3.2):

**UI:** GTM → Versions → seleccionar v17 → click "Publish"

**API:**
```python
tm.accounts().containers().versions().publish(path='accounts/.../versions/17').execute()
```

Tiempo de rollback: <1 minuto. Sin pérdida de configuración (las versiones nuevas no se borran).

---

## Resumen métricas mini-bloque 3.2

| Métrica | Valor |
|---|---|
| Tiempo total | ~70 min |
| OAuth re-authorizations | 1 (de 2 a 5 scopes) |
| API calls a GTM | ~30 (creación + read + publish) |
| Variables creadas | 17 |
| Triggers creados | 3 |
| Tags creados | 6 |
| Total componentes GTM live ahora | 8 tags + 3 triggers + 17 variables |
| Líneas de JS en Tracking Engine | ~95 (con comentarios) |
| ADR cerrado | ADR-0021 |

---

## Lo que viene (Fase 3 mini-bloques pendientes)

- **Mini-bloque 3.3** — Form → ERP webhook (SureForms hidden fields + endpoint `POST /api/leads/intake` + push a Vtiger)
- **Mini-bloque 3.4** — CAPI server-side desde ERP (mismo `event_id` que Tracking Engine para dedup)
- **Mini-bloque 3.5** — Observabilidad (Langfuse + Metabase dashboards funnel + ETL postgres-analytics)

---

**Generado:** Claude Code · 2026-04-28
**Tiempo total mini-bloque 3.2:** ~70 min
**Fase 3 progress:** 2 de 5 mini-bloques completados
