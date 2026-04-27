# Sesión 2026-04-27 — Acceso programático Google + audit definitivo + Meta parcial

> **Continuación de:** [2026-04-26-audit-real-y-arquitectura-tracking.md](2026-04-26-audit-real-y-arquitectura-tracking.md)
> **Tipo:** Setup técnico + auditoría programática
> **Duración:** ~5 horas (con pausas)
> **Próxima:** Decidir en frío si reintentamos Meta o saltamos a Fase 3

---

## Contexto inicial

Sesión planeada: **Setup acceso programático completo (Google + Meta) + audit definitivo vía APIs**. Resultado: Google completado y validado al 100%; Meta llegó a ~80% (System User + assets + app creados) pero **token generation bloqueado por cambios de UI/políticas Meta**. Dario decidió cortar Meta hoy y cerrar con lo logrado.

---

## Lo que se hizo

### 1. Setup Google — completado al 100%

**Plan original:** Service Account JSON key con grants Read en GA4 + GTM + Ads.

**Pivot necesario:** GA4 + GTM **rechazaron el email del service account** con error "no coincide con cuenta Google". Es una limitación conocida de Meta (perdón, Google) en cuentas sin Workspace — la UI de admin valida emails contra "Google Accounts conocidos" y rechaza `iam.gserviceaccount.com`. El service account sí está válido (verificado con auth API directa: `OK service account autenticado correctamente`), pero las UIs no aceptan grants.

**Solución implementada:** OAuth user flow.
- OAuth Client ID (Desktop app) creado en Google Cloud Console
- `keys/google-oauth-client.json` (gitignored)
- Pantalla de consentimiento configurada con `daizurma@gmail.com` como test user (después de error 403 inicial por test user faltante)
- Script `scripts/google_oauth_setup.py` ejecutado → browser OAuth flow → autorizado por Dario → refresh token persistente guardado en `keys/google-oauth-token.json`
- Scopes: `analytics.readonly` + `tagmanager.readonly`

**Validación:** auth contra Google APIs funcionando perfecto. Refresh token persistente, no expira (mientras no se revoque).

### 2. Audit programmatico Google ejecutado

Script `scripts/google_audit.py` corrió contra GA4 Admin API + Analytics Data API + Tag Manager API. Resultados completos documentados en [docs/audits/audit-google-stack-2026-04-27.md](../audits/audit-google-stack-2026-04-27.md).

**Hallazgos críticos:**

1. **GA4 — 5 accounts visibles** vía API (no era 1):
   - **Livskin** (`G-9CNPWS3NRX`) — la activa, livskin.site, data flowing ✅
   - **LivskinDEF** (`G-YJ4CCLJFSK`) — duplicada/legacy apuntando a livskinperu.com (dominio anterior)
   - Radish Store Chile, Hakuchu Marketing, Demo Account (otros proyectos)

2. **GTM container `GTM-P55KXDL6` — código exacto extraído:**
   - Live version 17 "meta pixel"
   - 2 tags: `GA - Config` (googtag) + `Pixel Meta - Config` (html)
   - Extraje el HTML literal del tag de Pixel: `fbq('init', '4410809639201712'); fbq('track', 'PageView');`

3. **Doble disparo Pixel CONFIRMADO con código real**, no hipótesis:
   - Plugin PixelYourSite dispara `fbq('init', X)` + `PageView` desde PHP/JS
   - GTM tag dispara `fbq('init', X)` + `PageView` desde HTML custom
   - Mismo Pixel ID, sin event_id custom para deduplicación
   - Cada visita = 2 PageViews a Meta = "Diagnóstico (1)" en Events Manager

4. **GA4 events últimas 48h:**
   - 8 page_views, 5 users, 5 session_start
   - 1 form_start + 1 form_submit ← **Dario NO recuerda haber probado el form**, alta probabilidad de **bot scraping** (form sin reCAPTCHA/Turnstile)
   - 0 whatsapp_click (tag no existe + link CTA roto)
   - 0 eventos canónicos del funnel (Lead/Schedule/Purchase) — esperado, es trabajo de Fase 3

