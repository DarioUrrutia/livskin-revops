# Sesión 2026-04-26 — Audit cross-VPS real + arquitectura tracking + módulo Agenda ERP

> **Continuación de:** [2026-04-26-bloque-foundation-activacion-produccion.md](2026-04-26-bloque-foundation-activacion-produccion.md)
> **Tipo:** Estratégica + audit
> **Duración:** ~3 horas
> **Próxima:** Setup acceso programático (Google + Meta) + auditoría definitiva con APIs

---

## Contexto inicial

Misma sesión continuó tras cerrar el Bloque 0 v2 con tag `v0.foundation` push. Claude propuso pasar a Fase 3 (tracking + observabilidad), planteándolo como instalación greenfield de Pixel + GA4 + GTM.

**Dario corrigió fuerte:** "antes de hacer algo, has revisado como te dije mi vps1 donde esta wordpress, porque me hablas de instalar cosas como google tag manager, o pixel o cosas asi, yo recuerdo que ya estan, a mi parecer no has hecho una investigacion exahustiva de el estado de las cosas, por eso hablas asi, es mas te pedi hacer eso para todos los vps".

Esa corrección gatilló todo lo demás de la sesión.

---

## Lo que se hizo

### 1. Audit exhaustivo cross-VPS por SSH

Verificación en vivo, no por screenshots ni asunciones:

**VPS 1 (livskin-wp):**
- 9 plugins instalados, 8 activos. Identificado código fuente real cargado en `https://livskin.site/`.
- **GTM `GTM-P55KXDL6` LIVE** disparando en home (script directo en `</body>`).
- **PixelYourSite** plugin activo con Pixel ID `4410809639201712` + token CAPI configurado (descubierto recién con screenshot que envió Dario).
- **SureForms** form `1569` ("Formulario pagina Inicio") visible en home con 5 campos (Nombres, Email, Teléfono, Tratamiento dropdown 8 opciones), 0 entries DB.
- **LatePoint** activo con servicios DEMO (Luxury Spa, Stone Therapy…) — no servicios reales de Livskin.
- **Complianz GDPR** configurado con region BR, datos Livskin, gtm_code = `GTM-P55KXDL6`.
- WhatsApp link CTA: `api.whatsapp.com/send?phone=` ← **número vacío, link roto**.

**VPS 2 (livskin-vps-operations):**
- 7 containers UP (n8n, vtiger, vtiger-db, metabase, postgres-analytics, nginx, livskin-sensor).
- **n8n: 0 workflows** (vacío).
- **Vtiger DB existe pero VIRGEN**: 0 leads, 0 contacts, 0 opportunities, 1 user admin.
- **postgres-analytics**: 4 tablas (events, leads, opportunities, crm_stages) con 0 filas cada una.
- **Metabase healthy** (`/api/health` 200), volúmenes en docker named (no host bind → simplifica migrate-from-home).
- Compose files nuevos en `/srv/livskin-revops/infra/docker/vps2-ops/` listos pero containers actuales aún montan desde `/home/livskin/apps/` (migración pendiente).

**VPS 3 (livskin-vps-erp):**
- 4 containers healthy (erp-flask, nginx-vps3, embeddings-service, postgres-data).
- **livskin_erp**: 17 tablas, 134 clientes / 88 ventas / 84 pagos cargados. audit_log con 8 entries (incluyendo `infra.deploy_completed` post-fix).
- **livskin_brain**: 7 tablas + pgvector 0.8.2 + pgcrypto. Schema listo, contenido vacío.
- Block 0 v2 confirmado completo, audit pipeline operativo.

**Externos verificados:**
- Cloudflare proxying livskin.site ✅
- Render `formulario-livskin.onrender.com` vivo, SIN tracking instalado.
- GTM container live en home.
- Audit doc completo en [docs/audits/estado-real-cross-vps-2026-04-26.md](../audits/estado-real-cross-vps-2026-04-26.md).

### 2. Audit Google + Meta vía screenshots de Dario

- **GA4**: Property "Livskin", Measurement ID `G-9CNPWS3NRX`, **data flowing últimas 48h** ✅. Enhanced Measurement ON.
- **GTM**: container `GTM-P55KXDL6` con 2 tags creados:
  - `GA - Config` (Etiqueta de Google) → trigger All Pages
  - `Pixel Meta - Config` (HTML personalizado)
  - "Cambios del espacio: 1" → cambios sin publicar.
- **Meta Business Manager** "Livksin Perú" (ID `444099014574638`) con 2 datasets:
  - `Livksin Pixel 2026` (ID `4410809639201712`) — el bueno
  - `Livksin Pixel` (ID `670708374433840`) — viejo con warning ⚠️
  - Diagnóstico (1) pendiente
- **Google Ads**: cuenta `216-312-4950` Livskin Centro, PEN, Peru TZ. **0 campañas** activas.
- **PixelYourSite**: descubierto que **SÍ tiene Pixel ID + token CAPI configurado**, contradiciendo audit inicial.

### 3. Diagnóstico arquitectónico del problema real

