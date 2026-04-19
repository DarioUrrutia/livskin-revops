# ADR-0002 — Arquitectura de datos: 3 VPS y 5 bases de datos

**Estado:** ✅ Aprobada  
**Fecha:** 2026-04-18  
**Autor propuesta:** Claude Code  
**Decisor final:** Dario  
**Fase del roadmap:** Fase 0 (fundación)  
**Workstream:** Infra + Datos

---

## 1. Contexto

El proyecto arranca con 2 VPS existentes:
- **VPS 1 (WordPress)** en 46.101.97.246 — presencia web pública
- **VPS 2 (Operations)** en 167.172.97.197 — stack de automatización Docker (n8n + Vtiger + Metabase + Postgres vacío)

El ERP actual de Livskin vive en **Render** (formulario-livskin.onrender.com) con **Google Sheets** como DB — un cuello de botella reconocido y aislado del resto de la infraestructura.

Durante la sesión estratégica del 2026-04-18, la decisora propuso crear un **3er VPS dedicado** a dos propósitos:
1. Alojar el ERP refactorizado (cuando migre desde Render)
2. Alojar el segundo cerebro (ADR-0001)

Esta ADR establece:
- Por qué un 3er VPS es la decisión correcta (vs. alternativas)
- El rol de cada VPS y su aislamiento
- Las 5 bases de datos del sistema, su tecnología, propósito y acceso
- Las reglas duras de separación OLTP/OLAP
- El flujo de datos end-to-end
- La comunicación entre VPS (ADR-0004 es la ADR específica)

**Referencias:**
- Plan maestro § 6 (arquitectura del sistema)
- ADR-0001 (segundo cerebro — define el uso de DB `livskin_brain`)
- ADR-0004 (DO VPC — define la red privada)
- ADR-0010 (Alembic migrations)

---

## 2. Problema que resuelve

Sin una arquitectura de datos explícita, el proyecto arrastra estos riesgos:

1. **Confusión de responsabilidades entre DBs.** El blueprint original mencionaba "memoria vectorial" pero no definía dónde vive vs la data analítica. En la conversación inicial llegamos a proponer erróneamente meter data operativa del ERP en la DB de analytics, lo cual es un antipatrón.
2. **Contención de recursos.** Una sola instancia Postgres para OLTP (ventas en tiempo real) + OLAP (queries complejas de Metabase) + vectores (pgvector) asfixia cualquier workload.
3. **Blast radius excesivo.** Si VPS 2 cae, caen todos: orquestación + CRM + analítica + ERP + cerebro.
4. **Compliance débil.** PII médica (conversaciones WhatsApp, datos clínicos) en el mismo servidor que tráfico público es defensa pobre si hay incidente.
5. **Opacidad de sizing.** Sin arquitectura clara, no se sabe cuándo ni qué escalar.

---

## 3. Opciones consideradas

### 3.1 Opción A — Todo en los 2 VPS existentes (rechazada)

Meter ERP refactorizado + segundo cerebro en VPS 2 junto con lo que ya hay.

**Pros:**
- Cero costo marginal
- Red Docker interna (latencia mínima)

**Contras:**
- VPS 2 tiene 3.8 GB RAM; con todo lo que ya hay + ERP + pgvector + embeddings service + ERP DB = saturación inmediata
- Contención entre OLTP intenso (ventas) y OLAP pesado (dashboards Metabase)
- Blast radius máximo (todo cae junto)
- PII + público en mismo servidor

**Descartada.**

### 3.2 Opción B — Dividir entre 2 VPS existentes (rechazada)

ERP en VPS 1 (WP), cerebro en VPS 2 (Ops).

**Pros:** usa infra existente.

**Contras:**
- VPS 1 tiene solo 1 GB RAM — no cabe ERP refactorizado + Postgres
- Mezcla mal: WordPress es público, ERP contiene data financiera
- Viola principio de separación

**Descartada.**

### 3.3 Opción C — 3er VPS dedicado a ERP + cerebro (elegida)

Nuevo VPS en DigitalOcean Frankfurt (misma región), $12/mes (2 GB / 50 GB).

