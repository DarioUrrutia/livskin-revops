# Backlog del proyecto Livskin

**Propósito:** artefacto vivo para capturar ideas, cambios, dudas y observaciones que no son acción inmediata pero **no deben perderse**.

**Uso:**
- Cualquier de los dos (Dario o Claude Code) agrega entradas cuando surjan ideas
- Al inicio de cada sesión, yo reviso el backlog y te propongo qué retomar
- Al cierre de cada sesión, movemos a "Hecho" o reordenamos prioridades
- Priorización por **impacto al proyecto**, no por orden cronológico

---

## Leyenda

- 🔴 Alta prioridad (bloquea algo o es riesgo activo)
- 🟡 Media prioridad (mejora importante, no bloquea)
- 🟢 Baja prioridad (nice to have)
- 💡 Idea/brainstorm (todavía sin decisión, a discutir)
- ❓ Duda abierta (requiere respuesta de usuaria)
- ✅ Hecho (se mantiene como historial)

---

## Prioritario

<!-- Cosas que hay que hacer pronto -->

### 🔴 Decisión a reabrir en Mini-bloque 3.4 — CAPI emitter ERP vs n8n
**Decisión 2026-04-26 (revisable):** CAPI emitido directamente desde ERP. **Decisión refinada conversación 2026-04-29:** la lógica original justificaba que el ORIGEN del evento es ERP (match quality), pero no que el EMISOR a Meta sea ERP. Patrón propuesto:

```
ERP (cita/venta) → POST a n8n /webhook/capi-event con payload completo
n8n recibe + valida + emite a Meta CAPI
ERP loggea audit_log "capi.event_emitted"
```

**Beneficios:** visualidad n8n + centralización outbound a Meta + match quality alta (PII viene de ERP) + ERP audit log preservado + edit nodo n8n si Meta cambia API.

**Costo:** un n8n workflow más + endpoint POST en ERP que va a n8n en vez de Meta directo.

**Trigger:** primera decisión al abrir Mini-bloque 3.4 (junto con Meta App Review + anuncio €2/día).
**Output:** ADR-0019 versión full con la decisión final.
**Agregado por:** Claude Code · 2026-04-29

---

### 🟡 Subir 134 clientes existentes a Meta como Custom Audience (Mini-bloque 3.4)
**Insight 2026-04-29:** los 134 clientes históricos del ERP son **word-of-mouth** (no vinieron de ads). No tienen `fbclid`/`gclid` para attribution histórica → Meta no los puede atribuir a ningún anuncio. **PERO** son el dataset de mejor calidad que tenemos para alimentar el algoritmo de Meta:
- **Custom Audience** ("Customer File"): subir hashed email + phone de los 134 → Meta los identifica en su universo de usuarios
- **Lookalike Audience (LAL) 1-3%**: Meta busca personas SIMILARES en Perú a tus mejores pacientes → audiencia inicial para campañas

**Acción:**
1. Export de los 134 clientes con email + phone (script Python desde ERP DB)
2. Hashing SHA-256 de email/phone normalizados
3. Subir CSV a Meta Ads Manager → Audiences → Custom Audience → Customer List
4. Crear LAL 1-3% Perú basado en esa Custom Audience
5. Documentar en runbook `audiences-meta.md` cómo refrescar la audience cada N meses (cada nuevo cliente real → re-upload incremental)

**Por qué esto importa:** es la primera vez que Meta ve "datos de pacientes pagos reales de Livskin", no proxies (form leads, page views). El algoritmo afina mucho mejor con conversiones reales.

**Trigger:** Mini-bloque 3.4 (CAPI), primer outbound a Meta — coherente con el bloque que cerrará la decisión Meta App Review.
**Pre-requisito:** decisión Meta App Review (necesario tener `ads_management` o subir manual desde UI).
**Estimado:** 30-45 min (script + upload + LAL).
**Agregado por:** Claude Code · 2026-04-29

---

### 🟡 Schema `clientes` ERP — heredar `first_touch_attribution` del lead al convertir
**Decisión 2026-04-29:** cuando un lead se convierte en cliente (primera cita pagada), el ERP debe **preservar el contexto de adquisición original** en `clientes`. Hoy `clientes` no tiene esa columna.

**Acción:**
1. Migration Alembic 0007 (post Mini-bloque 3.3): agregar columna `first_touch_attribution` JSONB a `clientes`
2. Estructura: `{fbclid, gclid, fbc, ga, utm_source, utm_campaign, utm_medium, utm_term, utm_content, lead_id, lead_created_at, conversion_date}`
3. Hook en lógica de conversión lead→cliente: copiar atribución del `leads` row al `clientes` row al crearlo
4. Endpoint `/api/clientes/<id>/attribution` para query (útil para dashboard analítico)

**Por qué importa:** cuando se haga un Purchase 60 días después del primer click, CAPI puede mandar el `fbclid` original aunque ya no esté en cookie del paciente. Cierra el ciclo de attribution end-to-end.

**Trigger:** post Mini-bloque 3.3 REWRITE, cuando ya esté el flujo lead→cliente completo. O directamente en bloque puente Agenda (que toca schema clientes igual).
**Estimado:** 30 min (migration simple + hook).
**Agregado por:** Claude Code · 2026-04-29

---

### 🔴 Mini-bloque 3.3 REWRITE — Form → n8n → Vtiger → ERP espejo (próxima sesión)
**Estado 2026-04-29:** intento incorrecto del 2026-04-29 (Form → ERP directo) **REVERTIDO completo**. El flujo correcto documentado en ADR-0011 v1.1 + ADR-0015 + memoria `project_acquisition_flow` requiere n8n + Vtiger en el medio. **Aplicar runbook OBLIGATORIO `docs/runbooks/preflight-cross-system.md` antes de empezar.**

**Componentes a construir:**

1. **Vtiger setup** (módulo Leads activo, custom fields para UTMs/click_ids/event_id, REST API auth, webhook on-change config)
   - Custom fields requeridos: `cf_fbclid`, `cf_gclid`, `cf_fbc`, `cf_ga`, `cf_utm_source`, `cf_utm_campaign`, `cf_utm_medium`, `cf_utm_term`, `cf_utm_content`, `cf_event_id`, `cf_landing_url`
