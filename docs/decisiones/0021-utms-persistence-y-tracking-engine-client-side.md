# ADR-0021 — UTMs persistence + Tracking Engine client-side

**Estado:** ✅ Aprobada
**Fecha:** 2026-04-28
**Autor propuesta:** Claude Code
**Decisor final:** Dario Urrutia
**Fase del roadmap:** Fase 3 — Tracking + observabilidad
**Workstream:** Tracking

---

## 1. Contexto

Hasta el 2026-04-28, el sitio `livskin.site` capturaba PageViews en GA4 y Meta Pixel via GTM, pero **sin contexto de origen del visitante**. Una persona llegaba al sitio, llenaba el form, y la métrica era "anonymous PageView + form_submit por Enhanced Measurement". Cero atribución a canal/campaña.

**Problema concreto:**
- ¿Vino de Instagram orgánico, ad pagado de Meta, búsqueda Google, link en bio? → No sabíamos
- ¿Cuál ad/campaña convirtió? → No sabíamos
- ¿Qué creativos performan? → Imposible medir
- Para Conversions API server-side (Mini-bloque 3.4) necesitamos `event_id` único por evento, sincronizable cliente-server, para deduplicar → No teníamos

**Audit del 2026-04-27 confirmó con código real:**
- GTM v17 tenía SOLO `GA - Config` (GA4 base) + `Pixel Meta - Config` (PageView)
- Cero variables, cero triggers custom, cero captura de UTMs ni click_ids
- Workspace draft tenía un cambio sin publicar potencialmente destructivo (trigger del Pixel removido)

**Forzantes de la decisión:**
- Fase 3 mini-bloque 3.4 (CAPI server-side) requiere `event_id` cliente+server consistente
- Fase 4 (Conversation Agent) necesita atribución por canal en `lead.source`
- Fase 5 (Acquisition Agent) necesita data de `creative_id` y `campaign_id` para optimizar
- Sin UTMs persistence → cualquier inversión en tracking server-side es ciega

Referencias:
- Master plan § 11.5 Fase 3
- Audit Google [docs/audits/audit-google-stack-2026-04-27.md](../audits/audit-google-stack-2026-04-27.md)
- Memoria `project_tracking_architecture` (decisión arquitectónica 2026-04-26)
- Mini-bloque 3.1 [docs/audits/mini-bloque-3-1-cleanup-vps1-2026-04-28.md](../audits/mini-bloque-3-1-cleanup-vps1-2026-04-28.md)

---

## 2. Opciones consideradas

### Opción A — Plugin WordPress dedicado (UTM Tracker, ConvertFlow, etc.)
Instalar plugin WP que se encarga de UTM persistence vía cookies + populator de formularios. Ejemplos: "UTM Grabber", "UTM Tracker", "Trackonomics".

### Opción B — Custom JS en theme (functions.php) + plugin WP
Escribir JS custom directamente en el tema Astra (functions.php que enqueea un script). Manejar cookies + populator manualmente en el JS theme-side.

### Opción C — GTM Custom HTML "Tracking Engine" centralizado
Un solo Custom HTML tag dentro de GTM (`lvk - Tracking Engine`, All Pages trigger) que hace TODO:
- Captura URL params → cookies first-party (30 días)
- First-touch landing URL + referrer
- Listener de WhatsApp click → push dataLayer event
- Listener de SureForms submit → push dataLayer event con `event_id` único
- Auto-populator de hidden fields en SureForms (cuando los agreguemos en mini-bloque 3.3)

Plus 17 variables GTM (11 cookies + 6 DataLayer) + 3 triggers + 5 event tags (3 GA4 + 2 Meta Pixel) que CONSUMEN los datos del Engine.

---

## 3. Análisis de tradeoffs

| Dimensión | Opción A (Plugin WP) | Opción B (Theme JS) | Opción C (GTM Engine) |
|---|---|---|---|
| **Costo** | $0 (free) o $15-50/mes (premium) | $0 | $0 |
| **Complejidad implementación** | Baja (instalar + config UI) | Media (escribir JS + enqueue) | Media (script + setup GTM API) |
| **Complejidad mantenimiento** | Alta (atado a updates plugin, breaking changes) | Alta (cambios theme = perdemos código) | Baja (todo en GTM, versionado nativo) |
| **Reversibilidad** | Media (desactivar plugin pierde data) | Baja (revertir JS theme = riesgo otras cosas) | Alta (revert version GTM = 1 click) |
| **Portfolio value** | Bajo ("usa plugin X") | Medio ("escribí JS para")| Alto ("orquestré GTM Engine custom + dedup CAPI") |
| **Alineación principios** | Viola P3 (depende de plugin) | Viola P5 (atado a tema) | ✅ P3 (control), P5 (reversible), P10 (un solo lugar) |
| **Future-proof Fase 4-5** | Limitado (plugin decide schema) | Manual cada cambio | ✅ Engine extensible (más events) |
| **Versionado** | Plugin (semver) | Git theme | GTM versions (auto-revert) |
| **Performance** | +1 plugin cargado | +1 script en theme | +1 tag en GTM (mismo costo) |
| **CAPI dedup** | Depende del plugin | Manual implementar | ✅ Implementado (event_id en JS) |

