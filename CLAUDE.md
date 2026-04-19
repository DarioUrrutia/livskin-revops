# CLAUDE.md — Contexto maestro del proyecto Livskin

> Este archivo es leído automáticamente por Claude Code al iniciar cada sesión.  
> Su propósito: cargar en memoria el contexto operativo suficiente para trabajar sin fricción.  
> Última actualización: 2026-04-18 (v1.0 — Fase 0)

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

1. **[docs/master-plan-mvp-livskin.md](docs/master-plan-mvp-livskin.md)** — plan maestro vivo, referencia autoritativa
2. **[docs/decisiones/README.md](docs/decisiones/README.md)** — index de 40+ ADRs con estado
3. **[docs/backlog.md](docs/backlog.md)** — backlog vivo de ideas/cambios/dudas (revisar qué retomar)
4. **[notes/compartido/](notes/compartido/)** — notas colaborativas recientes si las hay
5. **[docs/sesiones/](docs/sesiones/)** — último log de sesión para entender dónde quedamos
6. **Blueprint original** — [docs/livskin_pensamientos para una implemetacion profesional basica pero basada en ia.docx](docs/livskin_pensamientos%20para%20una%20implemetacion%20profesional%20basica%20pero%20basada%20en%20ia.docx)
7. **Memoria Claude Code** — ya cargada automáticamente (`user_profile`, `project_livskin_overview`, `project_stack`, `project_roadmap`, `feedback_operating_principles`, `vps_access`, `project_adr_system`, `reference_docs`)

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
| CRM | Vtiger 8.2 (master identidad cliente) |
| ERP | Flask refactorizado (master transacciones, 2 cuentas: tú + doctora) |
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

## 🗺️ Roadmap 10 semanas — estado actual

| Fase | Semana | Estado |
|---|---|---|
| 0 | 1 | 🚧 **En curso** (hoy, 2026-04-18) |
| 1 | 2 | ⏳ Pendiente |
| 2 | 3-4 | ⏳ |
| 3 | 5 | ⏳ |
| 4 | 6 | ⏳ |
| 5 | 7-8 | ⏳ |
| 6 | 9-10 | ⏳ |

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

**Cierre (mío, 2 min):** 
- Genero `docs/sesiones/YYYY-MM-DD-titulo.md` con qué se hizo, qué quedó pendiente, próximo paso
- Muevo items de backlog a "Hecho" si corresponde
- Actualizo CLAUDE.md, master plan, memoria si hubo cambios estructurales
- Si surgió idea nueva no-urgente → la agrego a `docs/backlog.md` con tu aprobación

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
2. **Commitear secretos** (archivos `.env*` salvo `.env.example`, `keys/*.pem`, `keys/*.key`, `keys/.env.integrations`).
3. **Push force a `main`.** Usar branches + PR.
4. **Proponer servicios pagos** sin preguntar. Principio 8.
5. **Correr implementación antes de tener dossier aprobado** para la decisión subyacente. Principio 9.
6. **Asumir que la usuaria conoce un término técnico.** Explicar siempre al aterrizar.
7. **Saltar fases del roadmap.** Cada fase tiene dependencies razonadas.
8. **Saltar el trámite WhatsApp Business API.** 5-10 días hábiles de Meta, bloqueo real.
9. **Tocar VPS en producción sin snapshot previo y sin staging validado.**
10. **Borrar/modificar historial git** sin autorización explícita.

---

## 📝 Estado al 2026-04-18 (cierre Fase 0)

**Lo que está hecho:**
- Repo conectado a GitHub `DarioUrrutia/livskin-revops`
- SSH a los 2 VPS existentes funcionando desde esta máquina (`keys/claude-livskin`)
- Auditoría en vivo completada sobre audit base 2026-04-16
- Datos reales del negocio procesados (74 ventas, 135 clientes, catálogo completo)
- ERP Livskin en producción en Render revisado (formulario-livskin.onrender.com)
- **Plan maestro v1.0 consolidado** en [docs/master-plan-mvp-livskin.md](docs/master-plan-mvp-livskin.md)
- **3 dossiers fundacionales aprobados** (segundo cerebro, arquitectura, seguridad)
- Repo reorganizado a estructura definitiva (infra/, integrations/, agents/, analytics/)
- Memoria Claude Code poblada con contexto completo
- 10 principios operativos codificados

**Lo que queda pendiente de tu parte:**
1. Crear Meta App + activar WhatsApp test number (15 min) — instrucciones en `integrations/whatsapp/README.md`
2. Iniciar trámite WhatsApp Business API para número producción (5-10 días Meta) — en paralelo
3. Instalar Bitwarden + guardar `keys/.env.integrations` como respaldo
4. Confirmar tu disponibilidad real semanal (asumido 12-15h)

**Próximo paso (Fase 1, Semana 2):**
- Provisionar VPS 3 ($12/mes)
- Configurar DO VPC entre los 3 VPS
- Instalar Docker + Postgres 16 + pgvector + embeddings service
- GitHub Actions CI/CD
- Alembic configurado
- Staging env

---

## 📚 Glosario rápido

Ver [docs/master-plan-mvp-livskin.md § 17](docs/master-plan-mvp-livskin.md#17-glosario) para definiciones completas.

**ADR** — Architecture Decision Record · **CAPI** — Conversion API de Meta · **DO VPC** — red privada DigitalOcean · **ETL** — Extract/Transform/Load · **MCP** — Model Context Protocol · **OLTP/OLAP** — operativo/analítico · **pgvector** — extensión Postgres para vectores · **RAG** — Retrieval-Augmented Generation · **SoT** — Source of Truth · **Strangler fig** — patrón de migración gradual.

---

**Este archivo se actualiza al cierre de cada fase del roadmap.** La versión autoritativa del proyecto es siempre el `master-plan-mvp-livskin.md`; este CLAUDE.md es un resumen navegable para arranque rápido.