2. **n8n workflow `/webhook/form-submit`** (recibe POST de mu-plugin, dedup v2 por phone, INSERT Vtiger Lead con TODOS los identifiers, envía WA template)
3. **n8n workflow `Vtiger → ERP espejo`** (recibe webhook on-change Vtiger, sync a `livskin_erp.leads` table)
4. **mu-plugin WordPress refactor** (POST a n8n webhook con 11 hidden fields: 4 click_ids/cookies + 5 UTMs + event_id + landing_url)
5. **Endpoint Flask renombrado** (de `/api/leads/intake` a `/api/leads/sync-from-n8n` — receptor del workflow de espejo, NO entrada principal)
6. **Migration Alembic 0006** — extender schema `leads` con columnas: `fbclid`, `gclid`, `fbc`, `ga`, `utm_source`, `utm_campaign`, `utm_medium`, `utm_term`, `utm_content`, `event_id`, `ip_at_submit`, `ua_at_submit`, `landing_url`
7. **Tests pytest + validación end-to-end** (lead manual real → flujo completo, verificar que click_ids viajan y persisten en `leads`)

**Estimado:** 2-3 sesiones (más complejo que el intento de hoy porque integra 3 sistemas + setup Vtiger desde virgen).

**Pre-requisitos antes de empezar (preflight obligatorio):**
- [ ] Releer 🔥 CRÍTICAS: `project_vtiger_erp_sot`, `project_acquisition_flow`, `project_n8n_orchestration_layer`, `feedback_must_re_read_adrs_before_coding`, `feedback_surgical_precision_erp`
- [ ] Query brain pgvector con keywords: "flujo lead form vtiger n8n erp"
- [ ] Citar ADR-0011 v1.1 + ADR-0015 en plan inicial
- [ ] Plan citado aprobado por Dario antes de tocar código

**Fase sugerida:** próxima sesión inmediata
**Agregado por:** Claude Code · 2026-04-29

---

### ~~🔴 Mini-bloque 3.3 Fase 3 — Form → ERP webhook~~ ❌ INVALIDADO 2026-04-29 (arquitectura incorrecta, ver item arriba)
**Estado 2026-04-28:** Mini-bloques 3.1 + 3.2 completados. El Tracking Engine en GTM ya inyecta `event_id` único al submit del form. Ahora toca el plumbing al backend:

**Acciones:**
1. ADR breve sobre arquitectura webhook (idempotencia, dedup por event_id, retry policy)
2. Endpoint Flask nuevo `POST /api/leads/intake` en ERP VPS 3
   - Schema validation Pydantic (Nombres, Email, Teléfono, Tratamiento, UTMs, click_ids, event_id, landing_url)
   - INSERT en `leads` table con full context
   - Audit log entry `lead.created`
   - Push secundario a Vtiger via REST API (best-effort, no blocking)
3. SureForms 1569: agregar 10-11 hidden fields via post_content blocks (`srfm/hidden`)
4. SureForms webhook config → POST a `/api/leads/intake`
5. Test con lead manual (Dario + alguien real)
6. Tests pytest del nuevo endpoint (mantener coverage ≥80%)

**Estimado:** 90-120 min.

**Después de 3.3:** los leads dejan de ser "anonymous form_submit en GA4" y se convierten en "row en `leads` table del ERP con full context (UTMs + click_ids + landing + event_id)". Primer paso real hacia atribución por canal.

**Fase sugerida:** próxima sesión inmediata
**Agregado por:** Claude Code · 2026-04-28

---

### ~~🔴 Cloudflare Turnstile en SureForms 1569 — URGENTE pre-Fase 3~~ ✅ COMPLETADO 2026-04-28
**Detectado 2026-04-27:** GA4 capturó 1 `form_submit` últimas 48h pero `wp_srfm_entries` tiene 0 entries en DB. Dario NO recuerda haber probado el form. Sin reCAPTCHA/Turnstile (`_srfm_form_recaptcha = none`), form público en home → **bot scraping confirmado**.

**Riesgo si no se resuelve antes de conectar webhook a ERP:**
- Falsos eventos GA4 que degradan métricas reales
- Spam que llenará la tabla `leads` del ERP cuando se conecte (Mini-bloque 3.3 Fase 3)
- Costos de procesamiento backend
- Falsos disparos de Meta CAPI cuando se conecte (Mini-bloque 3.4)

**Acción:**
1. Configurar Cloudflare Turnstile en dashboard CF
2. Plugin SureForms tiene integración nativa con reCAPTCHA — investigar si soporta Turnstile o requiere snippet custom
3. Si no soporta Turnstile nativo: usar reCAPTCHA v3 (libre + invisible)
4. Activar en form 1569 antes de cualquier integración con backend

**Fase sugerida:** primer paso Fase 3 (mini-bloque 3.1 limpieza VPS 1)
**Agregado por:** Claude Code · 2026-04-27

---

### 🔴 Decisión Meta — App Review formal vs saltar audit Meta
**Estado 2026-04-27:** Setup Meta llegó al 80% (System User + Claude Audit App + Pixel + Ad Account assets) pero token generation bloqueado por cambios Meta:
- Marketing API y Conversions API standalone ya no son "casos de uso" seleccionables
- Para `ads_read` real se requiere **App Review formal** (Business Verification + Standard Access tier review = 1-3 semanas)
- Graph API Explorer no permitió agregar permisos en UI actual

**Configuración persistente que se queda esperando:**
- Business Manager `Livskin Perú` (444099014574638) — owner del Pixel
- System User `Claude Audit` (61560721390798) con Pixel 2026 + Ad Account assets
- App `Claude Audit App` (941702218481777) en Business
- App con Claude Audit asignado como admin

**Decisión pendiente próxima sesión:**
- **Opción A:** Iniciar App Review formal (1-3 semanas espera, pero permanente y correcto)
- **Opción B:** Saltar Meta del audit por ahora — los datos Google ya validan 100% las decisiones arquitectónicas (doble disparo confirmado, eventos GA4 visibles)
- **Opción C:** Investigar si hay método actual Meta para read-only audit del propio Business sin review

