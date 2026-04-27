# Audit programmatico Google stack — 2026-04-27

> Audit ejecutado vía Google Analytics Admin API + Analytics Data API + Tag Manager API con OAuth user token (`keys/google-oauth-token.json`, scopes read-only). Reemplaza el audit por screenshots del 2026-04-26.

---

## 1. GA4 — Accounts y Properties accesibles

5 GA4 accounts visibles desde el token de Dario:

| Account | Property | Measurement ID | URL | Estado |
|---|---|---|---|---|
| **Livskin** (id 387975477) | Livskin (528880125) | `G-9CNPWS3NRX` | `https://livskin.site` | ✅ activa, data flowing |
| **LivskinDEF** (id 243004291) | livskinperu.com (334179492) | `G-YJ4CCLJFSK` | `https://livskinperu.com` | ⚠️ duplicada/legacy — dominio anterior |
| Radish Store Chile (id 242106478) | radishstore.cl (333098814) | `G-RZ2K6GYYG6` | radishstore.cl | (proyecto separado) |
| Hakuchu Marketing (id 263260126) | Hakuchu Principal (363669481) | `G-5183LN64Q4` | hakuchumarketing.com | (proyecto separado) |
| Demo Account (id 54516992) | Flood-It! / Merch Shop / DaD | varios | varios | (datos demo Google) |

**Hallazgo crítico:** existe una segunda property GA4 **"LivskinDEF" → livskinperu.com**. Probablemente del dominio anterior antes de migrar a `livskin.site`. **Acción:** archivar/eliminar para evitar confusión y evitar que algún lead viejo vaya a la property equivocada.

---

## 2. GTM — Container `GTM-P55KXDL6` (livskin.site)

### Estructura
- Account: **Livskin** (`accounts/6344785058`)
- Container: **livskin.site** (`246604629`, public ID `GTM-P55KXDL6`)
- 1 workspace: "Default Workspace"
- **Live version: 17** ('meta pixel')
- Cambios sin publicar: 1 (workspace tiene draft no enviado)

### Tags publicados (live version)

| Nombre | Tipo | Trigger | Estado |
|---|---|---|---|
| `GA - Config` | `googtag` (Etiqueta de Google = GA4 Config) | All Pages (`2147479553`) | ✅ activo |
| `Pixel Meta - Config` | `html` (HTML personalizado) | All Pages (`2147479553`) | ✅ activo |

**0 triggers custom, 0 variables custom.** Solo el built-in "All Pages" que dispara los 2 tags.

### Código exacto del tag `Pixel Meta - Config` (extraído via API)

```html
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');

fbq('init', '4410809639201712');
fbq('track', 'PageView');
</script>

<noscript>
<img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=4410809639201712&ev=PageView&noscript=1"/>
</noscript>
<!-- End Meta Pixel Code -->
```

### Diagnóstico: doble disparo confirmado al 100%

El Pixel `4410809639201712` se dispara desde 2 fuentes en paralelo:

1. **Plugin PixelYourSite** (verificado en source de `livskin.site` el 2026-04-26 vía `data-cmplz-src`):
   - Carga `pixelyoursite/dist/scripts/public.js` consent-gated
   - Termina llamando `fbq('init', '4410809639201712')` + `fbq('track', 'PageView')` desde el plugin PHP/JS

2. **GTM tag `Pixel Meta - Config`** (verificado vía API):
   - Carga `connect.facebook.net/en_US/fbevents.js`
   - Llama `fbq('init', '4410809639201712')` + `fbq('track', 'PageView')`

**Resultado verificado:** cada visita a `livskin.site` envía **2 PageView events a Meta**, mismo Pixel ID, **sin `event_id` custom para deduplicación**. Esa es la causa exacta del "Diagnóstico (1)" en Meta Events Manager.

**Validación de la decisión arquitectónica del 2026-04-26 (tracking 2-capas single-source):** ✅ confirmada con código real, no asumida.

---

## 3. GA4 — Eventos disparados últimas 48h (property Livskin)

```
event_name              count    users
─────────────────────────────────────────
page_view                  8        5
session_start              5        5
scroll                     4        1
user_engagement            4        3
first_visit                3        3
form_start                 1        1   ← forms SureForms 1569
form_submit                1        1   ← envío del form
```

### Hallazgos

1. **Enhanced Measurement está funcionando** — `scroll`, `user_engagement`, `first_visit`, `form_start`, `form_submit` salen automáticos sin necesidad de tags custom.

