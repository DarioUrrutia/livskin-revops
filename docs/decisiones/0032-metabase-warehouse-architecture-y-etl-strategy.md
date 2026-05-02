# ADR-0032 — Metabase como BI hub centralizado vía warehouse `analytics` con ETL n8n

**Estado:** ✅ Aprobada
**Fecha:** 2026-05-02
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 3 (Mini-bloque 3.5)
**Workstream:** Datos · Tracking · Observabilidad

---

## 1. Contexto

Mini-bloque 3.5 (último de Fase 3) construye **observabilidad + Metabase dashboards**. Pregunta arquitectónica clave: ¿cómo se conecta Metabase a las fuentes de datos del proyecto?

**Constraints del proyecto Livskin:**

1. **Metabase es BI cross-system** — no dashboard de un solo sistema. Métricas core como CAC require join multi-sistema:
   - Meta Ads spend (Meta API)
   - Lead attribution (Vtiger cf_NNN)
   - Cliente convertido (ERP)
   - Sin warehouse → join imposible o frágil

2. **Múltiples fuentes de datos diferentes (>5):** ERP, Vtiger, Meta Ads API, Google Ads API, GA4, Pixel/CAPI events, Brain pgvector (Fase 5+), Cost tracking (Fase 5+).

3. **Visión portfolio Dario** (RevOps profesional): mostrar BI con warehouse separado es estándar en empresas reales. Conectar Metabase directo a operacional es nivel junior, demuestra desconocimiento de separation of concerns.

4. **Master plan + `analytics/README.md`** explícitamente prevén warehouse separado en VPS 2 (`analytics` DB en `postgres-analytics`) consumido por Metabase con usuario `metabase_reader` SELECT-only.

5. **Volume actual bajo** (~200 leads en backfill, sin campañas pagadas aún) — el costo de operar warehouse hoy es marginal (5-min ETL n8n cron es trivial vs operacional), pero el valor crece con cada source nueva.

**Referencias:**
- `analytics/README.md` (estructura warehouse + dashboards planeados)
- ADR-0002 — Arquitectura datos 3 VPS (Metabase vive en VPS 2)
- ADR-0019 — Tracking architecture (Pixel + CAPI eventos como source de `events`)
- Memoria `project_attribution_chain_event_id.md` — el `event_id` es el hilo conductor multi-sistema, dashboards lo aprovechan
- Memoria `project_n8n_orchestration_layer.md` — n8n es la capa que orquesta TODOS los syncs cross-system, los ETLs viven ahí

---

## 2. Opciones consideradas

### Opción A — Metabase conecta directo a ERP DB (`livskin_erp`)

Conexión única de Metabase a Postgres ERP con usuario read-only. Dashboards construidos con queries directas sobre `leads`, `clientes`, `ventas`, `pagos`, `audit_log`, `infra_snapshots`.

**Pros:**
- Velocidad: 0 ETL, 0 migration, 0 sync drift. Setup en 30 min.
- Sin lag (data fresh real-time vs ETL cada 5 min).
- Una sola conexión para mantener.

**Cons:**
- Solo cubre data del ERP. **No hay forma de calcular CAC/ROAS** sin Meta+Google ads spend.
- Acopla queries Metabase al schema operacional. Cualquier refactor del ERP rompe dashboards.
- BI compite con producción operacional en mismo Postgres → degradación performance bajo carga.
- Imposible joinear con Vtiger (otra DB en otro VPS) en una query directa.
- No escalable: cada source nueva (Meta, Google, Brain) requiere nueva conexión Metabase + queries acopladas a cada schema. Multiplica complejidad.
- **Anti-portfolio**: muestra falta de entendimiento de BI architecture profesional.

### Opción B — Warehouse separado `analytics` con ETL n8n cross-system

Postgres `analytics` (VPS 2) consolida data de TODOS los sistemas vía ETL n8n. Metabase conecta SOLO a `analytics`. Schema warehouse-friendly (denormalized, optimized para queries analíticas).