**Recomendación Claude:** Opción B + agendar App Review en paralelo a Fase 3 (no bloqueante). Audit Meta detallado da nuance pero no cambia decisión arquitectónica que ya está validada con Google data.

**Trigger explícito para decidir (actualizado 2026-04-29):** **al iniciar Mini-bloque 3.4 (CAPI server-side desde ERP)**. Razones:
- Mini-bloque 3.4 envía conversiones server-side al Pixel; antes de empezar es el momento natural de definir si se hará App Review formal o se sigue con audit programático que ya tenemos
- Si para 3.4 ya pasaron >7 días desde 2026-04-27, los assets (System User, Pixel attached, Ad Account assigned) siguen sirviendo aunque no haya token con `ads_read`
- Dario debe responder UNA pregunta antes del primer commit de 3.4: "¿iniciamos App Review en paralelo o saltamos definitivamente Meta del audit programático?"

**Fase sugerida:** Mini-bloque 3.4 (CAPI) — primera decisión del bloque
**Referencia:** [docs/sesiones/2026-04-27-acceso-programatico-google-y-audit.md](sesiones/2026-04-27-acceso-programatico-google-y-audit.md)
**Agregado por:** Claude Code · 2026-04-27 · trigger clarificado 2026-04-29

---

### 🟡 Consolidación 3 Business Managers Meta
**Detectado 2026-04-27:** Dario tiene 3 Business Managers Meta (desorden de fase de aprendizaje):
1. **Livskin Perú** (1 activo, owns Pixel 2026 — el que usamos)
2. **Livskin Perú Comercial** (0 activos, contiene app `agent n8n` legacy)
3. **Dario Urrutia Martinez** (1 activo, personal)

**Acción:**
- Decidir BM canónico (probablemente Livskin Perú)
- Auditar qué hay en cada BM: apps, pixels viejos, ad accounts, pages, asset groups, system users
- Transferir/eliminar contenido de "Livskin Perú Comercial" (vacío hoy salvo agent n8n)
- Decidir si BM "Dario Urrutia Martinez" tiene assets que migrar o archivar
- Documentar BM canónico en CLAUDE.md / project memory

**Fase sugerida:** 1 sesión dedicada (~60 min), antes de Fase 5 (Acquisition Agent productivo)
**Agregado por:** Claude Code · 2026-04-27

---

### 🟡 Crear System User dedicado para Acquisition Agent en Fase 5
**Decisión 2026-04-27 (registrada cuando se discutió en sesión):** Cuando se construya Acquisition Agent productivo (Fase 5), crear System User Meta dedicado distinto a `Claude Audit` con scopes write (`ads_management`, `ads_read`, etc.). Razones:
- Principio de menor privilegio (separar identidades audit vs producción)
- Trazabilidad (audit log Meta diferencia "Acquisition Agent" vs "Claude Audit")
- Revocación granular (revocar uno sin tocar el otro)
- Rotación independiente (write tokens rotan más seguido)

Esto requiere App Review formal (a iniciar antes de Fase 5).

**Fase sugerida:** Fase 5 setup
**Referencia:** memoria `feedback_agent_governance.md` (procesos antes de libertad)
**Agregado por:** Claude Code · 2026-04-27

---

### 🟡 Archivar GA4 property "LivskinDEF" (livskinperu.com)
**Detectado 2026-04-27 vía audit programmatico:** existe property GA4 "LivskinDEF" (`G-YJ4CCLJFSK`) apuntando a `livskinperu.com`. Es del dominio anterior antes de migrar a `livskin.site`. **No se está usando**, riesgo: confusión + datos fragmentados si algún ad/campaña vieja sigue apuntando ahí.

**Acción:** archivar property en GA4 (no eliminar — preservar datos históricos por si alguna vez se necesitan).

**Fase sugerida:** Mini-bloque 3.1 (limpieza Fase 3)
**Agregado por:** Claude Code · 2026-04-27

---

