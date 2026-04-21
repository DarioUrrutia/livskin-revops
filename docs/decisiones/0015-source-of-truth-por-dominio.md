# ADR-0015 — Source of Truth por dominio

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-21
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos

---

## 1. Contexto

El sistema Livskin involucra múltiples dominios de datos y múltiples sistemas. Sin una asignación clara de **quién es autoritativo para qué**, inevitablemente surgen:

- **Data drift** — dos sistemas con el "mismo" dato que divergen en el tiempo
- **Conflictos de escritura** — ambos sistemas actualizan el mismo campo con valores distintos
- **Queries inconsistentes** — mismo reporte da números diferentes según la fuente
- **Pérdida de confianza** — comerciales/doctora no saben dónde confiar

Este dossier estaba marcado ✅ en el índice de ADRs desde 2026-04-18 pero el archivo nunca se escribió (ADR "huérfana"). Durante sesión del 2026-04-21 Dario clarificó explícitamente el rol narrow de Vtiger (marketing automation para digital only), lo que forzó reabrir y escribir este ADR oficialmente.

**Contradicción resuelta**: docs previos (CLAUDE.md, README.md, master-plan § 5, ADR-0001 § scope) decían "Vtiger = master identidad cliente". Eso era incorrecto — es legado de pensamiento temprano antes de clarificar que los 135 clientes históricos word-of-mouth nunca entran a Vtiger.

Referencias:
- ADR-0011 v1.1 (modelo de datos — usa asignaciones de SoT aquí definidas)
- ADR-0013 v2 (dedup cross-system)
- ADR-0001 (segundo cerebro — define layers del brain como SoT de conocimiento)
- Memorias `project_vtiger_erp_sot`, `project_acquisition_flow`, `project_erp_migration`

---

## 2. Opciones consideradas

### Opción A — SoT por dominio funcional (la correcta dado el sistema real)
Cada dominio (Lead, Cliente, Venta, Conocimiento clínico, Conversaciones, Catálogo, Creativos, etc.) tiene UN sistema autoritativo. Otros sistemas pueden tener réplicas read-only o read-mostly, pero el SoT es único por dominio.

### Opción B — SoT unificado en ERP Postgres (descartada)
Todo vive en Postgres. Vtiger se usa solo como UI para leads pero escribe a Postgres. Brain es solo vectores sobre Postgres.

### Opción C — SoT unificado en Vtiger (descartada)
Vtiger como CRM-first, todo lo demás (incluyendo transacciones) vive en Vtiger mediante módulos custom.

### Opción D — No explicitar SoT (dejar ambiguo)
Status quo hasta hoy.

---

## 3. Análisis de tradeoffs

| Dimensión | A (SoT por dominio) | B (todo Postgres) | C (todo Vtiger) | D (ambiguo) |
|---|---|---|---|---|
| Claridad arquitectónica | **Alta** | Alta | Alta | Nula |
| Respeto a fortalezas de cada sistema | **Alta** | Media | Baja | Media |
| Complejidad sync | Media | Baja | Baja | Alta (silenciosa) |
| Reversibilidad decisiones futuras | Media | Alta | Baja | Alta (caótica) |
| Trabajo de refactor necesario hoy | Mínimo | Alto (migrar Vtiger funcionalidad) | Altísimo | Cero |
| Mitigación de data drift | **Alta** | Alta | Alta | Nula |

---

## 4. Recomendación

**Opción A — SoT por dominio.**

Razones:
1. **Respeta fortalezas de cada sistema**: Vtiger es un CRM con automation nativo; Postgres es una DB relacional con ACID; pgvector es retrieval semántico. Usar cada uno para lo que hace bien.
2. **Realidad operativa ya apunta a esto**: los 135 clientes walk-in están solo en ERP, no hay forma sana de forzarlos a Vtiger sin crear fricción.
3. **Sync mínimo necesario**: entre Vtiger y ERP solo se sincroniza el estado del Lead cuando convierte (un solo evento, bien delimitado).
4. **Escalable**: agregar nuevo dominio (ej: analytics dashboards) no requiere rediseñar, solo asignar SoT al nuevo sistema.

**Tradeoff aceptado**: hay que documentar y mantener la tabla de SoT. A cambio: eliminamos data drift silencioso.

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-21 por Dario.

**Razonamiento de la decisora:**
> "Al final los registros de ventas se seguirán dando directamente en nuestro ERP, pero en nuestro Vtiger usaremos como una máquina que apoye a la adquisición de clientes más que todo, donde todo el flujo de marketing digital venga metida a nuestro Vtiger y gestionada automáticamente, por eso el todo de este proyecto."

