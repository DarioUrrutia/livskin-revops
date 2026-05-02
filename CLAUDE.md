# CLAUDE.md — Contexto maestro del proyecto Livskin

> Este archivo es leído automáticamente por Claude Code al iniciar cada sesión.  
> Su propósito: cargar en memoria el contexto operativo suficiente para trabajar sin fricción.  
> Última actualización: **2026-05-03 v3.0 (PIVOT ESTRATÉGICO — Doctrina "deterministic backbone first" elevada a principio operativo #11; audit honesto reduce scope agentes 5→1+2 scripts; Bridge Episode primera campaña paga FB Ads insertado entre Fase 3 cerrada y Fase 4 reescrita; ADR-0034 Conversation Agent IA → 💤 diferida)**

---

## 🧭 Quiénes somos y qué construimos

**Proyecto:** sistema RevOps con IA para **Livskin**, clínica de medicina estética en Wanchaq, Cusco, Perú.

**Usuaria:** Dario (Economista + MBA, residente en Milán). Principiante técnica, estilo "vibe coding". No escribe código — dirige, revisa, aprueba. Claude Code ejecuta ~80% del código.

**Doble objetivo:**
1. Operacional — sistema que responde leads en <60s, reactiva pacientes, gestiona campañas IA, libera tiempo humano, atribuye revenue a canal.
2. Portfolio — material de caso de estudio para transición a rol RevOps de clase mundial ($140-220K USD).

---

## 🔑 Referencias obligatorias al iniciar sesión

Lee en este orden antes de cualquier tarea sustantiva:

1. **[docs/sistema-mapa.md](docs/sistema-mapa.md)** — ⭐ system-map machine-readable autoritativo (Bloque 0.3) — VPS/containers/dependencias/SPOFs
2. **[docs/master-plan-mvp-livskin.md](docs/master-plan-mvp-livskin.md)** — plan maestro vivo
3. **[docs/audit-events-schema.md](docs/audit-events-schema.md)** — schema de los 49 eventos auditables (Bloque 0.8)
4. **[docs/runbooks/README.md](docs/runbooks/README.md)** — 12 runbooks ejecutables + DR drill procedure (Bloque 0.6 + 0.7)
5. **[skills/README.md](skills/README.md)** — capacidades AI-operables (livskin-ops + livskin-deploy)
6. **[docs/decisiones/README.md](docs/decisiones/README.md)** — index de 40+ ADRs con estado
7. **[docs/backlog.md](docs/backlog.md)** — backlog vivo
8. **[docs/sesiones/](docs/sesiones/)** — último log de sesión
9. **Blueprint original** — [docs/livskin_pensamientos para una implemetacion profesional basica pero basada en ia.docx](docs/livskin_pensamientos%20para%20una%20implemetacion%20profesional%20basica%20pero%20basada%20en%20ia.docx)
10. **Memoria Claude Code** — autoload (`user_profile`, `project_roadmap`, `project_stack`, etc.)

---

## 🎯 Principios operativos — no negociables

1. **Lo ejecutable supera a lo ideal.** Sistema 7/10 que se termina > 10/10 que se abandona.
2. **Tiempo humano es el recurso más caro.** >1h/día manual = mal diseñado.
3. **Una fuente de verdad por dominio.** No duplicar data sincronizada.
4. **Observabilidad desde el día uno.** Sin métricas no hay optimización.
5. **Reversibilidad de decisiones.** Arquitectura debe poder cambiarse sin reescribir todo.
6. **Respeto al equipo humano.** Refactor por dentro, UX igual por fuera.
7. **Honestidad técnica radical.** Dudas y riesgos documentados, no escondidos.
8. **Cero servicios pagos nuevos sin aprobación explícita.** Prioridad: self-hosted > cross-VPS > SaaS free > pago.
9. **Antes de implementar, definir.** Dossier aprobado + dependencies resueltas + exit criteria.
10. **Responder a la profundidad pedida.** Táctica → concisa. Estratégica → comprehensiva.
11. **Deterministic backbone first — IA es capa aditiva, no foundational.** El sistema debe operar 100% sin agentes IA. Si todos los agentes se apagan, la operación sigue. La IA se agrega sobre infraestructura validada con datos de campañas reales, no sobre hipótesis. Antes de aprobar un agente: aplicar filtro de 6 checks (memoria `project_agent_scope_audit_2026_05_03`). Articulado por Dario el 2026-05-03 tras audit honesto que reveló sobre-engineering del agent design original (5 agentes → 1 agente real + 2 scripts).

---

## 📂 Estructura del repo

```
Union VPS - Maestro - Livskin/           ← este folder = hub central
│
├── CLAUDE.md                            ← este archivo
├── README.md                            ← instrucciones humanas
├── .gitignore                           ← excluye secretos, keys, erp/, backups/
├── .claude/settings.json                ← permisos: DENY Edit/Write en erp/
│
├── docs/
│   ├── master-plan-mvp-livskin.md       ← ⭐ plan autoritativo
│   ├── backlog.md                       ← 📋 backlog vivo de ideas/cambios/dudas
│   ├── decisiones/                      ← ADRs (Architecture Decision Records)
│   │   ├── README.md                    ← index vivo de 40+ dossiers
│   │   ├── _template.md                 ← plantilla para nuevos
│   │   ├── 0001-segundo-cerebro-*.md    ← dossiers fundacionales
│   │   ├── 0002-arquitectura-*.md
│   │   └── 0003-seguridad-*.md
│   ├── sesiones/                        ← log cronológico de sesiones
│   ├── audits/                          ← audits periódicos
│   ├── seguridad/                       ← políticas y runbooks seguridad
│   ├── runbooks/                        ← procedimientos operativos (incl. obsidian-setup)
│   ├── diagramas/                       ← diagramas de arquitectura
│   ├── system-audit-2026-04-16.md       ← audit histórico
│   ├── consultas-y-decisiones.md        ← bitácora sesión anterior
│   ├── Datos Livskin.xlsx               ← datos reales (74 ventas, 135 clientes)
│   └── livskin_pensamientos....docx     ← blueprint original
│
├── notes/                               ← notas colaborativas + personales (Obsidian)
│   ├── compartido/                      ← versionada, colaborativa
│   └── privado/                         ← ⚠️ gitignored, solo tuya
│
├── infra/                               ← infraestructura (era raíz, ahora agrupado)
│   ├── docker/                          ← compose files por servicio
│   │   ├── n8n/, vtiger/, metabase/, postgres/, nginx/
│   ├── nginx/                           ← configs nginx
│   ├── scripts/                         ← backup.sh, restore.sh
│   └── sql/                             ← schema.sql base
│
├── integrations/                        ← servicios externos
│   ├── meta/                            ← Meta Business, pixel, CAPI, ads
│   ├── google/                          ← GA4, GTM, Search Console
│   ├── whatsapp/                        ← Cloud API, test number, templates
│   ├── cloudflare/                      ← DNS, SSL, WAF
│   ├── canva/                           ← Brand Kit, API
│   ├── anthropic/                       ← Claude API, budget
│   ├── fal-ai/                          ← Flux Pro
│   └── claude-design/                   ← integración landing pages + banners
│
├── agents/                              ← 4 agentes IA
│   ├── conversation/
│   │   ├── prompts/                     ← versionados con semver
│   │   ├── tools/                       ← specs de tool-calling
│   │   └── evals/                       ← golden set y criterios
│   ├── content/
│   ├── acquisition/
│   └── growth/
│
├── analytics/                           ← warehouse + dashboards
│   ├── schemas/                         ← schema DDL analytics DB
│   ├── migrations/                      ← Alembic migrations
│   └── dashboards/                      ← exports JSON de Metabase
│
├── keys/                                ← ⚠️ gitignored
│   ├── claude-livskin (pub+priv)        ← SSH key
│   ├── ssh_config                       ← config SSH local
│   ├── .env.integrations                ← ⚠️ tokens API (respaldo en Bitwarden)
│   └── .ppk files                       ← conservados por referencia
│
├── erp/                                 ← ⚠️ gitignored, repo separado
│   └── livskin-formulario/              ← clon del ERP (si corresponde)
│
└── backups/                             ← ⚠️ gitignored, pulls manuales
```

**Reglas duras:**
- `erp/` está en `.gitignore` Y en `.claude/settings.json` con deny de Edit/Write. No se toca sin autorización explícita de la usuaria.
- `keys/` y `backups/` están en `.gitignore` y nunca se commitean.
- `docs/decisiones/` son ADRs inmutables una vez aprobados (solo se actualiza status).
- Todo commit sigue naming: `tipo: descripción` (feat, fix, refactor, docs, chore, test, security, perf).

---

## 🏗️ Stack definitivo (resumen)

| Capa | Tecnología |
|---|---|
| Cloud | DigitalOcean (Frankfurt) — 3 VPS (WP + Ops + **Data nueva**) |
| Red privada inter-VPS | **DigitalOcean VPC** (no Tailscale) |
| Edge | Cloudflare DNS + SSL + WAF |
| Containerización | Docker + Compose + GitHub Actions CI/CD |
| CRM | Vtiger 8.2 (master del **lead digital** — marketing automation solamente) |
| ERP | Flask refactorizado (master de **cliente + transacciones**, 2 cuentas: tú + doctora) |
| Orquestación | n8n 2.14 (+ Agent SDK solo si necesario) |
| Data OLTP | MariaDB (WP, Vtiger) + Postgres (ERP) |
| Data OLAP | Postgres 16 + pgvector (analytics + segundo cerebro) |
| IA | Claude API (4 agentes) + Claude Design + fal.ai + Canva API |
| Embeddings | `multilingual-e5-small` (self-hosted, $0) |
| Tracking | Meta Pixel + CAPI + GA4 + MP + GTM |
| Canal | WhatsApp Cloud API (**test number en desarrollo**) |
| Observabilidad | Langfuse + Metabase + logs estructurados |

**NO usamos:** Airtable, Zapier/Make, HubSpot/Salesforce, Descript, LatePoint, S3/R2/B2, Tailscale, Pinterest/Bing/Reddit pixels.

---

## 🗺️ Roadmap — estado actual (v3.0 post-audit 2026-05-03)

| Fase | Estado |
|---|---|
| 0 | ✅ Completada (2026-04-18) |
| 1 | ✅ Completada (2026-04-20) |
| 2 | ✅ Implementación ~99% (auth + audit + dashboard + tests 81% coverage) |
| **Bloque 0 v2 (foundation cross-VPS)** | ✅ Completado 2026-04-26 |
| **Fase 3** | ✅ **CERRADA 2026-05-02** — 3.1 cleanup + 3.2 GTM + 3.3 form→Vtiger→ERP + 3.4 CAPI + 3.5 Metabase warehouse + 3.6 landings dedicadas |
| **Bloque 1 puente** | ✅ Completado 2026-05-02 — Match automático lead↔cliente (ADR-0033, 100% determinístico) |
| **🚀 BRIDGE EPISODE — Primera campaña paga** | 🆕 ARRANCANDO 2026-05-03 — FB Ads $100/5 días, 3 destinos (botox-mvp landing + prp-mvp landing nueva + WA directo doctora con shortcodes manuales). Captura data real para informar Fase 4 con datos. Detalle: `docs/campaigns/2026-05-first-campaign/plan.md` |
| **Fase 4 (REVISADA por audit 2026-05-03)** | ⏳ Post-Bridge Episode. **4A**: backbone determinístico restante (chatbot WA rule-based + módulo Agenda + notificaciones + re-engagement queue, **TODO sin IA**). **4B**: primer agente IA real = Brand Orchestrator (caso canónico subagentes, post-validación) |
| Fase 5 | ⏳ Acquisition synth + Growth narrative como **scripts con LLM ocasional**, NO agentes (audit 2026-05-03) |
| Fase 6 | ⏳ Cutover ERP Render→VPS3 + estabilización |

**ADRs supersedidas/diferidas por audit 2026-05-03:**
- ADR-0034 v1.0 Conversation Agent IA Foundation → 💤 Diferida. Será supersedida por ADR Conversation Agent v0 rule-based cuando se construya en Fase 4A.

**Doctrina rectora:** principio operativo #11 — IA es capa aditiva sobre backbone determinístico validado.

**Ver [docs/master-plan-mvp-livskin.md § 11](docs/master-plan-mvp-livskin.md#11-roadmap-10-semanas-con-6-workstreams) para detalle.**

---

## 🔐 Acceso a infraestructura

### VPS actuales

| Alias | IP pública | IP privada VPC | Hostname | Rol |
|---|---|---|---|---|
| `livskin-wp` | 46.101.97.246 | 10.114.0.3 | Livskin-WP-01 | WordPress (VPS 1) |
| `livskin-ops` | 167.172.97.197 | 10.114.0.2 | livskin-vps-operations | Orquestación + analítica (VPS 2) |
| `livskin-erp` | **139.59.214.7** | **10.114.0.4** | livskin-vps-erp | ERP + segundo cerebro (VPS 3 — provisionado 2026-04-19) |

Los 3 VPS están en DO VPC `10.114.0.0/20` Frankfurt. Latencia inter-VPS <2ms.

### Cómo conectar

```bash
ssh -F keys/ssh_config livskin-wp
ssh -F keys/ssh_config livskin-ops
ssh -F keys/ssh_config livskin-erp
```

Usuario: `livskin` (NO root — deshabilitado). Sudo NOPASSWD.  
Ver [memoria persistente vps_access](~/.claude/projects/.../memory/vps_access.md) para detalles.

---

## 💬 Cómo trabajar conmigo (reglas de colaboración)

### Tipos de sesión

| Tipo | Cuándo | Output |
|---|---|---|
| **Estratégica** | Decisiones estructurales, definiciones, planning | Dossier ADR + actualización master plan |
| **Ejecución** | Construcción con plan claro | Código + docs + commits |
| **Revisión** | Evaluación resultados, ajustes | Métricas + decisiones de ajuste |

### Rituales de sesión

**Arranque (mío, 2 min):** leo CLAUDE.md + `docs/backlog.md` + `notes/compartido/` + última sesión + memoria, te digo en 3 líneas dónde quedamos, qué hay en backlog relevante, y qué propongo hacer.

**Cierre (mío, 5-15 min):** ejecuto runbook estandarizado [docs/runbooks/cierre-sesion.md](docs/runbooks/cierre-sesion.md). 11 pasos: session log + ADRs + CLAUDE.md + master plan + backlog + memoria + capacidades agentes + git commit/push. Incluye filosofía + checklist + cuándo NO ejecutar completo. Es runbook vivo, evoluciona con cada sesión que descubra fricción nueva.

**Antes de cambios riesgosos:** plan explícito + tu aprobación. Nunca ejecuto destructivas sin check.

### Obsidian como interfaz visual del vault

El repo completo **es un vault de Obsidian**. Abres Obsidian, haces "Open folder as vault" sobre la raíz, y ves:
- Grafo de conexiones entre todos los docs
- Búsqueda full-text instantánea
- Tus notas personales en `notes/privado/` (gitignored)
- Notas colaborativas en `notes/compartido/` (versionadas)

Setup completo: [docs/runbooks/obsidian-setup.md](docs/runbooks/obsidian-setup.md).

### Si no entiendes algo

Para la usuaria: si en una respuesta mía no entiendes un término, **para y pregunta**. No asumas que es "lo que ya sabes". Ningún término es tonto.

Para mí (Claude Code): si una decisión es **reversible y pequeña**, ejecuto y muestro. Si es **irreversible o grande**, pregunto primero.

---

## 🚨 Lo que NUNCA debo hacer

1. **Editar código del ERP (`erp/`) sin autorización explícita** en esta sesión. Doble barrera: `.gitignore` + `.claude/settings.json` deny.
2. **TOCAR EL SISTEMA ACTUAL EN PRODUCCIÓN** — específicamente:
   - NO push commits al repo `DarioUrrutia/formulario-livskin`
   - NO modificar deploys del Render (`formulario-livskin.onrender.com`)
   - NO modificar variables de entorno del Render
   - NO escribir/borrar/modificar filas del Google Sheets DB (Sheet ID `1o4Vh4RN_Qfpaz8g08MReqgE3mFX0EGVSI5A69OsHB5g`)
   - NO redeploy del Render por accidente
   - **Solo lectura permitida** hasta cutover (Fase 6) cuando Dario explícitamente apruebe el corte. Ver memoria `feedback_production_preservation`.
3. **Commitear secretos** (archivos `.env*` salvo `.env.example`, `keys/*.pem`, `keys/*.key`, `keys/.env.integrations`).
4. **Commitear data con PII** — exports del Sheets `docs/Datos_Livskin_*.xlsx` están gitignored. Solo el viejo `docs/Datos Livskin.xlsx` (sin guion bajo) sigue tracked como referencia anonimizada.
5. **Push force a `main`.** Usar branches + PR.
6. **Proponer servicios pagos** sin preguntar. Principio 8.
7. **Correr implementación antes de tener dossier aprobado** para la decisión subyacente. Principio 9.
8. **Asumir que la usuaria conoce un término técnico.** Explicar siempre al aterrizar. Ver memoria `feedback_explain_to_beginner` — Dario es principiante en implementación.
9. **Saltar fases del roadmap.** Cada fase tiene dependencies razonadas. Ver memoria `feedback_roadmap_order`.
10. **Saltar el trámite WhatsApp Business API.** 5-10 días hábiles de Meta, bloqueo real.
11. **Tocar VPS en producción sin snapshot previo y sin staging validado.**
12. **Borrar/modificar historial git** sin autorización explícita.

---

## 📝 Estado al 2026-05-03 cierre (PIVOT ESTRATÉGICO — doctrina #11 + audit agentes + Bridge Episode)

### Sesión 2026-05-03 — Re-articulación estratégica del proyecto

**Pivot estratégico cerrado por Dario tras 3 conversaciones encadenadas:**

1. **Doctrina rectora explicitada**: "Deterministic backbone first — IA es capa aditiva, no foundational" → elevada a **principio operativo #11** (este archivo).

2. **Audit honesto del scope agentes** (memoria `project_agent_scope_audit_2026_05_03`):
   - 5 agentes originales → **1 agente real (Brand Orchestrator) + 2 scripts con LLM ocasional**
   - Conversation Agent IA → ⏸️ **diferido** (V1 será chatbot rule-based + handoff humano + templates Meta-approved)
   - Growth Analyzer + Infra-Security → ❌ **NO V1** (scripts/skills cubren)
   - **Framework de 6 checks** definido como gate obligatorio para aprobar agente futuro

3. **Bridge Episode insertado en roadmap**: primera campaña paga FB Ads $100/5 días entre Fase 3 (cerrada) y Fase 4 (reescrita post-audit). Captura data real → informa Fase 4 con datos, no hipótesis. Detalle: `docs/campaigns/2026-05-first-campaign/plan.md`.

4. **Auto-crítica de Claude documentada**: cuatro fallas en colaboración previa contribuyeron al sobreescalamiento (no empujar a customer development, aceptar premisa "5 agentes" sin friction, sumarse a sobre-engineering Bloque 0 v2, demasiados ADRs). Capturado en memoria audit.

**Memorias nuevas 🔥 CRÍTICAS:**
- `feedback_deterministic_backbone_first.md` — doctrina rectora
- `project_agent_scope_audit_2026_05_03.md` — operacionalización + framework 6 checks
- `project_first_paid_campaign_2026_05_03.md` — episodio efímero (archivar tras post-mortem)

**Memorias actualizadas con header de supersedimiento:**
- `project_agent_org_design.md` — visión válida, scope reducido
- `project_roadmap.md` — Bridge Episode + Fase 4/5 reescritas

**ADRs supersedidas/diferidas:**
- ADR-0034 v1.0 Conversation Agent IA Foundation → 💤 Diferida (será supersedida por ADR Conversation Agent v0 rule-based en Fase 4A)

**Bloque 1 commit pendiente push:** `60b609d feat(erp): match automático lead↔cliente al crear venta (ADR-0033)` — encaja perfecto con doctrina nueva (100% determinístico).

**Próximos pasos inmediatos:** ejecutar Bridge Episode tactical plan (FB Ads + landings + tracking manual) — NO construir agentes hasta post-mortem de campaña.

---

## 📝 Estado al 2026-05-02 cierre (Mini-bloque 3.6 ✅ + smoke comprehensivo + Op B atribución)

### Sesión 2026-05-01/02 — Mini-bloque 3.6 completo + arquitectura atribución end-to-end

**Logros del día:**

1. **Mini-bloque 3.6 ✅ COMPLETO** — Landings dedicadas Cloudflare Pages live (`campanas.livskin.site/botox-mvp/`)
   - Sistema convenciones HTML (`_shared/conventions.md` v1.0) + JS standalone (`livskin-tracking.js`) + JSON Schema validator
   - Modal consent v2 (centrado, GDPR-compliant) + WA tracking auto-detect en `PinkCTA`
   - GH Actions auto-deploy live (Node 22 + wrangler@4.87 pinned)
   - 5 commits: `ef431a7`, `cff7a0a`, `a5419c8`, `3138577`, `98f4327`

2. **n8n A1 WA_CLICK_PATCH_v1_1** — workflow patched live para aceptar `_source: "wa-click"` con phone vacío. Lead test creado en Vtiger validando E2E.

3. **n8n B3 BR3_SKIP_WA_CLICK_v1** — Op B implementada: WA-click leads filtrados del sync ERP (no son operacionales sin phone, viven solo en Vtiger para attribution marketing).

4. **Sensor cron instalado en VPS3** — `*/5 * * * *` collect + cleanup daily. Cierre de pendiente Bloque 0 v2.

5. **Smoke comprehensivo 16 tests** del journey "anuncio → paga": 14 PASS + 1 gap diseñado (consent persist) + 1 hallazgo (B3 race condition).

6. **Decisión arquitectónica clave**: el `event_id` UUID es el hilo conductor de atribución end-to-end. Anuncio → Pixel Lead → Vtiger cf_871 → (Fase 4) chatbot enriquece phone → ERP cliente → CAPI Purchase con MISMO event_id → Meta dedup full-funnel CERRADA. Op B funciona porque event_id (no phone) es primary correlation key.

**Memorias nuevas:**
- `project_attribution_chain_event_id.md` — modelo full-funnel
- `feedback_n8n_workflow_history_loads.md` — n8n 2.x carga desde workflow_history
- `feedback_n8n_db_modification_safety.md` — alpine sidecar in-place, NUNCA copy fuera del volumen

**Hallazgos pendientes:**
- **B3 race condition** (severidad media) — cron procesa solo 1 de N leads del mismo ciclo. HOTFIX próxima sesión 15-30 min.
- **WhatsApp Business API approve** — bloqueante Fase 4 Conversation Agent.

**Estado Fase 3:** 95% (4 de 5 mini-bloques completos). Solo falta 3.5 Observabilidad + Metabase.

**Próxima sesión propuesta:** HOTFIX B3 race (15-30 min) + Mini-bloque 3.5 Observabilidad + Metabase dashboards (4-6h).

---

### Sesión 2026-05-01 cierre — Mini-bloque 3.4 + plan 3.6

**Logros del día (sesión multi-fase):**

1. **Mini-bloque 3.4 ✅ COMPLETO** — CAPI server-side via n8n (commit `c4dd8a8`)
   - Token CAPI generado vía Events Manager → Pixel `4410809639201712` → "Configurar integración directa con Dataset Quality API"
   - **NO requiere App Review** (descartando preocupación inicial — confirmado vía 6 fuentes oficiales)
   - ADR-0019 v1.0 cerrado: ERP → n8n → Meta (Opción B), descartando Meta-enabled (health restrictions) + ERP-directo (no visualidad)
   - `services/capi_emitter_service.py` con 13 tests TDD pasan
   - Hook auto-emit en `/api/leads/sync-from-vtiger` CREATE
   - n8n Workflow [G3] (5 nodos) — hashing SHA-256 PII + POST Meta Graph API
   - Validación E2E: Lead creado → audit log `tracking.capi_event_emitted` → Meta `events_received: 1`

2. **PIVOT estratégico** — Mini-bloque 3.6 (Landings dedicadas) ANTES de 3.5 (Metabase)
   - Razón: sin landings dedicadas, no hay campañas pagas; sin campañas pagas, Metabase es ejercicio académico
   - Flow correcto: Landings (3.6) → mini campaña test → Metabase (3.5) con data real

3. **ADR-0031 v1.0 cerrado** — Landings hosting Cloudflare Pages + sistema convenciones
   - Hosting: Cloudflare Pages (free, edge global, deploy git push)
   - Subdomain: `campanas.livskin.site`
   - **Sistema NO un template fijo** (Dario clarificó variabilidad de cada landing) — sistema de convenciones HTML markup que cualquier landing nueva debe seguir
   - 24 categorías de gaps documentadas (cookies cross-subdomain, bot protection, compliance médico, noindex, form retry queue, etc.)

**7 decisiones tuyas pendientes (gating Mini-bloque 3.6):**
1. Privacy policy + terms — drafts existentes?
2. WhatsApp phone real — `+51982732978` o `+51980727888`?
3. Microsoft Clarity OK?
4. URLs estructura — `/botox` (UX) vs `/c/01` (Meta health-safer)?
5. Cloudflare Turnstile en landings?
6. Cloudflare account access para crear Pages project + DNS `campanas.livskin.site`?
7. Pixel compliance status para health category?

**Estado Fase 3:**
| Mini-bloque | Estado |
|---|---|
| 3.1 Cleanup VPS 1 | ✅ |
| 3.2 GTM Tracking Engine | ✅ |
| 3.3 REWRITE Form→Vtiger→ERP | ✅ |
| 3.4 CAPI server-side | ✅ |
| **3.6 Landings dedicadas (NUEVO inserto)** | ⏳ **próxima sesión** |
| 3.5 Observabilidad + Metabase | ⏳ después 3.6 |

**Próxima sesión:** Mini-bloque 3.6 — Landings dedicadas. Aplicar runbook preflight obligatorio. Sub-paso 3.6.1 (escribir conventions.md) requiere 7 decisiones tuyas resueltas primero.

### Sesión 2026-05-01 mañana — Mini-bloque 3.3 REWRITE COMPLETO

### Sesión multi-día 2026-04-29 → 2026-05-01 — Mini-bloque 3.3 REWRITE end-to-end

**Logro principal:** pipeline `form WP submit → Vtiger Lead → ERP leads` 100% operacional con first-touch attribution preservada. Validado E2E con lead real en producción.

**Componentes construidos (6 commits):**
- Migration Alembic 0006 — fbc/ga/event_id en leads + lead_touchpoints + form_submissions (CAPI match quality)
- Vtiger 12 custom fields cf_NNN + REST API verified + docs `integrations/vtiger/`
- n8n sistema organizacional (8 categorías + naming + URLs + tags) en `infra/n8n/`
- n8n workflow [A1] form→Vtiger Lead (16 nodes) — 4 smoke tests pasados
- Endpoint Flask `/api/leads/sync-from-vtiger` con 18 tests TDD — coverage 79%
- n8n workflow [B1] Vtiger→ERP receiver (13 nodes) — para futuro Custom PHP Hook
- n8n workflow [B3] cron pull cada 2 min (12 nodes) — reemplaza webhook on-change Vtiger 8.2 community
- mu-plugin WordPress `livskin-form-to-n8n.php` form-id agnostic + JS injection + post_meta opt-in

**Hallazgos importantes:**
- Vtiger 8.2 community usa fieldnames numéricos (cf_853, cf_855...) para custom fields — dictionary cf_NNN ↔ ERP en `integrations/vtiger/fields-mapping.md`
- SureForms NO tiene block "Hidden" nativo → mu-plugin inyecta hidden inputs via JS (defense-in-depth pattern)
- GTM Tracking Engine NO popula los hidden inputs `lvk_*` → mu-plugin self-sufficient (URL params + cookies + UUID)
- Picklist Vtiger cf_875 vs WP form dropdown desalineados → backlog item para alinear pre-F4
- Vtiger 8.2 community sin "Send To URL" workflow task → cron pull n8n (Opción C) en lugar de realtime webhook

**Memoria nueva crítica:** `project_agent_skills_inventory.md` — tracker continuo de capacidades por agente. Tabla retroactiva de TODO desde Bloque 0 v2 hasta hoy + qué agente la usará. Input pre-mapeado para sesión estratégica organizacional pre-Fase 5. Detectado por Dario como cabo suelto (yo no estaba tracking sistemáticamente).

**Memoria nueva:** `feedback_commit_approval_explicit.md` — cada commit/push requiere aprobación explícita en ese momento (Dario corrigió durante sesión).

**Runbook nuevo:** `wordpress-form-livskin-integration.md` — cómo activar/desactivar/debuggear forms WP nuevos.

**Runbook actualizado:** `cierre-sesion.md` § 8 — check OBLIGATORIO al inventory de skills si hubo build.

**Estado Fase 3:**
| Mini-bloque | Estado |
|---|---|
| 3.1 Limpieza VPS 1 | ✅ |
| 3.2 GTM Tracking Engine + UTM persistence | ✅ |
| **3.3 REWRITE Form → Vtiger → ERP pipeline** | ✅ **COMPLETO 2026-05-01** |
| 3.4 CAPI server-side | ⏳ próxima sesión |
| 3.5 Observabilidad + Metabase dashboards | ⏳ después de 3.4 |

**Fase 3 progress:** 60% (3 de 5 mini-bloques completos).

**Próxima sesión:** Mini-bloque 3.4 — CAPI server-side desde ERP (o desde n8n — decisión a reabrir). Aplicar runbook preflight obligatorio. Pre-requisito: decidir Meta App Review (Opción A/B/C) antes del primer commit.

**Optional pre-3.4:** test parcial manual end-to-end (Opción C aprobada por Dario) — convert lead manual a cliente + venta + pago para validar 60-70% del flow completo antes de tener todas las automatizaciones.

### Sesión 2026-04-29 (error arquitectónico + cleanup completo + reorganización)

**Lo que pasó:** implementé mini-bloque 3.3 (Form → ERP webhook) ignorando arquitectura cerrada hace una semana. El flujo correcto documentado en ADR-0011 v1.1 + ADR-0015 + memoria `project_acquisition_flow` es: **Form → n8n → Vtiger → ERP espejo**, no Form → ERP directo. Dario detectó el error al preguntar dónde encajaba Vtiger.

**Cleanup ejecutado completo (sistema vuelto al estado del cierre 2026-04-28):**
- `git revert` de los 2 commits del backend Flask (`ee0ddd2` + `0f9187d`) → push → CI redeploy → endpoint `/api/leads/intake` retorna 404 en producción
- `mu-plugin livskin-lead-webhook.php` eliminado de VPS 1 (otros plugins intactos)
- 2 leads test (LIVLEAD0001, LIVLEAD0002) + 2 touchpoints borrados de ERP DB
- Audit doc del 3.3 incorrecto borrado (no commiteado)

**Reorganización del sistema de memoria (token-efficient):**
- MEMORY.md reorganizado por criticidad: 5 categorías (🔥 CRÍTICAS, 📐 Arquitectura, 🚦 Gobernanza, 🛠 Patrones, 📋 Estado)
- 2 memorias 🔥 CRÍTICAS nuevas: `project_n8n_orchestration_layer.md` (n8n como capa visual orquestadora cross-system) + `feedback_must_re_read_adrs_before_coding.md` (protocolo obligatorio pre-flight)
- Brain pgvector Layer 2 re-indexado: 1.475 → **1.765 chunks** (94 archivos, todos los docs recientes incluidos)
- Runbook nuevo `preflight-cross-system.md` con protocolo 5-pasos obligatorio antes de tareas cross-system
- Cross-link en `cierre-sesion.md` para descoverability

**Filosofía operativa nueva:** NO releer todas las memorias por sesión. MEMORY.md compacto auto-carga + queries semánticas al brain pgvector bajo demanda (~2K tokens vs 25K leyendo 5 ADRs) + pre-flight checklist OBLIGATORIO antes de mini-bloques cross-system.

**Estado Fase 3:**
| Mini-bloque | Estado |
|---|---|
| 3.1 Limpieza VPS 1 | ✅ válido |
| 3.2 GTM Tracking Engine + UTM persistence | ✅ válido |
| **3.3 Form → ERP webhook** | ❌ **NO existe** (revertido) — REWRITE pendiente con flujo correcto Form→n8n→Vtiger→ERP |
| 3.4 CAPI server-side desde ERP | ⏳ pendiente |
| 3.5 Observabilidad | ⏳ pendiente |

**Fase 3 progress:** 2 de 5 mini-bloques (40%) — vuelve al estado del cierre de ayer.

**Próxima sesión:** Mini-bloque 3.3 REWRITE — Setup Vtiger + n8n + flow correcto. Aplicar runbook `preflight-cross-system.md` obligatorio antes de empezar.

### Sesión 2026-04-28 (Fase 3 arrancada con 2 mini-bloques completos)

Fase 3 progress: 0% → **40% en una sesión** (2 de 5 mini-bloques completos). Ejecutado **100% programáticamente** vía wp-cli + GTM API + scripts Python — sin tanteos UI. Detalle: [session log](docs/sesiones/2026-04-28-mini-bloques-3-1-y-3-2-fase3.md).

**Mini-bloque 3.1 — Limpieza VPS 1 ✅** ([audit](docs/audits/mini-bloque-3-1-cleanup-vps1-2026-04-28.md)):
- LatePoint + PixelYourSite desactivados (resuelve doble disparo Pixel)
- Cloudflare Turnstile en SureForms 1569 (native) + plugin para login form (bot scraping bloqueado)
- 3 social links arreglados: WhatsApp `+51982732978` + Instagram + Facebook
- Pixel legacy `670708374433840` saltado (Meta no permite archivar desde UI)

**Mini-bloque 3.2 — GTM Tracking Engine + UTM persistence ✅** ([audit](docs/audits/mini-bloque-3-2-tracking-engine-2026-04-28.md) + [ADR-0021](docs/decisiones/0021-utms-persistence-y-tracking-engine-client-side.md)):
- Pre-flight: revertido cambio destructivo en workspace draft (trigger Pixel hubiera quedado sin disparar)
- OAuth ampliado a 5 scopes (analytics.readonly + tagmanager.readonly + tagmanager.edit.containers + tagmanager.edit.containerversions + tagmanager.publish)
- 17 variables (11 cookies + 6 DLV) + 3 triggers + 6 tags nuevos creados via GTM API
- Tracking Engine JS de 95 líneas (UTM persistence + form submit listener + WhatsApp click listener + auto-populator hidden fields + event_id único para CAPI dedup)
- GTM v18 PUBLISHED LIVE (8 tags + 3 triggers + 17 variables)

**Validación browser-side end-to-end con Dario** (post hard refresh para CDN edge cache):
- ✅ Cookies `lvk_utm_*` persistidas
- ✅ `whatsapp_click` event con event_id + UTMs en dataLayer
- ✅ `gtm.scrollDepth` 75% disparado por nuestro trigger
- ✅ Sistema 100% operativo

**Aprendizajes consolidados:**
- Memoria `feedback_iteration_pattern_site`: protocolo de iteración del site (hipótesis + métricas before/after + lección)
- Memoria `feedback_programmatic_setup_pattern`: scripts API > UI tanteos (3-6x más rápido + reusable)
- Patrón de 3 scripts por dominio (inspect + build + validate) ya implementado para GTM

**Próxima sesión:** Mini-bloque 3.3 — Form → ERP webhook (90-120 min, el más denso técnicamente).

### Sesión 2026-04-27 (Google completado + Meta parcial)

Setup acceso programático Google **completado al 100%** + audit definitivo via APIs ejecutado. Meta llegó a ~80% (System User + assets + app creados) pero **token generation bloqueado** por cambios de UI/políticas Meta. Dario decidió cortar Meta hoy y cerrar con lo logrado. Detalle: [session log](docs/sesiones/2026-04-27-acceso-programatico-google-y-audit.md) + [audit Google](docs/audits/audit-google-stack-2026-04-27.md).

**Lo que se cerró hoy:**
- ✅ OAuth Google con refresh token persistente (`keys/google-oauth-token.json`, gitignored)
- ✅ Scripts `scripts/google_oauth_setup.py` + `scripts/google_audit.py` reusables
- ✅ Audit programático Google: 5 GA4 accounts detectadas, código exacto de tags GTM extraído, **doble disparo Pixel CONFIRMADO con código real** (no hipótesis)
- ✅ GA4 events últimas 48h pulleados — 1 form_submit detectado SIN entry en DB → **bot scraping confirmado** (form sin reCAPTCHA/Turnstile)
- ✅ 2da property GA4 "LivskinDEF" → livskinperu.com detectada (legacy a archivar)
- ✅ Meta System User "Claude Audit" + Claude Audit App creados (persistente para próxima sesión)

**Lo que quedó parcial:**
- ⏸️ Token Meta generation bloqueado — UI/políticas cambiaron, Marketing API ahora requiere App Review formal (1-3 semanas)
- ⏸️ Audit programático Meta diferido — los datos Google ya validan 100% las decisiones arquitectónicas

**Decisiones tomadas:**
1. **Acceso Google = OAuth user flow** (no service account) — Google sin Workspace no acepta service accounts en GA4/GTM admin UI
2. **Cloudflare Turnstile en SureForms 1569 = urgente Fase 3** — bot scraping confirmado
3. **Consolidación 3 Business Managers Meta = mini-proyecto pendiente** — desorden de fase de aprendizaje
4. **Honrar compromisos a Dario** — cuando se promete "5 min máx" no extender. Aprendizaje incorporado a memoria de gobernanza.

**Próxima sesión:** decisión en frío — (a) reintentar Meta con enfoque distinto, (b) saltar Meta y arrancar Fase 3 directo con datos Google (suficientes), (c) otra. Dario decide.

### Sesión 2026-04-26 (segunda mitad — audit + arquitectura)

Tras cerrar Bloque 0 v2 + tag `v0.foundation`, sesión profundizó en estado real cross-VPS y cerró 8 decisiones estratégicas. Ver [session log completo](docs/sesiones/2026-04-26-audit-real-y-arquitectura-tracking.md).

**Audit cross-VPS real ejecutado** ([docs/audits/estado-real-cross-vps-2026-04-26.md](docs/audits/estado-real-cross-vps-2026-04-26.md)):
- VPS 1 ya tiene GTM + GA4 + Pixel funcionando (no greenfield) — **doble disparo de Pixel detectado** (plugin PixelYourSite + GTM custom HTML).
- VPS 2 provisionado pero virgen: 0 workflows n8n, 0 leads/contacts/opps Vtiger, 0 filas analytics.
- VPS 3 sólido con 134 clientes / 88 ventas / 84 pagos reales + audit pipeline operativo.
- 2 Pixels en Meta (uno viejo a archivar). Diagnóstico (1) = duplicación.
- LatePoint con servicios demo → desactivar. Form Render no enlazado desde livskin.site.

**Decisiones arquitectónicas cerradas:**
1. **Tracking 2-capas single-source**: client-side = GTM única fuente; server-side CAPI = emitida desde ERP VPS 3 (no desde WordPress).
2. **Pixel `670708374433840` se archiva**, único activo `4410809639201712`.
3. **Módulo Agenda vive en ERP** (Opción B), no Vtiger. Doctora marca asistencia. ADR pendiente.
4. **Vtiger redefinido**: master del journey de marketing del lead. ERP gana el journey operativo (lead→cita→asistido→cliente→venta→pago).
5. **Precisión quirúrgica al ampliar ERP**: ADR aprobado + tests primero + endpoints aislados + feature flag + Alembic reversible + validación con doctora.
6. **Setup acceso programático completo en próxima sesión** (Google service account + Meta System User + Cloudflare token) → audit programático real reemplaza audit por screenshots.
7. **Cierre de sesión estandarizado** como runbook vivo: [docs/runbooks/cierre-sesion.md](docs/runbooks/cierre-sesion.md).
8. **Gobernanza de agentes reiterada**: procesos antes de libertad, deterministic > LLM, hard limits no soft, eval suite continua, humano al mando.

### Bloque 0 v2 — Cimientos cross-VPS state-of-the-art (cierre 2026-04-26)

Sistema **AI-operable end-to-end**:

| Sub-bloque | Estado |
|---|---|
| 0.1 Versionar 3 VPS al repo | ✅ VPS 1 + VPS 2 al repo (VPS 3 mantiene paths legacy hasta Fase 6) |
| 0.2 CI/CD multi-VPS | ✅ deploy-vps[1\|2\|3].yml con snapshot DO + rollback automático + audit |
| 0.3 System map autoritativo | ✅ docs/sistema-mapa.md machine-readable + endpoint /api/system-map.json |
| 0.4 Sensors uniformes cross-VPS | ✅ livskin-sensor + recolector cron + dashboard /admin/system-health |
| 0.5 Backups daily verificados | ✅ scripts cross-VPS + verify automático + audit log integration |
| 0.6 12 runbooks ejecutables | ✅ frontmatter YAML compatible con MCP skill execution |
| 0.7 DR drill procedure | ✅ cadencia semestral/trimestral + post-mortem template |
| 0.8 Audit log expandido | ✅ 49 eventos canónicos (8 categorías) + schema doc |
| 0.9 Skills + MCP scaffold | ✅ skills/livskin-ops + skills/livskin-deploy + mcp-livskin scaffold |

**Pendiente activar en producción:**
1. GitHub Secrets nuevos: DO_API_TOKEN, AUDIT_INTERNAL_TOKEN, VPS1_*, VPS2_*
2. Configurar `audit_internal_token` en .env de erp-flask en VPS 3
3. Migrate VPS 2 con `migrate-from-home.sh` (idempotente)
4. Deploy livskin-sensor en VPS 1 (systemd) + VPS 2 (container)
5. Instalar crons backup + sensor-collect (`install-cron.sh`)
6. Ejecutar `alembic upgrade head` (incluye migration 0004 infra_snapshots)

### Fase 2 — Implementación ~99%

(Lo que ya estaba al cierre del 2026-04-25, ahora extendido con Bloque 0:)

- ✅ ERP refactorizado funcional en https://erp.livskin.site con data real
- ✅ Auth bcrypt + login/logout (ADR-0026)
- ✅ Audit log middleware + dashboard /admin/audit-log (ADR-0027)
- ✅ Tests pytest 81% coverage (target ≥75%)
- ✅ CI/CD post-deploy testing en GitHub Actions
- ✅ Auditoría profunda Flask original — 11/13 gaps cerrados
- ⏳ Pendiente: Vtiger config (bloqueado WhatsApp Business API trámite)

### Histórico (pre-2026-04-26)

**Lo que está hecho:**
- ✅ **Fase 0** (2026-04-18): repo + plan maestro v1.0 + 3 dossiers fundacionales + memoria poblada
- ✅ **Fase 1** (2026-04-20): VPS 3 hardened + DO VPC + Postgres 16 + pgvector + embeddings + nginx + TLS + CI/CD + Alembic + brain Layer 2 (679 chunks indexados) + Obsidian
- 🚧 **Fase 2** (2026-04-21 a hoy):
  - **10 ADRs cerrados**: 0011-0015 (gobierno datos) + 0023-0027 (refactor + auth + audit)
  - **ERP refactorizado FUNCIONAL** en `https://erp.livskin.site`:
    - Stack: Flask + SQLAlchemy 2.0 + Pydantic v2 + structlog + gunicorn + Postgres 16
    - 12 tablas via Alembic 0001 + trigger DEBE dinámico via 0002
    - Las 6 fases de venta del Flask original preservadas exactas + auto-aplicar leftover FIFO con override
    - Capa de compat form-data → JSON (HTML 3500 líneas legacy preservado)
    - 12 endpoints implementados (CRUD clientes, client-lookup, dashboard, libro, gastos, pagos, venta legacy)
    - **Backfill REAL ejecutado**: 134 clientes + 88 ventas + 84 pagos del Excel productivo
  - **CI/CD workflow** cubre todo el stack con retry verify de URLs públicas
  - **Auditoría profunda** Flask original: 13 gaps identificados, 11 cerrados

**Lo que queda pendiente para cerrar Fase 2 al 100% (~5%):**
1. Decisión `erp-staging.livskin.site` (próxima sesión 2026-04-27)
2. Auth bcrypt middleware + login/logout (ADR-0026 implementación)
3. Audit log middleware (ADR-0027 implementación)
4. Tests poblados a coverage ≥75%
5. Vtiger configurado (bloqueado por trámite WhatsApp Business API — no path crítico)

**Lo que queda pendiente de tu parte (Dario):**
1. Activar WhatsApp test number — pendiente desde Fase 0
2. Trámite WhatsApp Business API (5-10 días Meta) — pendiente
3. Bitwarden + guardar `keys/.env.integrations` como respaldo
4. Decidir mañana 2026-04-27: destino de `erp-staging.livskin.site` (3 opciones en backlog)

**Próximo paso (cerrar Fase 2 + arrancar Fase 3):**
- Sesión 2026-04-27: erp-staging decision + auth + audit + tests
- Cuando Meta API approve: arrancar Conversation Agent (Fase 4) en paralelo a Fase 3 (tracking)

---

## 📚 Glosario rápido

Ver [docs/master-plan-mvp-livskin.md § 17](docs/master-plan-mvp-livskin.md#17-glosario) para definiciones completas.

**ADR** — Architecture Decision Record · **CAPI** — Conversion API de Meta · **DO VPC** — red privada DigitalOcean · **ETL** — Extract/Transform/Load · **MCP** — Model Context Protocol · **OLTP/OLAP** — operativo/analítico · **pgvector** — extensión Postgres para vectores · **RAG** — Retrieval-Augmented Generation · **SoT** — Source of Truth · **Strangler fig** — patrón de migración gradual.

---

**Este archivo se actualiza al cierre de cada fase del roadmap.** La versión autoritativa del proyecto es siempre el `master-plan-mvp-livskin.md`; este CLAUDE.md es un resumen navegable para arranque rápido.
