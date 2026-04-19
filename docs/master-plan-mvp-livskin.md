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
18. [Changelog](#18-changelog)

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

## 4. Filosofía operativa — 10 principios

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
| Vtiger CRM | 8.2.0 | CRM maestro — identidad cliente | VPS 2 container |
| n8n | 2.14.2 | Orquestador flujos | VPS 2 container |
| Metabase | latest | Dashboards BI | VPS 2 container |
| Langfuse | — | Observabilidad agentes IA | VPS 2 container (**Fase 3**) |
| **ERP Livskin (refactorizado)** | Flask + SQLAlchemy + Pydantic | Transacciones: ventas, pagos, gastos | VPS 3 container (**Fase 2**) |
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

### 10.1 Los 4 agentes

| Agente | Propósito | Frecuencia | Intervención humana/semana |
|---|---|---|---|
| **Conversation** | Primera línea atención pacientes vía WhatsApp | Tiempo real 24/7 | ~30 min/día (escalaciones a doctora) |
| **Content** | Generar 12 briefs semanales para ads + testimoniales | Semanal (domingos) | 15 min domingo (aprobación) |
| **Acquisition** | Convertir briefs a ads Meta + optimización autónoma | Semanal (lunes) + diario (tracking) | 10 min lunes |
| **Growth** | Análisis continuo + reporte ejecutivo semanal | Diario (análisis) + semanal (reporte) | 1 hora lunes |

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

**Objetivo:** ERP refactorizado en producción nueva con modelo profesional + segundo cerebro poblado con conocimiento base.

**Entregables:**
- **Dossiers aprobados:** 0011 (modelo Lead/Cliente/Venta), 0012 (stages Vtiger), 0013 (dedup), 0014 (naming), 0018 (schema cerebro)
- ERP refactorizado:
  - SQLAlchemy + psycopg2 (reemplazo de gspread)
  - Pydantic schemas para cada entidad
  - Service layer (VentaService, ClienteService, PagoService)
  - Type hints + mypy en CI
  - Pytest cobertura ≥70% lógica negocio
  - Logs estructurados (structlog)
  - Dockerfile + docker-compose
  - **Auth bcrypt + 2 cuentas fijas (tú + doctora)**
  - **Audit log tabla inmutable**
  - CSRF tokens + rate limiting
- Vtiger configurado (pipeline 7 stages, campos custom: fuente, utm_*, fbclid, gclid, tratamiento_interés, consent_marketing)
- **Layer 1 del cerebro poblado:** catálogo completo (21 tratamientos + 12 productos + áreas) con embeddings
- **Layer 2 del cerebro:** indexación del repo (todos los .md con embeddings, cron semanal)
- **Layer 3 del cerebro:** vistas SQL consolidadas
- **MCP server del cerebro desplegado** (yo puedo consultar desde Claude Code)
- Backfill: migración de 74 ventas + 135 clientes del Excel → `livskin_erp` con dedup contra Vtiger
- Sync inicial Vtiger ↔ ERP (n8n flows básicos)
- **Backups daily activados** (cuando entre data real)
- Parallel run Render vs VPS 3 por 1 semana; comparación manual

**Exit criteria:**
- El equipo comercial usa el ERP nuevo sin notar diferencia visual
- Revenue del día clasificable por fuente en Metabase
- Cutover: Render queda cold standby, VPS 3 autoritativo
- Yo (Claude Code) puedo preguntar al MCP server "¿cuáles son las contraindicaciones de botox?" y obtener respuesta precisa

### 11.5 Fase 3 — Tracking + observabilidad (Semana 5)

**Objetivo:** cada visita y click trazable hasta el revenue; observabilidad lista para agentes.

**Entregables:**
- **Dossiers aprobados:** 0017 (consent), 0021 (UTMs persistence)
- PixelYourSite configurado: Meta Pixel + GA4 + GTM (sin Pinterest/Bing/Reddit)
- GTM container creado con eventos: `page_view`, `view_content`, `lead_submit`, `whatsapp_click`, `purchase` (server-side)
- **Meta Conversion API** configurada en n8n (server-side events con fbclid)
- **GA4 Measurement Protocol** en n8n (server-side events)
- SureForms webhook payload: UTMs + fbclid + gclid + consent + landing + referer
- Script custom de UTM persistence en WP (localStorage)
- Complianz en modo reject-or-accept, ajustado
- **Langfuse desplegado** en VPS 2 (container adicional)
- **Cost tracking Claude API** activado (tabla `analytics.llm_costs`)
- Dashboards Metabase iniciales: "Leads por fuente", "Conversión por etapa"

**Exit criteria:**
- Lleno formulario con link UTM en navegador privado → evento aparece en Metabase con atribución correcta
- Meta Events Manager muestra el server-side event con match quality "Good"
- Langfuse captura primer request de prueba
- Cost tracker muestra $0.00 (aún no hay agentes)

### 11.6 Fase 4 — Conversation Agent (Semana 6)

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

**Entregables Semana 10 (estabilización):**
- **Dossiers aprobados:** 0039 (evals LLM-as-judge)
- Evals LLM-as-judge (Haiku) cada 100 conversaciones
- Golden set expandido a 50 conversaciones etiquetadas
- Runbooks: disaster recovery, key rotation, eliminación paciente (Ley 29733 baseline), incident response
- Lynis audit + OWASP ZAP scan inicial → report committed
- Documentación final arquitectura (diagrama canónico)
- Retrospectiva del primer mes en producción
- **Migración a WhatsApp número producción** (si Meta aprobó)

**Exit criteria:**
- Recibes lunes 09:00 reporte ejecutivo de la semana por WhatsApp
- Lynis score > 70 en los 3 VPS
- OWASP ZAP sin vulnerabilidades críticas/altas
- Todos los runbooks ejercitados al menos 1 vez (aunque sea en staging)
- Dashboard "Sistema completo" muestra salud end-to-end

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

## 18. Changelog

### v1.0 — 2026-04-18
- **Creación del plan maestro consolidado.**
- Integra: blueprint original (docx), system-audit 2026-04-16, datos reales del Excel, 39 decisiones tomadas en sesión de definición.
- Estructura de 6 workstreams paralelos a 10 semanas.
- Decisiones clave cerradas: 3er VPS a $12/mo, DO VPC (no Tailscale), refactor ERP (no rewrite), flujo citas WhatsApp (no LatePoint), 2 cuentas fijas ERP, embeddings self-hosted, Claude Design integrada al workstream creativo.
- 3 dossiers fundacionales aprobados: 0001 segundo cerebro, 0002 arquitectura datos, 0003 seguridad.
- Diferimentos explícitos: SUNAT, IGV, inventario, historial clínico, PDFs, offline mode, computer vision.

---

**Este es un documento vivo.** Al cierre de cada sesión de trabajo, se actualiza esta sección con los cambios de alcance o decisiones nuevas.