---

## 4. Recomendación

**Opción C — GTM Custom HTML "Tracking Engine" centralizado.**

Razones:

1. **Single source of truth para tracking client-side**: Todo lo que pase en el navegador queda definido en GTM. Si mañana migramos a Astro/Next.js/otro CMS, copiamos el GTM container y mantenemos el tracking funcionando. Plugins WP nos atan a WordPress.

2. **Reversibilidad real**: GTM tiene versioning nativo. Cualquier cambio se puede revertir a una version anterior con 1 click (lo demostramos hoy revirtiendo el cambio malo del workspace). Plugins no ofrecen eso.

3. **Trazabilidad**: cada cambio en GTM queda auditado (autor + timestamp + diff). Para portfolio profesional + accountability, el GTM API + version history es superior.

4. **Extensibilidad para Fase 4-5**: cuando lleguen Conversation Agent + Acquisition Agent, agregar nuevos events (`booking_scheduled`, `appointment_attended`, `purchase`) es agregar líneas al Engine + tags GA4/Pixel. No tocamos WP ni theme.

5. **Alineación con arquitectura tracking 2-capas single-source** (memoria `project_tracking_architecture`): Capa 1 client-side = GTM única fuente. Engine es la implementación natural de esa decisión.

6. **CAPI dedup nativo**: el `event_id` generado por Engine se inyecta tanto en dataLayer (cliente) como en hidden field `event_id` del form (que llegará al backend en mini-bloque 3.3) → cuando server-side CAPI emita el mismo `event_id`, Meta deduplica → match quality alto.

**Tradeoff aceptado:** Engine es JS dentro de GTM, requiere conocer GTM bien para mantenerlo. La curva de aprendizaje es real pero pagable una sola vez. La alternativa (plugin WP) es deuda técnica de bajo nivel para siempre.

---

## 5. Decisión

**Elección:** Opción C — GTM Custom HTML "Tracking Engine" centralizado.

**Fecha de aprobación:** 2026-04-28 por Dario Urrutia.

**Razonamiento de la decisora:**
> "vamos" (mini-bloque 3.2 con propuesta arquitectónica programmatic-first)

---

## 6. Consecuencias

### Desbloqueado por esta decisión

- ✅ Mini-bloque 3.4 (CAPI server-side desde ERP) — el `event_id` del Engine se sincroniza con el `event_id` que el ERP enviará a Meta CAPI
- ✅ Mini-bloque 3.5 (observabilidad Metabase) — los UTMs en GA4 + Pixel events permiten dashboards de "Leads por canal", "ROAS por campaña"
- ✅ Fase 4 Conversation Agent — `lead.source`, `lead.campaign`, `lead.creative` poblados desde primera interacción
- ✅ Fase 5 Acquisition Agent — optimización con data real de qué ads convierten

### Implementación realizada (2026-04-28)

#### Componentes GTM creados (workspace 18 → publicado v18)

**17 variables:**
- 11 First-Party Cookie variables (`Cookie - utm_source`, `Cookie - utm_medium`, `Cookie - utm_campaign`, `Cookie - utm_content`, `Cookie - utm_term`, `Cookie - fbclid`, `Cookie - gclid`, `Cookie - ttclid`, `Cookie - msclkid`, `Cookie - landing_url`, `Cookie - first_referrer`)
- 6 Data Layer variables (`DLV - event_id`, `DLV - form_id`, `DLV - click_url`, `DLV - utm_source_v`, `DLV - utm_medium_v`, `DLV - utm_campaign_v`)

**3 triggers:**
- `Trigger - form_submit_lvk` (Custom Event = `form_submit_lvk`) — disparo cuando JS detecta submit en SureForms
- `Trigger - whatsapp_click` (Custom Event = `whatsapp_click`) — disparo cuando JS detecta click en link `api.whatsapp.com` o `wa.me`
- `Trigger - scroll_75` (Scroll Depth 75% vertical, DOM_READY)

**8 tags totales (2 viejos + 6 nuevos):**
- `GA - Config` (existente, GA4 base PageView)
- `Pixel Meta - Config` (existente, Meta Pixel PageView)
- `lvk - Tracking Engine` (Custom HTML, All Pages — el corazón del sistema)
- `GA4 Event - whatsapp_click` (GA4 Event con UTMs como params)
- `GA4 Event - lead (form_submit)` (GA4 Event con UTMs + click_ids como params)
- `GA4 Event - scroll_75` (GA4 Event milestone scroll)
- `Meta Pixel - Lead` (Custom HTML con `fbq('track', 'Lead', {}, {eventID: ...})` para dedup CAPI)
- `Meta Pixel - Contact` (Custom HTML con `fbq('track', 'Contact', {}, {eventID: ...})`)