**Pros:**
- Aislamiento claro de responsabilidades
- RAM exclusiva para Postgres + pgvector + ERP Flask
- Blast radius limitado
- Simple de respaldar por separado
- Arquitectura 3-tier profesional (portfolio value)
- Red privada DO VPC gratis con los otros dos

**Contras:**
- +$12/mes
- Otro VPS que mantener (patches, seguridad)

**Elegida.** El costo es menor al margen de 1 paciente adicional/mes. La separación arquitectónica lo justifica.

### 3.4 Opción D — Managed database de DigitalOcean (rechazada para MVP)

DO Managed Postgres ($15-30/mes entry) + mantener ERP en Render.

**Pros:** sin mantenimiento DB.

**Contras:**
- Más caro
- Pierde flexibilidad (pgvector está disponible pero limitado)
- Managed DB + ERP Render sigue sin resolver la separación de ERP
- Viola principio 8 (costos)

**Descartada para MVP.** Reevaluar en mes 9+ si ventas >5,000/mes.

---

## 4. Arquitectura elegida — topología

### 4.1 Vista física

```
                      Internet (paciente, doctora, tú)
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │  Cloudflare (DNS + SSL + WAF)  │
                    └───┬────────────┬────────────┬──┘
                        │            │            │
             Pública    │            │            │
                        ▼            ▼            ▼
                 ┌────────────┐ ┌───────────┐ ┌───────────┐
                 │  VPS 1 WP  │ │ VPS 2 OPS │ │VPS 3 DATA │
                 │            │ │           │ │           │
                 │livskin.site│ │flow.  crm.│ │erp.       │
                 │            │ │dash.livsk.│ │erp-staging│
                 │(1GB/25GB)  │ │(4GB/78GB) │ │(2GB/50GB) │
                 └─────┬──────┘ └─────┬─────┘ └─────┬─────┘
                       │              │              │
                       └──────── DO VPC (privada, <1ms) ──────┘
                                      │
                              (solo tráfico inter-VPS)
```

### 4.2 Roles

| VPS | Hostname | IP pública | IP VPC | Rol | Responsabilidades |
|---|---|---|---|---|---|
| **VPS 1 — WordPress** | Livskin-WP-01 | 46.101.97.246 | 10.114.0.3 | Presencia pública | Web pública, SEO, captura leads, tracking client-side |
| **VPS 2 — Operations** | livskin-vps-operations | 167.172.97.197 | 10.114.0.2 | Orquestación + analítica | n8n flows, Vtiger CRM, Metabase dashboards, Langfuse, Postgres analytics |
| **VPS 3 — ERP** | livskin-vps-erp | 139.59.214.7 | 10.114.0.4 | OLTP + memoria | ERP transaccional refactorizado, Postgres + pgvector para segundo cerebro, embeddings service |

**VPS 3 provisionado 2026-04-19** con hardening baseline completo (UFW, Fail2Ban+whitelist, SSH endurecido, unattended-upgrades, Docker 29.4.0, swap 2GB). Lynis hardening index: 65/100.

### 4.3 Comunicación

- **Público:** solo por Cloudflare (DNS + WAF + proxy). Nunca puertos internos expuestos.
- **Privado entre VPS:** DigitalOcean VPC (ADR-0004). Gratis, latencia <1ms, tráfico nunca sale del data center.
- **Webhooks externos (Meta, WhatsApp):** llegan por Cloudflare al nginx correspondiente, que proxy-pasa al n8n en VPS 2.

Ver ADR-0004 para detalle de reglas de firewall y segmentación.

---

## 5. Las 5 bases de datos — diseño consolidado

### 5.1 Resumen

