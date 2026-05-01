# Sesión 2026-05-01 — Mini-bloque 3.4 CAPI completo + Plan Mini-bloque 3.6 Landings

**Duración:** sesión muy larga (continuación del cierre 3.3 REWRITE de la mañana → 3.4 + plan 3.6 en la tarde/noche).
**Fase:** 3 (Tracking).
**Resultado:** **Mini-bloque 3.4 ✅ COMPLETO + Mini-bloque 3.6 (Landings dedicadas) PLANEADO con ADR-0031 cerrado.**

---

## Contexto inicial

Sesión arranca tras cierre exitoso del Mini-bloque 3.3 REWRITE (commit `5de79fb`). Pipeline form WP → Vtiger → ERP operacional con first-touch attribution preservada.

Próximo paso planeado: Mini-bloque 3.4 (CAPI server-side desde ERP/n8n).

---

## Qué se hizo

### Mini-bloque 3.4 — CAPI server-side via n8n + ADR-0019 (commit `c4dd8a8`)

**Pre-flight cross-system completo:**
- 6 memorias críticas releídas literal
- Query brain pgvector con keywords CAPI + n8n
- Plan citado aprobado por Dario antes del primer commit

**Componentes construidos:**

1. **Token Meta CAPI generado + verificado** (~20 min)
   - Vía Events Manager → Pixel 4410809639201712 → Settings → Conversions API → "Configurar integración directa con Dataset Quality API" → Generate Access Token
   - Token guardado SOLO en `keys/.env.integrations` (gitignored)
   - Verificación API: `/me` returns System User ID `122111483606982522`
   - Verificación visual UI Meta: test event apareció con match quality alto (5 identifiers detectados — email + phone + IP + UA + fbc)
   - **Cero App Review formal requerida** (descartando preocupación inicial)
   - Pixel legacy `670708374433840` desmarcado intencionalmente del Quality API setup (evita binding permanente)

2. **ADR-0019 v1.0 escrito + aprobado** — Tracking architecture 2-capas Pixel + CAPI
   - Decisión: Opción B (ERP → n8n → Meta), descartando A (directo) y C (Meta-enabled hosted)
   - Razón Opción B: visualidad n8n + extensibilidad cross-platform + no health category restrictions de Opción C
   - Eventos canónicos definidos: Lead, Schedule (futuro), Purchase (futuro)
   - event_id deduplicación client+server obligatoria

3. **Backend ERP** — `services/capi_emitter_service.py`
   - 13 tests TDD pasan (validation, payload, feature flag, audit log)
   - Hook auto-emit en `/api/leads/sync-from-vtiger` CREATE
   - Non-blocking: si n8n cae, audit log + return ok=False (sin raise)
   - Feature flag `capi_emit_enabled` (False en tests, True en prod)
   - audit_service: + `tracking.capi_event_emitted` + `tracking.capi_event_failed` en KNOWN_ACTIONS
   - Coverage global 79.68% (251 tests pasan, +13 nuevos)

4. **n8n Workflow [G3] CAPI emit**
   - 5 nodos: webhook → Code (hash SHA-256 PII) → HTTP POST Meta → Code response → respond
   - Hashing: email (lowercase + trim), phone (digits only), external_id (trim)
   - Activo en `flow.livskin.site/webhook/growth/capi-emit`
   - Smoke test directo: Meta returns `events_received: 1` + fbtrace_id

5. **Validación E2E completa**
   - POST /api/leads/sync-from-vtiger con event_id
   - ERP creó lead 10 (LIVLEAD0001)
   - Hook capi_emitter disparó automáticamente
   - n8n [G3] hasheó PII + POSTeó a Meta
   - Audit log entry: `tracking.capi_event_emitted` ✅

**Aprendizajes técnicos registrados:**
- Gunicorn prefork: `docker cp` + restart container needed para reload
- `requests.post` testing: mockable con `unittest.mock.patch`
- conftest.py: env var override per test session (CAPI disabled global, override per test)

### PIVOT estratégico — Mini-bloque 3.6 (Landings) ANTES de 3.5 (Metabase)

**Trigger:** Dario subió mockup de landing creado en Claude Design al folder `landing page/` del repo + propuso usar Claude Design como herramienta para crear landings dedicadas para campañas Meta/Google pagas.

**Análisis del mockup actual** (`infra/landing-pages/botox-mvp/` — movido a folder convention):
- Standalone HTML + React via CDN (Babel runtime in-browser)
- Booking section con form fields nombre/email/phone/horario
- Submit del form → solo abre WhatsApp prepopulado (NO captura como lead)
- 0 tracking integrado (sin GTM, sin Pixel, sin event_id, sin UTM persistence)
- WhatsApp phone hardcoded `+51980727888` (mismatch con +51982732978 productivo)

