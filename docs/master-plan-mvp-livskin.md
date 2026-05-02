# Plan Maestro — Livskin RevOps MVP

**Versión:** 1.0 · **Fecha:** 2026-04-18 · **Estado:** Vivo (actualizado en cada decisión estructural)

> Este documento es la **referencia autoritativa del proyecto**. Cualquier decisión o conversación estratégica debe ser reflejada aquí. Lo que no está escrito aquí no existe para el proyecto.

---

## Índice

1. [Propósito y uso de este documento](#1-propósito-y-uso-de-este-documento)
2. [Contexto del proyecto](#2-contexto-del-proyecto)
3. [Doble objetivo estratégico](#3-doble-objetivo-estratégico)
4. [Filosofía operativa — 10 principios](#4-filosofía-operativa--10-principios)
5. [Stack tecnológico definitivo](#5-stack-tecnológico-definitivo)
6. [Arquitectura del sistema](#6-arquitectura-del-sistema)
7. [Segundo cerebro — workstream estratégico](#7-segundo-cerebro--workstream-estratégico)
8. [Seguridad — workstream estratégico](#8-seguridad--workstream-estratégico)
9. [Tracking y atribución](#9-tracking-y-atribución)
10. [Agentes IA](#10-agentes-ia)
11. [Roadmap 10 semanas con 6 workstreams](#11-roadmap-10-semanas-con-6-workstreams)
12. [Convenciones y estándares](#12-convenciones-y-estándares)
13. [Diferimentos explícitos](#13-diferimentos-explícitos)
14. [Riesgos y mitigaciones](#14-riesgos-y-mitigaciones)
15. [Observabilidad y auditoría continua](#15-observabilidad-y-auditoría-continua)
16. [Integración Claude Design](#16-integración-claude-design)
17. [Glosario](#17-glosario)
18. [Operación post-MVP y mantenimiento](#18-operación-post-mvp-y-mantenimiento)
19. [Changelog](#19-changelog)

---

## 1. Propósito y uso de este documento

Este plan maestro:

- **Consolida** todas las decisiones estructurales del proyecto Livskin en un solo lugar
- **Precede** cualquier implementación: nada se construye sin estar planificado aquí
- **Evoluciona** con el proyecto: cada decisión importante se refleja en el changelog
- **Es leído** al inicio de cada sesión de trabajo (tanto por la usuaria como por Claude Code)
- **Referencia** documentos más profundos (dossiers, audits, diagramas) en lugar de duplicar su contenido

**Qué NO es este documento:**
- No es un manual de uso del sistema (eso está en `docs/runbooks/`)
- No es documentación técnica detallada por componente (eso está en cada `integrations/*/README.md` y `agents/*/README.md`)
- No es un diario de sesión (eso está en `docs/sesiones/`)
- No es una decisión final aislada (eso está en `docs/decisiones/`)

---

## 2. Contexto del proyecto

### 2.1 La empresaria

| Atributo | Valor |
|---|---|
| Perfil profesional | Economista + MBA. Especializaciones: Finanzas, Marketing Digital |
| Residencia | Milán, Italia |
| Nivel técnico | Principiante declarado; estilo de trabajo "vibe coding" |
| Herramientas centrales | Claude Code (esta sesión), Claude Max 5x, Canva Pro |
| Disponibilidad | 12-15 h/semana (puede escalar) |

### 2.2 El negocio

**Livskin** es una clínica de medicina estética real, ubicada en **Wanchaq, Cusco, Perú**.

| Datos operativos | Valor |
|---|---|
| Mercado objetivo | Mujeres 35-60 años, clase media y media-alta de Cusco (3,000-5,000 estimadas) |
| Oferta | Botox, ácido hialurónico, PRP, hilos, exosomas, tratamientos faciales |
| Ticket range | S/.40 — S/.1,800 |
| Ticket promedio real (datos reales) | **S/.405** (medido sobre 74 ventas en 7 semanas) |
| Revenue promedio mensual | **~S/.18,000** (proyectado con datos reales) |
| Clientes registrados | **135** (al 2025-11-14) |
| Ventas registradas | **74** (período 2025-09-25 → 2025-11-14) |
| Mix de ventas | 82% tratamientos, 18% productos |
| Top categoría | **Botox: 34% del volumen** — producto estrella |
| Pagos digitales | 53% (Yape 31% + Plin 15% + Transferencia 6%) |
| Pagos efectivo | **47%** (crítico: mitad no trazable por defecto) |

### 2.3 El gap crítico actual

**No existe el campo "fuente del lead"** en los datos actuales. Consecuencia directa: hoy NO se puede atribuir revenue a canal de marketing. Cerrar este gap es el **primer objetivo funcional** del sistema nuevo.

### 2.4 Infraestructura heredada (al iniciar Fase 0)

| VPS | IP pública | IP VPC | Rol | Stack |
|---|---|---|---|---|
| WP (`livskin-wp`) | 46.101.97.246 | 10.114.0.3 | WordPress público | Ubuntu 22.04 + Nginx + PHP-FPM 8.1 + MariaDB 10.6 + WP 6.9.4 |
| Ops (`livskin-ops`) | 167.172.97.197 | 10.114.0.2 | Orquestación + analítica | Ubuntu 22.04 + Docker 29.3.1 + 6 contenedores (nginx, n8n, vtiger, vtiger-db, postgres-analytics, metabase) |
| ERP (`livskin-erp`) | **139.59.214.7** | **10.114.0.4** | ERP + segundo cerebro | Ubuntu 22.04.5 + Docker 29.4.0 — provisionado 2026-04-19, Postgres+pgvector y servicios pendientes |

Los 3 VPS en DO VPC `10.114.0.0/20` Frankfurt, latencia inter-VPS <2ms verificada.

### 2.5 Referencias documentales

- **Blueprint maestro:** `docs/livskin_pensamientos para una implemetacion profesional basica pero basada en ia.docx`
- **Audit técnico base:** `docs/system-audit-2026-04-16.md`
- **Bitácora previa:** `docs/consultas-y-decisiones.md`
- **Datos reales del negocio:** `docs/Datos Livskin.xlsx`
- **ERP actual en producción:** https://formulario-livskin.onrender.com/ (repo GitHub propio separado)

---

## 3. Doble objetivo estratégico

El proyecto persigue **dos objetivos simultáneos, no alternativos**. Toda decisión se evalúa contra ambos.

### 3.1 Objetivo operacional

Construir un sistema RevOps con IA que permita a Livskin:

- Responder leads en **<60 segundos** (vs competencia que responde en horas/días)
- Reactivar pacientes cada **45 días** (vs "cuando se acuerdan")
- Generar 12+ creativos de ads por semana (vs 1-2 hoy artesanales)
- Atribuir cada Sol de revenue a su canal de origen
- Liberar tiempo del equipo humano (la doctora + la empresaria) en ~80% de tareas operativas repetitivas
- Reducir CAC a <S/.80 por paciente convertido

### 3.2 Objetivo portfolio

La empresaria persigue en paralelo un desarrollo profesional como **RevOps de clase mundial** (target salarial $140-220K USD/año en el rol "AI RevOps"). Este proyecto es:

- **Caso de estudio técnico público** — arquitectura multi-VPS + multi-agente + observabilidad
- **Material de entrevistas** — decisiones explícitas con ADRs, tradeoffs documentados, migraciones zero-downtime
- **Ejemplo de implementación end-to-end** — pocas personas combinan Economía + MBA + Marketing + CRM + Claude Code + n8n + producción real

### 3.3 Regla cuando los objetivos chocan

Si una decisión favorece a uno pero perjudica al otro, **gana el operacional**. La clínica es real, los pacientes existen, el revenue depende del sistema. Elegir elegancia técnica sobre confiabilidad operacional es traicionar el proyecto.

---

## 4. Filosofía operativa — 11 principios

Rigen cada decisión técnica y estratégica. No son aspiracionales — son vinculantes.

1. **Lo ejecutable supera a lo ideal.** Sistema 7/10 que se termina y opera > sistema 10/10 que se abandona en el mes cuatro.
2. **Tiempo humano es el recurso más caro.** Cualquier proceso que exija >1h/día manual está mal diseñado.
3. **Una fuente de verdad por dominio.** No se duplica data sincronizada que eventualmente diverge.
4. **Observabilidad desde el día uno.** Un sistema sin métricas no se puede optimizar.
5. **Reversibilidad de decisiones.** Toda decisión arquitectónica debe poder cambiarse sin reescribir todo.
6. **Respeto al equipo humano.** La tecnología se refactoriza por dentro, el UX se mantiene.
7. **Honestidad técnica radical.** Dudas abiertas y riesgos se documentan; no se esconden.
8. **Cero servicios pagos nuevos sin aprobación explícita.** Prioridad: self-hosted > cross-VPS > SaaS free > SaaS pago.
9. **Antes de implementar, definir.** Cada construcción requiere dossier aprobado + dependencies resueltas + exit criteria.
10. **Responder a la profundidad pedida.** Conversación táctica → respuesta concisa. Conversación estratégica → respuesta comprehensiva con estructura.
11. **Deterministic backbone first — IA es capa aditiva, no foundational.** El sistema debe operar 100% sin agentes IA. Si todos los agentes se apagan, la operación sigue. La IA se agrega sobre infraestructura validada con datos de campañas reales, no sobre hipótesis. Antes de aprobar un agente IA, aplicar el filtro de 6 checks (memoria `project_agent_scope_audit_2026_05_03`). Articulado por Dario el 2026-05-03 tras audit honesto que reveló sobre-engineering del agent design original.

---

## 5. Stack tecnológico definitivo

### 5.1 Infraestructura

| Componente | Tecnología | Estado |
|---|---|---|
| Cloud provider | DigitalOcean (Frankfurt FRA1) | Activo |
| VPS 1 — WordPress público | DO Basic 1GB ($6/mes) | Activo |
| VPS 2 — Operaciones | DO Basic 4GB ($24/mes) | Activo |
| VPS 3 — ERP + cerebro | DO Basic 2GB/50GB ($12/mes) | ✅ Provisionado 2026-04-19, hardened |
| Red privada entre VPS | **DigitalOcean VPC** (gratis, <1ms) | **Fase 1** |
| DNS + SSL + WAF + proxy público | Cloudflare | Activo |
| Containerización | Docker + Docker Compose | Activo |
| CI/CD | GitHub Actions → SSH → `docker compose up` | **Fase 1** |
| DB migrations | Alembic | **Fase 1** |
| Staging environment | Mismo VPS 3, compose separado, `erp-staging.livskin.site` | **Fase 1** |

### 5.2 Aplicaciones operativas

| Componente | Versión | Rol | Ubicación |
|---|---|---|---|
| WordPress | 6.9.4 | Presencia web, SEO, landing pages | VPS 1 |
| PixelYourSite | 11.2.0.4 | Tracking client-side | VPS 1 (WP plugin) |
| SureForms | 2.7.0 | Formularios captura leads con webhook | VPS 1 (WP plugin) |
| Complianz GDPR | — | Cookie consent | VPS 1 (WP plugin) |
| UpdraftPlus | — | Backups WP | VPS 1 (WP plugin) |
| Vtiger CRM | 8.2.0 | Master del **lead digital** — marketing automation (NO master de cliente, ver ADR-0015) | VPS 2 container |
| n8n | 2.14.2 | Orquestador flujos | VPS 2 container |
| Metabase | latest | Dashboards BI | VPS 2 container |
| Langfuse | — | Observabilidad agentes IA | VPS 2 container (**Fase 3**) |
| **ERP Livskin (refactorizado)** | Flask + SQLAlchemy + Pydantic | Master de **cliente + transacciones** (ventas, pagos, gastos) — ver ADR-0015 | VPS 3 container (**Fase 2**) |
| Embeddings service | `multilingual-e5-small` (self-hosted) | Vectores para segundo cerebro | VPS 3 container (**Fase 1**) |

### 5.3 Bases de datos

| DB | Motor | Container / VPS | Rol | DBs internas |
|---|---|---|---|---|
| WP DB | MariaDB 10.6 | nativo / VPS 1 | Contenido WordPress | `livskin_wp` |
| Vtiger DB | MariaDB 10.6 | `vtiger-db` / VPS 2 (red aislada) | CRM state | `vtigercrm` |
| **Postgres Operations** | Postgres 16 | `postgres-analytics` / VPS 2 | Warehouse + Metabase | `analytics`, `metabase` |
| **Postgres Data** | Postgres 16 + pgvector | `postgres-data` / VPS 3 | ERP transaccional + segundo cerebro | `livskin_erp`, `livskin_brain` |

Ver Dossier #0002 para arquitectura completa de datos.

### 5.4 Inteligencia artificial

| Componente | Uso | Costo |
|---|---|---|
| Claude API (Opus/Sonnet/Haiku) | Cerebro de los 4 agentes | $50-120/mes |
| Claude Code (esta sesión) | Construcción del sistema | Claude Max ya pagado |
| Claude Design | Landing pages y banners (research preview) | Claude Max ya pagado |
| fal.ai Flux | Imágenes conceptuales artísticas | $20/mes |
| Canva API + Brand Kit | Producción visual con consistencia de marca | Canva Pro ya pagado |
| Embeddings | Self-hosted `multilingual-e5-small` | **$0** |

### 5.5 Tracking y marketing

| Componente | Uso |
|---|---|
| Meta Pixel | Tracking client-side visitantes WP |
| **Meta Conversion API** (server-side) | Atribución de conversiones a ads con fbclid — bypass ad-blockers |
| GA4 | Analytics client-side |
| **GA4 Measurement Protocol** (server-side) | Eventos server-side |
| Google Tag Manager | Contenedor universal de tags |
| Meta Marketing API | Gestión automatizada de campañas (Acquisition Engine) |
| Meta Ad Library API | Research de competencia (Content Agent) |
| WhatsApp Cloud API | Canal único de conversación — primero con **test number**, luego producción |

### 5.6 Colaboración y gestión

| Componente | Uso |
|---|---|
| GitHub | Source of truth código + infra + docs |
| Bitwarden (free) | Respaldo cifrado de `keys/.env.integrations` |
| Este folder (esta laptop) | Hub central de operaciones |

### 5.7 Lo que explícitamente NO usamos

Cada "no" está justificado. No re-abrir sin motivo fuerte.

| No usamos | Por qué |
|---|---|
| **Airtable** | Vtiger cumple; ya está instalado y pagado |
| **Zapier / Make** | n8n cumple, es self-hosted, gratis, más flexible |
| **HubSpot / Salesforce** | Vtiger es suficiente para la escala; costo 10-100× innecesario |
| **Descript** | FFmpeg + Whisper local cubren edición testimoniales |
| **LatePoint** | Reemplazado por flujo WhatsApp → Vtiger Calendar |
| **Backblaze B2 / Cloudflare R2 / AWS S3** | Backups cross-VPS + laptop pull cubren MVP (ver Principio 8) |
| **Tailscale** | DO VPC cumple mejor porque todos los VPS están en DO |
| **Pinterest / Bing / Reddit pixels** | PixelYourSite los soporta pero no aportan para clínica peruana |
| **Plugins prefabricados AI chatbot WP** | Construimos algo superior con Conversation Agent |
| **Agent SDK como framework principal** | n8n orquesta; Agent SDK solo si un agente requiere razonamiento multi-step complejo |

---

## 6. Arquitectura del sistema

### 6.1 Topología física

```
                                Internet
                                   │
                                   ▼
                ┌──────────────────────────────────────┐
                │     Cloudflare (DNS + SSL + WAF)      │
                │   livskin.site · flow · crm · dash · erp │
                └──┬─────────────────┬─────────────────┬─┘
                   │                 │                 │
                   ▼                 ▼                 ▼
          ┌────────────┐   ┌──────────────┐   ┌────────────┐
          │  VPS 1 WP  │   │  VPS 2 OPS   │   │VPS 3 DATA  │
          │            │   │              │   │            │
          │livskin.site│   │flow.livskin  │   │erp.livskin │
          │            │   │crm.livskin   │   │erp-staging │
          │            │   │dash.livskin  │   │            │
          └────────────┘   └──────────────┘   └────────────┘
                   │                 │                 │
                   └─────── DO VPC (privada, <1ms) ────┘
```

### 6.2 Docker networks (VPS 2)

| Network | Containers | Uso |
|---|---|---|
| `revops_net` | nginx, n8n, vtiger, postgres-analytics, metabase, **langfuse** (fase 3) | Comunicación entre servicios |
| `vtiger_internal` | vtiger, vtiger-db | Aislamiento estricto de la DB del CRM |

### 6.3 Docker networks (VPS 3)

| Network | Containers | Uso |
|---|---|---|
| `data_net` | nginx, erp-flask, postgres-data, embeddings-service | Comunicación interna |

### 6.4 Las 5 bases de datos y su rol (visión consolidada)

```
┌────────────────────────────────────────────────────────────────┐
│                       BASES OLTP (operativas)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  VPS 1                    VPS 2                    VPS 3       │
│  ┌──────────┐       ┌────────────┐         ┌──────────────┐   │
│  │livskin_wp│       │ vtigercrm  │         │ livskin_erp  │   │
│  │(MariaDB) │       │ (MariaDB)  │         │  (Postgres)  │   │
│  │          │       │            │         │              │   │
│  │contenido │       │state CRM   │         │ventas/pagos  │   │
│  │WordPress │       │clientes,   │         │gastos,       │   │
│  │          │       │leads,      │         │auth_users,   │   │
│  │          │       │oportunidad.│         │audit_log     │   │
│  └──────────┘       └────────────┘         └──────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                                │
                                │ ETL (n8n polling cada 5min)
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                       BASES OLAP (analíticas)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  VPS 2                                       VPS 3             │
│  ┌───────────────────────────┐      ┌──────────────────────┐  │
│  │     analytics             │      │   livskin_brain      │  │
│  │     (Postgres 16)         │      │ (Postgres 16 + pgvect│  │
│  │                           │      │                      │  │
│  │ leads, crm_stages         │      │ conversations        │  │
│  │ opportunities, events     │      │ creative_memory      │  │
│  │ ads_metrics, llm_costs    │      │ learnings            │  │
│  │ conversation_summary      │      │ clinic_knowledge     │  │
│  │                           │      │ project_knowledge    │  │
│  └───────────────────────────┘      └──────────────────────┘  │
│           │                                    │               │
│           └───────── Metabase ◄────────────────┘               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 6.5 Flujo end-to-end del lead

```
1. Paciente ve Meta Ad → click con fbclid
2. Aterriza en livskin.site/landing → PixelYourSite captura UTMs + fbclid
3. Complianz consent check
4. Paciente llena SureForms → webhook con payload + UTMs + fbclid + consent
5. n8n recibe:
    a) Crea Lead en Vtiger (identidad)
    b) Envía "Lead" event a Meta CAPI server-side (con fbclid)
    c) Envía "generate_lead" a GA4 Measurement Protocol
    d) INSERT en analytics.events
    e) Envía mensaje WhatsApp inicial vía Conversation Agent
6. Conversation Agent (en n8n):
    a) Consulta brain Layer 1 (catálogo clínico)
    b) Consulta brain Layer 4 (conversaciones similares pasadas)
    c) Genera respuesta con Claude API
    d) Envía mensaje por WhatsApp Cloud API (test number en fase 4)
    e) Guarda mensaje en livskin_brain.conversations con embedding
    f) Actualiza Vtiger con tag/nota
7. Paciente responde → ciclo 6 se repite hasta agendar cita
8. Cuando agenda:
    a) n8n crea Event en Vtiger Calendar
    b) Se sincroniza a calendario de la doctora (Google Calendar vía Vtiger)
9. Paciente atiende cita y compra:
    a) Recepción registra venta en ERP (VPS 3) → livskin_erp.ventas
    b) n8n detecta venta nueva (polling o trigger)
    c) Busca lead en Vtiger → obtiene fbclid/gclid originales
    d) Envía "Purchase" a Meta CAPI con fbclid → Meta atribuye al ad correcto
    e) Envía "purchase" a GA4
    f) INSERT en analytics.opportunities con revenue, fuente, campaña
