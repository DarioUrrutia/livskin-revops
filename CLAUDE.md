# CLAUDE.md — Contexto maestro del proyecto Livskin

> Este archivo es leído automáticamente por Claude Code al iniciar cada sesión.  
> Su propósito: cargar en memoria el contexto operativo suficiente para trabajar sin fricción.  
> Última actualización: 2026-04-26 (v2.0 — Bloque 0 cimientos cross-VPS state-of-the-art completo)

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

## 🗺️ Roadmap — estado actual

| Fase | Estado |
|---|---|
| 0 | ✅ Completada (2026-04-18) |
| 1 | ✅ Completada (2026-04-20) |
| 2 | ✅ Implementación ~99% (auth + audit + dashboard + tests 81% coverage al 2026-04-26) |
| **0 v2 (Bloque foundation cross-VPS)** | ✅ **Completado 2026-04-26** — versionado VPS 1+2 + CI/CD multi-VPS + system-map + sensors + backups + runbooks + DR drill + skills + MCP scaffold |
| 3 | ⏳ Próxima — tracking + observabilidad (Meta Pixel + GA4 + GTM + Langfuse + UTMs) |
| 4 | ⏳ Conversation Agent (WhatsApp test number) |
| 5 | ⏳ Content + Acquisition Agents |
| 6 | ⏳ Growth + cutover ERP real + 5to agente Infra+Security |

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

## 📝 Estado al 2026-04-26 (Bloque foundation completo + Fase 2 ~99%)

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