**Pros:**
- Cubre TODA la data del proyecto (ERP + Vtiger + Meta + Google + Pixel + Brain + costs).
- Aislamiento: BI no toca producción operacional.
- Schema warehouse estable independiente del schema operacional (refactors ERP no rompen dashboards).
- Pattern ETL n8n reutilizable: cada source nueva = nuevo workflow [E_n] siguiendo el mismo template.
- Joins multi-sistema posibles (CAC = Meta spend ÷ ERP clientes, ROAS = Meta spend ÷ ventas).
- Portfolio: estructura BI estándar de empresa real.
- Master plan + `analytics/README.md` ya lo previeron — no es decisión nueva, es ejecución de lo que ya está documentado.

**Cons:**
- Más trabajo upfront (~7-12h vs 2h opción A).
- Complejidad ETL n8n: idempotencia, dedup, ordering, retry, alerting.
- Lag: data en warehouse es 5-min stale vs real-time del ERP (aceptable para BI; fresh real-time para casos excepcionales se hace query directa al ERP por excepción).
- Mantenimiento: ETL workflows hay que monitorear (síntoma cuando fallan).

### Opción C — Híbrido: Metabase a warehouse + conexión read-only a ERP/Vtiger para dashboards específicos

Warehouse para todo lo cross-system (CAC, ROAS, journeys), pero algunos dashboards "operacionales" (Infra Health) consultan directo a ERP para data fresh real-time.

**Pros:**
- Combina lo mejor: warehouse para análitica, conexión directa para health/alerting que necesita real-time.

**Cons:**
- Complejidad: 2-3 conexiones Metabase a mantener.
- Confusión cognitiva: "dashboard X tira de A, dashboard Y tira de B, ¿por qué?"
- En la práctica, lag de 5 min es aceptable también para health (sensor cron ya es 5 min anyway).

---

## 3. Análisis de tradeoffs

| Dimensión | Opción A | Opción B | Opción C |
|---|---|---|---|
| Costo (infra) | $0 (ya hay Postgres ERP) | $0 (postgres-analytics ya está corriendo) | $0 |
| Complejidad implementación | Trivial (30 min) | Alta (7-12h) | Media (8-13h, B + tweaks) |
| Complejidad mantenimiento | Baja al inicio, sube con cada source | Alta inicial, plana después | Alta |
| Tiempo a primer dashboard útil | 30 min | ~5-6h | ~5-6h |
| Riesgo (drift, regression) | Alto (queries acopladas a operacional) | Bajo (warehouse estable) | Medio |
| Reversibilidad | Migrar a B después es costoso (rewrite queries) | Si decide volver a A, abandono warehouse (data loss aceptable) | Híbrido propio |
| Portfolio value | Bajo | Alto | Medio |
| Alineación principios operativos | ❌ contradice principio 3 ("una fuente de verdad por dominio") | ✅ respeta separation of concerns | Medio |
| Multi-sistema joins (CAC, ROAS) | Imposible / muy hacky | Natural | Mixto |
| Soporta Brain + cost tracking futuros | Requiere refactor mayor | Plug-and-play (nueva tabla + ETL) | Plug-and-play |

---

## 4. Recomendación

Yo (Claude Code) recomiendo **Opción B (warehouse + ETL n8n)** porque:

1. **Es el único enfoque que escala con la visión del proyecto.** Livskin tiene >5 fuentes de data heterogéneas; sin warehouse, el join CAC es imposible.

2. **Master plan + `analytics/README.md` ya lo definieron** — esta ADR formaliza la implementación, no inventa arquitectura nueva.

3. **Portfolio**: muestra entendimiento de BI architecture profesional, valioso para transición Dario a RevOps senior.

4. **Reversibilidad asimétrica favorable**: si después se decide simplificar (Opción A), abandonar warehouse es trivial (drop tables). Si se hace A primero, migrar a B requiere rewrite de queries Metabase, dashboards, etc.

5. **El costo upfront alto se amortiza**: una vez que el patrón [E_n] ETL está en producción, agregar source nueva (cuando llegue Meta Ads, Google Ads, Brain) es ~30-60 min copying template, no 4-6h por source.

**Tradeoff principal que aceptamos:** mayor tiempo de implementación inicial (7-12h vs 2h) y lag de ~5 min en data analítica vs real-time. Para BI, ese lag es estándar y aceptable.

---

## 5. Decisión

**Elección:** **Opción B — Warehouse `analytics` con ETL n8n centralizado**

**Fecha de aprobación:** 2026-05-02 por Dario

**Razonamiento de la decisora:**
> "Metabase es donde centralizamos la data del proyecto, no solo del ERP. Tiene que recopilar información de todos nuestros sistemas, incluso Vtiger y campañas. Opción B es la correcta."