---

## 6. Tabla canónica de SoT por dominio

| # | Dominio | SoT (autoritativo) | Réplicas / Copias | Dirección de sync |
|---|---|---|---|---|
| 1 | **Lead** (prospecto digital pre-primera-venta) | **Vtiger** | `leads` en Postgres (para lookups rápidos + analytics) | Vtiger → Postgres (one-way, via webhook en cada cambio de estado) |
| 2 | **Cliente** (humano que compró al menos una vez) | **ERP Postgres `livskin_erp.clientes`** | `cod_cliente_vinculado` en Vtiger Lead (solo para leads convertidos) | ERP → Vtiger al momento de convertir (one-way, one-time) |
| 3 | **Transacciones** (ventas, pagos, gastos) | **ERP Postgres** | Metabase / dashboards read-only views | ERP → Metabase (SQL queries vivas, sin réplica física) |
| 4 | **Catálogo de tratamientos/productos/áreas** | **ERP Postgres `catalogos` + Brain Layer 1 `clinic_knowledge`** | Vtiger picklists (para forms y pipelines), Metabase dimensiones | ERP → Vtiger (sync semanal o on-demand), ERP → Brain (re-embed cuando cambia) |
| 5 | **Conocimiento clínico autoritativo** (contraindicaciones, protocolos, FAQs, respuestas validadas por doctora) | **Brain Layer 1** (`livskin_brain.clinic_knowledge` + pgvector) | Exportable a Vtiger knowledge base si se quiere | Brain es SoT; actualizaciones vienen de doctora vía interface admin |
| 6 | **Conocimiento del proyecto** (docs, ADRs, runbooks, session logs) | **Brain Layer 2** (`livskin_brain.project_knowledge`) + repo git | Indexador brain-tools sincroniza desde repo | Repo → Brain (cron semanal) |
| 7 | **Vistas consolidadas SQL** (joins pre-computados para agentes) | **Brain Layer 3** (views + materialized views sobre livskin_erp) | Metabase usa mismas views | No hay réplica; es layer computed |
| 8 | **Conversaciones** (WA Cloud API, form submissions interpretadas) | **Brain Layer 4** (`livskin_brain.conversations` con embeddings) | `form_submissions` table en ERP (raw) para audit | WA → n8n → Brain (semantic) + ERP (raw audit); dos escrituras, sin conflicto |
| 9 | **Creativos + performance campañas** | **Brain Layer 5** (`livskin_brain.creative_memory`) — Fase 5 | Meta Ads API y Google Ads API siguen siendo SoT de métricas externas | Meta/Google → Brain (pull diario via n8n) |
| 10 | **Learnings del sistema** (Growth Agent findings, patterns detectados) | **Brain Layer 6** (`livskin_brain.learnings`) — Fase 6 | Dashboard ejecutivo read-only | Growth Agent → Brain (weekly writes) |
| 11 | **Identity + authentication** (users ERP) | **ERP Postgres `users` table** | Session tokens en n8n si aplica | ERP es único SoT; agentes consumen con service tokens |
| 12 | **Tracking events** (pixel fires, CAPI, MP) | **Meta Events Manager + GA4** (externos, SoT de atribución) | Langfuse (internos de agentes), Postgres `analytics.events` para raw server-side | n8n → Meta/GA4 (push); Meta/GA4 → n8n (pull para reporting) |
| 13 | **LLM cost tracking** | **Postgres `analytics.llm_costs`** (alimentada por Langfuse) | Langfuse UI | Langfuse → Postgres (ETL diario) |

---

## 7. Reglas de oro

1. **Un dato = un SoT.** Si duda, consulta esta tabla.
2. **Nunca escribir directo a un sistema que NO es SoT para ese dato.** Si necesitas actualizar algo, hazlo en el SoT; otros sistemas se actualizan via sync definido.
3. **Las réplicas son read-mostly**, con timeout/stale-ok aceptable por domain.
4. **Sync bidireccional está PROHIBIDO por default** — genera conflictos. Si absolutamente necesario, documentar reglas de conflict resolution en dossier separado.
5. **Toda nueva tabla/dato nuevo se agrega a esta tabla** antes de implementar.
6. **ADR-0015 es referencia autoritativa** — si otros docs contradicen esto, esos docs están desactualizados.

## 8. Eventos de sync canónicos