| DB | Motor | Container | VPS | Tipo | Responsabilidad |
|---|---|---|---|---|---|
| `livskin_wp` | MariaDB 10.6 | nativo | 1 | OLTP | Contenido WordPress |
| `vtigercrm` | MariaDB 10.6 | `vtiger-db` | 2 | OLTP | Estado del CRM |
| `analytics` | Postgres 16 | `postgres-analytics` | 2 | OLAP | Warehouse analítico |
| `metabase` | Postgres 16 | `postgres-analytics` | 2 | OLTP interno | Metadata Metabase |
| **`livskin_erp`** | **Postgres 16** | **`postgres-data`** | **3** | **OLTP** | **Transacciones del ERP** |
| **`livskin_brain`** | **Postgres 16 + pgvector** | **`postgres-data`** | **3** | **Semi-OLAP** | **Segundo cerebro** |

### 5.2 Regla dura: OLTP vs OLAP NO se mezclan

**OLTP** (Online Transaction Processing) = escrituras pequeñas y frecuentes, lecturas puntuales por clave primaria.
→ `livskin_wp`, `vtigercrm`, `livskin_erp`

**OLAP** (Online Analytical Processing) = lecturas complejas con JOINs sobre millones de filas agregadas.
→ `analytics`

**Semi-OLAP** = búsquedas vectoriales + SQL con filtros mixtos, latencia aceptable pero reads frecuentes.
→ `livskin_brain`

Un OLAP query pesado NUNCA debe bloquear un INSERT operativo. Por eso:
- `analytics` está en VPS 2 con Metabase (queries pesadas quedan contenidas)
- `livskin_erp` está en VPS 3 (ventas nunca esperan por un dashboard)
- `livskin_brain` comparte VPS 3 con ERP pero instancia Postgres separada sería la siguiente evolución si hay contención

### 5.3 Detalle por DB

#### 5.3.1 `livskin_wp` (MariaDB 10.6)

- **Ubicación:** VPS 1, MariaDB nativo (no Docker)
- **Puerto:** 3306 solo en 127.0.0.1
- **Usuario app:** `livskin_user` con permisos solo sobre `livskin_wp`
- **Contenido:** tablas estándar WordPress (`wp_posts`, `wp_users`, `wp_options`, etc.)
- **Backup:** UpdraftPlus (semanal automático a configurar en Fase 2)
- **Acceso externo:** ninguno (nginx/php-fpm local)

#### 5.3.2 `vtigercrm` (MariaDB 10.6)

- **Ubicación:** VPS 2, container `vtiger-db`
- **Red Docker:** `vtiger_internal` (aislada, solo Vtiger container la ve)
- **Puerto:** 3306 en red interna, NO expuesto al host ni a revops_net
- **Usuario app:** gestionado por Vtiger instalación
- **Contenido:** leads, contactos, accounts, potentials, events, tasks, campaigns, etc.
- **Backup:** pg_dump nocturno en Fase 2, rotación 7 días local + cross-VPS
- **Acceso externo:** ninguno (solo vía Vtiger API por n8n)

**Regla:** n8n NO hace queries SQL directas a `vtigercrm`. Todo pasa por Vtiger REST API (`/webservice.php`). Esto preserva la integridad de Vtiger (triggers, workflows internos) y desacopla.

#### 5.3.3 `analytics` (Postgres 16)

- **Ubicación:** VPS 2, container `postgres-analytics`
- **Red Docker:** `revops_net`
- **Puerto:** 5432 en red interna, NO expuesto al host
- **Usuario app:** `analytics_user` (read/write en DB `analytics`)
- **Usuario read-only:** `metabase_reader` (solo SELECT — para Metabase)
- **Contenido:** tablas de warehouse:
  ```
  leads                — leads extraídos de Vtiger
  crm_stages           — historial de cambios de etapa
  opportunities        — conversiones (leads → ventas) con revenue y atribución
  events               — eventos tracking (submits, clicks, conversiones)
  ads_metrics          — métricas de Meta Ads por creativo/día
  llm_costs            — tracking de costos Claude API por agente/día
  conversation_summary — resumen agregado de conversaciones (no contenido crudo)
  ```
- **Data source:** n8n ETL jobs pulling de Vtiger + `livskin_erp` + Meta Ads API
- **Backup:** pg_dump nocturno
- **Schema change:** Alembic obligatorio

#### 5.3.4 `metabase` (Postgres 16, interno Metabase)