El "Diagnóstico (1)" de Meta Events Manager es casi seguro **eventos duplicados**: el Pixel se está disparando desde DOS fuentes simultáneas:
- Plugin PixelYourSite (client-side `fbq()` + server-side CAPI desde PHP)
- GTM tag "Pixel Meta - Config" (client-side custom HTML)

Cada PageView se manda 2 veces a Meta. No rompe nada (Meta deduplica si event_id coincide), pero degrada match quality y enmascara métricas reales.

### 4. Decisión arquitectónica: tracking 2-capas single-source

Discutido y cerrado:
- **Capa 1 (client-side)**: una sola fuente. Recomendado **GTM como única fuente** (industria estándar, flexible, no atado a WordPress). Plugin PixelYourSite se desactivará. Tag GTM "Pixel Meta - Config" se afina + se publica versión.
- **Capa 2 (server-side CAPI)**: emitida desde **VPS 3 ERP**, NO desde WordPress. Razón: el ERP es el SoT operativo de conversiones reales (cita agendada, asistida, venta cerrada) — eventos que WordPress nunca verá. CAPI desde ERP supera al CAPI de PixelYourSite porque tiene email/teléfono real → match quality alto.
- **Pixel viejo `670708374433840`**: archivar. Único Pixel activo será `4410809639201712`.

### 5. Decisión: módulo Agenda en ERP (Opción B)

Pregunta crítica que abrió Dario: ¿dónde vive la cita agendada? Hoy la doctora la lleva en su cabeza/calendario personal. No hay sistema.

**3 opciones evaluadas:**
- A. Vtiger como SoT del calendario (CRM-standard pero la doctora no va a abrir Vtiger todos los días)
- B. ERP gana módulo Agenda (la doctora ya entra al ERP a facturar — sumamos agenda allí)
- C. Inferir estado desde mensajes WhatsApp (frágil, viola Principio 10)

**Decisión: Opción B confirmada por Dario.** Razones:
- Coincide con workflow real de la doctora (entra a ERP a diario)
- ERP es 100% bajo nuestro control (vs Vtiger atado a sus decisiones)
- Métricas de funnel (lead → cita → venta) en una sola DB → queries simples
- Server-side CAPI desde ERP necesita estos datos disponibles

Dario añadió requisito clave: **"precisión quirúrgica"** al ampliar ERP. Ya hay 134 clientes + 88 ventas reales en producción interna. El módulo nuevo NO puede romper nada existente.

### 6. Refinamiento del rol de Vtiger

CLAUDE.md decía "Vtiger = master del lead digital". Refinado:
- **Vtiger = master del journey de marketing del lead** (campañas drip, scoring, nurture flows)
- **ERP = master del journey operativo del lead** (lead → cita → asistido → cliente → venta → pago)
- **Brain = conocimiento clínico** (FAQs, tratamientos, preferencias)

Vtiger queda como CONSUMIDOR de eventos de marketing, no fuente. Lee del ERP, no escribe.

### 7. Decisión: subir a acceso programático completo

Hasta hoy, audit por screenshot tiene techo. Para resolver definitivamente fricciones cross-stack (UTMs llegan limpios del ad → site → form → DB?, event_ids coinciden client + server?, consent-mode respetado?), Claude necesita acceso vía API a:
- Google (GA4 + GTM + Ads)
- Meta (Pixel + Business + Ad accounts)
- Cloudflare (después)

Dario aprobó proceder con setup en próxima sesión. Plan:
- Setup 1: Google service account + JSON key en `keys/google-claude.json` (gitignored). Read-only en GA4 + GTM + Ads.
- Setup 2: Meta System User + token en `keys/.env.integrations`. Read-only en Pixel + Business + Ads.
- Después de setups: audit programático real → reporte definitivo.

### 8. Gobernanza de agentes — principios reiterados por Dario

Dario reforzó su posición sobre los agentes IA:
- "Procesos antes de libertad" — automatizaciones determinísticas primero, LLM solo donde realmente requiere lenguaje natural
- Mitigar alucinaciones — guardrails determinísticos que validen outputs antes de enviar
- "Yo al mando" — estructura organizacional con humano como CEO
- Presupuesto que no se puede perder — hard limits, no soft (ya implementado en Bloque 0.10)
- Validación → eval suite continua antes de cualquier deploy de cambio de prompt

### 9. Estandarización del cierre de sesión

Dario pidió convertir el cierre de sesión en estándar para no re-pensarlo cada vez. Resultado: nuevo runbook en [docs/runbooks/cierre-sesion.md](../runbooks/cierre-sesion.md) con:
- Filosofía + cuándo aplica
- Protocolo paso a paso (11 pasos)
- Checklist abreviado
- Cuándo NO ejecutar completo
- Evolución del runbook como artefacto vivo

---

## Decisiones tomadas (con su "por qué")

1. **Capa client-side single source = GTM** (no plugin PixelYourSite).
   *Por qué:* industria estándar, flexible, no atado a WordPress, eventos finos que el plugin free no soporta.