### 🟢 Anuncio Meta activo €2/día — revisar al iniciar Mini-bloque 3.4
**Detectado 2026-04-27:** anuncio "Cada perfil es único" activo en Meta Ads (€2/día, 433-1.4k impresiones, 2 respuestas). NO estaba en mi radar (yesterday's audit dijo "0 active campaigns" pero eso era Google Ads, no Meta).

**Acción:** revisar — ¿pausarlo durante setup tracking? ¿mantenerlo? ¿optimizarlo? Decidir cuando lleguemos.

**Trigger explícito (clarificado 2026-04-29):** **al iniciar Mini-bloque 3.4 (CAPI server-side)**. Razones:
- Si está activo cuando se conecte CAPI, los eventos server-side y client-side van a deduplicar correctamente solo si el `event_id` está alineado — hay que decidir si se mantiene o pausa para evitar disparos durante validación
- Si para 3.4 el anuncio ya generó conversiones reales (lead/cita), es un caso de prueba útil para validar el match quality del CAPI
- Combinarlo con la decisión Meta App Review (item arriba) — ambos se resuelven al inicio de 3.4

**Decisión a tomar:** pausar mientras se setea CAPI, optimizar (ajustar audiencia/copy basado en datos GTM), o mantener as-is durante el setup
**Fase sugerida:** Mini-bloque 3.4 (CAPI) — junto con decisión Meta App Review
**Agregado por:** Claude Code · 2026-04-27 · trigger clarificado 2026-04-29

---

### 🟡 Re-indexing automático de brain Layer 2 (project_knowledge) — antes de Fase 4
**Estado actualizado 2026-04-29:** re-index manual ejecutado hoy (1,765 chunks actualizados con docs de la última semana — runbooks, ADRs, sesiones, mini-bloques 3.1+3.2). La urgencia bajó de 🔴 a 🟡 porque la brain está al día. Pero la **automatización sigue pendiente**: si en próximas sesiones se generan nuevos docs y nadie corre `brain-index.sh` manualmente, volveremos a desincronizar.

**Riesgo restante:** cuando arranque Conversation Agent (Fase 4) y consulte la brain semanas después de la última re-indexación manual, no sabrá de decisiones recientes.

**Acción a implementar (~1 sesión):**
1. **Trigger primario:** webhook GitHub (`push` a main) → endpoint VPS 3 → re-index incremental de archivos cambiados desde último run
2. **Backup:** cron diario 3am que re-indexa cualquier archivo .md modificado en las últimas 24h
3. **Logging:** cada run registra entry en `embedding_runs` (started_at, completed_at, rows_processed, status, notes)
4. **Idempotencia:** hash del file path + content para no re-indexar lo que no cambió
5. **Capas adicionales pre-Fase 4:**
   - Layer 1 (`clinic_knowledge`): poblar con 5-10 FAQs típicas + precios + tratamientos validados por la doctora (ya existe item ❓ "Definir las 5-10 FAQs típicas")
   - Layer 4 (`conversations`): schema activo, se llena automáticamente cuando arranca el bot

**Exit criteria:**
- Push a main → 30s después, los archivos nuevos están en `project_knowledge`
- `embedding_runs` registra el run con timestamp y rows
- Query semántica de prueba: "¿cuál es la arquitectura de tracking?" → devuelve chunks de los docs de 2026-04-26

**Trigger más explícito para arrancar:** cuando se vaya a planear Mini-bloque 3.5 (Observabilidad) — combinable porque ambos requieren tocar VPS 3 + audit log integration. O si pasan >2 semanas sin tocarlo y la brain queda stale otra vez.

**Fase sugerida:** Mini-bloque 3.5 (Observabilidad) o pre-Fase 4
**Referencia:** docs/sesiones/2026-04-26-audit-real-y-arquitectura-tracking.md (issue detectado en cierre)
**Agregado por:** Claude Code · 2026-04-26 · actualizado 2026-04-29

---

### 🔴 Setup acceso programático a Google + Meta (próxima sesión inmediata)
**Pre-requisito de Fase 3.** Audit por screenshots tiene techo. Para resolver definitivamente fricciones cross-stack, Claude necesita acceso vía API.

**Setup 1 — Google service account:**
- Google Cloud Console → proyecto "livskin-claude-audit"
- Service account `claude-readonly@…`
- JSON key → `keys/google-claude.json` (gitignored)
- Grants read-only: GA4 (Viewer en property Livskin), GTM (Read en container `GTM-P55KXDL6`), Google Ads (Read-only en cuenta `216-312-4950`)

**Setup 2 — Meta System User:**
- Meta Business Settings → System Users → crear "claude-livskin-readonly"
- Token con scopes read-only: `ads_read`, `business_management`, `pages_read_engagement`
- Acceso a Pixel `4410809639201712` + Business `444099014574638` + Ad accounts `2885433191763149`
- Token a `keys/.env.integrations`

**Setup 3 — Cloudflare API token (diferido a Fase 3):**
- API Tokens → custom token con permisos read en zone livskin.site
- Token a `keys/.env.integrations`

**Output post-setup:**
- `docs/audits/audit-tracking-stack-real-2026-04-XX.md` — audit programático real
- ADR-00XX — arquitectura tracking client-server cerrada con datos reales
- Plan ejecutable de Fase 3 mini-bloques con orden y tiempos

**Fase sugerida:** próxima sesión (post 2026-04-26)
**Agregado por:** Claude Code · 2026-04-26

---

### 🔴 ADR-00XX — Módulo Agenda Mínima en ERP (entre Fase 3 y Fase 4)
**Decisión arquitectónica cerrada 2026-04-26 (Opción B):** ERP gana módulo Agenda con tabla `appointments`. Vtiger queda para marketing automation, no para citas.

**Requisito Dario:** "precisión quirúrgica" — el ERP ya tiene 134 clientes / 88 ventas / 84 pagos productivos, no se puede romper nada.

**Protocolo (8 pasos):**
1. ADR redactado y aprobado antes de cualquier código
2. Tests pytest primero (TDD)
3. Endpoints aislados (nuevo blueprint, no toca existentes)
4. Feature flag `settings.agenda_enabled`
5. Migración Alembic 0005 100% reversible
6. Validación con doctora (5 citas de prueba)
7. Runbook `agenda-mantenimiento.md`
8. Audit log integration (cada cambio en `appointments` → audit_log)

**Schema preliminar:**
- `appointments`: id, lead_id, cliente_id, treatment, scheduled_for, duration_min, status, channel, notes, created_by, attended_at, timestamps
- Status enum: `scheduled, confirmed, attended, no_show, cancelled, rescheduled`

**Output:**
- Migración Alembic 0005
- Endpoints `/api/appointments` (CRUD)
- 3 vistas UI: agenda hoy / semana / cita detalle
- Integración con `tracking_emitter` (emite `Schedule` + `CompleteRegistration` automáticamente)
- Tests ≥85% coverage del módulo nuevo

**Fase sugerida:** entre Fase 3 y Fase 4 (3-4 sesiones)
**Referencia:** [docs/sesiones/2026-04-26-audit-real-y-arquitectura-tracking.md](sesiones/2026-04-26-audit-real-y-arquitectura-tracking.md)
**Agregado por:** Claude Code · 2026-04-26

---

### 🟡 ADR-00XX — Arquitectura tracking 2-capas single-source
**Decisión 2026-04-26:**
- Capa client-side: GTM como única fuente. Plugin PixelYourSite se desactiva.
- Capa server-side CAPI: emitida desde ERP VPS 3 (no desde WordPress).
- Pixel viejo `670708374433840` se archiva. Único activo: `4410809639201712`.

**Por qué desde ERP no desde WP:**
- ERP tiene eventos reales del funnel (cita, venta) que WP no ve
- ERP tiene email/teléfono real → match quality superior

**Output esperado:**
- `docs/decisiones/00XX-arquitectura-tracking-client-server.md` cerrado
- Implementación en mini-bloques 3.1–3.5 de Fase 3 revisada

**Fase sugerida:** Fase 3 (Mini-bloque 3.4 lo requiere)
**Agregado por:** Claude Code · 2026-04-26

---

### 🟡 Refinamiento rol Vtiger en arquitectura
**Decisión 2026-04-26:** Vtiger NO es SoT operativo (eso es ERP). Vtiger es **motor de marketing automation**:
- Lead → campañas drip
- Scoring + nurture flows
- Segmentación
- LEE del ERP (vía Postgres FDW o API), no escribe

**Acción:** actualizar `docs/decisiones/0014-...` (gobierno datos) o crear ADR específico que documente el refinamiento. Actualizar memoria `project_vtiger_erp_sot.md` ya hecho en cierre 2026-04-26.

**Fase sugerida:** cuando se cierre ADR-00XX módulo Agenda
**Agregado por:** Claude Code · 2026-04-26

---

### 🟡 Sesión estratégica — Estructura organizacional de agentes IA
**Antes de Fase 5 (Brand Orchestrator).** Dario pidió pensar el sistema como organización empresarial: él CEO, agentes con rangos + funciones + subagentes + skills.

**Output esperado:**
- ADR-0030 — Brand Orchestrator multi-agent architecture
- `docs/agents/organization-chart.md` — organigrama + roles + rangos + cadencias reporting
- Subdirs `docs/agents/<agent-name>/` con SKILL.md + prompts/ + tools.json + evals/ + cadence.md
- Brand voice consolidado en `docs/brand/voice.md`
- Approval flows + métricas de éxito por agente

**Visión clave registrada en memoria `project_agent_org_design.md`:**
- Brand Orchestrator (era Content Agent) expandido a director creativo end-to-end (ads + landings + copies + email + implementación)
- Patrón: orquestador + subagentes especializados (Research, Concept, Copywriter, Visual, Implementation)
- Skills compartidas cross-agent (research-competition usado por Brand + Acquisition + Growth)
- Aprobación bloqueante de anuncios (NUNCA publica sin OK Dario)

**Combinable con:** Interludio Estratégico (entre Fase 3 y Fase 4) — mismo bloque ~4-8h porque consume arquetipos del interludio.

**Fase sugerida:** post-Fase 3, pre-Fase 4 (interludio + sesión organizacional juntos).
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 Dashboards admin secundarios — `/admin/users`, `/admin/sessions`, `/admin/system-health`
ADR-0026 + ADR-0027 mencionan estos dashboards. Hoy solo está `/admin/audit-log`. Pendiente:
- `/admin/users` — lista usuarios + status + last_login + reset password de otro
- `/admin/sessions` — sesiones activas + ability to revoke
- `/admin/system-health` — status de containers + backups + cert expiry

**Por qué baja prioridad:** la Ley 29733 ya está cubierta con `/admin/audit-log`. Estos dashboards mejoran capacidad operativa pero no son bloqueadores.
**Fase sugerida:** post-Fase 3 si Dario los necesita
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 CI/CD: tests pre-deploy en lugar de post-deploy
Hoy el workflow `deploy-vps3.yml` corre pytest DESPUÉS del deploy. Eso significa que código broken puede llegar a producción antes de que los tests lo detengan.

**Mejora:** build el container en el runner GHA, levantar Postgres temporal, correr pytest contra el build. Si pasa → deploy. Si falla → no deploy.

**Mitigación actual:** el ERP refactorizado está en validación interna (no producción real, Render sigue siendo prod hasta Fase 6). El riesgo es bajo.
**Fase sugerida:** Fase 6 antes del cutover Render→VPS 3
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 Limpiar gaps diferidos del Flask original
Dos gaps documentados en `docs/erp-flask-original-deep-analysis.md` no se cerraron por ser cosméticos / no críticos:
1. Métodos de pago primera fila — el HTML original tenía pre-fill heurístico de la primera fila de pagos según fecha; no replicado.
2. Multi-currency por item — el original soporta moneda por línea de venta; el refactor unifica moneda a nivel venta.
3. Categoría `__otro__` libre — el HTML acepta categoría arbitraria via `__otro__`, el refactor solo lista presets.

**Cuándo:** si la doctora reporta fricción específica al usar el sistema.
**Fase sugerida:** Fase 6 o reactiva.
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 Subir coverage de tests más allá del 81% actual
Actualmente 81.31% (target ADR-0023 era ≥75%, superado). Áreas con coverage bajo:
- `routes/api_venta.py` — 25%
- `routes/api_cliente.py` — 39%
- `services/dashboard_service.py` — 75% (falta cubrir cálculo aging + comparativas)
- `services/normalize_service.py` — 86% (edge cases de phone/email)

Subir a 90%+ daría más confianza para refactors futuros, pero no es bloqueador.
**Fase sugerida:** opcional, post-Fase 3
**Agregado por:** Claude Code · 2026-04-26

---

### 🟡 Capa de auto-mantenimiento — implementar al cierre de Fase 6
Para que Dario NO dependa de intervenir manualmente en el sistema cuando esté dirigiendo la empresa (target: 3-5 h/mes total incluyendo mantenimiento).

**Componentes a implementar en Fase 6:**
- **Watchtower** (gratis, self-hosted) — monitorea containers y aplica security updates de imágenes Docker automáticamente. Reduce el riesgo de CVEs sin intervención manual.
- **UptimeRobot free tier** (50 monitors gratis) — monitorea cada subdominio público cada 5 min. Si cae algo, email/SMS a Dario.
- **n8n workflows de alertas internas** — vigilan disco, RAM, costos Claude API; alertan vía WhatsApp cuando crucen umbrales (definidos en ADR-0003 § 15.2).
- **Monthly audit auto-ejecutado** — cron job del día 1-5 de cada mes corre audit completo (Lynis + docker state + cert expiry + disk + etc.) y commitea el report a `docs/audits/`.
- **Runbooks operativos completos** — en `docs/runbooks/` documentar procedimientos paso a paso para los 5-10 incidentes más probables (SSL expirado, disco lleno, container crash, API key comprometida, etc.). Así cualquier persona puede resolver sin experticia.

**Objetivo cuantitativo:** reducir mantenimiento a <5h/mes rutinario + incidentes que alerten automáticamente.

**Decisión a futuro (Año 1-2):** según volumen real de incidentes, evaluar Ruta A (tú + Claude Code), Ruta B (fractional DevOps $300-800/mo) o Ruta C (managed services DO Managed Postgres +$15/mo).

**Referencia:** esta decisión fue formalizada tras consulta de Dario el 2026-04-20 sobre "cómo se mantiene esto cuando yo esté dirigiendo la empresa". Documentado en master plan § "Operación post-MVP y mantenimiento".

**Fase sugerida:** Fase 6 (Semana 10) + ajustes post-lanzamiento según data real.  
**Agregado por:** Claude Code · 2026-04-20

---


### 🟡 Agregar passphrase a `livskin-vps-erp.ppk` al cerrar Fase 2
Durante Fase 1-2 la `.ppk` no tiene passphrase (decisión consciente por fricción de setup). Al terminar Fase 2 (cutover ERP completo), agregarle passphrase y guardar en Bitwarden.

**Cómo:** PuTTYgen → Load → tipear nueva passphrase + confirm → Save private key.  
**Fase sugerida:** cierre de Fase 2 (semana 4)  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Agregar IP de laptop de trabajo de Dario al whitelist Fail2Ban
La IP pública actual (`78.208.67.189`) es solo de la laptop personal en Milán. Cuando Dario conecte desde la laptop de trabajo por primera vez, si Fail2Ban la banea automáticamente, lo arreglamos y agregamos esa IP al `ignoreip` en `/etc/fail2ban/jail.d/ignoreip.local` en los 3 VPS.

**Fase sugerida:** cuando aparezca por primera vez (reactivo)  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Limpiar `/srv/livskin/` en VPS 3 (carpeta vieja pre-migración)
El 2026-04-20 se migraron los containers de `/srv/livskin/<svc>/` a `/srv/livskin-revops/infra/docker/<svc>/` como parte del setup de CI/CD. La carpeta vieja `/srv/livskin/` (postgres-data, embeddings-service, nginx) quedó como backup temporal.

**Cuándo borrarla:** después de 24-48h de operación estable desde la nueva ubicación (probable: 2026-04-22).  
**Cómo:** SSH a VPS 3 → `sudo rm -rf /srv/livskin/postgres-data /srv/livskin/embeddings-service /srv/livskin/nginx` (preservando `/srv/livskin/` mismo por si se necesita para algo futuro, o borrar todo si ya no tiene uso).  
**Agregado por:** Claude Code · 2026-04-20

---

### 🔴 Borrar snapshot VPS 3 cuando Fase 1 esté estable
Snapshot `livskin-vps-erp-baseline-post-hardening-2026-04-19` cuesta ~$3/mes si se mantiene permanente. Debe borrarse cuando la Fase 1 esté operativamente estable (típicamente 1-2 semanas post-deploy sin incidentes). Mientras tanto es cobertura por si algo falla y necesitamos rollback al estado pre-Postgres.

**Cuándo borrarlo:** ~2 semanas después de que Postgres + embeddings service estén corriendo sin incidentes (probable fecha: semana del 2026-05-03).  
**Dónde:** DO panel → droplet livskin-vps-erp → Backups & Snapshots → Delete.  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟢 Configurar email para `livskin.site` (MX + SPF + DKIM + DMARC)
Cloudflare alerta sobre falta de MX records. No bloquea nada operativo, pero:
- Sin MX: nadie puede mandar email a info@livskin.site, doctora@livskin.site, etc.
- Sin SPF/DKIM/DMARC: spammers pueden suplantar @livskin.site (afecta deliverability de marketing)

**Decisiones pendientes:**
- ¿Email propio en livskin.site? ¿O solo usan Gmail/Yahoo personales?
- Si sí: ¿qué proveedor? Google Workspace ($6/user/mes), Zoho Mail ($1/user/mes), ProtonMail (más caro), o self-hosted (descartado — dolor de cabeza para PYME)
- Dario confirma si necesita este canal de comunicación formal

**Fase sugerida:** no crítico hasta lanzamiento comercial formal. Si se decide email propio, 30 min de setup.  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Crear Dossier ADR-0019 (tracking architecture) en versión full
Actualmente es stub en el index. Al llegar a Fase 3 debe escribirse completo. Incluye server-side tracking, eventos, consent, match quality targets.

**Referencia:** docs/decisiones/README.md línea 0019  
**Fase sugerida:** Fase 3 (Semana 5)  
**Agregado por:** Claude Code · 2026-04-18

---

### ❓ Confirmar nombre del repo GitHub del ERP Livskin
La usuaria mencionó que el ERP tiene su propio repo GitHub. Necesario al llegar a Fase 2 para clonarlo en `erp/` local.

**Referencia:** ADR-0023 (ERP refactor)  
**Acción:** preguntar a Dario en próxima sesión  
**Agregado por:** Claude Code · 2026-04-18

---

### 🟡 Definir las 5-10 FAQs típicas de pacientes para Layer 1 del cerebro
Para poblar `clinic_knowledge` con las preguntas que más hacen los pacientes + respuesta autoritativa validada por la doctora.

**Referencia:** ADR-0001 sección 7.1  
**Fase sugerida:** Fase 2 (Semana 3-4)  
**Necesita input de:** la doctora  
**Agregado por:** Claude Code · 2026-04-18

---

## Mediano plazo

### 🟡 Plugin de WordPress para tracking server-side
Evaluar si hay plugin WP open-source que nos ayude con UTM persistence + server-side event forwarding, o si construimos script custom mínimo.

**Referencia:** ADR-0021 (UTMs persistence)  
**Fase sugerida:** Fase 3  
**Agregado por:** Claude Code · 2026-04-18

---

### 🟢 Explorar Dataview plugin de Obsidian para dashboards de proyecto
Dataview permite escribir queries SQL-like sobre frontmatter YAML de los .md. Podríamos generar "estado actual de todos los ADRs" en una tabla viva dentro de Obsidian.

**Fase sugerida:** Fase 0-1 (cuando Obsidian esté instalado)  
**Agregado por:** Claude Code · 2026-04-18

---

## Ideas (brainstorm, sin decisión aún)

### 💡 Integrar Pipedream o similar como redundancia de n8n
Si n8n cae, Pipedream podría actuar como failover para webhooks críticos (form submit). No urgente pero vale la pena evaluar.

**Agregado por:** Claude Code · 2026-04-18

---

### 💡 Caso de estudio público para LinkedIn
Al terminar Fase 6 (mes 2-3 de operación estable), publicar case study técnico: "Cómo construí un sistema RevOps multi-agente en 10 semanas solo con Claude Code". Material excelente para portfolio RevOps.

**Agregado por:** Claude Code · 2026-04-18

---

## Dudas abiertas

### ❓ ¿Livskin emite comprobantes electrónicos a SUNAT hoy?
Si ya factura electrónicamente, necesitamos integración con PSE (Nubefact, Efact, etc.). Si no, decisión de negocio diferida.

**Trigger para responder:** cuando Dario decida estrategia fiscal  
**Relacionado:** ADR-0099 (SUNAT — diferido)  
**Agregado por:** Claude Code · 2026-04-18

---

### ❓ ¿La clínica imprime recibos físicos a pacientes?
Condiciona si necesitamos módulo PDF/impresión en ERP.

**Relacionado:** ADR-0103 (PDFs — diferido)  
**Agregado por:** Claude Code · 2026-04-18

---

## Hecho (historial)

<!-- Los items completados se mueven aquí para mantener historial. No se borran. -->

### ✅ Audit minucioso VPS + integridad + flujos + items diferidos (2026-04-29)
Audit comprehensive post-cleanup del Mini-bloque 3.3 fallido. Verificado: VPS 1/2/3 healthy (uptime, disk, memory, services). Mini-bloques 3.1+3.2 intactos (curl + GTM API + GA4 events últimas 48h). Backups daily working post-instalación cron. Audit log immutable trigger funcional. Brain pgvector 1,765 chunks indexados. 3 issues menores deferidos a Mini-bloque 3.5 (sensor VPS 2 unhealthy flag, sensor VPS 1 Docker WARNING, system-map staleness por cron recolector cross-VPS no instalado). Output: [docs/audits/2026-04-29-audit-vps-integridad-flujos-deferred.md](audits/2026-04-29-audit-vps-integridad-flujos-deferred.md). 2026-04-29.

### ✅ Cleanup de organización + ADR-0030 file naming conventions + memorias reorganizadas (2026-04-29)
Tras Mini-bloque 3.3 fallido (Form→ERP directo), se ejecutó: (a) reversión completa del experimento (2 commits + mu-plugin VPS 1 + leads test ERP DB); (b) reorganización memorias por criticidad con header anti-overload; (c) 2 nuevas memorias 🔥 críticas (`project_n8n_orchestration_layer`, `feedback_must_re_read_adrs_before_coding`); (d) runbook `preflight-cross-system.md` cross-linked desde cierre-sesion; (e) ADR-0030 file naming conventions; (f) `infra/docker/_legacy/` con README + período de gracia; (g) `.gitignore` actualizado con `Senza nome*.canvas`. Backups cron VPS 3 instalado y verificado funcional. 2026-04-29.

### ✅ Fase 3 Mini-bloque 3.2 — GTM Tracking Engine + UTM persistence + dedup events (2026-04-28)
GTM v18 LIVE con 8 tags + 3 triggers + 17 variables. Tracking Engine JS de 95 líneas hace UTM persistence + form submit listener + WhatsApp click listener + event_id único para CAPI dedup. Validated end-to-end con Dario en DevTools (cookies persistidas, whatsapp_click con event_id + UTMs en dataLayer, scroll_75 disparado). ADR-0021 cerrada. Commit `f31cd93`. Doc: [docs/audits/mini-bloque-3-2-tracking-engine-2026-04-28.md](audits/mini-bloque-3-2-tracking-engine-2026-04-28.md).

### ✅ Fase 3 Mini-bloque 3.1 — Limpieza VPS 1 (2026-04-28)
LatePoint + PixelYourSite desactivados (resuelve doble disparo Pixel). Cloudflare Turnstile en SureForms 1569 (native) + plugin para login form (bot bloqueado). 3 social links arreglados (WhatsApp +51982732978 + Instagram + Facebook). Pixel legacy 670708374433840 saltado (Meta no permite archivar UI). 75 min. Commit `dbf5819`. Doc: [docs/audits/mini-bloque-3-1-cleanup-vps1-2026-04-28.md](audits/mini-bloque-3-1-cleanup-vps1-2026-04-28.md).

### ✅ Audit programmatico Google ejecutado (2026-04-27)
OAuth user flow setup + scripts reusables (`scripts/google_oauth_setup.py` + `scripts/google_audit.py`) + audit completo: 5 GA4 accounts detectadas, código exacto del tag GTM `Pixel Meta - Config` extraído, **doble disparo Pixel CONFIRMADO con código real** (no hipótesis), GA4 events últimas 48h visibles. Bot scraping detectado en form. Doc: [docs/audits/audit-google-stack-2026-04-27.md](audits/audit-google-stack-2026-04-27.md).

### ✅ Setup OAuth Google con refresh token persistente (2026-04-27)
Pivot de service account a OAuth user flow tras GA4/GTM admin UIs rechazaran service account email (limitación cuentas sin Workspace). Refresh token en `keys/google-oauth-token.json`. Scopes: analytics.readonly + tagmanager.readonly. Validado funcionando.

### ✅ Audit cross-VPS real ejecutado (2026-04-26)
Audit exhaustivo SSH-based de los 3 VPS + verificación stack Google/Meta vía screenshots. Hallazgos clave: VPS 1 ya tiene GTM + GA4 + Pixel funcionando con doble disparo; VPS 2 vacío (0 workflows, 0 leads); VPS 3 sólido con 134 clientes productivos. Doc: [docs/audits/estado-real-cross-vps-2026-04-26.md](audits/estado-real-cross-vps-2026-04-26.md).

### ✅ Decisión arquitectónica módulo Agenda en ERP (2026-04-26)
Tras evaluar 3 opciones (Vtiger / ERP / WhatsApp inferred), cerrada Opción B: ERP gana módulo Agenda con tabla `appointments`. Doctora marca asistencia. Vtiger redefinido a marketing automation. Detalle en session log.

### ✅ Decisión arquitectura tracking 2-capas single-source (2026-04-26)
Capa client = GTM única fuente; capa server-CAPI desde ERP. Pixel viejo a archivar. Plan migración en mini-bloques de Fase 3.

### ✅ Runbook estandarizado de cierre de sesión (2026-04-26)
[docs/runbooks/cierre-sesion.md](runbooks/cierre-sesion.md) — 11 pasos + filosofía + checklist + cuándo NO ejecutar. Evolutivo. Resuelve fricción de re-pensar el cierre cada sesión.

### ✅ Fase 0 — Repo reorganizado + 3 dossiers + master plan
Completada 2026-04-18. Ver session log correspondiente.

### ✅ ADR-0005 simplificada a "n8n único orquestador"
Originalmente aprobada como híbrido; revisada por Dario en misma sesión. Agent SDK diferido.
2026-04-18.

### ✅ Obsidian integrado al plan como capa humana del segundo cerebro
Dario propuso, se aprobó, se actualizó ADR-0001 con sección 9.2.
2026-04-18.

### ✅ VPS 3 provisionado y hardened
`livskin-vps-erp` @ 139.59.214.7 (VPC 10.114.0.4). Ubuntu 22.04.5, Docker 29.4.0, swap 2GB, UFW+Fail2Ban+unattended-upgrades activos. Lynis score 65/100. VPC connectivity a VPS 1 y 2 verificada (<2ms).
2026-04-19. Ver `docs/sesiones/2026-04-19-fase1-vps3-creado.md`.

### ✅ Whitelist Fail2Ban con ignoreip
Tras incidente de auto-ban en instalación de UFW: whitelist permanente creada en `/etc/fail2ban/jail.d/ignoreip.local` con 127.0.0.1/8, ::1, 10.114.0.0/20 (VPC), 78.208.67.189 (Dario Milan). 2026-04-19.

### ✅ CI/CD workflow extendido a stack ERP completo
Commit `7eb2d63` (2026-04-26). Workflow `.github/workflows/deploy-vps3.yml` ahora cubre: erp-flask con `--build`, alembic-erp + brain-tools `build only`, nginx `-s reload` tras cambios de config, retry verify de URLs públicas (3 intentos × 5s, sleep inicial 20s). Resuelve además el item original "Workflow CI/CD: agregar nginx reload" (2026-04-20).

### ✅ ERP refactorizado deployed funcional con data real
Commits del 2026-04-26 (`815cb0b` → `7eb2d63`). Stack: Flask + SQLAlchemy 2.0 + Pydantic v2 + structlog + gunicorn. Migration 0001 (12 tablas) + 0002 (trigger DEBE) aplicadas. Backfill ejecutado: 134 clientes + 88 ventas + 84 pagos del Excel productivo. URL `https://erp.livskin.site` responde con formulario funcional. Auditoría profunda Flask original cerró 11 de 13 gaps. Capa compat form-data preserva HTML legacy. 2026-04-26.

### ✅ erp-staging.livskin.site eliminado (decisión Opción A)
Durante Fases 2-5 el ERP nuevo está en validación interna (Render sigue siendo producción). Tener un staging del que ya está en validación era redundante. Staging real con DB separada se reabrirá en Fase 6 al hacer cutover real (ADR-0024 strangler fig). Commit `59e37c2`. DNS Cloudflare borrado por Dario. 2026-04-26.

### ✅ Auth bcrypt + login/logout + sesiones (ADR-0026)
Commit `87c07b5`. Stack: bcrypt 12 rounds, sesión 48h con auto-revoke por 2h inactividad, lockout 8 intentos / 15 min. 2 cuentas seedadas: Dario (admin) + Claudia Delgado (operadora). Templates login.html + change_password.html. Middleware Flask before_request protege todas las rutas excepto allowlist (login, logout, ping, static). CurrentUser dataclass desacoplado de SQLAlchemy session. Decorator @require_role para granularidad por rol. Passwords iniciales generadas + entregadas + cambiadas (Dario hizo su primer cambio). 2026-04-26.

### ✅ Audit log middleware + 30 eventos canónicos (ADR-0027)
Commit `75683c6` + migration 0003 (`0003_audit_immutable`). Trigger PL/pgSQL `audit_log_immutable()` rechaza UPDATE/DELETE a nivel DB (verificado: ni superuser puede modificar). AuditService.log() escribe entry atómicamente con la business logic dentro del session_scope. AuditService.log_isolated() para flujos donde el principal ya falló. 30 KNOWN_ACTIONS canónicos en 7 categorías (auth, venta, pago, gasto, cliente, lead, admin, webhook). Hooks instalados en auth (login_success/failed/lockout/logout/expired/inactivity/password_changed) + legacy_forms (venta/pago/gasto created con before/after states). Captura automática de IP, user-agent, user_id, user_role via flask.g + request. 2026-04-26.

### ✅ Dashboard /admin/audit-log con filtros + export CSV
Commit `9d72a60`. Tabla paginada (50/pag, max 500). Filtros: rango fechas, action, category, user, result, entity_id (búsqueda parcial). Export CSV respeta filtros, max 10000 filas, incluye before/after/metadata como JSON. UI minimalista con tags por categoría. @require_role("admin") protege endpoints (403 para Claudia). Header del formulario.html muestra link "audit log" solo para admin. Dropdowns muestran TODAS las categorías canónicas (no solo las que ya tienen entries) — fix `0dc52f5`. 2026-04-26.

### ✅ Test coverage 81.31% (target ADR-0023: ≥75%)
Commits `b7acedb` → `6450ae0`. 186 tests pasan en 76s. Cubre: auth_service (99%), audit_service (88%), cliente_service (87%), venta_service (93%), pago_service (93%), catalogo_service (100%), libro_service (100%), codgen_service (100%), middleware (100%), schemas (100%). Tests routes para auth + admin + legacy_forms + API JSON. CI/CD workflow ahora corre pytest post-deploy automáticamente (commit `6450ae0`). Conftest pattern: TRUNCATE-based cleanup, fixtures admin_user/operadora_user committeadas para que session_scope() las vea, db_session separada. DB livskin_erp_test creada en Postgres VPS 3. 2026-04-26.

---

## Cómo agregar una entrada nueva

Copia esta plantilla:

```markdown
### <icono> <título>
<Descripción breve — qué, por qué, qué falta>

**Referencia:** ADR-XXXX o doc relevante  
**Fase sugerida:** Fase N  
**Necesita input de:** <persona o "ninguno">  
**Agregado por:** <Dario | Claude Code> · YYYY-MM-DD
```

Y ubícala en la sección correcta según prioridad.