5. **Workspace GTM tiene 1 cambio no publicado** — pendiente decidir publicar o descartar.

### 3. Discusión arquitectónica reforzada

Dario expresó claramente:
- **Enfoque greenfield** — el sistema es nuevo (sitio nuevo, sin leads reales aún, página recién montada). Aprovechemos para borrar lo no necesario, lo mal configurado, lo que cause problemas. Pensar en config como algo nuevo desde cero.
- **Bot probable en form_submit** — sin reCAPTCHA/Turnstile, form público en home, 0 entries en DB pero GA4 capturó form_submit. Patrón de bot. **Acción urgente Fase 3:** Cloudflare Turnstile en SureForms 1569 antes de cualquier integración con backend.

### 4. Setup Meta — 80% completado, token bloqueado

**Lo que SÍ quedó configurado y persiste para próxima sesión:**

- ✅ Confirmado: 3 Business Managers existentes en cuenta Dario (desorden histórico de fase de aprendizaje):
  - **Livskin Perú** (1 activo, owns Pixel 2026 — el correcto, Business ID 444099014574638)
  - **Livskin Perú Comercial** (0 activos, contiene app `agent n8n`)
  - **Dario Urrutia Martinez** (1 activo, personal)
- ✅ System User **"Claude Audit"** creado en Business "Livskin Perú" (ID 61560721390798)
- ✅ Assets asignados al System User: Cuenta publicitaria 2885433191763149 (Ver rendimiento) + Pixel 2026 (Ver pixeles + Usar conjunto de datos de eventos)
- ✅ Pixel viejo legacy `670708374433840` desligado del System User (limpieza greenfield)
- ✅ App **"Claude Audit App"** creada (ID 941702218481777) en Business "Livskin Perú"
- ✅ Claude Audit (System User) asignado como admin de Claude Audit App

**Lo que se bloqueó:**

- ❌ Token generation falló iterativamente:
  - Intento 1: Sin app en Business → error "no hay permisos disponibles"
  - Intento 2: Conectar app `agent n8n` → error técnico (cross-business)
  - Intento 3: Crear "Claude Audit App" sin caso de uso → error "no hay permisos disponibles" (la app sin caso de uso no expone scopes)
  - Intento 4: Pivot a User Token via Graph API Explorer → UI no permitía agregar permisos (`ads_read`, `business_management`, `read_insights`) — sin barra búsqueda visible, sin scroll, dropdown solo mostraba `user_payment_tokens`

**Causa de fondo:** Meta cambió en últimos 18 meses cómo expone scopes. Marketing API y Conversions API standalone se quitaron de "casos de uso" típicos. Para acceso `ads_read` real ahora hay que pasar por **App Review formal** (Business Verification + Standard Access tier review), proceso de 1-3 semanas.

**Decisión Dario:** cortar Meta hoy, honrar compromiso de "5 min máx o paramos". La fricción es Meta, no nosotros.

---

## Decisiones tomadas

1. **Acceso programático Google = OAuth user flow** (no service account) por limitación de UIs Google sin Workspace. Refresh token persistente en `keys/google-oauth-token.json`.

2. **Audit Google = referencia autoritativa** para validar arquitectura tracking. El doble disparo Pixel ya está probado con código real, no hipótesis.

3. **Meta token = pendiente próxima sesión** — explorar opciones distintas:
   - (a) App Review formal con scopes `ads_read` (1-3 semanas) — probable correcto a largo plazo
   - (b) Saltar Meta del audit por ahora, los datos Google son suficientes para arrancar Fase 3
   - (c) Revisar si hay nuevos métodos Meta para read-only audit que no requieran review

