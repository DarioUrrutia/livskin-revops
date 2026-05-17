# CLAUDE.md — Contexto maestro del proyecto Livskin

> Este archivo es leído automáticamente por Claude Code al iniciar cada sesión.  
> Su propósito: cargar en memoria el contexto operativo suficiente para trabajar sin fricción.  
> Última actualización: **2026-05-04 v3.1 (DOCTRINA DE MARCA + GOBERNANZA DE CONTEXTOS — Principios #12 (modo declarado proyecto/campaña) y #13 (modo bootstrap único hasta post-mortem 1ª campaña) agregados; doctrina de marca v0.1 BORRADOR en `docs/brand/`; primera campaña pivota a "Día de la Madre 2026" como test del sistema; runbook de modos en `docs/runbooks/sesion-modo-proyecto-vs-campana.md`)**

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
12. **Modo de trabajo declarado por sesión.** Cada sesión declara explícitamente al iniciar: **modo PROYECTO** (toca sistema durable: master plan, ADRs, memorias críticas, infra core) o **modo CAMPAÑA** (toca solo `docs/campaigns/<actual>/` + `infra/landing-pages/<slug>/` + `infra/ad-creatives/<actual>/`). Las modificaciones se restringen al modo. Mezclar requiere división explícita en bloques con commit de barrera entre ellos. Sin modo declarado → la sesión deriva y contamina contextos. Articulado por Dario el 2026-05-04 tras detectar que sesiones largas mezclan tactical de campaña con doctrina durable. Workflow detallado en `docs/runbooks/sesion-modo-proyecto-vs-campana.md`. **Para arrancar campaña nueva**: ejecutar `python scripts/new-campaign.py` que fuerza al operador a declarar propósito + hipótesis + parámetros antes de generar archivos. Template en `docs/campaigns/_template/` (ver su `README.md`).
13. **Modo BOOTSTRAP — régimen único transitorio para construcción del sistema.** Aplica SOLO mientras la doctrina de marca + el primer ciclo completo de campaña están siendo construidos en paralelo. Permite feedback bidireccional doctrina ↔ campaña con disciplina especial: doctrina vive en estado borrador versionado (`v0.X`), refinamientos a doctrina por aprendizajes de campaña requieren commit separado con prefix `docs(brand)` y comentario explícito del insight, memorias 🔥 CRÍTICAS de marca se crean al cierre del bootstrap (no durante). **Trigger de cierre formal — REVISADO 2026-05-08 por Dario**: post-mortem de la **2da campaña paga** (originalmente era la 1ra; tras Bridge Episode 2026-05-03/08 con solo 6 leads, los 14 INS + 6 R doctrina capturados no tienen evidencia suficiente para aplicar con 1 sola campaña — bootstrap permanece ABIERTO). Al cierre: doctrina asciende `v0.X → v1.0`, eliminamos header BORRADOR, creamos memorias críticas, principio #13 marca el bootstrap como cerrado. A partir de ahí, modos PROYECTO/CAMPAÑA son separados estrictos sin excepciones.

14. **Sesión estratégica de agentes IA es bloque DEDICADO post-backbone determinístico cerrado.** Toda la layer multi-agente (Brand Orchestrator V1 con 5 subagentes, Acquisition synth script, Growth narrative script, Conversation Agent v0 rule-based formal, Infra+Security agent, VPS dedicado de agentes) se diseña en una sesión estratégica dedicada (4-8h totales, **divisible en 1-3 sesiones según necesidad** — Dario decide formato cuando lo arranque). Outputs: ADRs por agente, organigrama formal, skills inventory final, eval suites (mín 30 ejemplos), budget hard-caps, approval flows.

    **Pre-requisito obligatorio**: backbone determinístico CERRADO. Backbone cerrado = Fases 4A.1 + 4A.2 + 4A.3 + 4A.4 + 4A.5 + 4A.6 (interludio estratégico = brand voice + arquetipos + posicionamiento + plan estratégico, **PARTE del backbone**). El interludio NO es input a la sesión de agentes — es base conceptual del sistema con o sin agentes (memoria `project_interludio_estrategico_es_backbone.md`).

    **Excepción permitida — Brand Orchestrator V0 BOOTSTRAP**: discrecional. Dario puede aprobar arrancar Brand Orchestrator V0 antes de la sesión estratégica si el negocio demanda contenido a velocidad humana insuficiente. Scope V0 acotado: solo briefs + copy, monolítico (sin subagentes), brand voice borrador o firmada según disponibilidad, output siempre revisable antes de publicar (NUNCA agente publica directo). El bootstrap V0 alimenta la sesión estratégica con datos reales (scope refinado, herramientas validadas, métricas eficiencia).

    **Excepción Conversation Agent IA NO permitida en bootstrap**: mantener chatbot rule-based de Fase 4A.3 hasta que volumen WhatsApp >100 conv/día sostenido por 7+ días lo justifique (memoria `project_agent_scope_audit_2026_05_03.md` framework 6 checks).

    Articulado por Dario el 2026-05-10. Detalle: memoria `feedback_sesion_estrategica_agentes_dedicada.md`.

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

**Arranque (mío, 5-7 min — OBLIGATORIO desde Bloque B 2026-05-06):** ejecuto runbook estandarizado [docs/runbooks/arranque-sesion.md](docs/runbooks/arranque-sesion.md). 5 pasos: git status + leer `docs/sistema-mapa.md` §1+§2+§6 + leer `MEMORY.md` (incluye episodios efímeros `project_session_handoff_*`) + identificar modo (#12: PROYECTO/CAMPAÑA/BOOTSTRAP) + preflight cross-system si la tarea toca ≥2 sistemas. STOP hard si falta cualquiera. Doctrina: memoria 🔥 [`feedback_session_warmup_obligatorio.md`](~/.claude/projects/.../memory/feedback_session_warmup_obligatorio.md) + hook `UserPromptSubmit` en `.claude/settings.json` que valida lectura previa con telemetría tool-use.

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

## 📝 Estado al 2026-05-17 cierre (Sprint 0 + Sprint 1 WhatsApp + Sprint 2 parte 1-2 + Interludio Discovery Workbook)

### Sesión 2026-05-16/17 — modo PROYECTO declarado (#12) — ~14h continuas

**La sesión más larga del proyecto. 4 bloques: cimientos Meta+WA → cleanup masivo → Sprint 2 parte 1-2 → pivote a Interludio Discovery (Fase 4A.6).**

**Bloque 1 (~2h) — Sprint 0 + Sprint 1 cimientos Meta + WhatsApp Cloud API**:
- System User "Claude Audit" → renombrado "Claude Automation" + 15 activos asignados (1 Page + 1 Ad Account + 1 App + 1 Dominio + 8 WABAs + 2 Datasets)
- Token Meta con **15 scopes Advanced** generado (Marketing API ads + Pages + WhatsApp completos) — sin App Review formal (Development Mode + propios assets)
- App "Livskin Integraciones" (App ID `807721865486018`) — 3 use cases agregados: WhatsApp + Marketing API (Ads + Analytics) + Manage Page
- **WhatsApp Cloud API `+51 947 741 117` activado** (SIM nueva doctora): register CLOUD_API + verified_name "Livskin" AVAILABLE_WITHOUT_REVIEW + 2FA PIN `395609` + GREEN quality + STANDARD throughput
- Webhook `[D0] WA Inbound Receiver` deployed en n8n via CLI + SQL active=1/activeVersionId fix + restart container
- Meta App subscription configurada usando App Access Token (`{app_id}|{app_secret}`) — System User token NO alcanza para POST `/{app-id}/subscriptions`
- Smoke E2E: outbound text desde Livskin → +51982732978 OK + inbound recibido en n8n executions

**Bloque 2 (~3h) — Cleanup masivo Meta + smoke data residual**:
- **6 WABAs duplicadas/legacy eliminadas** (Meta NO permite delete via API, solo UI) → estado final 2 WABAs (productiva + test)
- **Cleanup smoke data residual cross-system** (4 sistemas): 1 lead ERP + 4 leads + 10 opportunities en analytics warehouse + 68 leads Vtiger soft-deleted purgados físicamente (cascada 6 tablas) → **543 filas eliminadas total**, consistencia ERP=88↔Analytics=88 ✅
- Hallazgo: **workflows E1/E2 son UPSERT-only, sin DELETE cascade** → orphan data en analytics cuando se borra en ERP (patrón a considerar al rediseñar sync)
- Hallazgo: **Vtiger 8.2 community no purga soft-deletes automático** → SQL cascada manual en `leadscf`, `leadaddress`, `leadsubdetails`, `modtracker_basic`, `leaddetails`, `crmentity`

**Bloque 3 (~3h) — Sprint 2 parte 1-2 (Migration + Parser)**:
- **Sprint 2.1 — Migration 0008** `wa_conversation_state` (26 cols, UNIQUE PARTIAL en `phone_lead WHERE state != 'closed'`) + `wa_messages` (19 cols, UNIQUE `meta_message_id` para idempotency). Aplicada en VPS3 livskin_erp DB.
- **Sprint 2.2 — Parser intent + fechas JS** (`infra/n8n/lib/wa_parser.js`, ~250 líneas, sin deps): 10 intents (`confirm`, `reject`, `ask_price`, `ask_human`, `ask_info`, `greeting`, `cancel`, `reschedule`, `propose_date`, `unknown`) + parser fechas tolerante (días semana, días relativos hoy/mañana/pasado, fechas numéricas + textual, horas am/pm/24h, múltiples opciones por mensaje). **24/24 tests pass**. Inline-eado en workflow `[D1] WA Inbound + Parser` y validado E2E con WA reales.
- 3 bugs encontrados y fixados durante testing: regex ask_human no aceptaba "con la doctora", confirm no aceptaba combinaciones con coma, parseDates "hoy" sumaba 1 día por timezone shift

**Bloque 4 (~6h) — PIVOTE a Interludio Discovery (Fase 4A.6) + Workbook iterativo**:

Tras Sprint 2.2, Claude proponía seguir a Sprint 2.3 (workflow D1 completo). **Dario detectó que era scaffolding sin contenido**:
> "esto va a ser scaffold sin contenido, parece mediocre... estamos yendo a ciegas... contenido de las respuestas... esto tiene que top de gama"

**Pivote correcto**: faltaba **Interludio Estratégico (Fase 4A.6)** del master plan — brand voice + arquetipos + posicionamiento + customer journey + copy real del bot. Doctrina #14 (interludio ES PARTE del backbone) se confirma.

**Outputs producidos**:
1. `docs/brand/interludio-discovery.md` (~600 líneas) — Bitácora narrativa con marcos conceptuales (postura A vs B del bot, 4 estrategias de precios, 6 escenarios drop-off, sistema global de captación)
2. `docs/brand/interludio-discovery-workbook.html` (89KB) — **Workbook interactivo digital** para encuentro con doctora:
   - 13 bloques sidebar navegación + progress bar + auto-save localStorage cada 500ms
   - Export Markdown + JSON, Import JSON (recovery)
   - **Datos del sistema pre-cargados**: 134 clientes, 88 ventas Sep-Nov 2025, S/35,995 revenue, ticket promedio S/409, top categorías reales (Botox 50.1%, HA 15.9%, Hilos 11.1%, Esperma Salmón 7.1%, PRP 2.5%), distribución pagos, catálogo 21 tratamientos del ERP, campañas Bridge + Día Madre stats
   - **Top 6 tratamientos pre-llenados** como fichas verdes con ventas + revenue + marcas sugeridas + áreas comunes
   - 💡 **Hints visibles** debajo de cada pregunta importante con ejemplos concretos
   - **Contexto local Cusco**: 6 painpoints específicos (clima altura, aceptación cultural, turista nacional, cliente extranjero, soroche, fototipo andino) + 2 slots libres
   - **Botón "➕ Agregar otro tratamiento"** dinámico (genera ficha 11+, persiste contador, botón eliminar)
   - **Upload fotos antes/después**: Canvas resize 600px + JPEG 70% compresión → base64 en localStorage → preview thumbnail + exportable en JSON

### Decisiones tomadas

1. **Bot guía activo SUTIL** (postura B), no pasivo reactivo. El bot avanza al objetivo (agendar consulta) en cada interacción.
2. **Estrategia de precios B (rango con disclaimer + consulta gratuita)** — top de gama. No "te lo dice la doctora privado" ni precio fijo público.
3. **NO bajar precios como respuesta a "es caro"** — devalúa. Agregar VALOR adicional (kit cuidado, seguimiento gratis).
4. **NUNCA Claude Haiku como Capa 2 del parser** (doctrina #11). Si parser confidence < 0.5 → escalar a humano (doctora), no IA.
5. **Interludio Estratégico (Fase 4A.6) PRIMERO, después Sprint 2.3** (workflow D1 completo). Codear sin contenido era mediocre.
6. **App "Livskin Integraciones" en Development Mode** se queda así — scopes funcionan para nuestros propios assets sin App Review formal.
7. **Tabla `wa_conversation_state` con UNIQUE PARTIAL** (no UNIQUE simple) en phone_lead para permitir history de conversaciones cerradas.
8. **Templates Meta a submitir post-encuentro** (4-6): `new_lead_appointment_request`, `lead_confirmed_appointment`, `lead_rejected_proposal`, `lead_waiting_4h`, reminders T-24h/T-3h.

### Hallazgos no obvios

1. **Meta NO permite delete/rename WABAs via API** — solo UI manual.
2. **Workflows ETL E1/E2 son UPSERT-only, no DELETE cascade** → orphan data en analytics warehouse al borrar en ERP.
3. **Vtiger 8.2 community no purga soft-deletes** → leads quedan con `deleted=1` indefinidamente.
4. **Webhook config Meta App requiere APP ACCESS TOKEN** (= `{app_id}|{app_secret}`) — System User token insuficiente para POST `/{app-id}/subscriptions`. PERO WABA subscription al app sí funciona con System User.
5. **Meta `name_status: AVAILABLE_WITHOUT_REVIEW`** = display name aprobado sin esperar review humano (fast path).
6. **WABA review status fluctúa** — APPROVED → PENDING tras agregar phone number nuevo (24-72h re-review).
7. **Parser "hoy 8pm" bug** — timezone shift naive `+5h` causaba overflow de día. Fix: peruDate calculation con offset explícito.
8. **localStorage tiene límite ~5-10MB** — fotos antes/después en base64 requieren canvas resize a 600px + JPEG 70% para que 12 fotos quepan en ~1.2MB.

### Errores cometidos por Claude (autocrítica)

1. **Construcción técnica sin contenido de negocio**: arrancamos Sprint 2 codeando tablas + parser + workflow sin diseñar primero customer journey + copy bot + scoring rules. Dario detectó. **Lección: mapa conceptual ANTES que código para componentes con alta carga de contenido (bot, email marketing, ads copy)**. Memoria nueva: `feedback_mapa_conceptual_antes_de_scaffold.md`.
2. **Información ya disponible en el sistema pero pedida a Dario**: en primer draft del workbook pedía "traer 134 clientes segmentados, top 5 tratamientos" cuando YO los tengo via SQL. **Lección: antes de pedir info al usuario, verificar si está en mi acceso programático.**
3. **Pedir cosas manuales innecesarias**: Dario corrigió *"Que sea la ultima vez que me pides hacer cosas manuales a mi, tienes acceso a todos mis sistemas, solo tienes que decirme que necesitas, que piensas hacer y mi confirmacion"*. **Lección: SSH/API yo, manual solo cuando no haya alternativa.** Memoria nueva: `feedback_no_pedir_manual_si_tengo_acceso.md`.
4. **Iteración v1→v2→v3 del workbook** — primera versión print-friendly. **Lección: preguntar formato al inicio antes de producir 60KB de HTML en vano.**

### Doctrinas confirmadas / refinadas

- **Doctrina #11 (deterministic backbone first)**: confirmada — sustituimos Claude Haiku Capa 2 por escalar-a-humano cuando confidence < 0.5
- **Doctrina #14 (interludio estratégico es PARTE del backbone)**: confirmada — pivote a interludio antes de Sprint 2.3
- **Doctrina #8 (cero pago sin aprobación)**: confirmada — todo el día $0 nuevo
- **Doctrina nueva implícita (candidata a Principio #15)**: "Cuando el componente tiene alta carga de CONTENIDO (no solo lógica), diseñar mapa conceptual + capturar voice/personas/copy ANTES de codear scaffold". A discutir formal en próxima sesión.

### Files creados/modificados

**Nuevos** (commit pendiente push):
- `infra/docker/alembic-erp/migrations/versions/2026_05_16_1930-0008_wa_conversation.py`
- `infra/n8n/lib/wa_parser.js`
- `infra/n8n/workflows/D-conversation/d1-wa-inbound-parser.json`
- `docs/brand/interludio-discovery.md`
- `docs/brand/interludio-discovery-workbook.html`
- `docs/sesiones/2026-05-17-sprint01-bot-broker-discovery-workbook.md`

**Modificados** (gitignored):
- `keys/.env.integrations` — META_SYSTEM_USER_ID/TOKEN, META_APP_SECRET, META_WEBHOOK_VERIFY_TOKEN, META_WA_PROD_* (5 keys)

**Deploy VPS3**: migration 0008 aplicada, tablas `wa_conversation_state` + `wa_messages` creadas
**Deploy VPS2**: n8n workflow `d0-wa-inbound-receiver` reemplazado con `[D1] WA Inbound + Parser`

### Próxima sesión propuesta

**Encuentro doctora (3-4h, presencial)** — Dario lleva laptop con `docs/brand/interludio-discovery-workbook.html` abierto en Chrome:

1. **Pre-encuentro (1h antes)**: cuestionario corto a doctora día previo, pedir screenshots chats reales anonimizados, fotos clínica/profesional/logo, reseñas Google, investigar competencia Cusco.
2. **Durante encuentro**: workbook abierto, auto-save activo, audio recorder en celular (con permiso), llenar 13 bloques, subir fotos antes/después.
3. **Post-encuentro (~6h con Claude)**: codificar 12 outputs en `docs/brand/`: `voice-v1.md`, `personas.md`, `journey-map.md`, `catalogo-tratamientos.md`, `precios-strategy.md`, `painpoints-responses.md`, `diferenciacion.md`, `operacion.md`, `casos-exito.md`, `reengagement.md`, `scoring-rules.md`, `captacion-global.md`.
4. **Después**: Sprint 2.3 (Workflow D1 completo) con COPY REAL en cada response del bot, no placeholders.

---

## 📝 Estado al 2026-05-13 cierre (Sprint A — Email institucional info@livskin.site + cleanup Meta legacy)

### Sesión 2026-05-13 — modo PROYECTO declarado (#12)

**Sprint A propuesto al cierre del 2026-05-10 ejecutado completo** (~4-5h):

**Email institucional `info@livskin.site` operacional E2E** — stack final $0/mes:
- **Inbound**: Cloudflare Email Routing (3 MX + DKIM CF + SPF inicial). Rule literal `info@livskin.site → daizurma@gmail.com` (Gmail principal). Destination address verified.
- **Outbound**: Gmail Send Mail As en cuenta `daizurma@gmail.com` → Brevo SMTP (`smtp-relay.brevo.com:587`, user `ab370e001@smtp-brevo.com`, key Standard 64-char). DKIM Brevo (2 selectors) + SPF extendido + DMARC `p=none` monitor-only.
- **UX filter**: Gmail filtro permanente `deliveredto:info@livskin.site` → Never send to Spam.
- **Smoke E2E validado**: outbound firma DKIM `d=livskin.site`, TLS, inbox externo.

**Cleanup identidad Meta (durante setup)**:
- `info@livskin.site` agregado a Meta Accounts Center (FB only; IG/Threads habrían REEMPLAZADO daizurma2 si los marcábamos).
- `durrutia@livskinperu.com` ELIMINADO del Accounts Center — dominio extinto = mail zombi = riesgo recovery.
- BM Livskin Perú People: business email del único admin actualizado `durrutia@livskinperu.com` → `daizurma2@gmail.com`.
- Estado final: 4 recovery options (info@ + daizurma2 + +51 + +39).

**Hallazgos no obvios (en runbook + session log)**:
1. CF Email Routing tiene 2 toggles separados ("DNS configurado" vs "servicio enabled"). Activación real en UI nueva `cloudflare.com/email-routing` → "+ Onboard Domain" → Done.
2. DigitalOcean bloquea TODOS los SMTP ports outbound (25/465/587) — smoke tests SMTP desde VPS imposibles, hay que usar Gmail Send Mail As o API HTTPS.
3. Gmail `deliveredto:` operator filtra forwards independiente del sender original — único método robusto anti-spam en setups nuevos sin reputación.
4. Meta Accounts Center NO tiene "email primary" del perfil FB. El "displayed email" en BM People es un campo INDEPENDIENTE editable ("Correo electrónico del negocio") por persona dentro de cada BM.
5. Instagram y Threads permiten solo 1 email por cuenta (Facebook sí permite múltiples).

### Files creados/modificados

**Nuevos**: `integrations/email/README.md` + `integrations/email/.env.example` + `docs/runbooks/email-institucional-setup.md` + `docs/sesiones/2026-05-13-email-institucional-cleanup-meta.md`

**Modificados**: `keys/.env.integrations` (gitignored, BREVO_SMTP_*) + `integrations/README.md` + `docs/runbooks/README.md` (v2.1→2.2, runbook #22) + `docs/backlog.md`

### Commit

```
9f533c5 feat(email): setup email institucional info@livskin.site + cleanup Meta legacy
```

### Próxima sesión propuesta

**Verificar destrabe Meta BM** (5 min) — 72h+ desde Domain Verification livskin.site (2026-05-10). Login `business.facebook.com` y verificar si restricción "WhatsApp Business restringida" (#2655121) se levantó.

**Si Meta destrabó** → **Sprint B**: Fase 4A.2 + 4A.3 (WA test number con +51947741117 doctora + bot-broker rule-based bidireccional).

**Si sigue trabado + docs RUC disponibles** → submit Business Verification formal Meta (1-3 sem review).

**Si sigue trabado + docs RUC no disponibles** → **Sprint C parcial**: Fase 4A.5 email marketing tool (MailerLite Free) + 2 flujos base (re-engagement inactivos + post-venta seguimiento). Aprovecha email institucional recién montado.

---

## 📝 Estado al 2026-05-10 cierre (Doctrina #14 + Workflow A2 bidireccional + cleanup Meta + auditoría exhaustiva)

### Sesión 2026-05-10 — modo PROYECTO declarado (#12)

**Sesión maratónica ~10h dividida en 4 bloques principales**:

**Bloque 1 — Audit + cleanup Meta Business** (~3h):
- Audit 15 puntos del ecosistema Meta paso a paso con screenshots
- 3 Business Managers detectados (Livskin Perú activo, Livskin Perú Comercial vacío, D'Claudia con doctora hosting Página FB + IG)
- Cleanup: 4 OAuth integrations eliminadas (Manychat + ReplyRush + agent n8n + n8n agent residuales) + Claude Audit App + agent n8n developer apps + System User Claude Audit neutralizado
- Pixel legacy `670708374433840` desconectado de cuenta publicitaria
- App Meta "Livskin Integraciones" creada (App ID `807721865486018`)
- Test number Cloud API `+1 555-191-3740` activado
- Domain Verification livskin.site + www.livskin.site via Cloudflare DNS TXT (programático API)
- Dominio agregado al perfil del BM (potencial unblocker shadow ban — re-revisión Meta 24-48h)

**Bloque 2 — Workflow A2 sync ERP→Vtiger (cierre bidireccional)** (~3h):
- ADR-0036 escrito (4 opciones consideradas, decisión cron pull patrón B3)
- Vtiger leadstatus picklist cleanup (Opción A replace estricto): 11 valores legacy → 6 español congruentes con ERP (Nuevo/Contactado/Agendado/Asistió/Cliente/Perdido)
- Workflow A1 actualizado: leadstatus 'New' → 'Nuevo'
- Endpoint ERP `/api/internal/leads/pending-vtiger-sync` con 17 tests pytest
- Workflow n8n [A2] importado + active=1 + activeVersionId fix + smoke E2E real exitoso (Vtiger LEA68 leadstatus Nuevo→Cliente, latencia ~2 min)
- 2 audit events nuevos categoría tracking.* (`vtiger_leadstatus_synced/failed`)
- Total eventos canónicos: 56 → 60
- **Bidireccional ERP↔Vtiger CERRADO COMPLETAMENTE** ⭐

**Bloque 3 — Doctrina #14 + auditoría exhaustiva** (~2h):
- Articulación del Principio Operativo #14 nuevo en CLAUDE.md
- 5 agentes Explore en paralelo auditaron todo el repo (master plan + 57 memorias + 22 ADRs + backlog/brand/runbooks/sesiones + código)
- Detectaron 2 contradicciones críticas + 6 menores + 8 gaps + 11 archivos a actualizar
- 11 updates en cascada ejecutados (CLAUDE.md, master plan v3.2, 5 memorias, 3 ADRs, 2 .md companions n8n, backlog, session log)

**Bloque 4 — Doctrina/memorias persistentes** (~2h):
- 2 memorias 🔥 CRÍTICAS nuevas: `feedback_sesion_estrategica_agentes_dedicada.md` + `project_interludio_estrategico_es_backbone.md`
- 4 memorias actualizadas: MEMORY.md + project_agent_org_design + project_roadmap + project_infra_security_agent
- Skills inventory actualizado con todas las capacidades de hoy
- ADR-0034 status DIFERIDA → SUPERSEDIDA por doctrina #14
- ADR-0001 § 9.1 tabla consumidores brain refleja V0/V1 + scripts
- README ADRs: 22 ADRs físicos (era 20), reservados 0037-0039 agregados

### Doctrinas articuladas hoy

**Principio Operativo #14**: Sesión estratégica de agentes IA es bloque DEDICADO post-backbone determinístico cerrado. Excepción permitida: Brand Orchestrator V0 BOOTSTRAP discrecional (briefs+copy monolítico, output revisable antes publicar). Conversation Agent IA NO bootstrap (rule-based hasta volumen >100 conv/día sostenido).

**Principio #13 trigger cierre revisado**: 2da campaña paga (era 1ra). Bridge Episode con solo 6 leads no aporta evidencia suficiente para cerrar bootstrap doctrina v0.1 → v1.0.

**Memoria `project_interludio_estrategico_es_backbone.md`**: interludio estratégico (brand voice + arquetipos + posicionamiento + plan estratégico) es PARTE del backbone (Fase 4A.6), no input externo a sesión de agentes.

### Bugs encontrados y arreglados

1. **A1 webhookId vacío post-SQL update ayer** → causaba `Cannot read properties of undefined (reading 'endsWith')` al activar workflow. Fix: borrar A1 completo + re-import via CLI con UUID webhookId nuevo.
2. **A2 sin activeVersionId post-import CLI** → n8n no procesaba workflow aunque active=1. Fix: SQL UPDATE `activeVersionId = versionId`.
3. **n8n CLI execute en standalone fallaba** (port 5679 ya en uso). Workaround: activación + restart en lugar de execute manual.
4. **Token Meta v4 visible en screenshots** del dashboard → revocado al final + valor limpiado de `keys/.env.integrations`.

### Estado al cierre

| Sistema | Estado |
|---|---|
| ERP `erp.livskin.site` | ✅ Funcionando + endpoint A2 deployed |
| Bidireccional ERP↔Vtiger | ✅ CERRADO (workflow A2 productivo) |
| Picklist Vtiger | ✅ 6 valores español congruentes |
| Workflows n8n | ✅ 7 activos (A1 + A2 + B1 + B3 + E1 + E2 + G3) |
| Meta App "Livskin Integraciones" | ✅ Creada, test number activo |
| WhatsApp Cloud API +51947741117 | 🔴 Bloqueado por restricción Meta (24-48h re-revisión post Domain Verif) |
| Tests ERP | ✅ 357 tests, coverage 75%+ |
| Audit events canónicos | ✅ 60 (10 categorías) |
| ADRs físicos | ✅ 22 (0001-0036) |
| Master plan | ✅ v3.2 actualizada |
| Bootstrap principio #13 | 🟡 ABIERTO hasta 2da campaña paga |

### 4 Commits del día

```
848dc75 docs: doctrina #14 + 11 updates en cascada para estabilizar layer agentes IA
9bb6f14 fix(n8n): A1 webhookId UUID format + smoke E2E A2 exitoso
9599081 feat(erp+n8n): ADR-0036 Workflow [A2] sync ERP -> Vtiger (cierra bidireccional)
e8cd4df docs(meta): audit Meta Business completo + cleanup ejecutado
ce2f978 fix(vtiger): cleanup leadstatus picklist + workflow A1 + ERP sync mapping
```

### Próxima sesión propuesta

**Sprint A — Email institucional + watchpoint Meta** (~30 min Zoho + pasivo):
- Zoho Mail Free + buzón `info@livskin.site`
- DNS records Cloudflare via API
- IMAP setup Gmail Android
- Watchpoint pasivo (24-48h): restricción Meta BM se levanta tras Domain Verification + cleanup OAuth

Si Meta destraba → Sprint B (Fase 4A.2 + 4A.3 implementación). Si no → Submit Business Verification cuando lleguen docs RUC.

---

## 📝 Estado al 2026-05-05 cierre (Bloque 0.5 Backups daily ACTIVADO + smoke integral 9 capas + auto-correcciones de proceso)

### Sesión 2026-05-05 — modo PROYECTO declarado (#12)

**Trabajos durables completados en esta sesión** (~6h, sin interferir Bridge Episode en curso):

1. **Smoke test integral 9 capas** ejecutado: VPS healthy, endpoints públicos 200, certs válidos 38-86d, DBs intactas (134 clientes / 88 ventas / 84 pagos / brain 1765 chunks), n8n cron jobs activos (5124 executions/7d en B3+E1+E2 con 100% success), audit log freshness OK, sensors recolectando 5min via VPC. **Resultado: sistema sano, sin issues críticos**.

2. **🔴 Bloque 0.5 Backups daily ACTIVADO** (resuelve el 🔴 CRÍTICO #1 del audit 2026-04-29):
   - Cron `/etc/cron.d/livskin-backups` instalado en los 3 VPS (02:00 backup, 04:00 verify, 05:00 cleanup)
   - SSH keys dedicadas `~/.ssh/backup-target` regeneradas en VPS1+VPS2 (las viejas se habían perdido)
   - User `backup` en destinos + dirs `/srv/backups/{local,vps1,vps2,vps3}/` con permisos correctos
   - AUDIT_INTERNAL_TOKEN distribuido a `/srv/livskin-revops/keys/.audit-internal-token` en los 3 VPS
   - **Bug fix**: `common.sh` línea `${2:-{}}` producía JSON malformed → fix `${2:-}` + default explícito (commit `ab38c6c`)
   - **Validación end-to-end 2026-05-05 19:43-19:44 UTC**: 6 audit events (`infra.backup_started/completed` x 3 VPS) registrados en livskin_erp.audit_log + archivos transferidos cross-VPS via VPC. Total 309MB respaldados (5.5M wp_db + 278M wp_files + 132K vtiger_db + 44K analytics + 856K metabase + 12M n8n_data + 141K erp_db + 2.7M brain_db).
   - Próximo cron run automático: 2026-05-06 02:00 UTC

3. **Eliminado Sub-bloque 3.2 Agenda backend** (12 archivos, escrito sin preflight el 2026-05-05 mañana). Decisión Dario: rebuild en Fase 4A post-Bridge con preflight estricto.

4. **VPS3 sync con main** — branch `chore/foundation-cross-vps` avanzada de `60b609d` a `e1ee4dd` via fast-forward. VPS1+VPS2 jalaron main también (pendiente desde commit `370ee37` que deshabilitó deploy automático).

**Auto-crítica documentada**: en esta sesión inicialmente fallé al no leer system-map ANTES de hacer audit infra (inventé `datos.livskin.site`, conté 66 leads sin filtrar `deleted=0`, marqué CRÍTICO un 403 que yo mismo causé, marqué backups "rotos" cuando estaban declarados pendientes en system-map §7). Tras corrección de Dario, leí los 140+ archivos del proyecto sistemáticamente. **Memoria nueva 🔥 a crear mañana (Bloque B endurecimiento)**: `feedback_session_warmup_obligatorio.md` + hook UserPromptSubmit que verifique lectura previa.

**Próxima sesión propuesta** (mañana 2026-05-06):
- Mañana: Bloque B endurecimiento de proceso (memoria warmup + hook + brain re-index)
- Tarde + 2026-05-07/08: ADRs refinamiento gobierno datos (rol Vtiger narrow) + GA4 cleanup
- 2026-05-09 fin Bridge Episode + 2026-05-12/13 post-mortem + cierre bootstrap (#13)

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