---

## 6. Consecuencias

### Desbloqueado por esta decisión

- Mini-bloque 3.5 ejecutable con scope claro (warehouse + ETLs internos hoy + Meta/Google ETLs cuando haya campañas reales).
- Pattern ETL n8n reusable: cada source nueva sigue template `[E_n]` (idempotent UPSERT, cron schedule, audit log).
- Alertas centralizadas (Metabase alerts o n8n cron) — un solo lugar para health monitoring.
- Brand Orchestrator F5 + Conversation Agent F4 obtendrán métricas históricas + cohorts directamente del warehouse sin tocar producción operacional.

### Bloqueado / descartado

- Opción A (Metabase directo a ERP) descartada por anti-escalable + acoplamiento queries.
- Opción C (híbrido) descartada por complejidad cognitiva sin beneficio claro.

### Implementación derivada — Mini-bloque 3.5 (HOY)

**Sub-pasos hoy (~7-8h scope):**
- [ ] **3.5.1** Migration `analytics` DB: extend tablas existentes + crear `ads_metrics` (vacía, ready), `infra_snapshots_daily`, `agent_costs` (vacía Fase 5+) (60 min)
- [ ] **3.5.2** Usuario `metabase_reader` SELECT-only en `analytics` DB (10 min)
- [ ] **3.5.3** ETL [E1] `livskin_erp.leads/clientes/ventas/pagos` → `analytics.leads + opportunities` (n8n cron 5 min, idempotent UPSERT) (90 min)
- [ ] **3.5.4** ETL [E2] `Vtiger Leads + cf_NNN` → enriquece `analytics.leads` (n8n cron 5 min) (60 min)
- [ ] **3.5.5** ETL [E3] `livskin_erp.audit_log` → `analytics.crm_stages` (lifecycle changes) (45 min)
- [ ] **3.5.6** ETL [E4] `livskin_erp.infra_snapshots` → `analytics.infra_snapshots_daily` (rollup nocturno) (30 min)
- [ ] **3.5.7** Metabase reconfigurar conexión a `analytics` DB (15 min)
- [ ] **3.5.8** Dashboard 1 — Leads/día por canal+UTM (45 min)
- [ ] **3.5.9** Dashboard 2 — Funnel: leads → clientes → ventas (60 min)
- [ ] **3.5.10** Dashboard 3 — Attribution preserved (UTMs end-to-end) (45 min)
- [ ] **3.5.11** Dashboard 4 — Infra Health (sensors + audit + uptime) (45 min)
- [ ] **3.5.12** Alertas básicas (zero leads 24h, sensor stale, audit anomalies) (45 min)
- [ ] **3.5.13** Smoke E2E + screenshots + cleanup (30 min)

### Implementación diferida — Mini-bloque 3.5.B (cuando lances primera campaña paga)

**Sub-pasos diferidos (~5-6h, sesión separada):**
- [ ] **3.5.14** ETL [E5] `Meta Ads API` → `analytics.ads_metrics` (n8n cron horario, OAuth Meta + scopes Marketing API) (90 min)
- [ ] **3.5.15** ETL [E6] `Google Ads API` → `analytics.ads_metrics` (n8n cron horario, OAuth Google ya validado en sesión 2026-04-27) (90 min)
- [ ] **3.5.16** ETL [E7] GA4 events → `analytics.events` (eventos cross-platform comparison) (60 min)
- [ ] **3.5.17** Dashboard CAC por canal (spend / clientes adquiridos) (45 min)
- [ ] **3.5.18** Dashboard ROAS por campaña (revenue / spend) (45 min)
- [ ] **3.5.19** Dashboard Tracking Health (Match Quality CAPI, eventos recibidos, dedup ratio) (60 min)
- [ ] **3.5.20** Smoke E2E con campaña real + screenshots (30 min)

**Razón del diferimiento:** Meta Ads API y Google Ads API devuelven `[]` sin campañas activas. Construir ETLs hoy contra empty data es trabajo preventivo sin valor inmediato y sin manera de validar que funciona. Cuando arranque la primera campaña con landing botox-mvp, ahí tiene sentido — tenemos data en vivo para verificar.

### Mejoras anticipadas (extensibilidad sin re-arquitectura)

