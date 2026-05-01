# ADR-0031 — Landings dedicadas: hosting Cloudflare Pages + sistema de convenciones

**Estado:** ✅ Aprobada (plan acordado 2026-05-01, ejecución en próxima sesión)
**Fecha:** 2026-05-01
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 3 (Mini-bloque 3.6 — NUEVO inserto entre 3.4 y 3.5)
**Workstream:** Tracking + Acquisition

---

## 1. Contexto

Hasta hoy (2026-05-01) Livskin tiene UNA landing: la home de WordPress (`livskin.site`) con form 1569 integrado vía mu-plugin (Mini-bloque 3.3 REWRITE). Funciona para captura orgánica + tráfico directo.

**Necesidad emergente:** las campañas pagas Meta/Google requieren **landings dedicadas por producto/temporada** (botox-mar2026, prp-abr2026, etc.) optimizadas para conversión específica de cada ad set. Razones:
- Quality Score Google Ads + Meta Relevance Score mejoran cuando ad → landing son temáticamente alineadas
- Ad creatives pueden testear copies/visuals distintos pero siempre apuntar a una página optimizada
- Permite A/B testing por landing
- Conversion rate landing dedicada típicamente 2-3x vs landing genérica

**Constraint clave declarado por Dario:** las landings se crearán en **Claude Design** (claude.ai/design — herramienta UI de Anthropic). Cada landing **variará en estructura** (secciones, formularios, botones, headers, footers). NO un template fijo — un **sistema de convenciones reutilizable**.

**Pre-requisitos cumplidos:**
- ✅ Pipeline form → Vtiger → ERP operacional (Mini-bloque 3.3)
- ✅ CAPI server-side via n8n + ADR-0019 cerrado (Mini-bloque 3.4)
- ✅ Cloudflare ya configurado para `livskin.site`
- ✅ Mockup landing Botox subido al repo (`infra/landing-pages/botox-mvp/`)

**Referencias:**
- ADR-0011 v1.1 — schema `leads` + `lead_touchpoints` soporta multi-source attribution
- ADR-0015 — Vtiger es SoT del Lead lifecycle
- ADR-0019 — CAPI emit via n8n (landings dispararán Lead events)
- ADR-0021 — UTMs persistence client-side
- ADR-0030 — file naming conventions (kebab-case, no espacios)
- Memoria `project_n8n_orchestration_layer` — n8n como capa visible

---

## 2. Opciones consideradas

### Opción A — WordPress VPS 1 subdir `/campanas/`

Hostear landings dentro del mismo WP (subdirectories como `livskin.site/campanas/botox/`).

**Pros:**
- Misma infra, mismo SSL, deploy via SCP
- Cookies first-party automáticas (mismo subdomain)

**Contras:**
- Acopla landings con CMS WP (cualquier issue WP afecta landings)
- WP no es óptimo para landings estáticas de alta performance
- Plugins WP pueden conflict con tracking custom
- Deploy manual via SCP (no automatizado)

### Opción B — Cloudflare Pages (free, edge global)

Hosting estático edge en Cloudflare Pages. Subdomain dedicado `campanas.livskin.site`. Deploy via Git push.

**Pros:**
- **Free tier** suficiente (500 builds/mes, bandwidth ilimitado)
- **Edge global** = milisegundos de latencia (crítico para Quality Score + UX mobile)
- Deploy automático via GitHub Actions / native Git integration
- Preview branches para iterar sin afectar producción
- SSL automatic
- Ya tenemos Cloudflare configurado para `livskin.site` (mismo account)

**Contras:**
- Subdomain separado → cookies cross-subdomain requieren `domain=.livskin.site`
- 1 service más a configurar (~20 min setup)

### Opción C — VPS dedicado nuevo

Crear VPS aparte solo para landings.

**Pros:**
- Aislamiento total
- Control completo sobre nginx/static serving

**Contras:**
- ~$6/mes adicional (viola CLAUDE.md principio 8 — cero servicios pagos sin aprobación)
- Setup adicional (snapshot + hardening + backups + monitoring)
- Latencia worse que edge global