- **Ubicación:** misma instancia que `analytics`, DB separada
- **Contenido:** metadata de Metabase (dashboards, queries guardadas, usuarios, permisos)
- **Gestión:** 100% automática por Metabase, no tocamos directamente
- **Backup:** pg_dump junto a `analytics`

#### 5.3.5 `livskin_erp` (Postgres 16)

**🚨 Nueva — Fase 1-2**

- **Ubicación:** VPS 3, container `postgres-data`
- **Red Docker:** `data_net`
- **Puerto:** 5432 en red interna, NO expuesto al host (accedido desde otros VPS solo vía VPC → conexión SSH-tunneled o psycopg2 sobre VPC)
- **Usuario app:** `erp_user` (read/write en DB `livskin_erp`)
- **Usuario read-only:** `analytics_etl_reader` (solo SELECT, usado por n8n para ETL hacia `analytics`)
- **Contenido inicial (Fase 2):**
  ```
  auth_users             — 2 cuentas (tú + doctora) con bcrypt, roles
  auth_sessions          — sesiones activas
  clientes               — maestro de clientes del ERP (sincronizado con Vtiger identidad)
  ventas                 — transacciones de venta (id, fecha, cliente, items, totales)
  venta_items            — line items por venta (tratamiento, producto, cantidad, precio)
  pagos                  — registros de pago (efectivo, Yape, Plin, transferencia)
  pago_asignaciones      — link many-to-many pagos ↔ ventas (para crédito)
  gastos                 — gastos del negocio por categoría
  productos              — catálogo productos (referencia a clinic_knowledge)
  tratamientos           — catálogo tratamientos (referencia a clinic_knowledge)
  audit_log              — tabla inmutable: quién cambió qué cuándo
  alembic_version        — control de migrations
  ```
- **Migrations:** Alembic obligatorio (ADR-0010)
- **Backup:** pg_dump nocturno + cross-VPS copy a VPS 2

**Relación con Vtiger:**
- `clientes.id_vtiger` es FK opcional al lead en Vtiger
- Cuando ERP crea cliente nuevo: n8n lo replica a Vtiger (identidad)
- Cuando Vtiger detecta cambio de datos de contacto: n8n propaga a `clientes`
- **Source of truth:** Vtiger para identidad (nombre, teléfono, email) · ERP para transacciones (ventas, pagos, crédito)

#### 5.3.6 `livskin_brain` (Postgres 16 + pgvector)

**🚨 Nueva — Fase 1**

- **Ubicación:** VPS 3, misma instancia `postgres-data` que `livskin_erp`
- **Red Docker:** `data_net`
- **Usuario app:** `brain_user` (read/write en DB `livskin_brain`)
- **Usuario read-only:** `brain_reader` (para Metabase que lee L3/L5/L6)
- **Extensión obligatoria:** `pgvector >= 0.7.0`
- **Contenido:**
  ```
  clinic_knowledge       — L1: catálogo + brand voice + protocolos + FAQs
  project_knowledge      — L2: chunks de docs del repo
  conversations          — L4: mensajes WhatsApp con embedding
  creative_memory        — L5: briefs + creativos + performance
  learnings              — L6: insights destilados
  v_lead_full_context    — L3: vista SQL derivada
  embedding_runs         — log de operaciones de re-embedding
  alembic_version        — control de migrations
  ```
- **Ver ADR-0001** para schema completo.

---

## 6. Flujo de datos end-to-end

### 6.1 Flujo de un lead que convierte en venta