#### JavaScript del Tracking Engine (resumen funcional)

```javascript
// 1. Captura URL params en page load → cookies first-party 30 días
//    (utm_source, utm_medium, utm_campaign, utm_content, utm_term,
//     fbclid, gclid, ttclid, msclkid)
// 2. First-touch: guarda landing_url + first_referrer si no existen
// 3. Auto-populator: busca inputs name=utm_* en cualquier form, los rellena
// 4. WhatsApp click listener: detect click → genEventId() → dataLayer push
// 5. SureForms submit listener: detect submit → genEventId() → inject hidden
//    field event_id en form → dataLayer push (event_id sera key de dedup CAPI)
```

Código completo en `scripts/gtm_build_tracking_engine.py` (constante `TRACKING_ENGINE_JS`).

#### Schema de cookies (todas con prefijo `lvk_` + `;SameSite=Lax`)

| Cookie | TTL | Set on | Used by |
|---|---|---|---|
| `lvk_utm_source` | 30 días | URL `?utm_source=` | GA4/Pixel events + form fields |
| `lvk_utm_medium` | 30 días | URL `?utm_medium=` | GA4/Pixel events |
| `lvk_utm_campaign` | 30 días | URL `?utm_campaign=` | GA4/Pixel events |
| `lvk_utm_content` | 30 días | URL `?utm_content=` | GA4 events |
| `lvk_utm_term` | 30 días | URL `?utm_term=` | GA4 events |
| `lvk_fbclid` | 30 días | URL `?fbclid=` | GA4 lead event + CAPI dedup futura |
| `lvk_gclid` | 30 días | URL `?gclid=` | GA4 lead event |
| `lvk_ttclid` | 30 días | URL `?ttclid=` | GA4 lead event |
| `lvk_msclkid` | 30 días | URL `?msclkid=` | GA4 lead event |
| `lvk_landing_url` | 30 días | First touch | Auditoría + atribución |
| `lvk_first_referrer` | 30 días | First touch | Auditoría + atribución |

### Bloqueado / descartado

- **Plugin WP UTM tracking** (Opción A) descartada — viola principio de control, atado a plugin lifecycle
- **Custom JS en theme** (Opción B) descartada — viola principio de reversibilidad, atado a tema Astra
- **Hidden fields fijos en SureForms 1569** (decisión 2026-04-28): diferido a mini-bloque 3.3. El Tracking Engine inyecta dinámicamente solo `event_id` al submit. Cuando wire webhook ERP en 3.3, definimos exactamente qué hidden fields agregar al form para que lleguen al backend POST body.

### Implementación derivada

- [x] GTM v18 publicada (2026-04-28)
- [x] OAuth refresh token expandido a 5 scopes (analytics.readonly + tagmanager.readonly + tagmanager.edit.containers + tagmanager.edit.containerversions + tagmanager.publish)
- [x] Scripts reusables en `scripts/`:
  - `gtm_inspect_workspace.py` — inspección + status workspace
  - `gtm_build_tracking_engine.py` — build inicial (NO re-correr, ya creó components)
  - `gtm_publish_v18.py` — publish workspace as new version (template para futuros publishes)
  - `google_audit.py` — auditoría reusable (re-correr para ver eventos pulleados)
- [ ] Validación browser-side end-to-end (Dario, cuando guste): abrir `livskin.site/?utm_source=test` con DevTools, verificar cookies set + tags fire
- [ ] Mini-bloque 3.3 (siguiente): Form → ERP webhook + hidden fields en form 1569 mapeados al schema ERP
- [ ] Mini-bloque 3.4 (después): CAPI server-side desde ERP usando el mismo `event_id` para dedup

### Cuándo reabrir esta decisión

- Si Meta cambia su política de Pixel events o requiere nuevo formato → revisar tag schemas
- Si se descontinúa GTM (improbable) → migrar Engine a otro tag manager (Matomo Tag Manager, Adobe DTM)
- Si volumen de events supera límites GA4 free tier (50k events/día) → considerar GA4 360 o BigQuery export
- Migración de WordPress a otro CMS → GTM container es portable; solo cambia el snippet de carga
- Cuando llegue Fase 5 Acquisition Agent → puede requerir más events custom (p.ej. `ad_view`, `ad_click_attributed`)

---

## 7. Changelog de esta ADR

- 2026-04-28 — v1.0 — Creada y aprobada en Mini-bloque 3.2 (sesión 2026-04-28).

---

**Notas:**
- Los scripts en `scripts/gtm_*.py` son reusables. Dependencias: `keys/google-oauth-token.json` + scopes configurados.
- Para revertir GTM v18 → v17 (rollback): UI GTM → Versions → click v17 → "Publish". O via API con `tagmanager.accounts.containers.versions.publish(path=v17_path)`.
- Backup tactic: si algo del Engine rompe el sitio, el live version se puede restaurar a v17 en <1 minuto.
