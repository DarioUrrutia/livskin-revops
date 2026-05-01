# Convenciones HTML para landings — contrato con `livskin-tracking.js`

**Última actualización:** 2026-05-01
**Versión:** 1.0
**Aplica a:** cualquier landing en `infra/landing-pages/<name>/`

---

## Propósito

Toda landing creada (manual en Claude Design, generada por Brand Orchestrator IA en F5+, o cualquier otro origen) **DEBE** seguir estas convenciones HTML para que el sistema de tracking + form capture + Pixel + CAPI funcione automáticamente sin tocar el código de la landing.

`livskin-tracking.js` (script standalone) lee el DOM buscando estas convenciones. Si la landing las respeta → integración automática. Si no → el script intenta detectar mediante fuzzy matching pero puede fallar.

---

## 1. Convenciones obligatorias (CONTRATO ESTRICTO)

### 1.1 Meta tags en `<head>`

```html
<head>
  <!-- ... otros meta tags ... -->

  <!-- OBLIGATORIO — define el tratamiento target de esta landing -->
  <meta name="livskin-treatment" content="Botox">
  <!-- Valores válidos: deben coincidir con livskin-config-master.json → treatments[].label -->

  <!-- OBLIGATORIO — slug de la landing (usado para campaign attribution) -->
  <meta name="livskin-landing-slug" content="botox-mvp">

  <!-- OBLIGATORIO — versión del schema convenciones que respeta esta landing -->
  <meta name="livskin-conventions-version" content="1.0">

  <!-- OBLIGATORIO en producción — bloquea Google indexing -->
  <meta name="robots" content="noindex,nofollow">

  <!-- OBLIGATORIO — OG tags para compartir en social/WhatsApp -->
  <meta property="og:title" content="Botox que se ve natural | Livskin">
  <meta property="og:description" content="Aplicación médica en Cusco. Resultados naturales en 7 días.">
  <meta property="og:image" content="/uploads/og-image.jpg">
  <meta property="og:type" content="website">
</head>
```

### 1.2 Form a interceptar

El form que captura el lead debe tener UNA de estas marcas:

```html
<!-- Opción A — atributo data (preferida) -->
<form data-livskin-form="true">
  <!-- ... fields ... -->
</form>

<!-- Opción B — clase CSS (alternativa, menos limpia) -->
<form class="livskin-form">
  <!-- ... fields ... -->
</form>
```

`livskin-tracking.js` busca en este orden y solo intercepta forms marcados.

### 1.3 Fields semánticos en el form

Los inputs DEBEN usar estos `name` attribute exactos (case-sensitive):

| Campo | `name` attr requerido | Tipo HTML | Required? |
|---|---|---|---|
| Nombre completo | `nombre` | `text` | ✅ |
| Teléfono | `phone` | `tel` | ✅ |
| Email | `email` | `email` | ✅ |
| Tratamiento (si la landing tiene dropdown distinto al meta) | `tratamiento` | `select` | Opcional |
| Horario preferido | `horario` | `text`/`select` | Opcional |
| Mensaje libre | `mensaje` | `textarea` | Opcional |
| **Consent marketing checkbox** | `consent_marketing` | `checkbox` | ✅ obligatorio |

#### Ejemplo correcto

```html
<form data-livskin-form="true">
  <input name="nombre" type="text" required placeholder="Tu nombre completo" />
  <input name="phone" type="tel" required placeholder="+51 999 000 000" />
  <input name="email" type="email" required placeholder="tu@email.com" />

  <select name="tratamiento">
    <option value="Botox">Botox</option>
    <option value="PRP">PRP</option>
  </select>

  <label>
    <input name="consent_marketing" type="checkbox" required />
    Acepto la <a href="/privacy" target="_blank">política de privacidad</a> y autorizo el tratamiento de mis datos.
  </label>

  <button type="submit">Reservar consulta</button>
</form>
```

#### Si tu landing tiene fields adicionales (ej: edad, dirección)

Pueden existir libremente. El script los IGNORA en el payload a [A1] webhook (n8n no los espera). Si querés que viajen al ERP, ver sección 4 (extension).

### 1.4 WhatsApp links

```html
<!-- OBLIGATORIO — link a WhatsApp marcado para tracking -->
<a data-livskin-wa="true"
   href="https://wa.me/51980727888?text=Hola,%20vengo%20del%20aviso%20de%20Botox"
   target="_blank">
  Chatear por WhatsApp
</a>
```