```
[1] Paciente ve ad Meta → click con fbclid
    │
    ▼
[2] livskin.site/landing (VPS 1 WordPress)
    │   PixelYourSite captura UTMs + fbclid
    │   → Meta Pixel (client-side)
    │   → GA4 (client-side)
    │   Complianz valida consent
    │   UTMs guardadas en cookie + localStorage
    ▼
[3] Paciente llena SureForms
    │   Form captura hidden fields (UTMs, fbclid, gclid)
    │   → webhook HTTPS a flow.livskin.site
    ▼
[4] n8n recibe (VPS 2, container n8n)
    │
    ├─► [4a] Vtiger API: POST /ws/create Lead
    │         → INSERT en vtigercrm.leads (VPS 2)
    │         → incluye utm_source, utm_medium, utm_campaign,
    │           fbclid, gclid, consent, tratamiento_interés
    │
    ├─► [4b] Meta Conversion API (HTTPS externa)
    │         → envía "Lead" event con fbclid hasheado
    │         → Meta atribuye a la campaña correcta
    │
    ├─► [4c] GA4 Measurement Protocol (HTTPS externa)
    │         → envía "generate_lead" event
    │
    └─► [4d] INSERT en analytics.events (VPS 2, postgres-analytics)
              → tabla canonical de todos los eventos
    │
    ▼
[5] n8n dispara Conversation Agent
    │
    ├─► [5a] Llama al brain (VPS 3, livskin_brain):
    │         - brain_get_clinic_knowledge(tratamiento_interés) → L1
    │         - no hay historial (L4 vacío para este paciente)
    │
    ├─► [5b] Llama Claude API con prompt + contexto
    │         → respuesta generada
    │
    ├─► [5c] WhatsApp Cloud API: envía mensaje
    │         (test number en Fase 4, prod cuando Meta apruebe)
    │
    └─► [5d] INSERT en livskin_brain.conversations (VPS 3)
              → mensaje + embedding
    │
    ▼
[6] Paciente responde → loop vuelve a [5] con historial creciente
    │   Cada mensaje agrega fila a L4 (conversations)
    │
    ▼
[7] Paciente agenda cita (conversación completada)
    │
    ├─► [7a] n8n crea Event en Vtiger Calendar (vía API)
    │         → INSERT en vtigercrm.events (VPS 2)
    │
    └─► [7b] n8n marca el Lead como "Cita Agendada" (stage change)
              → UPDATE en vtigercrm.leads
    │
    ▼
[8] Día de la cita: paciente asiste, compra
    │
    ├─► [8a] Recepción/doctora registra venta en ERP UI
    │         → HTTP POST a erp.livskin.site (VPS 3)
    │         → ERP Flask valida con Pydantic
    │         → SQLAlchemy INSERT en livskin_erp.ventas (VPS 3)
    │         → INSERT en livskin_erp.venta_items
    │         → INSERT en livskin_erp.pagos
    │         → INSERT en livskin_erp.audit_log
    │
    └─► [8b] Trigger Postgres o polling n8n detecta venta nueva
    │
    ▼
[9] n8n cierra el loop de atribución
    │
    ├─► [9a] Busca el lead en vtigercrm por teléfono/email
    │         → obtiene fbclid/gclid originales
    │
    ├─► [9b] Meta Conversion API: "Purchase" event con fbclid
    │         → Meta sabe que el ad x generó S/. y revenue
    │
    ├─► [9c] GA4: "purchase" event
    │
    ├─► [9d] INSERT en analytics.opportunities con:
    │         revenue, cliente_id, fuente, campaña, lead_id, fecha_lead, fecha_venta
    │
    └─► [9e] UPDATE vtigercrm.leads (stage = "Ganada")
    │
    ▼
[10] Metabase dashboards se refrescan con nueva conversión
     │   Growth Agent la captura en su análisis diario
     │
     ▼
[11] Día 45 post-venta:
     │   Cron n8n detecta ventas con fecha = hoy-45
     │   → Conversation Agent genera mensaje de reactivación
     │     personalizado según último tratamiento
     │   → WhatsApp Cloud API envía
     │   → nueva conversación empieza en L4 (brain)
```

### 6.2 Flujo ETL (nocturno)

```
[1] n8n cron diario 03:00 UTC
    │
    ├─► [1a] Query vtigercrm vía API
    │         → transformación → INSERT/UPDATE en analytics.leads, crm_stages
    │
    ├─► [1b] Query livskin_erp (VPS 3 via VPC)
    │         → transformación → INSERT/UPDATE en analytics.opportunities
    │
    ├─► [1c] Query livskin_brain (VPS 3 via VPC)
    │         → conversation_summary → INSERT en analytics.conversation_summary
    │
    └─► [1d] Meta Ads API pull horario
              → INSERT en analytics.ads_metrics
```

