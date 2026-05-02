# Livskin RevOps System

Sistema RevOps self-hosted para [livskin.site](https://livskin.site) — clínica de medicina estética en Wanchaq, Cusco.

Este repositorio es el **hub central de operaciones** del proyecto. Desde aquí se gestiona infraestructura, integraciones, agentes IA, analítica y documentación.

> **Documento autoritativo del plan:** [docs/master-plan-mvp-livskin.md](docs/master-plan-mvp-livskin.md)
> **Contexto para Claude Code (auto-cargado al iniciar):** [CLAUDE.md](CLAUDE.md)
> **Index de decisiones (ADRs):** [docs/decisiones/README.md](docs/decisiones/README.md)
> **Doctrina rectora:** principio operativo #11 — *"Deterministic backbone first — IA es capa aditiva, no foundational"* (memoria 🔥 CRÍTICA `feedback_deterministic_backbone_first.md`)

---

## Arquitectura

```
Usuarios públicos → Cloudflare (DNS + SSL + WAF + Pages)
                          │
                ┌─────────┼──────────┐
                ▼         ▼          ▼
             VPS 1     VPS 2       VPS 3                Cloudflare Pages
             WP        Ops         Data + ERP            campanas.livskin.site
             1GB       4GB         2GB
                                                         (landings dedicadas)
             WordPress  n8n        ERP Flask
                        Vtiger     Postgres + pgvector
                        Metabase   Embeddings service
                        Postgres   (segundo cerebro)
                        analytics
                        sensor

             └────── DO VPC privada (10.114.0.x) ──────┘
```

**Subdominios live (verificados 2026-05-03):**

| Subdominio | Destino | Estado |
|---|---|---|
| `livskin.site` → `www.livskin.site` | VPS 1 (WordPress) | ✅ |
| `flow.livskin.site` | VPS 2 (n8n) | ✅ |
| `crm.livskin.site` | VPS 2 (Vtiger) | ✅ |
| `dash.livskin.site` | VPS 2 (Metabase) | ✅ |
| `erp.livskin.site` | VPS 3 (ERP refactorizado) | ✅ |
| `campanas.livskin.site` | Cloudflare Pages (landings) | ✅ |

**Eliminado 2026-04-26** (decisión Opción A, commit `59e37c2`): `erp-staging.livskin.site` ya no existe. Razón: durante Fases 2-5 el ERP en VPS 3 actúa como staging del Render productivo — staging del staging era redundante. Reaparece como staging real con DB separada en **Fase 6** al cutover (ADR-0024 strangler fig).

---

## Stack

| Capa | Tecnologías |
|---|---|
| Cloud | DigitalOcean Frankfurt — 3 VPS conectados por **DO VPC** privada |
| Edge | Cloudflare — DNS + SSL + WAF + Pages (landings) |
| Containerización | Docker + Docker Compose + GitHub Actions CI/CD |
| CRM | Vtiger 8.2 (master del **lead digital** — marketing automation) |
| ERP | Flask refactorizado (master de **cliente + transacciones**, 2 cuentas: tú + doctora) |
| Orquestación | n8n 2.x — 6 workflows live (A1, B1, B3, E1, E2, G3) |
| Data OLTP | MariaDB (WP, Vtiger) + Postgres 16 (ERP) |
| Data OLAP | Postgres 16 + pgvector (analytics warehouse + segundo cerebro Layer 2) |
| IA | Claude API (1 agente real V1 + 2 scripts) + Claude Design + fal.ai + Canva API |
| Embeddings | `multilingual-e5-small` self-hosted ($0) — Layer 2 con 1.765 chunks indexados |
| Tracking | Meta Pixel (4410809639201712) + Conversion API server-side via n8n + GA4 + GTM |
| Canal | WhatsApp Cloud API (test number `+393514918531` — provisorio) |
| Observabilidad | audit_log inmutable + Metabase + logs estructurados + livskin-sensor cross-VPS |

**Stack explícitamente NO usado:** Airtable, Zapier/Make, HubSpot, Salesforce, LatePoint, Descript, Pinterest/Bing/Reddit pixels.

---

## Estructura del repo

```
livskin-revops/
│
├── CLAUDE.md                       # ⭐ contexto auto-cargado por Claude Code
├── README.md                       # este archivo
├── .gitignore                      # excluye secretos, keys, erp/, backups/
├── .claude/settings.json           # permisos Claude Code (DENY en erp/)
│
├── docs/
│   ├── master-plan-mvp-livskin.md  # ⭐ PLAN AUTORITATIVO
│   ├── backlog.md                  # backlog vivo (pendiente + histórico ✅)
│   ├── audit-events-schema.md      # 56 eventos canónicos del audit_log
│   ├── sistema-mapa.md             # mapa machine-readable VPS/containers/flujos
│   ├── decisiones/                 # ADRs físicos (20 reales) + index
│   ├── runbooks/                   # 18 runbooks operativos (frontmatter MCP)
│   ├── audits/                     # auditorías ad-hoc + estratégicas
│   ├── sesiones/                   # log cronológico de sesiones de trabajo
│   ├── campaigns/                  # planes de campañas pagas (con tracking)
│   ├── seguridad/                  # políticas de seguridad
│   ├── legal/                      # privacy + terms + cookie policy
│   └── legacy/                     # docs históricos pre-roadmap (referencia)
│
├── infra/                          # infraestructura
│   ├── docker/                     # docker-compose por servicio
│   │   ├── vps1-wp/                # plugins WP + mu-plugin
│   │   ├── vps2-ops/               # n8n + vtiger + metabase + postgres-analytics
│   │   ├── erp-flask/              # ERP refactorizado (VPS 3)
│   │   ├── postgres-data/          # Postgres + pgvector (VPS 3)
│   │   ├── embeddings-service/     # multilingual-e5-small (VPS 3)
│   │   ├── alembic-erp/            # migrations ERP
│   │   ├── alembic-brain/          # migrations brain
│   │   ├── brain-tools/            # CLI brain (indexer + query)
│   │   ├── nginx-vps3/             # reverse proxy VPS 3
│   │   ├── livskin-sensor/         # health sensor cross-VPS
│   │   └── mcp-livskin/            # MCP scaffold (Fase 6+)
│   ├── n8n/workflows/              # workflows como JSON versionado
│   ├── nginx/                      # configs nginx
│   ├── scripts/                    # backup-vps[1|2|3].sh + sensor-collect
│   └── cloudflare-pages/           # landings dedicadas (campanas.livskin.site)
│
├── analytics/                      # warehouse + dashboards
│   ├── schemas/                    # DDL v2 + v3 opportunities
│   ├── migrations/                 # Alembic warehouse
│   └── dashboards/                 # exports JSON Metabase
│
├── integrations/                   # servicios externos
│   ├── meta/                       # Business Manager, Pixel, CAPI
│   ├── google/                     # GA4, GTM, Search Console
│   ├── whatsapp/                   # Cloud API, test number, templates
│   ├── cloudflare/                 # DNS, SSL, WAF, Pages
│   ├── canva/                      # Brand Kit, API
│   ├── anthropic/                  # Claude API, budget
│   ├── fal-ai/                     # Flux Pro
│   └── claude-design/              # landing pages + banners
│
├── agents/                         # 1 agente real V1 + 2 scripts (post-audit 2026-05-03)
│   ├── README.md                   # scope reducido per audit
│   ├── conversation/               # ⏸️ diferido (V1 será chatbot rule-based)
│   ├── content/                    # → Brand Orchestrator (único agente IA V1)
│   ├── acquisition/                # → script con LLM ocasional, no agente
│   └── growth/                     # → script con LLM ocasional, no agente
│
├── skills/                         # capacidades determinísticas reutilizables
│   ├── livskin-ops/                # read-only ops (deploy del 5to agente)
│   └── livskin-deploy/             # deploys autorizados
│
├── notes/                          # vault Obsidian (compartido + privado)
│   ├── compartido/                 # versionado con git
│   └── privado/                    # ⚠️ gitignored, solo de Dario
│
├── scripts/                        # scripts ad-hoc (Python + shell)
│
├── keys/                           # ⚠️ gitignored
│   ├── claude-livskin (pub+priv)   # SSH key VPS
│   ├── ssh_config                  # config SSH local
│   └── .env.integrations           # ⚠️ tokens API (respaldo Bitwarden)
│
└── memory/                         # ⚠️ ruta del .claude del proyecto (gitignored)
                                    # 🔥 memorias CRÍTICAS + arquitectura + gobernanza
```

---

## Setup (nueva máquina)

Pre-requisitos: Git, OpenSSH.

```bash
# 1. Clonar el repo
git clone https://github.com/DarioUrrutia/livskin-revops.git "livskin-revops"
cd "livskin-revops"

# 2. Descargar credenciales desde Bitwarden
#    (guardar como keys/.env.integrations)
#    (guardar las SSH keys privadas si no las tienes)

# 3. Asegurar permisos SSH key
chmod 600 keys/claude-livskin

# 4. Probar conexión a los 3 VPS
ssh -F keys/ssh_config livskin-wp 'whoami && uptime'
ssh -F keys/ssh_config livskin-ops 'whoami && uptime'
ssh -F keys/ssh_config livskin-erp 'whoami && uptime'

# 5. Abrir en Claude Code → lee CLAUDE.md + memoria + último session log
```

---

## Cómo trabajar con este repo

Las decisiones se toman vía **ADRs** (Architecture Decision Records) en `docs/decisiones/`. Cada decisión importante tiene su propio documento con contexto, opciones, tradeoffs y resolución.

Sesiones de trabajo quedan logueadas en `docs/sesiones/YYYY-MM-DD-titulo.md`.

Auditorías en `docs/audits/`.

**Flujo de trabajo habitual:**

```
1. Claude Code lee CLAUDE.md + última sesión + memorias 🔥 CRÍTICAS al iniciar
2. Se trabaja en una sesión (estratégica o ejecución)
3. Al cierre: session log + ADRs actualizados si hubo decisiones
4. Commit + push (branch → PR → merge)
5. CI/CD desplega cambios a VPS
```

**Ramas:**
- `main` — producción, siempre deployable
- `chore/foundation-cross-vps` — branch histórica del Bloque 0 v2 (legacy, no se mergea, los commits siguen entrando a main)
- `feature/*` — nuevas funcionalidades
- `fix/*` — correcciones

**Commits:** naming `tipo: descripción` (feat, fix, refactor, docs, chore, test, security, perf).

---

## Roadmap (estado al 2026-05-03)

| Fase | Estado | Notas |
|---|---|---|
| 0 — Fundación | ✅ Completa (2026-04-18) | repo + dossiers + memoria |
| 1 — VPS 3 + infra | ✅ Completa (2026-04-20) | postgres + pgvector + brain L2 |
| 2 — ERP refactor + gobierno datos | ✅ ~99% (2026-04-26) | erp-staging eliminado decisión cerrada (vuelve en Fase 6) |
| Bloque 0 v2 — Cross-VPS state-of-the-art | ✅ Completo (2026-04-26) | sensors + backups + 18 runbooks + skills MCP |
| 3 — Tracking + atribución end-to-end | ✅ **CERRADA** (2026-05-02) | 3.1+3.2+3.3+3.4+3.5+3.6 + Bloque 1 puente |
| 🚀 **Bridge Episode** — Primera campaña paga FB Ads | **EN CURSO 2026-05-03** | $100/5 días, 3 destinos. Detalle: [docs/campaigns/2026-05-first-campaign/plan.md](docs/campaigns/2026-05-first-campaign/plan.md) |
| 4A — Backbone determinístico restante | ⏳ Post-campaña | chatbot WA rule-based + módulo Agenda + notifs + re-engagement |
| 4B — Brand Orchestrator (1er agente IA real) | ⏳ Post-4A validado | caso canónico subagentes; brand voice consolidado primero |
| 5 — Acquisition synth + Growth narrative | ⏳ Post-4B con ROI | scripts con LLM ocasional, NO agentes (audit 2026-05-03) |
| 6 — Cutover ERP Render→VPS3 + estabilización | ⏳ Final MVP | TRUNCATE sintéticos + populate catálogo real |

**ADRs supersedidas/diferidas por audit 2026-05-03:**
- ADR-0034 v1.0 Conversation Agent IA Foundation → 💤 Diferida (será supersedida por ADR Conversation Agent v0 rule-based en Fase 4A)

Detalle completo: [docs/master-plan-mvp-livskin.md § 11](docs/master-plan-mvp-livskin.md#11-roadmap-10-semanas-con-6-workstreams).

---

## Filosofía operativa — 11 principios

Rigen cada decisión técnica y estratégica. Vinculantes, no aspiracionales.

1. Lo ejecutable supera a lo ideal
2. Tiempo humano es el recurso más caro
3. Una fuente de verdad por dominio
4. Observabilidad desde el día uno
5. Reversibilidad de decisiones
6. Respeto al equipo humano
7. Honestidad técnica radical
8. Cero servicios pagos nuevos sin aprobación explícita
9. Antes de implementar, definir
10. Responder a la profundidad pedida
11. **Deterministic backbone first — IA es capa aditiva, no foundational** (articulado 2026-05-03)

Detalle completo: [master plan § 4](docs/master-plan-mvp-livskin.md#4-filosofía-operativa--11-principios).

---

## Seguridad

Ver [ADR-0003](docs/decisiones/0003-seguridad-baseline-y-auditorias.md).

Resumen de controles baseline:
- UFW + Fail2Ban en los 3 VPS
- Root login deshabilitado, SSH key-only, sudo NOPASSWD
- DO VPC privada entre VPS (no hay tráfico inter-VPS por internet público)
- TLS en todo el tráfico externo (Cloudflare Full Strict)
- Cloudflare Turnstile en SureForms 1569 + plugin login form (mini-bloque 3.1)
- Secretos en `.env` gitignored + respaldo Bitwarden cifrado
- 2FA obligatorio en DO, Cloudflare, GitHub, Anthropic
- Audit log inmutable en ERP (56 eventos canónicos en 10 categorías)
- Auditorías mensuales automatizadas + ad-hoc

---

## Backups

Estrategia escalonada (ver `infra/scripts/backups/`):

| Tipo | Frecuencia | Ubicación |
|---|---|---|
| Snapshot DigitalOcean pre-deploy | Auto vía CI/CD | DO console |
| Daily backup-vps[1\|2\|3].sh | 03:00 UTC cron | `/srv/backups/` cross-VPS |
| Verificación automática | post-backup | audit log integration |

---

## Licencia y uso

Proyecto privado. Código del ERP vive en repo separado (no incluido aquí — `erp/` está gitignored).

---

**Mantenido por:** Dario Urrutia
**Herramienta principal de construcción:** [Claude Code](https://claude.ai/code)
**Última actualización:** 2026-05-03 (post-pivot estratégico + audit scope agentes)