El warehouse + pattern ETL [E_n] permite agregar fuentes futuras sin tocar la decisión arquitectónica:

| Source futura | Tabla destino | Fase | ETL effort |
|---|---|---|---|
| Brain pgvector conversation summaries | `analytics.conversation_summary` | F4-F5 | 60 min |
| Langfuse LLM costs | `analytics.agent_costs` | F5+ | 45 min |
| WhatsApp Cloud API metrics (templates sent, delivery rate) | `analytics.wa_messages_summary` | F4+ | 60 min |
| TikTok Ads API (si Dario decide expandir) | `analytics.ads_metrics` (mismo schema, distinct platform col) | F5+ | 90 min |
| Vtiger scoring history (si v2 de scoring entra en F4) | `analytics.lead_scoring_history` | F4 | 45 min |
| Doctora actions (manual phone capture, escalations) | `analytics.doctora_actions` | F4 | 45 min |

Cada uno: nuevo workflow `[E_n]` siguiendo el template del [E1], optional Alembic migration si tabla nueva.

### Riesgos identificados + mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| ETL [E1-E6] tiene bug y warehouse queda stale | Media | Alto | Audit log entries por ETL run + alerting si stale >15 min |
| Drift schema ERP vs warehouse | Baja | Medio | Cada Alembic migration ERP requiere check explícito de impacto en ETLs |
| Lag 5 min insuficiente para algún caso | Baja | Bajo | Excepción: query directa a ERP solo para ese dashboard puntual |
| Costo postgres-analytics crece con tiempo | Baja | Bajo | Retention policy: rollups mensuales, raw data >12 meses se archiva |
| Metabase queries lentas en warehouse | Media | Medio | Indices en columnas joinables (utm_*, vtiger_id, fecha), materialized views si necesario |

### Cuándo reabrir esta decisión

- **Trigger 1 (volume)**: si warehouse `analytics` supera 10M filas en cualquier tabla → considerar particionado, columnar storage (TimescaleDB extension), o migración a herramienta dedicada (BigQuery, Snowflake). MVP no se acerca.
- **Trigger 2 (BI tool)**: si Metabase queda chico (queries dashboard >10s típicas, >50 dashboards activos) → considerar Looker, Superset, o tooling más serio. MVP no se acerca.
- **Trigger 3 (multi-tenant)**: si Livskin escala a múltiples clínicas con data segregada → re-evaluar schema (probable agregar `tenant_id` columna).
- **Trigger 4 (real-time)**: si emergiera caso de uso real-time crítico (ej: alertas que no toleran 5-min lag) → considerar streaming (Debezium CDC, Kafka). Actualmente no hay caso.
- **Revisión obligatoria**: cada cierre trimestral de Fase del roadmap.

### Notas de mejoras continuas

Esta arquitectura está diseñada para **mejoras incrementales sin breaking changes**:

1. **Schema additive**: agregar columnas a tablas existentes vía Alembic — ETLs siguen funcionando con `INSERT ... ON CONFLICT` ignorando columns nuevas hasta que se popule.
2. **Source addition**: nueva source = nuevo workflow [E_n], 0 cambios a sources existentes.
3. **Query optimization**: dashboards lentos se optimizan con indices o materialized views, sin tocar ETL.
4. **Schema evolution**: si una tabla necesita refactor mayor, se versiona (`leads_v2`) y migra dashboards uno por uno; tabla vieja queda hasta que todos los dashboards migran.
5. **Monitoreo del warehouse mismo**: dashboard meta-observability ("ETLs status, lag, throughput") en sí mismo en Metabase.

**No hay decisión congelada hasta el final del proyecto.** Esta ADR define el approach, pero cada sub-componente (un ETL, un dashboard, una alerta) evoluciona iterativamente con feedback de uso real.

---

## 7. Changelog de esta ADR

- 2026-05-02 — v1.0 — Creada y aprobada por Dario en sesión Mini-bloque 3.5 arranque.

---

**Notas:**

- Las ADRs son inmutables una vez aprobadas salvo cambios de status.
- Esta ADR se considera "alive" porque define una arquitectura extensible — cambios en sub-componentes (workflows ETL específicos, dashboards individuales) NO requieren superseder esta ADR. Solo cambios que rompan el approach (ej: abandonar warehouse) requerirían ADR-NNNN nuevo que la superseda.