---

## 7. Seguridad de DBs (resumen; detalle en ADR-0003)

| Protección | Nivel |
|---|---|
| Contraseñas DB | Únicas, generadas aleatoriamente, en `.env` gitignored |
| Puertos expuestos al host | Ninguno (solo Docker networks internas) |
| Puertos expuestos a internet | **Ninguno** (DBs nunca en internet público) |
| Acceso cross-VPS | Solo por DO VPC (red privada), credentials distintas por VPS |
| Usuarios app | Least privilege (solo los permisos que necesitan) |
| Encryption at rest | DO volumes cifrados por defecto |
| Encryption in transit | TLS opcional local (las redes ya están privadas), obligatorio para conexiones cross-VPS |
| Backups | Cifrados con gpg antes de salir del VPS |
| PII sensible | Columnas cifradas con pgcrypto (ver ADR-0003) |

---

## 8. Backups — estrategia por DB

Ver ADR-0041 para política completa. Resumen:

| DB | Herramienta | Frecuencia | Retención local | Cross-VPS | Fase activación |
|---|---|---|---|---|---|
| `livskin_wp` | UpdraftPlus + mysqldump | Semanal + pre-changes | 7 días | Sí, a VPS 2 | Fase 2 |
| `vtigercrm` | mysqldump en container | Diario | 7 días | Sí, a VPS 3 | Fase 2 |
| `analytics` | pg_dump | Diario | 7 días | Sí, a VPS 3 | Fase 2 |
| `metabase` | pg_dump (junto con analytics) | Diario | 7 días | Sí | Fase 2 |
| `livskin_erp` | pg_dump | Diario | 14 días | Sí, a VPS 2 | Fase 2 |
| `livskin_brain` | pg_dump | Diario | 14 días | Sí, a VPS 2 | Fase 2 |

Snapshot manual de los 3 VPS cada fase de roadmap (tier `manual`, retenido indefinidamente o hasta nueva sesión de limpieza).

---

## 9. Escalamiento planeado — umbrales pre-definidos

| DB | Trigger | Acción |
|---|---|---|
| `analytics` | >10M filas en tablas principales | Particionamiento por mes (pg_partman) |
| `livskin_erp` | >100k ventas/año | Índices revisados, query tuning |
| `livskin_brain` | >1M vectores | Evaluar migración a Qdrant o instancia Postgres dedicada |
| Cualquier | Disco VPS < 20% | Upgrade disco DO (+$X) |
| Cualquier | Query p99 > 500ms sostenido | pg_stat_statements + index tuning |
| VPS 3 | RAM sostenida >85% | Upgrade 2→4 GB |
| Volumen total | >5,000 ventas/mes | Evaluar DO Managed Postgres |

---

## 10. Tradeoffs aceptados

| Tradeoff | Impacto | Por qué lo aceptamos |
|---|---|---|
| +$12/mes por VPS 3 | Costo recurrente | Justificado por separación arquitectónica + portfolio value |
| ERP y cerebro en misma instancia Postgres | Contención si uno explota | Overhead de instancia separada no justifica al volumen; mitigamos con pools separados |
| Cross-VPS queries tienen latencia red (<1ms vía VPC) | Marginal | Compensado por aislamiento |
| Postgres + pgvector en misma DB comparten recursos | Queries Metabase podrían afectar búsqueda vectorial | Solo si ambas están en misma instancia — aquí están separadas (analytics en VPS 2, brain en VPS 3) |
| Vtiger accede a su DB aislada por red Docker propia | Menos flexible para queries directas | Protege integridad del CRM; disciplinamos a usar API |
| 3 VPS para mantener | +3× security patches | Automatizado con unattended-upgrades + audit mensual |

---

## 11. Decisión