`livskin-tracking.js`:
- Click listener → genera `event_id` UUID
- Fire `fbq('track', 'Lead', { event_id })` (Pixel client-side)
- POST a `[A1]` webhook con datos mínimos (sin form fields, solo phone WhatsApp + UTMs)
- Después abre WhatsApp con event_id agregado a la URL como `&event_id=<uuid>`

### 1.5 Banner de cookies (consent management)

```html
<!-- OBLIGATORIO — placeholder donde livskin-tracking.js inyecta el banner -->
<div id="livskin-cookie-banner" data-livskin-banner="true"></div>
```

El script inyecta el banner si:
- No existe cookie `lvk_consent` (primera visita)
- Cookie `lvk_consent` tiene valor distinto a `accepted_all` o `rejected_all`

---

## 2. Convenciones recomendadas (no obligatorias pero highly recommended)

### 2.1 Estructura semántica

```html
<body>
  <header>...</header>
  <main>
    <section id="hero">...</section>
    <section id="benefits">...</section>
    <section id="testimonials">...</section>
    <section id="booking">  <!-- form va acá -->
      <form data-livskin-form="true">...</form>
    </section>
  </main>
  <footer>
    <a href="/privacy">Privacidad</a>
    <a href="/terms">Términos</a>
    <a href="/cookies">Cookies</a>
  </footer>
</body>
```

### 2.2 Footer obligatorio (compliance Meta Ads)

```html
<footer>
  <div>© 2026 Livskin · Cusco, Perú</div>
  <nav>
    <a href="/privacy">Política de Privacidad</a>
    <a href="/terms">Términos de Uso</a>
    <a href="/cookies">Política de Cookies</a>
  </nav>
  <p class="disclaimer">
    Información de carácter informativo, no reemplaza consulta médica presencial.
    Resultados varían entre pacientes.
  </p>
</footer>
```

### 2.3 Antes/después con disclaimer

```html
<section class="before-after">
  <h2>Resultados reales</h2>
  <img src="/uploads/before.jpg" alt="Antes del tratamiento" />
  <img src="/uploads/after.jpg" alt="Después de 14 días" />
  <p class="disclaimer">
    Resultados particulares de pacientes con consentimiento firmado.
    No representan resultados garantizados — varían según factores individuales.
  </p>
</section>
```

---

## 3. Configuración por landing (`livskin-config.json`)

Cada landing debe tener un `livskin-config.json` en su carpeta con esta estructura:

```json
{
  "slug": "botox-mvp",
  "treatment_canonical_label": "Botox",
  "wa_phone_e164": "+51980727888",
  "wa_message_template": "Hola, vengo del aviso de {{treatment}} de Livskin",
  "noindex": true,
  "og": {
    "title": "Botox que se ve natural | Livskin",
    "description": "Aplicación médica en Cusco. Resultados naturales en 7 días.",
    "image": "/uploads/og-image.jpg"
  },
  "lighthouse_target_mobile": 70,
  "consent_required_for_marketing_cookies": true,
  "_meta": {
    "created": "2026-05-01",
    "campaign_period": "2026-05-2026-08",
    "owner": "Brand Orchestrator (cuando F5 esté activo)"
  }
}
```

El **build process** (GitHub Actions) lee este archivo e inyecta valores en el HTML:
- Reemplaza `{{wa_phone}}` en hrefs WhatsApp con `wa_phone_e164`
- Reemplaza `{{treatment}}` en `wa_message_template`
- Inyecta meta tags OG desde `og.*`
- Aplica `noindex` si `true`
- Falla deploy si Lighthouse mobile < `lighthouse_target_mobile`

---

## 4. Cómo extender (campos custom no estándar)

Si tu landing necesita un campo NO estándar (ej: "edad" para landings de tratamientos restringidos por edad):

```html
<input name="edad"
       type="number"
       data-livskin-extra="true"
       data-livskin-erp-field="edad" />
```

El atributo `data-livskin-extra="true"` indica al script que debe incluirlo en el payload bajo `extra_fields.<name>`. El backend [A1] preserva esos en `lead_touchpoints.form_data_json` (JSONB).

---

## 5. Lo que el script `livskin-tracking.js` HACE automáticamente

Si tu landing respeta las convenciones de arriba, el script hace lo siguiente sin que toques nada:

### Al cargar la página:
1. Lee URL params (`utm_source`, `fbclid`, `gclid`, etc.)
2. Setea cookies `lvk_*` con `domain=.livskin.site` (cross-subdomain) por 90 días
3. Si URL no tiene params, lee cookies existentes (multi-session attribution)
4. Lee cookies `_fbc` y `_ga` (set automáticamente por Pixel y GA)
5. Captura `window.location.href` → `lvk_landing_url`
6. Lee meta `livskin-treatment` → contexto del tratamiento
7. Inyecta banner de consent si no hay decisión previa
8. Si user accepta cookies marketing: fire `fbq('track', 'PageView')` + GA pageview