### Opción D — Vercel / Netlify free tier

Similar a Cloudflare Pages.

**Pros/Contras:**
- DX excelente
- Pero **vendor lock-in** suave (build system específico)
- Y Cloudflare ya es nuestro DNS/CDN — coherencia mejor

---

## 3. Análisis de tradeoffs

| Dimensión | A: WP subdir | **B: CF Pages** | C: VPS dedicado | D: Vercel/Netlify |
|---|---|---|---|---|
| Costo monetario | $0 | **$0** | $6+/mes | $0 |
| Edge global / latencia | ❌ Solo Frankfurt | ✅ Edge global | ❌ 1 región | ✅ Edge global |
| Performance Quality Score Ads | Medio | **Alto** | Medio | Alto |
| Deploy automation | ❌ Manual SCP | ✅ Git push CI/CD | Setup propio | ✅ Git push |
| Aislamiento de WP issues | ❌ Acoplado | ✅ Separado | ✅ Separado | ✅ Separado |
| Cookies cross-subdomain | ✅ Mismo subdomain | ⚠️ Requiere `domain=.livskin.site` | ⚠️ Idem | ⚠️ Idem |
| Vendor lock-in | Bajo | Bajo (Cloudflare ya usado) | Bajo | Medio |
| Setup time | ~30 min | ~30 min | ~3-4h | ~30 min |
| Reversibilidad | Alta | Alta | Alta | Alta |

---

## 4. Recomendación

**Opción B — Cloudflare Pages.**

Razones:
1. **Costo zero** — coherente con CLAUDE.md principio 8
2. **Edge global** — Quality Score Google Ads + relevance Meta usan métricas de performance
3. **Deploy git push** — workflow consistente con resto del repo
4. **Cloudflare ya usado** — DNS + WAF + Pixel CDN ya allí
5. **Subdomain dedicado** = aislamiento limpio de WP livskin.site

**Tradeoff aceptado:** cookies cross-subdomain → resuelto con `domain=.livskin.site` en cookie set (regla técnica documentada).

---

## 5. Decisión

**Elección:** Opción B — Cloudflare Pages con subdomain `campanas.livskin.site`.

**Aprobada:** 2026-05-01 por Dario.

---

## 6. Sistema de convenciones (clave del ADR)

### 6.1 Estructura de archivos

```
infra/landing-pages/
├── _shared/
│   ├── livskin-tracking.js          ← UN script estándar (yo escribo)
│   ├── conventions.md               ← convenciones HTML para Claude Design
│   └── README.md
├── _template/                       ← landing minimal funcional
│   ├── index.html
│   └── livskin-config.json
├── botox-mvp/                       ← primera landing real
│   ├── index.html                   ← export Claude Design
│   ├── app.jsx, sections.jsx, ...   ← otros archivos del export
│   ├── assets/, fonts/, uploads/
│   └── livskin-config.json          ← config específica
└── ...
```

### 6.2 Convenciones HTML (CONTRATO ENTRE LANDINGS Y SISTEMA)

Cualquier landing creada en Claude Design **DEBE** seguir estas convenciones para integrar:

| Elemento | Convención |
|---|---|
| Form a interceptar | `<form data-livskin-form="true">` o clase `.livskin-form` |
| Field nombre | `<input name="nombre">` o `data-livskin-field="nombre"` |
| Field teléfono | `<input name="phone">` o `data-livskin-field="phone"` |
| Field email | `<input name="email">` |
| Field horario/preferencia | `<input name="horario">` (opcional) |
| Tratamiento target | `<meta name="livskin-treatment" content="Botox">` en `<head>` |
| WhatsApp link | `<a data-livskin-wa="true" href="https://wa.me/...">` |

**Si Claude Design exports siguen estas convenciones (semantic `name` attrs) → cero edits manuales necesarias.**

### 6.3 livskin-config.json schema