2. **Capa server-side CAPI emite desde ERP, no desde WordPress.**
   *Por qué:* ERP tiene los eventos reales del funnel (cita, venta) que WordPress nunca verá. ERP tiene email/teléfono real → match quality superior.

3. **Pixel `670708374433840` se archiva**, único activo será `4410809639201712`.
   *Por qué:* eliminar fuente de duplicación + ruido en métricas.

4. **Módulo Agenda vive en ERP (Opción B)**, no Vtiger.
   *Por qué:* doctora ya entra al ERP a diario, schema bajo nuestro control, métricas funnel en una DB.

5. **Vtiger = motor de marketing automation**, no SoT operativo.
   *Por qué:* refinamiento del modelo SoT-por-dominio. ERP gana el journey operativo.

6. **Construcción del módulo Agenda con "precisión quirúrgica"**:
   - ADR aprobado antes de migración
   - Tests pytest primero, código después
   - Endpoints aislados (nuevo blueprint, NO toca rutas existentes)
   - Feature flag inicial (`settings.agenda_enabled`)
   - Migración Alembic 100% reversible (upgrade + downgrade simétricos)
   - Validación con doctora con 5 citas de prueba antes de quitar flag
   - Documentación viva en `docs/runbooks/agenda-mantenimiento.md`

7. **Setup acceso programático completo en próxima sesión**, antes de tocar tracking/CAPI/eventos en serio.

8. **Cierre de sesión estandarizado** como runbook ejecutable, evolutivo.

---

## Hallazgos relevantes

- El sitio livskin.site **YA tiene** GTM + GA4 + Pixel funcionando (no greenfield).
- Hay **doble disparo de Pixel** (plugin + GTM) — origen del Diagnóstico 1 de Meta.
- Hay **2 Pixels** en Meta Business — el viejo debe archivarse.
- Vtiger está **completamente vacío** (0 leads/contacts/opps).
- n8n está **completamente vacío** (0 workflows).
- postgres-analytics está **completamente vacío** (0 filas en 4 tablas).
- ERP tiene **datos reales productivos** (134 clientes, 88 ventas, 84 pagos).
- LatePoint tiene **servicios demo**, no se va a usar (Dario decidió desactivar).
- Form Render `formulario-livskin.onrender.com` **NO está enlazado desde livskin.site** — el form de captura visible en home es SureForms 1569.
- Dario no recuerda por qué tiene 2 pixels — likely intentó GTM primero, no le funcionó visiblemente, fue al plugin como backup, ambos quedaron live.

---

## Lo que queda pendiente (próximas sesiones)

### Próxima sesión inmediata (60-90 min)
- **Setup acceso programático** completo (Google + Meta service accounts + tokens)
- **Auditoría programática real** vía APIs:
  - Resolver definitivamente el misterio de los 2 pixels con datos
  - Confirmar UTMs llegan limpios al form y a DB
  - Inspeccionar código exacto del tag GTM "Pixel Meta - Config"
  - Pulleo eventos GA4 últimas 48h
  - Verificar match quality del Pixel
- **Reporte final**: `docs/audits/audit-tracking-stack-real-2026-04-XX.md`
- **ADR cerrado**: `docs/decisiones/00XX-arquitectura-tracking-client-server.md`

### Después (Fase 3 mini-bloques)
1. Limpieza VPS 1: desactivar PixelYourSite + LatePoint + archivar Pixel viejo + fix CTA WA
2. GTM event tagging: form_submit, whatsapp_click, scroll milestones + UTM persistence + click ID capture (gclid/fbclid/ttclid) + publicar versión
3. Form → ERP webhook: SureForms 1569 → POST `/api/leads/intake` → INSERT en `leads` table + push a Vtiger
4. CAPI server-side desde ERP + GA4 Measurement Protocol server-side

### Bloque puente (entre Fase 3 y Fase 4)
- **Módulo Agenda Mínima en ERP** (3-4 sub-sesiones):
  - ADR redactado y aprobado
  - Schema `appointments` (11 campos)
  - Migración Alembic 0005
  - 3 vistas UI: agenda hoy / semana / cita detalle
  - Tests pytest (mantener coverage ≥80%)
  - Validación con doctora (5 citas de prueba)
  - Runbook agenda-mantenimiento.md

### Fase 4
- Conversation Agent en WhatsApp test number
- Bot agenda automáticamente en `appointments`
- Eval suite continua

---

## Próxima sesión propuesta

**Setup acceso programático + auditoría definitiva.**

Llega Claude preparado con:
- URLs exactas para crear service account Google
- URLs exactas para crear System User Meta
- Lista de scopes exactos para read-only en cada API
- Script de validación post-setup

Tiempo estimado: 60-90 min total (paso-a-paso al estilo GitHub Secrets).

Output: audit programático real + decisiones arquitectónicas tracking en ADR + plan ejecutable de Fase 3 mini-bloques con orden y tiempos.

---

**Cerrada por:** Claude Code · 2026-04-26 (~22:00 hora Milán, fin del día Dario)