4. **Limpieza pendiente formal en backlog:**
   - 3 Business Managers Meta a consolidar (Livskin Perú vs Livskin Perú Comercial vs personal)
   - GA4 property "LivskinDEF" a archivar
   - Pixel viejo `670708374433840` a archivar en Meta
   - Plugin PixelYourSite + LatePoint a desactivar (ya decidido ayer)
   - Cloudflare Turnstile en SureForms 1569 (urgente — bot detectado)
   - GTM workspace con cambio no publicado (decidir publicar o descartar)

5. **Honrar compromisos a Dario** — cuando se promete "5 min máx" no extender a 30. Aprendizaje incorporado a memoria de gobernanza.

---

## Lecciones operativas (para incorporar a memoria)

### Sobre Meta API + Business Manager

- **Service accounts no funcionan para grants en GA4/GTM** sin Google Workspace. Pivot directo a OAuth user flow.
- **Marketing API + Conversions API ya no son "casos de uso"** seleccionables al crear apps Meta. El acceso programático real requiere App Review formal.
- **Las UIs Meta + Google rotan frecuentemente** — guías paso-a-paso quedan obsoletas en semanas. Mejor **scripts programáticos** que UIs guiadas.
- **3 Business Managers** es síntoma de fase de aprendizaje. La consolidación es un mini-proyecto en sí mismo.

### Sobre el flujo de trabajo con Dario

- **Cuando Dario expresa "no quiero más tanteos"** = llegamos al límite de tolerancia operativa. No discutir, parar y pivotar a algo que SÍ funcione.
- **5 min de promesa = 5 min real**, no expandible. Honrar es construir confianza.
- **Greenfield mindset** es la postura natural de Dario para infraestructura del proyecto: borrar lo malo, pensar nuevo, sin nostalgia por configuraciones legacy.

### Sobre auditoría programática

- **Google APIs (Analytics + Tag Manager) son extraordinariamente buenas** para audit. El script de hoy se reutiliza tal cual en futuras auditorías.
- **El audit programmatico revela cosas invisibles a screenshots**: 5 GA4 accounts (no 1), código exacto de tags, eventos disparados últimas 48h, workspaces sin publicar.
- **Doble disparo Pixel = probado con datos**, no asumido. Validación arquitectónica = sólida.

---

## Lo que queda pendiente

### Próxima sesión inmediata
**Decisión en frío:**
- (a) ¿Reintentamos Meta token? Con qué método? App Review formal? Otro path?
- (b) ¿Saltamos Meta del audit por ahora y arrancamos Fase 3 con Google solo? Los datos Google son **suficientes** para validar arquitectura.
- (c) ¿Otra opción?

Dario decide tras descansar.

### Backlog (formalizado en cierre)
- 🔴 **Re-indexing automático brain Layer 2** antes de Fase 4 (item ya existente)
- 🔴 **Cloudflare Turnstile en SureForms 1569** — urgente, bot detectado
- 🟡 **Consolidación 3 Business Managers Meta** — sesión dedicada (~60 min)
- 🟡 **App Review formal Meta para `ads_read`** (cuando se decida hacerla, 1-3 semanas)
- 🟡 **Sistema operativo de archivado** — Pixel viejo, GA4 LivskinDEF, plugins, etc.
- 🟢 **Anuncio Meta activo (€2/día)** — revisarlo en Fase 3 (no estaba en radar)

---

## Próxima sesión propuesta

**Decisión arquitectónica:** Meta path o Fase 3 directo. ~15 min de discusión, después arrancamos lo que se decida.

Si Fase 3 directo: arrancamos mini-bloque 3.1 (limpieza VPS 1 — desactivar plugins redundantes + archivar pixel viejo + fix CTA WhatsApp).

Si reintentar Meta: investigamos primero qué método actual soporta Meta REALMENTE para el caso "auditoría read-only del propio Business sin App Review", antes de tocar UI.

---

**Cerrada por:** Claude Code · 2026-04-27 (~21:00 hora Milán, fin del día Dario)