### Sync 1: Vtiger → Postgres (Lead updates)
- Trigger: webhook de Vtiger al cambiar estado de lead, score, cualquier campo custom
- Destino: `leads` table en Postgres
- Implementado: Fase 2

### Sync 2: ERP → Vtiger (Lead conversion)
- Trigger: registro de venta en ERP cuando el cliente tiene `cod_lead_origen` set
- Destino: Vtiger Lead record → update estado=`cliente`, `cod_cliente_vinculado=LIVCLIENTxxxx`
- Implementado: Fase 2-4

### Sync 3: ERP → Brain Layer 1 (Catálogo refresh)
- Trigger: cambio en `catalogos` table
- Destino: re-embed afectados en `clinic_knowledge`
- Implementado: Fase 2

### Sync 4: Repo → Brain Layer 2 (docs indexing)
- Trigger: cron semanal
- Destino: `project_knowledge` en brain
- Implementado: YA EXISTE (ADR-0018 / Fase 1 brain-tools)

### Sync 5: WhatsApp → Brain Layer 4 + ERP (conversation logging)
- Trigger: cada mensaje inbound/outbound en WA Cloud API
- Destinos:
  - `livskin_brain.conversations` con embedding (semantic query)
  - `livskin_erp.form_submissions` si es form-triggered (audit)
- Implementado: Fase 4

### Sync 6: Meta Ads + Google Ads → Postgres analytics
- Trigger: n8n cron diario
- Destinos: `analytics.meta_ads_daily`, `analytics.google_ads_daily`
- Implementado: Fase 3

---

## 9. Qué se difiere explícitamente

- **Conflict resolution entre sistemas**: por ahora evitamos tener conflictos con reglas above. Si alguna vez dos sistemas escriben el mismo campo, escribir dossier ADR específico.
- **Distributed transactions cross-system**: no usamos 2PC ni Saga pattern. Aceptamos eventual consistency para syncs 1 y 2 (latencia típica <5s).
- **Schema versioning cross-system**: Alembic para Postgres (ya configurado), Vtiger usa su propio versioning interno. Coordinación manual.
- **Backup unificado**: cada SoT tiene su propio backup strategy (ADR-0003). No consolidamos.

---

## 10. Consecuencias

### Desbloqueado
- ADR-0011 v1.1 tiene asignaciones SoT no-ambiguas
- ADR-0013 v2 puede razonar sobre cross-system dedup sin ambigüedad
- Conversation Agent (ADR-0029) sabe dónde query cada dato sin adivinar
- Dashboard unificado sabe de dónde tirar cada métrica
- Backfill (ADR-0025) sabe qué tablas poblar y dónde NO tocar
- Implementación de sync flows en n8n tiene contract claro

### Bloqueado / descartado
- No se permiten tablas de "espejo completo" de Cliente en Vtiger (evita replicación de los 135 históricos)
- No se permite escribir ventas desde Vtiger directo (solo ERP)
- No se permite escribir leads desde ERP directo (solo Vtiger — excepto en backfill one-time)
- No se permite duplicar conocimiento clínico en Vtiger knowledge base (solo Brain L1 es autoritativo)

### Implementación derivada
- [ ] Actualizar CLAUDE.md línea stack: "Vtiger (master identidad cliente)" → "Vtiger (master lead digital)"
- [ ] Actualizar README.md idem
- [ ] Actualizar master-plan-mvp-livskin.md § 5 idem
- [ ] ADR-0001 revisión: línea "la tabla clientes vive en Vtiger" → actualizar (opción: crear ADR-0001 v1.1 o nota aclaratoria)
- [ ] Documentar en `integrations/vtiger/README.md` (Fase 2) las reglas SoT
- [ ] Documentar en cada integration README el dominio del que es SoT (si aplica)
- [ ] Diagrama canónico en `docs/diagramas/` (Fase 2 o 6) que visualiza flujos de sync

### Cuándo reabrir
- Si surge un dominio nuevo no listado en la tabla § 6
- Si se detecta data drift entre SoT y réplica (sugiere que las reglas de sync fallan)
- Si se decide consolidar sistemas (ej: migrar Vtiger funcionalidad a ERP)
- Integración con CDP externo (Segment, mParticle, RudderStack) que cambie el landscape
- Revisión trimestral obligatoria: 2026-07-21

---

## 11. Changelog

- 2026-04-21 — v1.0 — Creada (resuelve ADR huérfana). Contrapartida a la malinterpretación previa de "Vtiger = master cliente" documentada en CLAUDE.md/README.md/master-plan/ADR-0001.
