# Livskin RevOps System

Sistema RevOps self-hosted para [livskin.site](https://livskin.site) — clínica de medicina estética en Wanchaq, Cusco.

Este repositorio es el **hub central de operaciones** del proyecto. Desde aquí se gestiona infraestructura, integraciones, agentes IA, analítica y documentación.

> **Documento autoritativo:** [docs/master-plan-mvp-livskin.md](docs/master-plan-mvp-livskin.md)  
> **Contexto para Claude Code:** [CLAUDE.md](CLAUDE.md)  
> **Index de decisiones:** [docs/decisiones/README.md](docs/decisiones/README.md)

---

## Arquitectura

```
Usuario → Cloudflare (DNS + SSL + WAF)
              │
    ┌─────────┼──────────┐
    ▼         ▼          ▼
  VPS 1     VPS 2       VPS 3
  WP        Ops         Data (nuevo)
  1GB       4GB         2GB

  WordPress  n8n         ERP Flask
             Vtiger      Postgres + pgvector
             Metabase    Embeddings service
             Postgres    (segundo cerebro)
             analytics

       └── DO VPC privada ───┘
```

Subdominios Cloudflare:
- `livskin.site` → VPS 1 (WordPress)
- `flow.livskin.site` → VPS 2 (n8n)
- `crm.livskin.site` → VPS 2 (Vtiger)
- `dash.livskin.site` → VPS 2 (Metabase)
- `erp.livskin.site` → VPS 3 (ERP refactorizado) — **Fase 1-2**
- `erp-staging.livskin.site` → VPS 3 (staging ERP) — **Fase 1**

---

## Stack

| Capa | Tecnologías |
|---|---|
| Cloud | DigitalOcean Frankfurt — 3 VPS conectados por **DO VPC** privada |
| Edge | Cloudflare — DNS + SSL + WAF + proxy |
| Containerización | Docker + Docker Compose + GitHub Actions CI/CD |
| CRM | Vtiger 8.2 (master de identidad cliente) |
| ERP | Flask refactorizado (master de transacciones, 2 cuentas: tú + doctora) |
| Orquestación | n8n 2.14 (primary) + Agent SDK (cuando aplique) |
| Data OLTP | MariaDB (WP, Vtiger) + Postgres (ERP) |
| Data OLAP | Postgres 16 + pgvector (analytics + segundo cerebro) |
| IA | Claude API (4 agentes) + Claude Design + fal.ai Flux + Canva API |
| Embeddings | `multilingual-e5-small` self-hosted ($0) |
| Tracking | Meta Pixel + Conversion API + GA4 + Measurement Protocol + GTM |
| Canal | WhatsApp Cloud API (test number en desarrollo) |
| Observabilidad | Langfuse + Metabase + logs estructurados |

**Stack explícitamente NO usado:** Airtable, Zapier/Make, HubSpot, Salesforce, LatePoint, Descript, Pinterest/Bing/Reddit pixels. Ver [master plan § 5.7](docs/master-plan-mvp-livskin.md#57-lo-que-explícitamente-no-usamos).

---

## Estructura del repo

```
livskin-revops/
│
├── CLAUDE.md                       # contexto maestro (leído por Claude Code al iniciar)
├── README.md                       # este archivo
├── .gitignore                      # excluye secretos, keys, erp/, backups/
├── .claude/settings.json           # permisos Claude Code (DENY en erp/)
│
├── docs/
│   ├── master-plan-mvp-livskin.md  # ⭐ PLAN AUTORITATIVO
│   ├── decisiones/                 # ADRs (Architecture Decision Records)
│   │   ├── README.md               # index de decisiones (40+)
│   │   ├── _template.md            # plantilla ADR
│   │   ├── 0001-segundo-cerebro-*.md
│   │   ├── 0002-arquitectura-*.md
│   │   └── 0003-seguridad-*.md
│   ├── sesiones/                   # log cronológico de sesiones de trabajo
│   ├── audits/                     # auditorías mensuales/trimestrales
│   ├── seguridad/                  # políticas de seguridad
│   ├── runbooks/                   # procedimientos operativos
│   ├── diagramas/                  # diagramas arquitectura
│   ├── system-audit-2026-04-16.md  # audit histórico previo
│   ├── consultas-y-decisiones.md   # bitácora sesión anterior
│   ├── Datos Livskin.xlsx          # data real negocio
│   └── livskin_pensamientos....docx # blueprint original
│
├── infra/                          # infraestructura servicios
│   ├── docker/                     # docker-compose por servicio
│   │   ├── n8n/
│   │   ├── vtiger/
│   │   ├── metabase/
│   │   ├── postgres/
│   │   └── nginx/
│   ├── nginx/                      # configs nginx
│   ├── scripts/                    # backup.sh, restore.sh
│   └── sql/                        # schemas base
│
├── integrations/                   # servicios externos (cada uno con README)
│   ├── meta/                       # Business Manager, Pixel, CAPI, Ads
│   ├── google/                     # GA4, GTM, Search Console
│   ├── whatsapp/                   # Cloud API, test number, templates
│   ├── cloudflare/                 # DNS, SSL, WAF
│   ├── canva/                      # Brand Kit, API
│   ├── anthropic/                  # Claude API, budget
│   ├── fal-ai/                     # Flux Pro
│   └── claude-design/              # landing pages + banners
│
├── agents/                         # 4 agentes IA (Fase 4-6)
│   ├── conversation/
│   │   ├── prompts/                # versionados
│   │   ├── tools/                  # tool specs
│   │   └── evals/                  # golden set
│   ├── content/
│   ├── acquisition/
│   └── growth/
│
├── analytics/                      # warehouse + dashboards
│   ├── schemas/                    # DDL de analytics DB
│   ├── migrations/                 # Alembic
│   └── dashboards/                 # exports Metabase
│
├── keys/                           # ⚠️ gitignored
│   ├── claude-livskin (pub+priv)   # SSH key para VPS
│   ├── ssh_config                  # config SSH local
│   ├── .env.integrations           # ⚠️ tokens API (respaldo Bitwarden)
│   └── *.ppk                       # conservadas por referencia
│
├── erp/                            # ⚠️ gitignored — repo separado
│   └── livskin-formulario/         # clon del ERP (opcional, solo local)
│
└── backups/                        # ⚠️ gitignored — pulls manuales
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

# 4. Probar conexión a VPS
ssh -F keys/ssh_config livskin-wp 'whoami'
ssh -F keys/ssh_config livskin-ops 'whoami'
# livskin-data cuando esté creado (Fase 1)

# 5. Abrir en Claude Code → lee CLAUDE.md + memoria + último session log
```

---

## Cómo trabajar con este repo

Las decisiones se toman vía **ADRs** (Architecture Decision Records) en `docs/decisiones/`. Cada decisión importante tiene su propio documento con contexto, opciones, tradeoffs y resolución.

Sesiones de trabajo quedan logueadas en `docs/sesiones/YYYY-MM-DD-titulo.md`.

Auditorías en `docs/audits/`.

**Flujo de trabajo habitual:**

```
1. Claude Code lee CLAUDE.md + última sesión al iniciar
2. Se trabaja en una sesión (estratégica o ejecución)
3. Al cierre: session log + ADRs actualizados si hubo decisiones
4. Commit + push (branch → PR → merge)
5. CI/CD desplega cambios a VPS (Fase 1+)
```

**Ramas:**
- `main` — producción, siempre deployable
- `staging` — pre-producción (Fase 1+)
- `feature/*` — nuevas funcionalidades
- `fix/*` — correcciones

**Commits:** naming `tipo: descripción` (feat, fix, refactor, docs, chore, test, security, perf).

---

## Roadmap 10 semanas

| Fase | Semana | Foco | Estado |
|---|---|---|---|
| 0 | 1 | Fundación: docs, reorganización, dossiers | 🚧 En curso (2026-04-18) |
| 1 | 2 | VPS 3, DO VPC, Postgres+pgvector, CI/CD | ⏳ |
| 2 | 3-4 | Gobierno datos + ERP refactor + backfill | ⏳ |
| 3 | 5 | Tracking + observabilidad (Langfuse) | ⏳ |
| 4 | 6 | Conversation Agent con test number WhatsApp | ⏳ |
| 5 | 7-8 | Content Agent + Acquisition Engine | ⏳ |
| 6 | 9-10 | Growth Agent + evals + estabilización | ⏳ |

Detalle completo: [docs/master-plan-mvp-livskin.md § 11](docs/master-plan-mvp-livskin.md#11-roadmap-10-semanas-con-6-workstreams).

---

## Seguridad

Ver [ADR-0003](docs/decisiones/0003-seguridad-baseline-y-auditorias.md).

Resumen de controles baseline:
- UFW + Fail2Ban en los 3 VPS
- Root login deshabilitado, SSH key-only, sudo NOPASSWD
- DO VPC privada entre VPS (no hay tráfico inter-VPS por internet público)
- TLS en todo el tráfico externo (Cloudflare Full Strict)
- Secretos en `.env` gitignored + respaldo Bitwarden cifrado
- 2FA obligatorio en DO, Cloudflare, GitHub, Anthropic
- Audit log inmutable en ERP
- Auditorías mensuales automatizadas + trimestrales comprehensivas

---

## Backups

Estrategia escalonada:

| Fase | Tipo | Frecuencia | Ubicación |
|---|---|---|---|
| 0 | Snapshot manual baseline | 1 vez pre-cambios | Local `backups/` |
| 2+ | Daily por DB | 03:00 UTC | Local + cross-VPS |
| Futuro | Off-site real | Semanal | Pendiente (no habilitado aún) |

Ver [ADR-0041](docs/decisiones/README.md) para política completa.

---

## Licencia y uso

Proyecto privado. Código del ERP vive en repo separado (no incluido aquí).

---

**Mantenido por:** Dario Urrutia  
**Herramienta principal de construcción:** [Claude Code](https://claude.ai/code)  
**Última actualización README:** 2026-04-18 (Fase 0)