```json
{
  "treatment": "Botox",
  "wa_phone": "+51982732978",
  "wa_message_template": "Hola, vengo del aviso de {{treatment}} de Livskin",
  "noindex": true,
  "og": {
    "title": "Botox que se ve natural | Livskin",
    "description": "Aplicación médica en Cusco. Resultados en 7 días.",
    "image": "/uploads/og-image.jpg"
  }
}
```

### 6.4 livskin-tracking.js (especificación)

Comportamiento defensivo (any landing siguiendo convenciones funciona):

```
on DOMContentLoaded:
  1. Parse URL params → cookies lvk_* (domain=.livskin.site, 90 días)
  2. Read meta livskin-treatment → window.livskinContext
  3. Si form data-livskin-form existe:
     a. Inject 11 hidden inputs (silently)
     b. Populate desde URL params + cookies
     c. Attach submit listener
        - Generate UUID event_id
        - Capture fields via name semantic
        - Validate phone (E.164 normalize)
        - POST async a https://flow.livskin.site/webhook/acquisition/form-submit
        - Si POST falla → localStorage queue + retry next visit
        - Después abrir WhatsApp si data-livskin-wa
  4. Si NO form pero data-livskin-wa link existe:
     - Click listener → event_id → fbq('track','Lead') → abrir WhatsApp con event_id en query
  5. Pixel PageView automático con UTMs
  6. Si window.clarity disponible → push tracking events
```

### 6.5 Build process (GitHub Actions CI/CD)

Trigger: push a `infra/landing-pages/<name>/` (o cualquier file ahí).

```yaml
1. Read livskin-config.json
2. Inject <script src="/livskin-tracking.js"></script> al <body> de index.html
3. Inject <meta robots noindex,nofollow> si config.noindex=true
4. Inject OG meta tags desde config.og
5. Reemplazar placeholders {{wa_phone}}, {{treatment}}, etc.
6. Copiar _shared/livskin-tracking.js al root de la landing
7. Lighthouse score check (mobile >70 mandatory, fail si bajo)
8. Deploy a Cloudflare Pages → URL: campanas.livskin.site/<landing-name>/
```

---

## 7. Compliance + checklist mínimo PRE-LANZAMIENTO primer ad real

### Crítico (gating del MVP)

| # | Requisito | Detalle |
|---|---|---|
| 1 | Cookies con `domain=.livskin.site` | Cross-subdomain attribution funciona |
| 2 | Bot protection | Cloudflare Turnstile o reCAPTCHA en form |
| 3 | Compliance médico footer | Privacy policy link + Terms link + disclaimer "resultados varían" |
| 4 | `noindex,nofollow` meta | Landings de campañas pagas NO en Google orgánico |
| 5 | Form retry/queue | localStorage si n8n cae, retry siguiente visita |

### Importante pre-lanzamiento

| # | Requisito | Detalle |
|---|---|---|
| 6 | Lighthouse mobile ≥70 | Quality Score Google Ads |
| 7 | Mobile-first crítico | Test cross-device Safari iOS + Android Chrome |
| 8 | OG meta tags | Preview en WhatsApp/FB sharing |
| 9 | Thank-you state post-submit | Modal/page si WhatsApp no abre |
| 10 | Microsoft Clarity heatmaps | Free, optimization data |
| 11 | WhatsApp number consistency | Centralized en livskin-config.json |

### Diferible (post-launch optimization)

A/B testing infra, versioning campañas, asset optimization, multi-language, form abandon tracking, click-to-call.

### Específicas Meta Ads + categoría health

| # | Tema | Acción |
|---|---|---|
| 19 | Special ad categories Meta | Verificar restricciones health antes de ad creation |
| 20 | Antes/después en ads | Tener creatives alternativos sin antes/después (Meta strict) |
| 21 | URLs `/botox` vs neutras | Decisión Dario — neutral safer pero peor UX |
| 22 | Pixel compliance health | Verificar status en Meta Business |

---

## 8. Decisiones pendientes de Dario (gating del Mini-bloque 3.6)

Antes de re-arrancar 3.6.1:

1. **Privacy policy + terms** — ¿drafts existentes? Si no, hay que escribirlos antes del 1er ad.
2. **WhatsApp phone real productivo** — `+51982732978` (memoria CLAUDE.md) o `+51980727888` (footer landing actual). ⚠️ Mismatch a resolver.
3. **Microsoft Clarity** — ¿OK instalar? (free, anónimo, datos en EU).
4. **URLs estructura** — `/botox` (UX-friendly) vs `/c/01` (Meta-safer). Trade-off real.
5. **Cloudflare Turnstile** — ¿activamos mismo widget que form 1569 en landings?
6. **Cloudflare account access** — ¿podés crear nuevo proyecto Pages + DNS record para `campanas.livskin.site`?
7. **Pixel compliance health** — ¿verificar status del Pixel `4410809639201712` para health category?

Estas 7 decisiones bloquean Sub-paso 3.6.1 (escritura del livskin-tracking.js asume answers).

---

## 9. Consecuencias

### Desbloqueado por esta decisión

- Workflow: Dario crea landing en Claude Design → exporta → repo → CI/CD deploy
- Brand Orchestrator F5 podrá auto-generar landings siguiendo mismas convenciones
- Subir 134 clientes Custom Audience puede coordinarse con primera campaña real (test bonus después de 3.6 cierre)
- Mini-bloque 3.5 Metabase: con data real de campañas, dashboards tienen sentido (vs ejercicio académico)

### Bloqueado / descartado

- Hostear landings en VPS dedicado (descartado por costo)
- WordPress subdir hosting (descartado por acoplamiento + performance)
- Vercel/Netlify (descartado por vendor lock-in soft)
- Template fijo único (descartado por requisito de Dario — variabilidad de cada landing)

### Implementación derivada (Mini-bloque 3.6)

| # | Sub-paso | Estimado |
|---|---|---|
| 3.6.1 | Convenciones markup `_shared/conventions.md` | 30 min |
| 3.6.2 | `livskin-tracking.js` defensivo + UUID + form POST [A1] + Pixel | 90 min |
| 3.6.3 | Schema `livskin-config.json` + parser build | 30 min |
| 3.6.4 | Cloudflare Pages setup + DNS `campanas.livskin.site` | 20 min (gating Cloudflare access tuyo) |
| 3.6.5 | GitHub Actions workflow `deploy-landings.yml` | 60 min |
| 3.6.6 | CORS en [A1] webhook para `*.livskin.site` (n8n config) | 10 min |
| 3.6.7 | Migrar `botox-mvp/` adaptando markup según convenciones + integrar tracking | 45 min |
| 3.6.8 | `_template/` minimal funcional referencia | 30 min |
| 3.6.9 | Runbook `landing-pages-deploy.md` | 30 min |
| 3.6.10 | Smoke test E2E lead via landing → Vtiger → ERP → CAPI | 30 min |

**Total: ~6 horas (1-2 sesiones).**

### Cuándo reabrir esta decisión

- Si CF Pages free tier insuficiente (>500 builds/mes) → considerar Pro plan o cambio
- Si Brand Orchestrator F5 genera >20 landings/mes y volumen rompe cap
- Si Meta cambia requisitos para health category de forma incompatible
- Si performance edge de CF Pages se degrada significativamente
- **Revisión trimestral obligatoria:** 2026-08-01

---

## 10. Changelog

- 2026-05-01 — v1.0 — Creada y aprobada (cierre sesión 2026-05-01, ejecución diferida a próxima sesión)

---

## 11. Cross-references

- ADR-0019 — CAPI tracking architecture (landings disparan Lead events via mismo flow)
- ADR-0021 — UTMs persistence client-side (cookies extendidas con `domain=.livskin.site`)
- ADR-0030 — file naming conventions (kebab-case folder names)
- Memoria `project_n8n_orchestration_layer` — n8n receive form-submit webhook
- Memoria `project_capi_match_quality` — match quality identifiers (event_id propagado)
- Memoria `project_agent_skills_inventory` — landings system es input para Brand Orchestrator F5

**Notas:**
- Inmutable salvo cambios de status.
- 7 decisiones pendientes de Dario están listadas — son gating del Mini-bloque 3.6.