### Al submit del form (form con `data-livskin-form`):
1. Genera `event_id` UUID v4
2. Captura todos los fields semantic (`nombre`, `phone`, `email`, etc.)
3. Captura `consent_marketing` checkbox
4. Captura extras (`data-livskin-extra="true"`)
5. Construye payload completo (user fields + UTMs + cookies + IP via server + UA)
6. POST async a `https://flow.livskin.site/webhook/acquisition/form-submit`
7. Si user accepta cookies marketing:
   - Fire `fbq('track', 'Lead', { event_id, content_name: treatment })` client-side
8. Si POST falla: localStorage queue → retry siguiente visita
9. Después abre WhatsApp si el botón submit es WA, o muestra success state

### Al click en link `data-livskin-wa`:
1. Genera `event_id` UUID
2. Fire `fbq('track', 'Lead', { event_id })` si consent
3. POST mínimo a `[A1]` (sin form fields, solo phone WA + UTMs)
4. Append `event_id` a la URL del WhatsApp link

---

## 6. Lo que el script NO HACE (para que vos sepas)

- ❌ NO captura datos sin consent del user (excepto cookies esenciales)
- ❌ NO trackea cross-domain (solo livskin.site + subdominios)
- ❌ NO hashea PII en el cliente (eso lo hace n8n [G3] en server-side)
- ❌ NO valida formato del phone profundamente (eso lo hace [A1] workflow)
- ❌ NO modifica el DOM más allá de inyectar banner de consent
- ❌ NO interfiere con frameworks (React, Vue, etc.) — usa event listeners pasivos

---

## 7. Checklist pre-deploy de cualquier landing nueva

Antes de hacer git push de una landing nueva a `infra/landing-pages/<name>/`:

```
[ ] index.html tiene meta livskin-treatment + livskin-landing-slug
[ ] index.html tiene meta robots noindex,nofollow (en producción)
[ ] index.html tiene OG meta tags válidos
[ ] Form tiene data-livskin-form="true"
[ ] Inputs usan name semántico (nombre, phone, email)
[ ] Checkbox consent_marketing presente y required
[ ] Footer linkea privacy + terms + cookies
[ ] Disclaimer "resultados varían" en sección antes/después
[ ] WhatsApp links tienen data-livskin-wa="true"
[ ] livskin-config.json válido en la carpeta
[ ] og:image existe en uploads/
[ ] Lighthouse mobile score ≥ 70 (verificado local con Lighthouse CLI)
[ ] Test browser: form submit funciona en local con stub server [A1]
```

GitHub Actions valida automáticamente los items técnicos al deploy.

---

## 8. Versionado de estas convenciones

Si en el futuro estas convenciones cambian (ej: agregar nuevo field obligatorio):

- **v1.x** — cambios backward-compatible (agregar opciones, no romper)
- **v2.0** — breaking changes (rename fields, etc.)

Cada landing declara su `livskin-conventions-version` en meta. El script `livskin-tracking.js` puede comportarse diferente según versión.

---

## 9. Cross-references

- [`livskin-tracking.js`](livskin-tracking.js) — script que consume estas convenciones (Mini-bloque 3.6.2)
- [`livskin-config.json` schema](livskin-config-schema.json) — schema validador (Mini-bloque 3.6.3)
- [`/`livskin-config-master.json`](../../../livskin-config-master.json) — datos canónicos del negocio
- [Privacy policy](../../../docs/legal/privacy-policy.md) — texto al que linkea el footer
- [Cookie policy](../../../docs/legal/cookie-policy.md) — texto al que linkea el banner consent
- [ADR-0031](../../../docs/decisiones/0031-landings-dedicadas-cloudflare-pages-y-sistema-convenciones.md) — decisión arquitectónica
- [ADR-0019](../../../docs/decisiones/0019-arquitectura-tracking-2-capas-pixel-capi.md) — CAPI tracking architecture

---

## 10. Cuándo reabrir estas convenciones

- Nuevo tipo de campo común (ej: agregamos "fecha de cumpleaños" a múltiples landings) → considerar agregar al estándar
- Nuevo canal (TikTok, Snap, LinkedIn) requiere meta tag adicional
- Brand Orchestrator F5 detecta patrones que sugieren cambio
- Update mayor de Pixel Meta o Google Tag

**Las convenciones son un contrato — modificar requiere version bump + plan de migración para landings existentes.**