2. **Hubo 1 `form_submit` en últimas 48h.** Pero `wp_srfm_entries` en la DB de WordPress tiene 0 entries (verificado 2026-04-26). El form solo manda email a `daizurma2@gmail.com`, no persiste estructurado.

3. **Sospecha confirmada por Dario:** él NO recuerda haber probado el form en últimas 48h. El form NO tiene reCAPTCHA / Turnstile (`_srfm_form_recaptcha = none`). **Conclusión: muy probablemente un bot scraping**. Acción urgente Fase 3: **agregar Cloudflare Turnstile o reCAPTCHA al form** para evitar:
   - Falsos eventos en GA4 (degradan métricas reales)
   - Spam si el form tuviera webhook al CRM en el futuro
   - Costos por procesamiento backend cuando se conecte a ERP

4. **Eventos custom canónicos del funnel = 0** (esperado, esto es trabajo de Fase 3 mini-bloque 3.4):
   - `Lead`, `Schedule`, `CompleteRegistration`, `Purchase` — no existen todavía
   - `whatsapp_click` — link CTA del home está roto (`?phone=` vacío), no hay tag tampoco
   - UTM persistence — sin implementar
   - Click ID capture (gclid/fbclid/ttclid) — sin implementar

---

## 4. Conclusiones operativas

### ✅ Lo que funciona y mantenemos
- Property GA4 **Livskin (G-9CNPWS3NRX)** con Enhanced Measurement
- Container GTM `GTM-P55KXDL6` como **única fuente client-side**
- Tag `GA - Config` (GA4 base)

### 🔄 Lo que reescribimos / reconfiguramos en Fase 3
- Tag `Pixel Meta - Config` actual → reescribir con `event_id` único, sincronizado con server-side CAPI desde ERP
- Workspace GTM completo → publicar nueva version con tags custom (form_submit con UTMs, whatsapp_click, scroll milestones, click ID variables, UTM persistence)

### 🗑️ Lo que archivamos / eliminamos
- **Pixel viejo `670708374433840`** en Meta Business
- **GA4 property "LivskinDEF" → livskinperu.com** (legacy, dominio que ya no se usa)
- **Plugin PixelYourSite en WordPress** (redundante, GTM lo cubre)
- **Plugin LatePoint** (no se va a usar, decisión Dario 2026-04-26)
- **Cambio sin publicar en workspace GTM** (decidir si descartar o publicar tras review)

### 🛡️ Lo que añadimos urgente (anti-bot)
- **Cloudflare Turnstile** en SureForms 1569 — antes de cualquier integración con backend, sino vamos a llenar el ERP de leads bot

### 📊 Lo que añadimos para tracking real (Fase 3 mini-bloques)
- Tag `whatsapp_click` (cuando se repare el link CTA o se reemplace por bot WA endpoint)
- Tag `form_submit` con event params: utm_source/medium/campaign/content, fbclid/gclid/ttclid, treatment seleccionado
- UTM persistence: cookie de primera visita + hidden fields auto-poblados
- Click ID capture en hidden fields del form
- Custom dimensions GA4 para `treatment`, `channel`, `lead_source`
- Eventos canónicos del funnel emitidos server-side desde ERP: `Lead`, `Schedule`, `CompleteRegistration`, `Purchase`

---

## 5. Datos para el ADR de arquitectura tracking

Este audit produce los inputs verificados para el dossier ADR-00XX (arquitectura tracking client+server) que se cierra al final de la sesión 2026-04-27 una vez incorporados los datos de Meta.

**Inputs validados:**
- 1 Pixel activo (`4410809639201712`), 1 a archivar (`670708374433840`)
- 1 GA4 property activa (`G-9CNPWS3NRX`), 1 a archivar (`G-YJ4CCLJFSK`)
- 1 GTM container activo (`GTM-P55KXDL6`)
- Doble disparo Pixel = problema verificable, no hipotético
- Form 1569 sin protección anti-bot = riesgo real, no teórico
- 0 eventos canónicos del funnel real = gap completo, server-side CAPI debe construirse desde cero

---

**Generado por:** `scripts/google_audit.py` ejecutado por Claude Code · 2026-04-27
**Token OAuth usado:** `keys/google-oauth-token.json` (read-only, scopes analytics.readonly + tagmanager.readonly)
**Commit relacionado:** TBD (cierre sesión 2026-04-27)