**Decisión PIVOT (justificada por Dario "seguir"):**
1. Mini-bloque 3.5 Metabase **diferido** — sin data real de campañas, dashboards son ejercicio académico
2. Mini-bloque 3.6 Landings dedicadas **PRIORIDAD** — sin landings, no podemos correr campañas Meta pagas
3. Flow correcto: Landings → mini campaña test → Metabase con data real

**ADR-0031 escrito + aprobado** — Landings hosting Cloudflare Pages + sistema de convenciones
- Hosting: Cloudflare Pages (free, edge global, deploy git push)
- Subdomain: `campanas.livskin.site`
- Sistema NO un template fijo (Dario clarificó variabilidad de cada landing) — un **sistema de convenciones HTML markup** que cualquier landing nueva debe seguir
- Estructura: `infra/landing-pages/<name>/` + `_shared/livskin-tracking.js` reutilizable + `_template/`
- 7 decisiones pendientes de Dario gatean inicio del 3.6.1 (privacy policy, phone real, Clarity, URLs, Turnstile, Cloudflare access, Pixel health compliance)

**Análisis exhaustivo de gaps detectados** (24 categorías):
- 🔴 Críticos: cookies cross-subdomain, bot protection, compliance médico, noindex, form retry queue
- 🟡 Importantes: Lighthouse score, mobile-first, OG meta tags, thank-you state, Microsoft Clarity, phone consistency
- 🟢 Diferibles: A/B testing infra, versioning, asset optimization, multi-language, etc.
- Específicos Meta health category: ad restrictions, antes/después policy, URLs neutras, Pixel compliance status

---

## Decisiones tomadas

### 1. CAPI emit vía n8n (Opción B) en ADR-0019

ERP → n8n [G3] → Meta. Razones: visualidad para Dario + extensibilidad cross-platform (Google CAPI / TikTok futuro) + bypass health restrictions del Meta-hosted CAPI. Tradeoff: ~+300ms latencia (no crítico).

### 2. Pixel canónico único `4410809639201712`

Pixel legacy `670708374433840` a archivar. Backlog item subido a urgencia post-Dataset Quality API setup (evitar token bind permanente).

### 3. PIVOT 3.6 antes de 3.5

Razón: data flow → infra. Sin landings dedicadas, las campañas pagas no pueden arrancar. Sin campañas, Metabase es ejercicio académico.

### 4. Hosting Cloudflare Pages para landings

Free + edge global + deploy git push + ya usamos Cloudflare. Razones detalladas en ADR-0031.

### 5. Sistema de convenciones, NO template fijo

Cada landing varía en estructura. La INTEGRACIÓN con tracking es estándar via convenciones HTML markup (`name="phone"`, `data-livskin-form`, etc.). El JS standalone `livskin-tracking.js` es defensivo — funciona con cualquier landing siguiendo convenciones.

---

## Hallazgos relevantes

### CAPI standalone NO requiere App Review

Confirmado vía 6 fuentes oficiales + UI Meta. Diferente al issue de 2026-04-27 que era para `ads_read` (audit programático).

### Meta cambió "Conversions API" como casos de uso

Lo que decía Dario sobre Meta cambiando — confirmado. Pero CAPI específicamente está disponible vía path "Dataset Quality API" en Events Manager. NO requiere review.

### Meta-enabled CAPI (lanzado Apr 15 2026)

Producto NUEVO de Meta para "one-click CAPI hosted". Evaluado y descartado por:
- Restricciones health category casi seguras
- No documenta integración con backend ERP custom
- No menciona custom event_id support → rompería deduplicación con Pixel client-side existente

### SureForms NO tiene block "hidden" nativo

Confirmado en código fuente del plugin. mu-plugin actual inyecta hidden inputs via JS — pattern reusable para landings standalone.

### Claude Design exports

- HTML standalone + React via CDN (Babel runtime)
- Cero build process (acceptable MVP, optimizable F5+)
- Tweaks panel solo runtime (no persiste en build final)
- Folder ya copiado a `infra/landing-pages/botox-mvp/`

### Phone mismatch detectado

Footer landing dice `+51980727888`, CLAUDE.md memoria dice `+51982732978`. Backlog item para resolver.

---

## Lo que queda pendiente (próxima sesión)

### Inmediato — pre-arranque Mini-bloque 3.6

Decisiones tuyas pendientes (7 total — gating del 3.6.1):

1. **Privacy policy + terms** — ¿drafts existentes? Si no, hay que escribirlos antes del 1er ad real (puede ser sub-paso 3.6.0 = "Compliance docs writing", ~1h)
2. **WhatsApp phone real productivo** — `+51982732978` o `+51980727888`
3. **Microsoft Clarity OK?** (free, datos EU)
4. **URLs estructura** — `/botox` vs `/c/01` (Meta health policy trade-off)
5. **Cloudflare Turnstile en landings** — sí/no
6. **Cloudflare account access** — confirmar que podés crear proyecto Pages + DNS record `campanas.livskin.site`
7. **Pixel compliance status** — verificar en Meta Business si Pixel autorizado para health category