10. Metabase muestra:
    - CAC por fuente
    - LTV por cohorte
    - Revenue por campaña
    - Top ads ganadores
```

Ver Dossier #0002 para diagramas detallados y reglas de sincronización.

---

## 7. Segundo cerebro — workstream estratégico

El segundo cerebro NO es una base de datos más. Es el **sistema de conocimiento acumulado** que diferencia a Livskin de cualquier clínica con sistema básico.

### 7.1 Las 6 capas

| # | Capa | Contenido | Tabla principal | Se puebla en |
|---|---|---|---|---|
| L1 | **Conocimiento clínico** | Catálogo 21 tratamientos + 12 productos, precios, contraindicaciones, brand voice, protocolos | `clinic_knowledge` | Fase 2 |
| L2 | **Conocimiento proyecto** | Todos los docs markdown del repo indexados semanalmente | `project_knowledge` | Fase 2 |
| L3 | **Data operativa (vistas)** | Vistas SQL sobre Vtiger + ERP + analytics | `v_lead_full_context`, etc. | Fase 2 |
| L4 | **Conversaciones** | Cada mensaje WhatsApp con embedding | `conversations` | Fase 4 |
| L5 | **Memoria creativa** | Cada brief + creativo + performance | `creative_memory` | Fase 5 |
| L6 | **Learnings** | Insights y hipótesis del Growth Agent | `learnings` | Fase 6 |

### 7.2 Tecnologías elegidas

| Componente | Elección | Razón |
|---|---|---|
| Vector store | **pgvector** en Postgres 16 | Extensión oficial, escala a 1M+ vectores, permite filtros SQL combinados |
| Modelo embeddings | **multilingual-e5-small** (self-hosted) | Gratis, español excelente, 384-dim, ~200 MB RAM |
| Embedding service | Container propio en VPS 3 | API HTTP interna `POST /embed` |
| Búsqueda | Cosine similarity + SQL filters | Combina semántica con filtros estructurados |
| Exposición externa | **MCP server** para Claude Code | Yo (Claude Code) consulto por lenguaje natural |

### 7.3 MCP server del cerebro

El MCP server es la **joya del workstream**. Expone el segundo cerebro a Claude Code como herramienta. Así puedo preguntar desde tu laptop:

- "¿Qué aprendimos de los creativos de Botox de marzo?"
- "¿Por qué decidimos last-touch attribution en vez de multi-touch?"
- "¿Qué conversaciones tuvieron patrón de objeción por precio?"

Yo busco semánticamente en el cerebro y te cito fuentes exactas.

**Ver Dossier #0001 para filosofía completa, schemas, y cronograma por capa.**

---

## 8. Seguridad — workstream estratégico

### 8.1 Las 10 dimensiones

| # | Dimensión | Cubre |
|---|---|---|
| S1 | Red externa | UFW, Cloudflare WAF, SSL público, anti-DDoS |
| S2 | Red interna | DO VPC entre VPS, Docker networks aisladas |
| S3 | Identidad y acceso | SSH key-only, root off, sudo NOPASSWD, 2FA en GitHub/DO/Cloudflare |
| S4 | Apps — autenticación | bcrypt, sesiones con expiración, CSRF tokens |
| S5 | Apps — inyección | Pydantic, SQLAlchemy parametrizado, auto-escape templates |
| S6 | Data en reposo | `.env` gitignored, backups cifrados, audit log inmutable, pgcrypto para PII |
| S7 | Data en tránsito | TLS 1.2+ en todo, Cloudflare Origin Cert, DO VPC privado |
| S8 | Secretos | `.env.integrations` + Bitwarden, rotación trimestral API keys |
| S9 | Observabilidad forense | Logs centralizados, Fail2Ban, Langfuse, audit log ERP, monthly audit |
| S10 | Compliance | Ley 29733 baseline, GDPR-like consent, retention policy |

### 8.2 Baseline obligatoria en los 3 VPS

- UFW activo con política restrictiva (solo 22, 80, 443)
- Fail2Ban con jail sshd (3 intentos, ban 2h)
- SSH: key-only, no password, no root login, puerto 22 (con Fail2Ban)
- `unattended-upgrades` activo
- `certbot` timer para renovación automática de SSL
- Backups de configuración esencial diarios (cuando entre Fase 2+)
- Audit automático mensual (comando único desde Claude Code)

### 8.3 Auditorías programadas

| Cadencia | Qué | Owner | Output |
|---|---|---|---|
| Semanal | Anomalías logs, costs tracking, failed logins | Automatizado | Alerta WhatsApp si algo |
| **Mensual** | **Audit completo infra + apps (Lynis, `docker ps`, certs, disk, logs)** | **Claude Code con 1 comando** | **`docs/audits/YYYY-MM-DD-monthly.md`** |
| Trimestral | Revisión política seguridad + rotación keys + OWASP ZAP scan | Tú + yo | `docs/audits/YYYY-QN-security.md` |
| Anual | Audit integral + pentest básico | Externo ideal, yo suficiente al inicio | `docs/audits/YYYY-annual.md` |

**Ver Dossier #0003 para runbooks, access control matrix, y cronograma por fase.**

---

## 9. Tracking y atribución

### 9.1 Arquitectura

Doble capa: **client-side** (navegador) + **server-side** (n8n). La server-side es crítica porque:
- Bypass ad-blockers (~30-40% de usuarios)
- iOS 14.5+ limita client-side cookies
- Meta CAPI requiere server-side para match quality alto

### 9.2 Pixels activos

| Pixel | Client-side | Server-side | Uso |
|---|---|---|---|
| Meta Pixel | ✅ via PixelYourSite | ✅ Meta CAPI desde n8n | Tracking visitantes + atribución conversiones |
| GA4 | ✅ via PixelYourSite | ✅ Measurement Protocol | Analytics + conversiones |
| GTM | ✅ container universal | — | Orquestación de otros tags |

### 9.3 UTMs y click IDs capturados

```
utm_source, utm_medium, utm_campaign, utm_content, utm_term
fbclid, gclid, ttclid
referer, landing_url
user_agent, ip (hashed)
session_id, timestamp
consent flag
```

### 9.4 Decisiones de atribución

- **MVP:** last-touch (simple, matches Meta default)
- **Fase 2:** multi-touch (linear o time-decay)
- **Persistencia UTMs:** localStorage al primer arribo; el form los lee desde ahí
- **Consent:** reject-or-accept para MVP (Complianz default); granular fase 2

---

## 10. Agentes IA

### 10.1 Los 4 agentes (MVP) + 5to (post-MVP, en evaluación)

**MVP (Fases 4-6)**:

| Agente | Propósito | Frecuencia | Intervención humana/semana |
|---|---|---|---|
| **Conversation** | Primera línea atención pacientes vía WhatsApp | Tiempo real 24/7 | ~30 min/día (escalaciones a doctora) |
| **Content** | Generar 12 briefs semanales para ads + testimoniales | Semanal (domingos) | 15 min domingo (aprobación) |
| **Acquisition** | Convertir briefs a ads Meta + optimización autónoma | Semanal (lunes) + diario (tracking) | 10 min lunes |
| **Growth** | Análisis continuo + reporte ejecutivo semanal | Diario (análisis) + semanal (reporte) | 1 hora lunes |

**Cierre de Fase 6 / extensión inmediata** (decisión Dario 2026-04-25):

| Agente | Propósito | Frecuencia | Intervención humana/semana |
|---|---|---|---|
| **Infra + Security** | Mantenimiento autónomo de servidores + monitoreo de seguridad; ejecuta acciones safe automáticamente, propone acciones riesgosas a Dario | Continuo (alertas) + scheduled (audits, backups, updates) | ~30 min/semana (autorizaciones de acciones risk) |

**Timing**: se construye en Fase 6 / extensión, **aprovechando que ya se setupean** Watchtower + UptimeRobot + n8n alertas + monthly audit + backups + runbooks (sensors/tools que el agente usa). Construir todo junto evita doble configuración.

Detalle del 5to agente y plan operativo: memoria `project_infra_security_agent`.

### 10.2 Orquestación híbrida

- **n8n** orquesta todos los flujos entrantes/salientes (webhooks, APIs, DB)
- **Claude API direct** (tool-calling) para agentes simples (Conversation inicial)
- **Agent SDK** reservado para agentes que requieran razonamiento multi-step dentro de una sola decisión (fase 2+)

### 10.3 Integración con segundo cerebro

Cada agente, antes de decidir, consulta las capas relevantes:

| Agente | Consulta capas |
|---|---|
| Conversation | L1 (clínica) + L3 (contexto paciente) + L4 (conversaciones previas) |
| Content | L2 (proyecto) + L5 (creativos previos) + L6 (learnings) |
| Acquisition | L5 (creativos + performance) + L6 (learnings) |
| Growth | L3 + L5 + L6 (todo el histórico analítico) |

### 10.4 Escalación doctora

- Conversation Agent escala a WhatsApp personal de la doctora cuando detecta:
  - Pregunta médica específica (contraindicaciones, medicación)
  - Solicitud de precio complejo / negociación
  - Intención clara de compra inmediata
  - Caso VIP / referido alto valor
- Mensaje incluye link al lead en Vtiger + resumen conversación
- La doctora responde directo al paciente
- Sistema detecta handoff y lo registra

---

## 11. Roadmap 10 semanas con 6 workstreams

### 11.1 Vista consolidada

```
Semana     0    1    2    3    4    5    6    7    8    9    10
          ─────────────────────────────────────────────────────────