**Arquitectura aprobada:**
- **3 VPS** en DigitalOcean Frankfurt (mismo data center para VPC)
- **5 bases de datos** distribuidas: `livskin_wp` (WP), `vtigercrm` (Ops), `analytics` + `metabase` (Ops), `livskin_erp` + `livskin_brain` (Data nuevo)
- **Separación estricta OLTP vs OLAP** a nivel de instancia Postgres
- **DO VPC** (privada) para comunicación entre los 3 VPS (ADR-0004)
- **Cloudflare** sigue siendo la única puerta pública
- **Alembic** obligatorio para todas las DBs que manejemos (ADR-0010)
- **Backups** cross-VPS + local retention escalonada (ADR-0041)

**Fecha de aprobación:** 2026-04-18 por Dario.

**Razonamiento de la decisora:** separar data operativa de analítica es limpieza arquitectónica no negociable. El VPS dedicado a data aísla el blast radius y protege el activo más crítico (transacciones + conocimiento acumulado). Costo ($12/mes) es marginal vs beneficio.

---

## 12. Consecuencias

### Desbloqueado por esta decisión
- ERP puede migrar desde Render con estrategia strangler fig
- Segundo cerebro (ADR-0001) tiene ubicación física definitiva
- Metabase puede hacer queries pesadas sin asfixiar n8n
- Backups cross-VPS tienen destino lógico claro (cada VPS respalda a otro)
- Escalamiento futuro es modular (se upgrade VPS individualmente)

### Tareas derivadas (pendientes)
- [ ] **Fase 1:** provisionar VPS 3 en DigitalOcean Frankfurt ($12/mo)
- [ ] **Fase 1:** hardening baseline (idéntico a VPS 1 y 2)
- [ ] **Fase 1:** activar DO VPC entre los 3 VPS (ADR-0004)
- [ ] **Fase 1:** desplegar container `postgres-data` con Postgres 16 + pgvector
- [ ] **Fase 1:** crear DBs `livskin_erp` y `livskin_brain` con usuarios app
- [ ] **Fase 1:** desplegar container `embeddings-service`
- [ ] **Fase 1:** configurar Nginx + Cloudflare DNS (`erp.livskin.site`, `erp-staging.livskin.site`)
- [ ] **Fase 1:** configurar Alembic para cada DB manejada
- [ ] **Fase 1:** configurar GitHub Actions CI/CD (push → VPS 3)
- [ ] **Fase 2:** schemas completos de `livskin_erp` aplicados
- [ ] **Fase 2:** schemas de `livskin_brain` aplicados (ver ADR-0001)
- [ ] **Fase 2:** ERP refactorizado desplegado
- [ ] **Fase 2:** Backfill 74 ventas + 135 clientes
- [ ] **Fase 2:** backups cross-VPS configurados (cron + rsync/scp sobre VPC)

### Cuándo reabrir esta decisión
- Volumen supera 10M filas en `analytics` (pg_partman o migración a dedicated)
- Contención Postgres en VPS 3 sostenida: evaluar instancias separadas para ERP y brain
- Incidente mayor en DO Frankfurt: evaluar multi-region o multi-provider
- Cambio en estrategia de negocio (ej: multi-clínica): reevaluar aislamiento por tenant

---

## 13. Referencias

- Plan maestro § 6 — arquitectura del sistema
- ADR-0001 — segundo cerebro (define el uso de `livskin_brain`)
- ADR-0003 — seguridad baseline
- ADR-0004 — comunicación entre VPS (DO VPC)
- ADR-0010 — Alembic migrations
- ADR-0041 — política de backups
- DO VPC docs: https://docs.digitalocean.com/products/networking/vpc/
- pgvector docs: https://github.com/pgvector/pgvector

---

## 14. Changelog

- 2026-04-18 — v1.0 — Creada, aprobada en sesión estratégica de Fase 0
- 2026-04-19 — v1.1 — VPS 3 provisionado (`livskin-vps-erp` @ 139.59.214.7). IPs VPC de los 3 VPS confirmadas (10.114.0.2-4). Conectividad VPC verificada en vivo con ping <2ms entre los 3. ADR-0004 (DO VPC) pasa a estado implementado. Ver [session log 2026-04-19](../sesiones/2026-04-19-fase1-vps3-creado.md) y [audit](../audits/2026-04-19-vps3-baseline.md).