### Sub-pasos del Mini-bloque 3.6 (~6 horas total)

| # | Acción | Estimado |
|---|---|---|
| 3.6.1 | `_shared/conventions.md` (markup HTML que Claude Design debe seguir) | 30 min |
| 3.6.2 | `livskin-tracking.js` defensivo + UUID + form POST [A1] + Pixel | 90 min |
| 3.6.3 | Schema `livskin-config.json` + parser build | 30 min |
| 3.6.4 | Cloudflare Pages setup + DNS `campanas.livskin.site` | 20 min |
| 3.6.5 | GitHub Actions workflow `deploy-landings.yml` con inyección script | 60 min |
| 3.6.6 | CORS en [A1] webhook para `*.livskin.site` (n8n config) | 10 min |
| 3.6.7 | Migrar `botox-mvp/` adaptando markup según convenciones + integrar tracking | 45 min |
| 3.6.8 | `_template/` minimal funcional referencia | 30 min |
| 3.6.9 | Runbook `docs/runbooks/landing-pages-deploy.md` | 30 min |
| 3.6.10 | Smoke test E2E lead via landing → Vtiger → ERP → CAPI | 30 min |

### Después del 3.6 — Mini-bloque 3.5 Metabase (diferido)

| # | Acción | Estimado |
|---|---|---|
| 3.5.1 | Metabase setup wizard + DB connection livskin_erp via analytics_etl_reader | 30 min |
| 3.5.2 | 4 dashboards SQL (leads diarios, funnel, cohort attribution, CAC) | 4-6h |
| 3.5.3 | Fix sensores cross-VPS (VPS 2 unhealthy + VPS 1 Docker WARNING + cron recolector) | 2-3h |
| 3.5.4 | Brain re-indexing automatic (webhook GitHub + cron daily fallback) | 1-2h |
| 3.5.5 | Alertas n8n (disk + RAM + costos agentes + capi_failed) | 2-3h |

### Bonus pendientes

- **Subir 134 clientes Custom Audience** (script Python + SHA-256 upload) — coordinable con primera campaña real
- **Pixel legacy archivar** `670708374433840` — 1 min en Meta UI

---

## Próxima sesión propuesta

**Arrancar Mini-bloque 3.6 — Landings dedicadas.**

**Pre-flight obligatorio antes del primer commit:**
1. Releer 5 memorias 🔥 CRÍTICAS literal
2. Query brain pgvector con keywords "landing pages tracking attribution Cloudflare Pages"
3. Citar ADR-0019 + ADR-0031 + ADR-0021 en plan inicial
4. Plan citado aprobado por Dario antes de tocar código

**Antes de 3.6.1, las 7 decisiones pendientes de Dario deben estar resueltas.**

Si Dario quiere optimizar tiempo: puede pre-resolver decisiones (especialmente 1, 2, 6) mientras yo no estoy.

---

## Estado general del proyecto al cierre

### Fase 3 progress
| Mini-bloque | Estado |
|---|---|
| 3.1 Cleanup VPS 1 | ✅ |
| 3.2 GTM Tracking Engine | ✅ |
| 3.3 REWRITE Form→Vtiger→ERP pipeline | ✅ |
| 3.4 CAPI server-side via n8n | ✅ |
| **3.6 Landings dedicadas (NUEVO inserto)** | ⏳ próxima sesión |
| 3.5 Observabilidad + Metabase (DIFERIDO) | ⏳ después de 3.6 |

**80% Fase 3 completada** (4 de 5 mini-bloques originales) + 3.6 nuevo agregado.

### Commits del día (sesión multi-fase)

**Mañana (cierre 3.3 REWRITE):**
- `5de79fb` — docs+feat: cierre Mini-bloque 3.3 REWRITE (mu-plugin + runbooks + session log)

**Tarde (Mini-bloque 3.4):**
- `c4dd8a8` — feat(fase3): Mini-bloque 3.4 — CAPI server-side via n8n + ADR-0019

**Final (cierre + plan 3.6):**
- (commit pendiente este cierre) — docs+plan: cierre 2026-05-01 + ADR-0031 landings + plan 3.6

---

## Referencias

- ADR-0019 — CAPI tracking architecture (este Mini-bloque 3.4)
- ADR-0031 — Landings hosting CF Pages + sistema convenciones (NUEVO HOY — plan 3.6)
- `infra/docker/erp-flask/services/capi_emitter_service.py` — CAPI emit service
- `infra/n8n/workflows/G-growth/g3-capi-emit-to-meta.{md,json}` — workflow [G3]
- `infra/landing-pages/botox-mvp/` — primer mockup landing (a integrar en 3.6.7)
- Token CAPI Meta + META_PIXEL_ID en `keys/.env.integrations` (gitignored)

**Hito clave:** pipeline tracking completo Pixel client + CAPI server validado. Lead via cualquier path (form WP, landing futura) → Vtiger → ERP → CAPI Meta con event_id deduplicado.