Infra      ██   ██   ░░   ──   ──   ──   ░░   ──   ──   ──   ░░
Datos      ░░   ░░   ██   ██   ░░   ──   ──   ──   ──   ──   ──
Tracking   ──   ──   ──   ──   ██   ██   ──   ──   ──   ──   ──
Agentes    ░░   ──   ──   ──   ──   ░░   ██   ██   ██   ██   ░░
Cerebro    ░░   ██   ██   ██   ░░   ░░   ██   ██   ██   ██   ██
Seguridad  ██   ██   ██   ░░   ██   ░░   ░░   ░░   ░░   ░░   ██

██ = fase activa / poblándose
░░ = preparación / mantenimiento
── = no afecta este workstream en esta semana
```

**Interludio estratégico** (1-2 sesiones dedicadas, ~4-8h) entre Fase 3 y Fase 4 — ver § 11.5b. Produce arquetipos + segmentación + plan estratégico que alimentan Fases 4-5. No desplaza fechas si se hace con foco.

**Bridge Episode** (5-7 días, primera campaña paga FB Ads $100) — ver § 11.5c. Insertado el 2026-05-03 post-audit. Captura data real para informar Fase 4 con datos, no hipótesis. Doctrina rectora: principio operativo #11.

### 11.2 Fase 0 — Fundación (Semana 1)

**Objetivo:** hub central listo, cero pérdida al cambiar de máquina.

**Entregables:**
- Repo reorganizado (infra/, integrations/, agents/, analytics/, docs/ subcarpetas)
- `CLAUDE.md` maestro en la raíz
- Este documento (`master-plan-mvp-livskin.md`) publicado y aprobado
- **3 dossiers fundacionales aprobados:** 0001 (segundo cerebro), 0002 (arquitectura datos), 0003 (seguridad)
- Index de dossiers en `docs/decisiones/README.md` con 40+ entradas mapeadas
- Bitwarden instalado, `.env.integrations` creado y respaldado
- Snapshot manual de VPS 1 y VPS 2 en `backups/baseline-pre-fase0-2026-04-18/`
- Trámite WhatsApp Business API iniciado (tú)
- Meta App creada con test number (tú, 15 min)
- API keys Anthropic + fal.ai generadas y cargadas en `.env.integrations`
- Memoria Claude Code actualizada con estado final

**Exit criteria:**
- Puedes cerrar esta laptop, abrir otra, `git clone`, bajar `.env.integrations` desde Bitwarden, y retomar sin pérdida de contexto
- La próxima sesión arranca cargando CLAUDE.md + master plan + memoria, lee los 3 dossiers, y sabe en qué está

### 11.3 Fase 1 — VPS 3 + red privada + infra datos (Semana 2)

**Objetivo:** infraestructura de datos lista, CI/CD funcionando.

**Entregables:**
- VPS 3 provisionado ($12/mes, 2 GB / 50 GB, Frankfurt)
- Hardening base (UFW, Fail2Ban, SSH key, sudo NOPASSWD, unattended-upgrades)
- DO VPC activa entre los 3 VPS
- Docker + Docker Compose instalados
- Postgres 16 + pgvector extension
- DBs creadas: `livskin_erp`, `livskin_brain` (schemas base)
- Embeddings service containerizado (`multilingual-e5-small`)
- Nginx en VPS 3 + Cloudflare DNS `erp.livskin.site` y `erp-staging.livskin.site`
- GitHub Actions pipeline: push a main → SSH → git pull + docker compose up
- Alembic configurado en el repo (`analytics/migrations/` y `erp/migrations/`)
- Staging env separado (compose diferenciado)
- **Layer 1 y 2 del cerebro: infra lista pero vacía**

**Exit criteria:**
- `git push` en laptop → cambio aparece en VPS 3 automáticamente en <2min
- `curl erp-staging.livskin.site` devuelve 200 (aunque sea placeholder)
- Postgres responde desde los otros 2 VPS vía DO VPC (<1ms latencia)

### 11.4 Fase 2 — Gobierno datos + ERP refactor + segundo cerebro L1-L3 (Semanas 3-4)

**Estado al 2026-04-26: implementación ~95% completa.** ERP refactorizado deployed en VPS 3, funcional, con data real backfilleada (134 clientes + 88 ventas + 84 pagos del Excel productivo). Pendiente: auth+audit middleware, tests ≥75% coverage, decisión erp-staging. **Render sigue siendo producción real; cutover continúa diferido a Fase 6** (memoria `project_cutover_strategy`).

**Cambio operativo vs plan original (2026-04-26):** Dario aprobó saltar el plumbing sintético y backfillear directo data real. Razón: el script `scripts/backfill_excel.py` es idempotente, la migration 0001 puede recrear schema limpio si falla, y la data real (88 ventas) es chica + altamente representativa. Esto acelera la validación funcional sin riesgo de producción (Render sigue intacto).

**Objetivo original:** ERP refactorizado instalado en VPS 3 en **dormant standby** + segundo cerebro poblado con conocimiento base.

**Entregables:**
- **Dossiers aprobados:** 0011 (modelo Lead/Cliente/Venta), 0012 (stages Vtiger), 0013 (dedup), 0014 (naming), 0018 (schema cerebro), 0023 (refactor), 0024 (strangler → clone+standby), 0025 (backfill re-runable), 0026 (auth), 0027 (audit log) — ✅ todos completos al 2026-04-25
- ERP refactorizado (instalado en VPS 3, validación interna, sin tráfico real):
  - ✅ SQLAlchemy 2.0 + psycopg2 (reemplazo de gspread)
  - ✅ Pydantic v2 schemas para cada entidad (cliente, venta, pago, gasto, catálogo, client_lookup)
  - ✅ Service layer (VentaService, ClienteService, PagoService, GastoService, CatalogoService, DashboardService, LibroService, NormalizeService, CodgenService, ClientLookupService)
  - ✅ Type hints
  - ⏳ Pytest cobertura ≥75% (estructura existe, falta poblar)
  - ✅ Logs estructurados (structlog)
  - ✅ Dockerfile + docker-compose + gunicorn (production WSGI)
  - ⏳ **Auth bcrypt + 2 cuentas fijas (tú + doctora)** — definido (ADR-0026), implementación pendiente
  - ⏳ **Audit log tabla inmutable** — tabla `audit_log` ya existe en migration 0001, middleware pendiente (ADR-0027)
  - ⏳ CSRF tokens + rate limiting
  - ✅ **Las 6 fases de venta del Flask original preservadas exactas** en `venta_service.save_venta()`
  - ✅ Trigger PL/pgSQL `recompute_venta_debe()` recalcula `pagado` y `debe` atómicamente (migration 0002)
  - ✅ Capa de compat form-data → JSON (`routes/legacy_forms.py`) preserva HTML del Flask original
- ⏳ Vtiger configurado — bloqueado por trámite WhatsApp Business API (no afecta path crítico ERP)
- ⏳ Layer 1 del cerebro (catálogo) — pendiente
- ✅ **Layer 2 del cerebro** (Fase 1): indexación del repo con embeddings, query CLI
- ⏳ Layer 3 del cerebro: vistas SQL consolidadas — pendiente
- ⏳ MCP server proper — diferido a Fase 6
- ✅ **Backfill REAL ejecutado** (no sintético — Dario aprobó MVP-speed): 134 clientes + 88 ventas + 84 pagos del Excel productivo, vía `scripts/backfill_excel.py`
- ⏳ Sync inicial Vtiger ↔ ERP — bloqueado con Vtiger
- ⏳ Backups daily — pendiente (Fase 6 con resto de auto-mantenimiento)

**Exit criteria (revisados 2026-04-26):**
- ✅ ERP nuevo corre end-to-end en `erp.livskin.site` con data real (modo validación interna — nadie lo usa productivamente)
- ⏳ Revenue clasificable por fuente — pendiente tracking pixel + UTMs (Fase 3)
- ✅ Render sigue operando como producción real SIN cambios
- ✅ Backfill script ejecutado con éxito contra export real
- ⏳ MCP server query — diferido
- ⏳ Auth + audit middleware operativos — pendiente
- ⏳ Tests coverage ≥75% — pendiente

**CI/CD operativo (validado 2026-04-26):**
- Workflow `.github/workflows/deploy-vps3.yml` cubre: erp-flask con `--build`, alembic-erp + brain-tools `build only`, nginx `-s reload`, retry verify de URLs públicas (3 intentos × 5s sleep, sleep inicial 20s)

**Bugs corregidos durante implementación 2026-04-26:**
- Códigos secuenciales colisionaban en venta multi-item → fix `next_codigos_batch(count)`
- Pydantic aceptaba valores negativos en montos → fix `Field(ge=0)`
- Atomicidad rota: try/except dentro de `session_scope` cachaba excepciones → fix try/except FUERA del context manager en routes
- Abono fantasma con cod_item inexistente → fix excepción `AbonoCodItemInvalido`
- Doble counting de `credito_aplicado` en agregados de cliente → fix en `cliente_service.get_full_history()`
- Race condition CI/CD vs rebuild manual → workflow ahora maneja erp-flask + retry

**Auditoría profunda Flask original** (tras feedback de usuaria sobre lectura superficial):
- Documento `docs/erp-flask-original-deep-analysis.md` mapea 13 gaps entre original y refactor
- 11 cerrados sistemáticamente (bloques A-F de commits)
- 2 diferidos no críticos: métodos pago primera fila (cosmético), multi-currency por item

### 11.5 Fase 3 — Tracking + observabilidad (Semana 5) — REVISADA 2026-04-26

**Estado real al 2026-04-26 (post-audit):** el stack tracking en VPS 1 NO es greenfield — ya existe GTM `GTM-P55KXDL6` LIVE, GA4 `G-9CNPWS3NRX` capturando datos, Pixel `4410809639201712` configurado en PixelYourSite + GTM (doble disparo causa "Diagnóstico (1)" en Meta). Pixel viejo `670708374433840` a archivar. LatePoint a desactivar (servicios demo). Form Render no enlazado desde livskin.site. Vtiger 0 leads/contacts. n8n 0 workflows. Detalle: [docs/audits/estado-real-cross-vps-2026-04-26.md](../audits/estado-real-cross-vps-2026-04-26.md).

**Pre-requisito Fase 3:** sesión "Setup acceso programático + audit definitivo" (Google service account + Meta System User → audit cross-stack vía APIs en lugar de screenshots).

**Arquitectura tracking 2-capas (decisión 2026-04-26):**
- **Capa 1 client-side single source = GTM** (no plugin PixelYourSite — se desactiva).
- **Capa 2 server-side CAPI emitida desde ERP VPS 3** (no desde WordPress) — porque eventos reales del funnel (cita agendada, asistida, venta) viven en ERP.

**Objetivo:** cada visita y click trazable hasta el revenue; observabilidad lista para agentes; un solo client-side source + un solo server-side CAPI.

**Entregables (mini-bloques ejecutables):**

**Mini-bloque 3.1 — Limpieza VPS 1**
- Desactivar plugin PixelYourSite (redundante con GTM)
- Desactivar plugin LatePoint (no se usa)
- Archivar Pixel viejo `670708374433840` en Meta
- Resolver Diagnóstico (1) del Pixel `4410809639201712`
- Reparar link WhatsApp CTA del home (hoy `?phone=` vacío)

**Mini-bloque 3.2 — GTM event tagging + UTM persistence**
- Tag GTM: `form_submit` (SureForms 1569) → GA4 + Pixel
- Tag GTM: `whatsapp_click` → GA4 + Pixel
- Tag GTM: `scroll_75pct` + engagement events
- UTM persistence: cookie de primera visita + hidden fields auto-poblados en SureForms
- Click ID capture: `fbclid`, `gclid`, `ttclid` en hidden fields
- Publicar nueva versión del container GTM
- ADR-0021 (UTMs persistence) cerrado

**Mini-bloque 3.3 — Form → ERP webhook**
- Endpoint nuevo en ERP: `POST /api/leads/intake` (idempotente, valida + INSERT en `leads` table)
- Webhook desde SureForms 1569 → ERP intake
- Push secundario a Vtiger (marketing automation)
- Tests pytest (mantener coverage ≥80%)
- Audit log: nuevo evento `lead.created`

**Mini-bloque 3.4 — CAPI server-side desde ERP**
- Módulo `services/tracking_emitter.py` en ERP Flask
- Listener del audit_log: cuando se inserta evento canónico → POST a Meta CAPI + GA4 Measurement Protocol
- Eventos: `Lead` (lead created), `Schedule` (appointment created — Bloque puente), `Purchase` (venta closed)
- Mismo `event_id` y `external_id` cliente+server para deduplicación
- Test: enviar evento de prueba → verificar match quality "Good" en Events Manager
- ADR-0019 (tracking architecture) cerrado en versión full

**Mini-bloque 3.5 — Observabilidad**
- Langfuse desplegado en VPS 2 (container adicional)
- Dashboards Metabase: "Leads por fuente", "Conversión por etapa", "Cost LLM diario" (Bloque 0.10)
- Postgres-analytics ETL: poblar `events`, `leads`, `opportunities` desde ERP + Vtiger
- ADR-0017 (consent) cerrado

**Exit criteria:**
- Lleno formulario con link UTM en navegador privado → evento aparece en GA4 + Pixel con UTMs + match quality "Good"
- Mismo lead aparece en `leads` table del ERP con UTMs persistidos
- Meta Events Manager muestra eventos client + server con event_id coincidente (deduplicados)
- Diagnóstico Pixel = 0 issues
- Langfuse captura primer request de prueba (cuando arranque Fase 4)

### 11.5a Bloque puente — Módulo Agenda Mínima en ERP (entre Fase 3 y Fase 4)

**Objetivo:** llenar el agujero del funnel actual (lead → ??? → venta). Hoy no existe sistema que registre que una cita fue agendada, asistida o no-show. Sin esto, server-side CAPI no puede emitir `Schedule` ni `CompleteRegistration`, y métricas reales del funnel son imposibles.

**Decisión arquitectónica (2026-04-26):** ERP es SoT operativo único (Opción B). Vtiger queda para marketing automation, no como sistema de citas.

**Por qué aquí y no antes o después:**
- **No antes (en Fase 3):** Fase 3 es captura. Agenda es procesamiento post-captura.
- **No después (en Fase 4):** Fase 4 (Conversation Agent) necesita escribir en `appointments` automáticamente. Sin la tabla, el bot no tiene dónde agendar.
- **Aquí:** plumbing tracking listo + antes de que el bot necesite la tabla.

**Duración estimada:** 3-4 sesiones (~6-12h totales).

**Protocolo "precisión quirúrgica" (requisito explícito Dario 2026-04-26):**
1. ADR-00XX (módulo Agenda ERP) redactado, aprobado por Dario antes de cualquier código
2. Tests pytest primero — definen comportamiento esperado
3. Endpoints aislados — nuevo blueprint Flask `routes/agenda.py`, NO toca rutas existentes
4. Feature flag — UI detrás de `settings.agenda_enabled = True/False`
5. Migración Alembic 0005 100% reversible (`upgrade()` + `downgrade()` simétricos)
6. Validación con doctora — 5 citas de prueba antes de quitar feature flag
7. Documentación viva en `docs/runbooks/agenda-mantenimiento.md`
8. Audit log integration — cada cambio en `appointments` queda en audit_log

**Entregables:**
- **Schema** `appointments` (11 campos: lead_id, cliente_id, treatment, scheduled_for, duration_min, status, channel, notes, created_by, attended_at, timestamps). Status enum: `scheduled, confirmed, attended, no_show, cancelled, rescheduled`.
- **Endpoints REST**: GET/POST/PUT en `/api/appointments`, GET listas (hoy/semana), POST cambio status
- **3 vistas UI mínimas** en ERP:
  - "Agenda hoy" — lista de citas del día con botones [Confirmar] [Asistió] [No asistió] [Reagendar]
  - "Agenda semana" — calendario simple
  - "Cita detalle" — vista edit + link al lead origen + link al cliente si convirtió
- **Tracking integration**: emisión automática de eventos `Schedule` (al INSERT) + `CompleteRegistration` (al status='attended') vía `tracking_emitter` (Mini-bloque 3.4)
- **Tests pytest** ≥85% coverage del módulo nuevo
- **Runbook** `agenda-mantenimiento.md`

**Exit criteria:**
- Doctora marca asistencia de 5 citas reales sin reportar fricción
- Cada `appointments.create` emite evento `Schedule` a Meta + GA4 con match quality "Good"
- Cada `attended` emite `CompleteRegistration`
- 0 regresiones en endpoints ERP existentes (verificado por tests + manual)
- Feature flag puede revertirse sin pérdida de data



### 11.5b Interludio estratégico — Definición de estrategia, segmentos y plan de negocio (entre Fase 3 y Fase 4)

**Objetivo:** producir el input narrativo que los agentes de Fases 4-5 van a consumir como contexto de prompt.

**Por qué aquí y no antes o después:**
- **No antes:** violaría plumbing-first. Sin ERP + Vtiger + tracking operativos con data sintética, la discusión estratégica es abstracta y difícil de aterrizar.
- **No después:** Fase 4 (Conversation Agent) y Fase 5 (Content Agent) necesitan arquetipos como input literal a sus prompts. Sin esto, los agentes no pueden responder contextualmente ni generar creativos que resuenen.
- **Aquí es el único slot correcto:** plumbing validado con data sintética + antes de los agentes que consumen los outputs.

**Duración estimada:** 1-2 sesiones dedicadas (4-8h totales). No interrumpe fases — se hace **entre** Fase 3 y Fase 4, no dentro.

**Entregables:**
- **Posicionamiento de Livskin** — propuesta de valor diferenciada vs competencia local Cusco (clínicas, dermatólogos, estéticas independientes). 1 pager en `docs/estrategia/posicionamiento.md`.
- **Segmentación de clientes / arquetipos** — 3-5 perfiles tipo en `notes/compartido/arquetipos/*.md`:
  - Demografía + psicografía
  - Motivaciones, objeciones típicas, canales
  - Tono de comunicación, prueba social que funciona
  - Recorrido de compra esperado (touchpoints)
- **Plan estratégico 6-12-24 meses** en `docs/estrategia/plan-estrategico.md`:
  - Objetivos comerciales por horizonte
  - KPIs primarios
  - Roadmap de servicios/tratamientos a priorizar/desinvertir
- **Brand voice aprobada** (consolidación de ADR-0016 con input fresco)

**Exit criteria:**
- 3-5 archivos `arquetipos/<nombre>.md` listos para referenciar en prompts de Conversation + Content Agent
- Posicionamiento y plan estratégico commiteados
- Validación (idealmente) con la doctora sobre realismo de arquetipos vs clientes actuales

**Inputs para esta sesión:**
- Data real existente (74 ventas, 135 clientes del Excel) — sirve como evidencia empírica
- Métricas que Fase 3 empezó a capturar (aunque sintéticas, el modelo mental de tracking ya opera)
- Blueprint original (livskin_pensamientos...docx)

**Importante:** no es una fase numerada del roadmap (no añade semanas ni cambia exit criteria de Fases 1-6). Es un **interludio narrativo-estratégico** de 1-2 sesiones que encaja entre Fase 3 y Fase 4 sin desplazar fechas si se hace con foco.

### 11.5c Bridge Episode — Primera campaña paga FB Ads (insertado 2026-05-03 post-audit)

**⚠️ Insertado el 2026-05-03 entre Fase 3 (cerrada) y Fase 4 (reescrita).** Resultado del audit honesto del scope de agentes (`docs/audits/agent-scope-audit-2026-05-03.md`) + articulación del principio operativo #11 (`feedback_deterministic_backbone_first.md`).

**Objetivo:** validar el deterministic backbone construido con tráfico real ANTES de construir agentes IA. Captura data para informar Fase 4 con datos en mano, no hipótesis.

**No es fase numerada del roadmap** (similar al interludio § 11.5b) — es un **episodio puente operacional de 5-7 días** entre Fase 3 cerrada y Fase 4 reescrita.

**Setup:**
- Budget: $100 USD lifetime / 5 días
- Audiencia: F25-55, Cusco + Lima, intereses skincare/beauty/aesthetic
- 3 destinos: landing botox-mvp (existente) + landing prp-mvp (a crear) + WhatsApp directo doctora con shortcodes manuales
- Atribución del WA: shortcodes pre-poblados `[BTX-MAY-FB]`, `[PRP-MAY-FB]`, `[GEN-MAY-FB]` en mensajes que la doctora copia a tracking sheet manual

**Plan táctico completo:** `docs/campaigns/2026-05-first-campaign/plan.md`
**Cheat sheet doctora:** `docs/campaigns/2026-05-first-campaign/tracking-sheet-template.md`
**Memoria efímera:** `project_first_paid_campaign_2026_05_03.md` (archivar tras post-mortem)

**Exit criteria:**
- Campaña corrió 5 días + Ads Manager muestra impresiones + clicks reales
- Vtiger tiene leads con `utm_source=facebook` correctamente atribuidos
- Doctora llenó al menos 5 entradas tracking sheet manual
- **Post-mortem ejecutado con data real** — los aprendizajes informan decisión de próxima fase

**Aprendizajes esperados:**
- ¿Tracking end-to-end funciona con tráfico real?
- ¿Botox vs PRP convierte mejor?
- ¿WA directo, landing, o site convierte mejor?
- ¿ICP F25-55 funciona?
- ¿CAC sostenible para tratamientos $300-800?
- ¿Las creatividades hechas por Dario+Claude convierten? → informa urgencia construir Brand Orchestrator IA

### 11.6 Fase 4 (REVISADA POR AUDIT 2026-05-03)

**⚠️ La Fase 4 fue reescrita drásticamente.** La versión original ("Conversation Agent IA") fue **diferida** por audit. La versión revisada divide Fase 4 en dos sub-bloques con orden estricto:

**Sub-bloque 4A — Cerrar el deterministic backbone restante** (post-Bridge Episode):
- Chatbot WhatsApp **rule-based** (state machine Python en ERP, NO IA)
- Módulo Agenda mínimo en ERP (tabla `appointments` + UI tab + audit log)
- Notificaciones a doctora (n8n workflow chico, sin IA)
- Re-engagement queue determinística (cron SQL → cola para doctora)
- Cualquier hallazgo del Bridge Episode que sea bloqueante

**Sub-bloque 4B — Primer agente IA real: Brand Orchestrator** (solo cuando 4A está validado):
- Caso canónico subagent pattern (5 subagentes: research/concept/copy/visual/implementation)
- Brand voice consolidado como input (debe estar listo del trabajo paralelo del Bridge Episode)
- Eval suite previa con 30+ ejemplos
- Budget hard-cap (~$70/mes per audit)
- VPS dedicado de agentes (`agents.livskin.site`) — decisión arquitectónica formal con ADR-0035 cuando arranque construcción

**Conversation Agent IA — diferido**: V1 es chatbot rule-based de 4A. Reabrir cuando volumen WA >100 conv/día sostenido (memoria `project_agent_scope_audit_2026_05_03`).

**ADR-0034 v1.0** (Conversation Agent IA Foundation, escrita 2026-05-02) → marcada 💤 Diferida; será supersedida por ADR Conversation Agent v0 rule-based cuando se construya en Fase 4A.

---

### 11.6 (versión histórica, diferida) — Fase 4 — Conversation Agent IA (Semana 6)

> **⚠️ DIFERIDA por audit 2026-05-03**. Conservado como referencia histórica del scope original. Ver § 11.6 reescrita arriba.

**Objetivo:** primer agente productivo respondiendo leads reales en <60s.

**Entregables:**
- **Dossier aprobado:** 0029 (Conversation Agent completo)
- Prompt v1.0 Conversation Agent (español, brand voice, escalación)
- Tools implementadas:
  - `vtiger_get_lead`, `vtiger_update_lead`
  - `whatsapp_send` (vía test number Meta)
  - `calendar_check_availability`
  - `brain_search_similar`, `brain_get_patient_history`, `brain_get_clinic_knowledge`
- n8n workflow: webhook WhatsApp → orquestación → Claude API → respuesta
- Escalación a doctora (N23 rules) implementada
- **Layer 4 del cerebro activo:** cada mensaje entrante/saliente se guarda con embedding
- Lead scoring v1 funcionando (reglas simples 0-100)
- Dashboard Metabase "Conversation Agent — primeras conversaciones"
- Golden set inicial de **10 conversaciones etiquetadas** (para evals futuros)

**Exit criteria:**
- Tú envías WhatsApp desde tu teléfono al test number → agente responde en <60s con mensaje contextual correcto
- Si preguntas algo médico → escala a la doctora con link a Vtiger
- Cada mensaje queda en `livskin_brain.conversations` con embedding
- Langfuse muestra la ejecución completa con costo estimado

### 11.7 Fase 5 — Content Agent + Acquisition Engine (Semanas 7-8)

**Objetivo:** creativos generados automáticamente + campañas auto-optimizándose.

**Entregables Semana 7 (Content Agent):**
- **Dossiers aprobados:** 0030 (Content Agent con Claude Design), 0045 (pipeline creativo), 0046 (landing pages)
- Research Meta Ad Library automatizado (domingos)
- Análisis performance semana anterior (pull de Meta Ads API)
- Generación de 12 briefs (copy + hook + CTA + descripción visual)
- Pipeline producción:
  - **Claude Design** genera concepto → export Canva → Brand Kit
  - fal.ai Flux para visuales artísticos conceptuales
  - Canva API para variantes de formato (feed, story, reel, banner)
- **Layer 5 del cerebro activo:** cada brief + creativo se guarda con text + visual embeddings
- Mini-dashboard de aprobación dominical (tú apruebas 12 en 15 min)

**Entregables Semana 8 (Acquisition Engine):**
- **Dossier aprobado:** 0031 (Acquisition Engine)
- Conversión briefs aprobados → ads Meta (lunes)
- Testing matrix: S/.15-20/día × 3 días por creativo
- Escalado automático ganadores (CPL bajo)
- Pausa automática perdedores (CPL > umbral)
- Retargeting sobre visitantes WP no convertidos
- Dashboard Metabase "Acquisition — decisiones automáticas"

**Exit criteria:**
- Domingo 22:00 recibes 12 briefs listos para aprobar en WhatsApp
- Lunes el Acquisition Engine ha creado los ads aprobados en Meta
- Dashboards muestran performance y decisiones automáticas

### 11.8 Fase 6 — Growth Agent + evals + estabilización (Semanas 9-10)

**Objetivo:** sistema completo observado, evaluado, documentado.

**Entregables Semana 9 (Growth Agent):**
- **Dossier aprobado:** 0032 (Growth Agent)
- Pulls diarios: Meta Ads + Vtiger + WordPress analytics + livskin_erp + livskin_brain
- Cálculo automático: CAC, LTV emergente, conversión por etapa, ROI por creativo
- Detección de anomalías (alertas)
- Ejecución automática de decisiones low-risk (ajustar budgets menores)
- **Layer 6 del cerebro activo:** learnings semanales escritos por Growth Agent
- Reporte semanal ejecutivo por WhatsApp los lunes
- Reactivación 45 días v1 funcionando

**Entregables Semana 10 (estabilización + cutover ERP):**
- **Dossiers aprobados:** 0039 (evals LLM-as-judge)
- Evals LLM-as-judge (Haiku) cada 100 conversaciones
- Golden set expandido a 50 conversaciones etiquetadas
- Runbooks: disaster recovery, key rotation, eliminación paciente (Ley 29733 baseline), incident response
- Lynis audit + OWASP ZAP scan inicial → report committed
- Documentación final arquitectura (diagrama canónico)
- Retrospectiva del primer mes en producción
- **Migración a WhatsApp número producción** (si Meta aprobó)
- **CUTOVER ERP — Render → VPS 3 (hito explícito)**:
  - Trigger: Dario confirma que el sistema completo end-to-end funciona a su satisfacción
  - Pasos operativos:
    1. Aviso a comerciales (doctora + Dario) 48h antes con ventana de corte
    2. Ejecutar backfill script (ADR-0025) en modo **real**: pull live de Google Sheets → poblar `livskin_erp` en VPS 3
    3. Validación manual de totales (revenue agregado, nº clientes, nº ventas) entre ambos sistemas
    4. DNS switch: `erp.livskin.site` apunta a VPS 3 (ya está así, pero confirmar)
    5. Comunicar a comerciales que pueden usar nuevo sistema
    6. Render queda en cold standby por **60 días** (ADR-0024) — NO se apaga inmediatamente
    7. Post-cutover: monitoreo intensivo primeras 72h
  - Exit del cutover: 1 semana de operación sobre VPS 3 sin regresiones funcionales reportadas
  - Detalle completo del procedimiento + plan de rollback: ver ADR-0024

**Exit criteria Fase 6:**
- Recibes lunes 09:00 reporte ejecutivo de la semana por WhatsApp
- Lynis score > 70 en los 3 VPS
- OWASP ZAP sin vulnerabilidades críticas/altas
- Todos los runbooks ejercitados al menos 1 vez (aunque sea en staging)
- Dashboard "Sistema completo" muestra salud end-to-end
- **Cutover ERP ejecutado** — comerciales trabajan sobre `erp.livskin.site` (VPS 3), Render en cold standby

---

## 12. Convenciones y estándares

### 12.1 Idioma

| Contexto | Idioma | Ejemplo |
|---|---|---|
| UI usuarios finales (WP, ERP, dashboards) | Español | "Registrar venta" |
| Columnas DB | Español | `ventas.monto_total` |
| Código (variables, funciones, clases) | Inglés | `def create_sale(client_id): ...` |
| Comentarios en código | Inglés | `# Deduplicate by phone first` |
| Docs operativos (README, dossiers, runbooks) | Español | este documento |
| CLAUDE.md | Español | para contexto natural |
| Commits git | Español (o inglés, el que salga natural) | pero consistente dentro de cada commit |

### 12.2 Time zones

- **DB:** siempre UTC (`TIMESTAMPTZ` en Postgres)
- **ERP UI:** hora de Lima (UTC-5)
- **Metabase dashboards:** hora de Lima
- **Reports a usuaria (Milán):** hora de Milán (CEST UTC+2) con nota "datos agregados en hora Lima"
- **Logs:** UTC con indicador `Z`

### 12.3 Naming conventions

**Campañas Meta:**
```
{fuente}_{producto}_{mes}_{zona}_{segmento}
Ejemplo: FB_Botox_Dic26_Wanchaq_35-45F
```

**Fuentes del lead (taxonomía cerrada):**
```
fb_ad · ig_ad · google_ad · tiktok_ad
organic_seo · organic_social · referral
walk_in · wa_direct · otro
```

**Commits git:**
```
<tipo>: <descripción corta>

<cuerpo opcional>

Refs: ADR-0001, #issue_si_aplica
```

Tipos: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `security`, `perf`.

**Branches git:**
```
main                    # producción
staging                 # pre-producción
feature/<desc>          # nueva funcionalidad
fix/<desc>              # bug fix
docs/<desc>             # solo docs
```

**Archivos ADR:**
```
NNNN-titulo-kebab-case.md
Ejemplo: 0001-segundo-cerebro-filosofia-y-alcance.md
```

### 12.4 Git workflow

- `main` siempre deployable
- Cambios llegan por PR desde `feature/*`
- PR auto-merge si CI pasa + self-approved (single-user)
- Deploy automático a VPS tras merge a `main` (Fase 1+)

### 12.5 Versionado semántico (futuro)

Para el ERP cuando esté estable:
```
v<major>.<minor>.<patch>
v1.0.0 = primer cutover
v1.0.1 = fix
v1.1.0 = feature
v2.0.0 = breaking change (raro)
```

---

## 13. Diferimentos explícitos

**Estos temas NO entran en el MVP.** Están documentados para evitar re-apertura.

| # | Tema | Razón | Trigger para reabrir |
|---|---|---|---|
| 0099 | SUNAT / comprobantes electrónicos | Decisión de negocio pendiente, no técnica | Cuando Livskin decida formalizar facturación electrónica |
| 0100 | IGV inclusive/exclusive | Depende del trigger anterior | Junto con SUNAT |
| 0101 | Inventario productos | No crítico para revenue; máx. registro de compras en `gastos` | Si el negocio crece a retail significativo |
| 0102 | Historial clínico paciente | Requiere diseño específico con la doctora | Post-MVP, dossier propio |
| 0103 | PDFs / impresión | Sin evidencia que hoy impriman | Si el equipo lo pide |
| 0104 | Offline mode ERP | Edge case, depende de frecuencia cortes internet | Si se reportan cortes frecuentes en Cusco |
| 0105 | Computer vision clínica (fotos antes/después) | Blueprint lo menciona pero agrega complejidad | Mes 4-6 cuando haya volumen de fotos |
| — | Multi-touch attribution | Complejo sin agregar value MVP | Cuando volumen justifique |
| — | Memoria vectorial multi-idioma | Ya usamos multilingual model | Si expansión a clínicas no hispanas |
| — | Fine-tuning propio de modelos | Requiere dataset grande | Cuando 10k+ conversaciones históricas |

---

## 14. Riesgos y mitigaciones

### 14.1 Riesgos del proyecto (no técnicos)

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| "Es muy grande para mí sola" (burnout) | Media | Alto | 4 agentes (no 7), 10 semanas (no 4), exits criteria claros, podemos pausar |
| Tensión clínica vs construcción | Media | Medio | 12-15 h/semana declaradas + sistema diseñado para liberar tiempo |
| Volumen real Wanchaq distinto | Alta | Medio | Sistema se mide desde día 1, recalibramos |
| WhatsApp API rechazo Meta | Baja | Medio | Test number destraba desarrollo, producción solo para lanzamiento |
| Costos Claude API exceden | Baja | Bajo | Budget alerts + caching + Haiku para tareas simples |

### 14.2 Riesgos técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Migración ERP rompe producción | Baja | Alto | Strangler fig + parallel run + Render standby 1 mes |
| Datos históricos corruptos en backfill | Media | Medio | Script de validación + comparación con Excel original |
| Prompt injection a Conversation Agent | Media | Medio | Separación strict sistema/usuario + sanitización entrada |
| Fuga credenciales | Baja | Alto | `.gitignore` + Bitwarden + rotación trimestral + audit log |
| RAM VPS 2 se satura en Fase 3-4 | Media | Medio | Umbrales pre-definidos, upgrade a 8 GB listo |
| RAM VPS 3 insuficiente con embeddings | Baja | Medio | Monitorear pgvector index build; upgrade a 4 GB si pasa |
| DO zona Frankfurt tiene incidente | Muy baja | Alto | Backups baseline + procedimiento de restore documentado |

### 14.3 Riesgos de compliance (diferidos pero identificados)

| Riesgo | Mitigación planificada |
|---|---|
| Ley 29733 Perú — derecho supresión | Runbook en Fase 6 |
| GDPR en visitantes UE | Cookie consent Complianz ya activo |
| SUNAT auditoría sin comprobantes | Diferido — decisión negocio |

---

## 15. Observabilidad y auditoría continua

### 15.1 Métricas monitoreadas desde día 1

| Nivel | Métricas | Dónde se ven | Cadencia |
|---|---|---|---|
| **Infra** | CPU, RAM, disco por VPS | Metabase "Infra Health" | Cada 5 min (n8n pull) |
| **Uptime** | 5 subdominios livskin.site | UptimeRobot free tier | Cada 5 min |
| **Apps** | Response time, 5xx errors | Nginx logs + n8n alerts | Continuo |
| **DB** | Slow queries, connection count | pg_stat_statements → Metabase | Cada hora |
| **Agentes IA** | Latencia, errores, cost per call | Langfuse | Continuo (Fase 3+) |
| **Business** | Leads/día, conversión, CAC, revenue | Metabase dashboards | Tiempo real |

### 15.2 Umbrales pre-definidos de escalamiento

No esperar a pánico. Cada umbral tiene acción definida.

| Trigger | Recurso | Acción |
|---|---|---|
| RAM VPS 2 > 85% sostenido 7d | Ops | Upgrade 4→8 GB ($24→$48) |
| RAM VPS 3 > 85% sostenido 7d | Data | Upgrade 2→4 GB ($12→$24) |
| Disco cualquier VPS < 20% libre | Cualquiera | Limpieza → upgrade si sigue |
| Claude API cost > $150/mes | — | Review prompts, caching, Haiku |
| Ventas/mes > 5,000 | Data | Evaluar DO Managed Postgres |
| Conversaciones WA/día > 1,000 | Ops | Agregar Redis queue n8n |
| Downtime > 1h en un mes | Cualquier VPS | Post-mortem obligatorio |

### 15.3 Documentación continua

- **Cada sesión estratégica** (como esta) → `docs/sesiones/YYYY-MM-DD-titulo.md`
- **Cada decisión importante** → nuevo ADR en `docs/decisiones/`
- **Cada audit mensual** → `docs/audits/YYYY-MM-DD-monthly.md`
- **Cada runbook** → `docs/runbooks/<tema>.md` (disaster-recovery, key-rotation, paciente-supresion, etc.)
- **Este master plan** actualizado con changelog al final

---

## 16. Integración Claude Design

### 16.1 Qué es

Herramienta de Anthropic lanzada 2026-04-17 (hace 2 días). Research preview para Claude Max (ya pagado). Powered by Claude Opus 4.7.

### 16.2 Capacidades

- Generar diseños: mockups, prototipos, slides, one-pagers, banners
- Edición por prompt + sliders para elementos específicos
- Design system aprendido desde codebase o archivos de diseño
- Export: PDF, URL (página web), PPTX, **directo a Canva editable**, **directo a Claude Code**

### 16.3 Dónde encaja en Livskin

**Landing pages para livskin.site:**
```
Tú describes "landing Botox Wanchaq" a Claude Design
    ↓
Claude Design genera mockup visual
    ↓ (iteras con sliders y prompts)
Export a Claude Code
    ↓ (yo convierto a WP template o HTML Tailwind)
Deploy a livskin.site/landing/botox-wanchaq
    ↓
Tracking PixelYourSite + GTM automático
```

**Banners para Meta Ads:**
```
Content Agent genera brief (copy + concepto)
    ↓
Claude Design genera concepto visual on-brand
    ↓
Export a Canva (editable)
    ↓
Canva aplica Brand Kit y genera variantes (feed, story, reel, banner)
    ↓
Acquisition Engine publica en Meta Ads
```

**Pitch decks y one-pagers:**
```
One-pager para pacientes VIP presentando paquete facial completo
Pitch deck interno para revisiones trimestrales
Export PDF directo
```

### 16.4 Limitaciones conocidas

- Research preview → puede cambiar
- No API aún (uso humano vía claude.ai/design)
- Integración WordPress no directa (pasar por Claude Code)

### 16.5 Decisión

**Integrar desde Fase 5** dentro del Content Agent workstream. Reemplaza parcialmente a fal.ai para banners con branding. fal.ai queda para visuales artísticos conceptuales. **Cero costo adicional.**

---

## 17. Glosario

| Término | Definición |
|---|---|
| **ADR** | Architecture Decision Record. Documento corto que registra una decisión arquitectónica con contexto, opciones, tradeoffs y resolución. Vive en `docs/decisiones/`. |
| **Agent SDK** | Framework oficial de Anthropic para construir agentes IA complejos con orquestación multi-step. No es nuestro default (usamos n8n). |
| **Alembic** | Herramienta Python para versionar cambios de schema de DB. Cada cambio es una migration numerada con upgrade/downgrade. |
| **Backfill** | Proceso de cargar data histórica en un sistema nuevo. Aquí: migrar las 74 ventas y 135 clientes del Excel a Postgres. |
| **CAPI** | Conversion API de Meta. Server-side alternativa al pixel client-side, bypassa ad-blockers. |
| **CLAUDE.md** | Archivo en raíz del repo que Claude Code lee automáticamente al iniciar sesión. Contiene contexto operativo del proyecto. |
| **Cutover** | Momento del corte definitivo de sistema viejo a sistema nuevo en una migración. |
| **DO VPC** | DigitalOcean Virtual Private Cloud. Red privada gratis entre droplets del mismo data center. Reemplaza a Tailscale en nuestro diseño. |
| **ETL** | Extract, Transform, Load. Proceso de mover data entre sistemas (aquí: de Vtiger/ERP a analytics). |
| **Embedding** | Representación vectorial de un texto. Permite búsqueda semántica (significado) en vez de léxica (palabras exactas). |
| **Golden set** | Conjunto de ejemplos etiquetados manualmente que sirve como "verdad" para evaluar cambios en prompts. |
| **LLM-as-judge** | Usar un modelo LLM para evaluar la calidad de respuestas de otro modelo. Escalable, imperfecto pero útil. |
| **MCP server** | Model Context Protocol server. Estándar de Anthropic para exponer herramientas/datos a Claude. Aquí expondremos el segundo cerebro. |
| **OLTP / OLAP** | Online Transaction Processing (DBs operativas, escrituras frecuentes) vs Online Analytical Processing (DBs analíticas, queries complejas). No se mezclan. |
| **Parallel run** | Correr sistema viejo y nuevo simultáneamente durante una migración para comparar consistencia antes del cutover. |
| **pgvector** | Extensión de Postgres que añade tipo `vector` e índices para búsqueda por similitud coseno/euclidiana. |
| **Prompt injection** | Ataque donde el usuario intenta cambiar las instrucciones del sistema del agente vía el mensaje de entrada. |
| **RAG** | Retrieval-Augmented Generation. Antes de que el LLM genere, buscamos en una base de conocimiento y le inyectamos contexto relevante. |
| **Rollback** | Revertir a estado anterior tras una migration fallida. |
| **Segundo cerebro** | Nuestro nombre para el sistema de conocimiento acumulado (6 capas, pgvector-based). |
| **Source of truth (SoT)** | La DB o sistema que tiene la versión autoritativa de un dato. Otros sistemas son copias derivadas. |
| **Strangler fig** | Patrón de migración donde el sistema nuevo va "estrangulando" al viejo paulatinamente. Zero-downtime. |
| **UTM** | Parámetros de URL que identifican fuente/campaña (utm_source, utm_medium, utm_campaign). |
| **Vibe coding** | Estilo de trabajo donde el humano describe intención y el AI implementa. El humano no escribe código. |

---

## 18. Operación post-MVP y mantenimiento

Filosofía: **el sistema se construye para que Dario NO sea programadora a tiempo completo.** Al cerrar Fase 6, el mantenimiento rutinario debe ser <5 h/mes.

### 18.1 Cuatro tipos de mantenimiento (y quién los hace)

| Tipo | Qué es | Frecuencia | Quién |
|---|---|---|---|
| **Operación diaria** | Agentes respondiendo leads, generando creativos, optimizando ads | Continua 24/7 | Automático (los 4 agentes) |
| **Rutinario** | Backups, security updates, SSL, audits | Semanal/mensual | Automatizado (cron + alertas) |
| **Evolución** | Nuevas features, campos, integraciones | 1-3 meses | Dario + Claude Code o fractional DevOps |
| **Incidentes** | Algo se rompió | Esporádico | Dario (alertada por WhatsApp) + Claude Code |

### 18.2 Tiempo esperado de Dario post-Fase 6

| Actividad | Tiempo/mes |
|---|---|
| Escalaciones del Conversation Agent (trabajo real del negocio) | 5-10 h |
| Aprobar creativos semanales (Content Agent) | 1 h |
| Revisar reporte semanal (Growth Agent) | 1 h |
| Revisar audit mensual del sistema | 0.5 h |
| Responder a alertas del sistema (cuando aparecen) | 1-2 h |
| **Total mantenimiento operacional** | **~3-5 h/mes** |

Esto vs alternativa sin sistema: 20-30 h/semana respondiendo leads + diseñando creativos + pausando ads manualmente. **El sistema libera ~15-25 h/semana.**

### 18.3 Decisiones de diseño que reducen mantenimiento

- `restart: unless-stopped` en todos los containers → auto-recovery
- `unattended-upgrades` en los 3 VPS → security patches auto
- Cloudflare Origin Cert válido hasta 2041 → no renovar SSL
- Docker volumes con data persistida → survive container updates
- CI/CD GitHub Actions → nunca tocar VPS manualmente para deploy
- Alembic migrations versionadas → schema changes reproducibles
- Langfuse + Metabase + logs estructurados → observabilidad auto

### 18.4 Capa de auto-mantenimiento (pendiente implementar — Fase 6)

Al cierre de Fase 6 se agrega (ver backlog):
- Watchtower para updates de imágenes Docker
- UptimeRobot para uptime monitoring externo
- Alertas a WhatsApp vía n8n por anomalías
- Monthly audit auto-ejecutado
- Runbooks completos en `docs/runbooks/`

### 18.5 Tres rutas de mantenimiento post-MVP

**Ruta A — Dario + Claude Code:** 1-2 intervenciones/mes · $100/mo (Claude Max ya pagado) · máxima flexibilidad, cero costo extra.

**Ruta B — Fractional DevOps contratado:** $300-800/mo · cero tiempo de Dario en incidentes · depende del contratado.

**Ruta C — Migración a managed services** (DO Managed Postgres, etc.): +$30-100/mo · reduce superficie self-hosted · vendor lock-in parcial.

**Recomendación:** Ruta A meses 0-6 post-lanzamiento → evaluar según data real → decidir B o C según patrones de incidentes.

### 18.6 Principio rector

Principio 6 del proyecto: "respeto al equipo humano — la tecnología está al servicio de las personas, no al revés". Si al final de Fase 6 Dario se siente **atada** al sistema en vez de **liberada**, algo se hizo mal y se rediseña.

---

## 19. Changelog

### v1.0 — 2026-04-18
- **Creación del plan maestro consolidado.**
- Integra: blueprint original (docx), system-audit 2026-04-16, datos reales del Excel, 39 decisiones tomadas en sesión de definición.
- Estructura de 6 workstreams paralelos a 10 semanas.
- Decisiones clave cerradas: 3er VPS a $12/mo, DO VPC (no Tailscale), refactor ERP (no rewrite), flujo citas WhatsApp (no LatePoint), 2 cuentas fijas ERP, embeddings self-hosted, Claude Design integrada al workstream creativo.
- 3 dossiers fundacionales aprobados: 0001 segundo cerebro, 0002 arquitectura datos, 0003 seguridad.
- Diferimentos explícitos: SUNAT, IGV, inventario, historial clínico, PDFs, offline mode, computer vision.

### v1.1 — 2026-04-20
- **Fase 1 completada al 100%** — plumbing máquina (VPS 3, Postgres+pgvector, embeddings, CI/CD, Alembic, brain-tools) + capa humana (Obsidian).
- **§ 18 agregado** — Operación post-MVP y mantenimiento. Target <5h/mes post-cutover. 3 rutas evaluadas (A: Dario+Claude Code, B: fractional DevOps, C: managed services).
- **§ 11.5b agregado** — Interludio estratégico entre Fase 3 y Fase 4. Define el slot correcto para la sesión estratégica (segmentación + arquetipos + plan de negocio) sin violar plumbing-first ni desplazar fases. Respuesta a observación de Dario de que sesiones estratégicas son slots programados, no alternativas ad-hoc al trabajo táctico.

### v1.2 — 2026-04-21
- **ADRs 0011-0014 aprobados** (MVP): modelo de datos, stages Vtiger, dedup, naming. Basados en análisis del Flask real en Render + Excel.
- **§ 11.4 Fase 2 re-encuadrada**: el cutover ERP **NO ocurre** al final de Fase 2. VPS 3 queda en dormant standby durante Fases 2-5 con data sintética; Render sigue siendo producción sin cambios.
- **§ 11.8 Fase 6 actualizada**: el cutover ERP (Render → VPS 3) se incorpora como hito explícito con plan operativo. Trigger: Dario confirma que el sistema completo end-to-end funciona.
- **Razón del cambio**: preserva producción real durante todo el MVP, minimiza riesgo a comerciales, permite iterar schema sin afectar operaciones. Decisión de Dario 2026-04-21, memoria `project_cutover_strategy`.

### v1.3 — 2026-04-21
- **ADR-0013 v2 (reescrita)**: dedup con phone como anchor universal, 2 canales (form + WA), tabla `lead_touchpoints` para multi-touch tracking, cross-system dedup Vtiger↔ERP explícito. Elimina modelo polimórfico over-engineered.
- **ADR-0011 v1.1**: corrige SoT (Cliente=ERP no Vtiger), agrega `lead_touchpoints` + `form_submissions`, columnas de scoring/intent/handoff/nurture en `leads`, campos renombrados a convención ADR-0013 v2.
- **ADR-0015 escrita** (era orphan): SoT por dominio oficializado. Tabla canónica de 13 dominios con sistema autoritativo + reglas de sync.
- **§ 5.2 corregido**: Vtiger ya no es "CRM maestro identidad cliente" → ahora "master del lead digital solamente". ERP es master de cliente + transacciones.
- **Razón del cambio**: clarificación de Dario sobre scope narrow de Vtiger (marketing automation para adquisición digital). Los 135 clientes históricos word-of-mouth nunca entran a Vtiger. Memorias `project_vtiger_erp_sot`, `project_acquisition_flow`, `project_whatsapp_architecture`.

### v1.4 — 2026-05-03 — PIVOT ESTRATÉGICO

- **Principio operativo #11 nuevo**: *"Deterministic backbone first — IA es capa aditiva, no foundational."* — articulado por Dario tras audit honesto. Memoria 🔥 CRÍTICA `feedback_deterministic_backbone_first.md`.
- **Audit del scope de agentes ejecutado** (`docs/audits/agent-scope-audit-2026-05-03.md`):
  - 5 agentes originales → **1 agente real (Brand Orchestrator) + 2 scripts con LLM ocasional**
  - Conversation Agent IA → ⏸️ **diferido**, V1 será chatbot rule-based + handoff humano + templates Meta-approved
  - Growth Analyzer + Infra-Security → ❌ **NO V1** (scripts/skills cubren)
  - **Framework de 6 checks** definido como gate obligatorio para aprobar agente futuro
  - Memoria 🔥 CRÍTICA `project_agent_scope_audit_2026_05_03.md`
- **Bridge Episode insertado en roadmap** (§ 11.5c): primera campaña paga FB Ads $100/5 días entre Fase 3 (cerrada) y Fase 4 (reescrita). Captura data real → informa Fase 4 con datos, no hipótesis.
- **§ 11.6 Fase 4 reescrita**:
  - Versión original (Conversation Agent IA) movida a sección histórica diferida
  - Versión revisada divide Fase 4 en 4A (backbone determinístico restante: chatbot rule-based + agenda + notifs + re-engagement) y 4B (primer agente IA real = Brand Orchestrator)
- **§ 11.7 Fase 5 reescrita**: Acquisition + Growth → scripts con LLM ocasional, NO agentes
- **ADR-0034 v1.0** (Conversation Agent IA Foundation, escrita 2026-05-02) → marcada 💤 Diferida con header explicativo
- **Auto-crítica de Claude documentada**: 4 fallas en colaboración previa (no empujar customer development, aceptar premisa "5 agentes" sin friction, sumarse al sobre-engineering Bloque 0 v2, demasiados ADRs)
- **Razón del cambio**: Dario detectó en sesión que las decisiones sobre agentes se estaban escalando críticamente sin haberlas estructurado. Articuló doctrina rectora: el sistema debe operar 100% sin agentes; la IA se suma sobre infraestructura validada con datos de campañas reales.

---

**Este es un documento vivo.** Al cierre de cada sesión de trabajo, se actualiza esta sección con los cambios de alcance o decisiones nuevas.
