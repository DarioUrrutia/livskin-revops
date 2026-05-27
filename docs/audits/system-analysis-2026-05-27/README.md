---
type: system-analysis
created: 2026-05-27
status: closed
duration_min: 240
analysts: 4 sub-agents (estabilidad + escalabilidad + automatización + velocidad) + análisis cross-cutting
purpose: identificar gaps del backbone determinístico antes de sesión estratégica agentes IA
trigger: usuario solicitó cierre de sistema (doctrina #14) tras post-mortem 2da campaña
---

# Análisis Comprehensivo del Sistema — 2026-05-27

> Objetivo: identificar TODOS los gaps que bloquean cerrar el backbone determinístico (Fase 4A) antes de la sesión estratégica de agentes IA.
> 4 dimensiones × 12+ subsistemas = inventario completo + roadmap priorizado.

---

## 0. Resumen ejecutivo (TL;DR)

### Scores por dimensión

| Dimensión | Score | Estado | Top problema |
|---|---|---|---|
| 🔴 **Escalabilidad** | **3.5/10** | crítico | n8n SQLite single-writer rompe a 10x volumen |
| 🟡 **Automatización** | **4.0/10** | bajo | 21 pasos manuales recurrentes en ops/campañas |
| 🟡 **Velocidad campaña** | **5.5/10** | medio | Templates Meta tardan 48-72h cada lanzamiento |
| 🟡 **Estabilidad** | **5.5/10** | medio | Postgres-data SPOF + VPS1 RAM 92% |

### Promedio sistema: **4.6/10** — "operacional pero frágil; NO listo para escalar 10x"

### 🔴 Top 10 issues CRÍTICOS (consolidados)

| # | Gap | Dimensión | Impacto | Fix |
|---|---|---|---|---|
| 1 | n8n SQLite single-writer bloquea concurrencia | Escala | Se rompe a >50 conv/día | Migrar n8n → Postgres |
| 2 | Postgres-data sin replicas (SPOF absoluto) | Estab | VPS3 down = ERP/brain caen | Replica streaming + failover docs |
| 3 | wa_messages sin partition/retention | Escala | Crece linealmente sin bound | pg_partman monthly + archive >90d |
| 4 | Templates Meta WhatsApp tardan 48-72h cada vez | Vel | Bloqueador 40-60% campañas <5d | Pre-aprobar pool 15-20 templates ahora |
| 5 | F1/F2/F3 + B3 cron sin distributed lock | Estab+Escala | Overlap → Postgres deadlock | Redis + jitter + SETNX |
| 6 | VPS1 RAM 92% (957MB total) | Estab | OOM inminente bajo pico | Upgrade RAM o swap optimization |
| 7 | Doctora 100% manual responde leads | Auto | ~1-2h/día perdidas | **Yossie v2 ya cubre — VALIDAR fix de hoy en prod** |
| 8 | Setup campaña = 28-35h humanas | Vel | Reduce 3 campañas/mes a 1 | YAML source-of-truth + Marketing API |
| 9 | Sin dashboard real-time campaña | Vel+Auto | Decisiones reactivas vs proactivas | Metabase live (4h build) |
| 10 | CAPI emit sin retry + sin DLQ | Estab | Eventos perdidos silenciosos | Retry exponencial + audit_log |

### 🎯 Recomendación: 3 sprints (~6 semanas) para cerrar backbone

| Sprint | Objetivo | Duración |
|---|---|---|
| **S1 Estabilización** | Top 5 issues críticos resueltos | 2 sem |
| **S2 Cierre Fase 4A** | 4A.4 smoke E2E + 4A.5 email + 4A.6 interludio doctora | 2 sem |
| **S3 Velocidad campaña** | YAML config + templates pre-aprobados + live dashboard | 2 sem |

Tras estos 3 sprints → backbone CERRADO → sesión estratégica agentes IA habilitada.

---

## 1. Metodología

**Inputs:**
- 4 sub-agentes Explore en paralelo (35 min total), uno por dimensión, con prompts específicos
- Lectura cross-cutting: estado real producción vs docs (algunos docs estaban desactualizados)
- Verificación SQL en producción VPS3 (DB stats, exec counts) + n8n executions 7d
- Inventario Fase 4A real vs CLAUDE.md
- FASE A previa (fixes wa_messages + q2 parser) ya aplicada y validada E2E

**Outputs originales agentes:** 4 reportes individuales (63 gaps totales).

**Consolidación:** este documento elimina duplicados, corrige stale references, prioriza por bloqueador-de-escala.

---

## 2. Inventario de subsistemas

### Subsistemas operativos (12)

| # | Subsistema | Estado | Notas |
|---|---|---|---|
| 1 | **VPS1 livskin-wp** (WordPress + form + GTM) | 🟡 | RAM 92% crítico |
| 2 | **VPS2 livskin-ops** (n8n + Vtiger + Metabase + analytics PG) | 🟢 | Saludable |
| 3 | **VPS3 livskin-erp** (Flask + Postgres + brain pgvector) | 🟢 | DB 34MB / disk 55% |
| 4 | **n8n workflows** (12 activos) | 🟡 | SQLite limita concurrencia |
| 5 | **Vtiger CRM** (lead lifecycle) | 🟢 | Bidireccional cerrado 2026-05-10 |
| 6 | **ERP Flask** (cliente + transacciones + agenda) | 🟢 | 75% test coverage, agenda ✅ |
| 7 | **Postgres ERP** (livskin_erp) | 🟢 | Funcional, pero SPOF |
| 8 | **WhatsApp Cloud API** (+51947741117) | 🟢 | STANDARD tier, templates 7/8 APPROVED |
| 9 | **Bot Yossie v2** (state machine rule-based) | 🟢 | Productivo, 196 exec/7d, fixes HOY |
| 10 | **Meta Ads + CAPI** | 🟢 | Pixel + CAPI G3 funcionando |
| 11 | **Cloudflare** (DNS + WAF + Email Routing) | 🟢 | Funcional |
| 12 | **Email institucional** (info@livskin.site) | 🟢 | Operacional 2026-05-13 |

### Subsistemas pendientes (4A.X incompletos)

| Item | Estado real (verificado) | Discrepancia con docs |
|---|---|---|
| **4A.1 Módulo Agenda ERP** | ✅ COMPLETO (ADR-0035, deployed) | Coherente |
| **4A.2 WA Cloud API doctora** | ✅ COMPLETO (+51947741117 productivo) | Docs decían "bloqueado por Meta" — superseded |
| **4A.3 Bot-broker rule-based** | ✅ COMPLETO (Yossie v2 + fixes hoy) | Docs decían pendiente — superseded |
| **4A.3 sub Workflow A2** | ✅ COMPLETO (2026-05-10) | Coherente |
| **4A.4 Smoke E2E completo** | ⏳ **PARCIAL** — partes validadas pero NO un solo flow WA→cita→venta→CAPI Purchase | Crítico |
| **4A.5 Email marketing + flujos** | ⏳ **PARCIAL** — institucional ✅, marketing tool + 2 flujos + re-engagement PENDIENTE | — |
| **4A.6 Interludio estratégico doctora** | ⏳ **WORKBOOK READY** — encuentro 3-4h con doctora PENDIENTE | — |

**Conclusión Fase 4A real**: 3 de 6 sub-fases completas, 3 pendientes (4A.4 + 4A.5 + 4A.6).

---

## 3. Matriz dimensión × subsistema

Score 0-10 (10 = excelente, 0 = roto). Vacío = no aplica.

| Subsistema | Estab | Escala | Auto | Vel | Avg |
|---|---|---|---|---|---|
| VPS1 WP | 4 | 5 | 7 | 5 | 5.3 |
| VPS2 Ops | 6 | 4 | — | — | 5.0 |
| VPS3 ERP | 6 | 5 | — | — | 5.5 |
| n8n workflows | 6 | 3 ⚠️ | 5 | 5 | 4.8 |
| Vtiger CRM | 7 | 4 | 6 | 5 | 5.5 |
| ERP Flask | 7 | 5 | 5 | — | 5.7 |
| Postgres ERP | 5 ⚠️ | 4 | — | — | 4.5 |
| WhatsApp Cloud | 6 | 4 | 8 | 3 ⚠️ | 5.3 |
| Bot Yossie v2 | 7 | 5 | 9 | — | 7.0 |
| Meta Ads + CAPI | 6 | 5 | 3 | 4 | 4.5 |
| Cloudflare | 8 | 8 | — | — | 8.0 |
| Email institucional | 9 | 9 | — | — | 9.0 |
| **AVG** | **6.0** | **4.7** | **6.1** | **4.4** | **5.3** |

⚠️ = bottleneck identificado

---

## 4. Gaps consolidados (63 → top 35 únicos)

Notación: `[ID]` `severidad` `título` — `dimensión(es)` afectada(s)

### 4.1 CRÍTICOS — bloquean cierre backbone o causan caída

| ID | Sev | Gap | Dim | Fix |
|---|---|---|---|---|
| C-01 | 🔴 | n8n SQLite single-writer bloquea concurrencia (>50 conv/día) | Escala | Migrar n8n → Postgres existente (~$0) |
| C-02 | 🔴 | Postgres-data SPOF (VPS3 down = ERP + brain + audit caen) | Estab | Streaming replica VPS2 + restore runbook validado |
| C-03 | 🔴 | wa_messages sin partition/retention (crece sin bound) | Escala | pg_partman monthly, archive >90d |
| C-04 | 🔴 | Templates Meta WhatsApp tardan 48-72h cada campaña | Vel | Pre-aprobar pool 15-20 templates genéricos AHORA |
| C-05 | 🔴 | F1/F2/F3 + B3 cron sin distributed lock | Estab+Escala | Redis SETNX + jitter timing |
| C-06 | 🔴 | VPS1 RAM 92% sostenido — OOM inminente | Estab | Upgrade RAM (DO $6→$12/mes) o swap+PHP-FPM tune |
| C-07 | 🔴 | Smoke E2E (lead WA → cita → venta → CAPI Purchase) NO validado en 1 solo flow | Auto+Vel | Ejecutar flow real con cliente de prueba; documentar |
| C-08 | 🔴 | CAPI emit sin retry + sin DLQ (eventos perdidos silenciosos) | Estab | Retry exponencial 3x + audit_log on failure |

### 4.2 ALTOS — degradación severa pero recuperable

| ID | Sev | Gap | Dim | Fix |
|---|---|---|---|---|
| A-01 | 🟠 | Setup campaña = 28-35h humanas (vs 10-15h posible) | Vel | YAML source-of-truth + Marketing API script |
| A-02 | 🟠 | Sin dashboard real-time campaña en vivo | Vel+Auto | Metabase live (4h build, Google Sheets + Meta API daily snapshot) |
| A-03 | 🟠 | Doctora marca asistencia ERP → 2-5min lag Vtiger | Auto | Workflow A2 cron 2min ✅ existe, monitorear drift |
| A-04 | 🟠 | A2 workflow tiene drift (3509 vs ~5040 esperados 7d, ~70% rate) | Auto+Estab | Investigar overlap o queries lentas |
| A-05 | 🟠 | Vtiger session NO cacheada — 8 API calls/cron B3 | Escala | Cache session 5 min, reduce 8 steps → 1-2 |
| A-06 | 🟠 | Postgres connections pool no configurado explícito | Escala | sqlalchemy pool_size=20 + max_overflow=10 |
| A-07 | 🟠 | Vtiger API tokens sin rotación documentada | Estab | Runbook rotación trimestral + audit log entry |
| A-08 | 🟠 | Meta CAPI token sin pre-commit hook (riesgo accidental leak) | Estab | Pre-commit gitleaks + secret scanning CI |
| A-09 | 🟠 | Race condition: 2+ webhooks lead concurrentes → audit posible inconsistencia | Estab | Lock per phone_lead en UPSERT (pg_advisory_lock) |
| A-10 | 🟠 | infra_snapshots crece 22k rows/mes sin retention | Escala | Cron diario: DELETE WHERE ts < NOW() - 90 days |
| A-11 | 🟠 | DR drill cadencia sin enforcement (último drill desconocido) | Estab | Cron semestral + último_validado en sistema-mapa.md |
| A-12 | 🟠 | 4A.5 email marketing tool + flujos + re-engagement queue PENDIENTE | Auto | MailerLite Free + 2 flujos + cron re-engagement |
| A-13 | 🟠 | 4A.6 Interludio doctora encuentro PENDIENTE (workbook listo) | Auto+Vel | Agendar 3-4h con doctora |
| A-14 | 🟠 | Dashboard endpoint `_compute_aging` N+1 queries (loop Python) | Escala | Rewrite con GROUP BY + HAVING en SQL |
| A-15 | 🟠 | Workflow B3 no batch (8 calls Vtiger serial = 200s a 100 leads) | Escala | Parallelize n8n Batch node o promesas |

### 4.3 MEDIOS — mejoras sustanciales pero no bloqueantes

| ID | Sev | Gap | Dim | Fix |
|---|---|---|---|---|
| M-01 | 🟡 | Postgres-analytics password "livskin" literal (deuda técnica) | Estab | Rotar a generated 32-char |
| M-02 | 🟡 | ERP user passwords sin 90d enforcement | Estab | Trigger + reminder cron |
| M-03 | 🟡 | Audit_log sin archive (lineal forever) | Escala | Partition por año + archive >2 años |
| M-04 | 🟡 | API endpoints sin rate limit | Estab | Flask-Limiter + Redis backend |
| M-05 | 🟡 | Cron jobs sin alerting (fail silently) | Estab | Slack webhook on workflow error |
| M-06 | 🟡 | Brand banners reusables pero copies cada vez manual | Vel | Templates copy con placeholders {{TREATMENT}}+{{PAIN}}+{{EMOTION}} |
| M-07 | 🟡 | Landing pages requieren duplicación manual por campaña | Vel | Landing genérica + tweaks config-driven |
| M-08 | 🟡 | Shortcodes campaña generados manualmente (riesgo typos) | Vel | Script generator + validation contra históricos |
| M-09 | 🟡 | Smoke E2E pre-launch manual checklist memorizado | Vel | Playwright script reproducible |
| M-10 | 🟡 | Post-mortem 2-3h sesión manual | Vel+Auto | Script auto-fill §1-6 desde daily-reports.jsonl + tracking-sheet |
| M-11 | 🟡 | Audiencias Custom Meta upload manual UI | Vel | Marketing API batch upload script |
| M-12 | 🟡 | Landing tracking eventos no granulares (scroll, CTA visible) | Vel | Pixel events checkpoint cada 25% + form_viewed |

### 4.4 BAJOS — nice-to-have

| ID | Sev | Gap | Dim | Fix |
|---|---|---|---|---|
| B-01 | 🟢 | Health checks heterogéneos entre VPS | Estab | Uniformizar /api/health en los 3 |
| B-02 | 🟢 | Meta 2FA PIN en .env plaintext | Estab | Mover a Bitwarden (ya está backup) |
| B-03 | 🟢 | Dashboard templates aprobados/PENDING no centralizado | Vel | Script lee Graph API → docs/integrations/whatsapp/status.md |
| B-04 | 🟢 | Vtiger custom fields mapping actualización ad-hoc | Auto | Cron weekly crawl + diff alerts |
| B-05 | 🟢 | Daily campaign report manual screenshot | Vel | Cron extrae Meta API + genera daily-reports/YYYY-MM-DD.md |

---

## 5. Hallazgos cross-cutting (gaps que cruzan dimensiones)

### CC-01: La concurrencia es el bloqueador #1 del backbone
**Gaps relacionados:** C-01 (n8n SQLite), C-05 (sin distributed lock), A-04 (A2 drift), A-09 (race condition webhooks)

**Tesis:** el sistema funciona para 1-5 leads/día concurrentes. A 50+ leads simultáneos (campaña paga real), múltiples puntos fallan en cascada:
- n8n SQLite bloquea writes
- Cron jobs solapan sin distributed lock
- Webhooks múltiples del mismo lead pueden corromper audit_log
- B3 cron tarda más que su intervalo

**Fix integrado:** Adoptar Redis (1 contenedor en VPS2) + migrar n8n a Postgres + implementar SETNX en crons + pg_advisory_lock en endpoints UPSERT. ~12-16h de trabajo, transforma escalabilidad de 3.5 → 7.

### CC-02: La velocidad de campaña depende de assets pre-armados, no de heroics
**Gaps relacionados:** C-04 (templates Meta), A-01 (setup 28-35h), A-02 (sin dashboard live), M-06 (copy manual), M-11 (audiencias manual)

**Tesis:** lanzar campañas rápido NO es problema de Claude o Dario "siendo más rápidos". Es problema de assets pre-armados:
- Templates Meta aprobados → 0h espera (vs 48-72h)
- Copy templates con placeholders → 1h render (vs 6-8h crear)
- Audiencias Custom subidas via API → 5 min (vs 30 min UI)
- Marketing API script → 1 min crear campaign (vs 1.5-2h UI)

**Fix integrado:** "Campaign Launch Kit" pre-armado (templates aprobados + copy library + audience API + Marketing API script). Inversión única ~12h, reduce cada launch de 28-35h a 10-15h.

### CC-03: La estabilidad de credentials es deuda técnica acumulada
**Gaps relacionados:** A-07 (Vtiger sin rotación), A-08 (CAPI sin pre-commit), M-01 (PG-analytics literal), M-02 (ERP users sin 90d), B-02 (Meta 2FA plaintext)

**Tesis:** 5 credenciales NO rotadas + sin enforcement. Si una se filtra (commit accidente, backup leak, ex-developer), el blast radius es enorme.

**Fix integrado:** Política unified rotación 90d + pre-commit gitleaks + Bitwarden enforcement + audit log entry por rotación. ~4h de runbook + tooling.

### CC-04: Observabilidad existe a nivel infraestructura pero NO a nivel negocio
**Gaps relacionados:** A-02 (sin dashboard campaña), M-05 (cron silent fail), M-10 (post-mortem manual), B-05 (daily report manual)

**Tesis:** sabemos cuándo cae un VPS (sensors), pero NO sabemos en tiempo real:
- ¿Cuántos leads recibimos hoy?
- ¿Conversion rate funnel?
- ¿Doctora response time?
- ¿Qué placement convierte mejor RIGHT NOW?

Decisiones de campaña son post-hoc (post-mortem) en lugar de in-flight.

**Fix integrado:** Metabase dashboard "Campaña Live" con 8 tiles auto-refresh. ~6h build. Cuando hay campaña activa, abierto todo el día.

### CC-05: Fase 4A está más avanzada que CLAUDE.md indica
**Verificación real producción 2026-05-27:**
- 4A.1 ✅ Agenda (deployed con feature flag, validar status real)
- 4A.2 ✅ WA Cloud API doctora (productivo +51947741117)
- 4A.3 ✅ Bot Yossie v2 (deployed + 196 exec/7d + fixes hoy)
- 4A.3 sub ✅ Workflow A2
- 4A.4 ⏳ Smoke E2E **NO validado** como flow único
- 4A.5 ⏳ Email institucional ✅ pero marketing+flows NO
- 4A.6 ⏳ Workbook listo, encuentro doctora pendiente

**Acción:** actualizar CLAUDE.md + master plan post-cierre Fase 4A. 3 sub-fases ya pueden marcarse cerradas.

---

## 6. Roadmap de remediación (3 sprints)

### SPRINT 1 — Estabilización backbone (2 semanas, ~40h)

**Objetivo:** resolver top 8 issues críticos. Tras este sprint el sistema soporta 10x volumen sin caer.

**Tareas:**

| # | Tarea | Dim | Horas | Dep |
|---|---|---|---|---|
| 1.1 | Provisionar Redis (1 container VPS2, no pago) | Escala | 1h | - |
| 1.2 | Migrar n8n a Postgres (existente VPS3) | Escala | 4h | 1.1 |
| 1.3 | Implementar SETNX distributed lock en F1/F2/F3/B3 | Estab+Escala | 3h | 1.1 |
| 1.4 | Streaming replica Postgres-data VPS3 → VPS2 | Estab | 4h | - |
| 1.5 | Runbook restore + failover + DR drill ejecutado | Estab | 3h | 1.4 |
| 1.6 | pg_partman wa_messages monthly partitioning | Escala | 2h | - |
| 1.7 | infra_snapshots retention cron (DELETE >90d) | Escala | 1h | - |
| 1.8 | CAPI emit retry exponencial + DLQ | Estab | 3h | - |
| 1.9 | Pre-commit gitleaks + secret scanning CI | Estab | 2h | - |
| 1.10 | Rotación TODAS las credenciales pendientes (Vtiger, PG-analytics, ERP users) | Estab | 3h | - |
| 1.11 | Upgrade VPS1 RAM (DO console click) o swap+PHP-FPM tune | Estab | 2h | - |
| 1.12 | Sumitir batch 15-20 templates Meta WhatsApp ahora | Vel | 1h | - |
| 1.13 | Endpoint pool sizing erp-flask + max_connections PG | Escala | 1h | - |
| 1.14 | Workflow A2 drift investigation + fix | Auto | 2h | - |
| 1.15 | pg_advisory_lock en endpoints UPSERT críticos | Estab | 2h | - |
| 1.16 | Tests + smoke E2E + deploy | Todas | 6h | todas |

**Total: ~40h** (5 días-persona o 2 sem a 4h/día)

**Exit criteria:**
- n8n corriendo en Postgres
- 10 webhooks simultáneos validados sin lock contention
- Postgres-data replica corriendo
- DR drill ejecutado exitosamente
- 15+ templates Meta APPROVED
- Todas las credenciales rotadas
- VPS1 RAM <80% sostenido

### SPRINT 2 — Cierre Fase 4A (2 semanas, ~30-40h)

**Objetivo:** cerrar las 3 sub-fases 4A pendientes.

**Tareas:**

| # | Tarea | Sub-fase | Horas |
|---|---|---|---|
| 2.1 | Smoke E2E completo: lead test WA → bot → cita ERP → asistencia → cliente → venta → CAPI Purchase | 4A.4 | 4h |
| 2.2 | Documentar resultado en `docs/audits/smoke-e2e-2026-XX-XX.md` | 4A.4 | 1h |
| 2.3 | MailerLite Free setup + integración ERP | 4A.5 | 4h |
| 2.4 | Flujo email 1: welcome post-form-submit | 4A.5 | 3h |
| 2.5 | Flujo email 2: post-cita asistida | 4A.5 | 3h |
| 2.6 | Re-engagement queue determinística (cron 60d+ sin actividad) | 4A.5 | 4h |
| 2.7 | Email notifications lead/cliente desde ERP (key events) | 4A.5 | 3h |
| 2.8 | Encuentro Interludio doctora 3-4h (presencial) | 4A.6 | 4h |
| 2.9 | Codificar 12 outputs brand: voice-v1, personas, journey, catálogo, etc. | 4A.6 | 6h |
| 2.10 | Actualizar copy bot Yossie v2 con voice-v1 (no placeholders) | 4A.3 refinement | 4h |
| 2.11 | Actualizar copy email flujos con voice-v1 | 4A.5 refinement | 2h |
| 2.12 | ADRs cierre Fase 4A (1 por sub-fase) | docs | 2h |

**Total: ~40h**

**Exit criteria:**
- Smoke E2E un solo flow WA→cita→venta→CAPI ejecutado y documentado
- 2 flujos email automatizados corriendo
- Re-engagement queue procesando
- Brand voice v1.0 + personas + journey codificados
- Bot Yossie + emails con copy real (no placeholders)
- CLAUDE.md actualizado, 4A.4+4A.5+4A.6 marcados ✅

### SPRINT 3 — Velocidad campaña + observabilidad (2 semanas, ~30h)

**Objetivo:** reducir setup-de-campaña de 28-35h a 10-15h. Dashboard live.

**Tareas:**

| # | Tarea | Dim | Horas |
|---|---|---|---|
| 3.1 | YAML source-of-truth `campaign.yml` schema + parser | Vel | 4h |
| 3.2 | Marketing API script `meta_deploy_campaign.py` (campaign + ad sets + ads desde YAML) | Vel | 6h |
| 3.3 | Copy templates library con placeholders por treatment+pain+emotion | Vel | 4h |
| 3.4 | Shortcode generator script + validation | Vel | 1h |
| 3.5 | Audience Custom upload API script | Vel | 2h |
| 3.6 | Metabase dashboard "Campaña Live" (8 tiles auto-refresh) | Vel+Auto | 6h |
| 3.7 | Daily snapshot JSON cron (Meta API + Google Sheets) | Vel+Auto | 3h |
| 3.8 | Post-mortem auto-fill script (§1-6 desde daily-reports) | Vel+Auto | 2h |
| 3.9 | Slack alerting cron job failures | Auto | 2h |
| 3.10 | Landing genérica + tweaks config-driven | Vel | (DEFERIDO post-sprint) |

**Total: ~30h**

**Exit criteria:**
- Campaña 3 lanzada en <15h humanas (vs 28-35h de campaña 2)
- Dashboard live operacional durante campaña
- Post-mortem 50% auto-generado
- 1 alert Slack disparada en cron failure (test)

---

## 7. Decisiones requeridas del usuario

Antes de arrancar Sprint 1, tomar decisiones:

| # | Decisión | Opciones |
|---|---|---|
| D1 | ¿Aprobar upgrade VPS1 RAM ($6→$12/mes)? | A) Sí, $6/mes extra · B) Optimizar PHP-FPM + swap (0 costo, +2h trabajo) |
| D2 | ¿Adoptar Redis (1 container VPS2)? | A) Sí, container free · B) Postgres-based queue alternativa |
| D3 | ¿Sprint 1 + 2 + 3 secuenciales o paralelos donde posible? | A) Estricto secuencial (6 sem total) · B) Paralelo donde dependencies permitan (~4 sem) |
| D4 | ¿Cuándo encuentro Interludio doctora? | Agendar fecha específica para Sprint 2 |
| D5 | ¿Aprobar pre-aprobación batch 15-20 templates Meta? | A) Sí, hacer ahora (Sprint 1.12) · B) Postergar a Sprint 2 |
| D6 | ¿Cierre backbone determinístico = trigger formal sesión estratégica agentes IA? | A) Sí, dispara automáticamente al cerrar S3 · B) Decisión separada post-S3 |

---

## 8. Lo que QUEDA explícitamente fuera

Para no contaminar scope:

- ❌ Agentes IA (todo lo de capa LLM) — sesión estratégica DEDICADA post-backbone (doctrina #14)
- ❌ Mejorar conversión campaña — problema de marketing/creative, NO de sistema (separado)
- ❌ Refactor mayor ERP — está funcional, scope creep
- ❌ Migrar de VPS DO a cloud serverless — escala que aún no necesitamos
- ❌ Multi-tenant / múltiples clínicas — out of scope
- ❌ Mobile app — out of scope

---

## 9. Inputs originales (4 reportes agentes)

Cada uno está disponible en `tasks/*.output` jsonl si se necesita auditar. Resumen aquí ya consolida.

- **Estabilidad** (18 gaps, score 5.5/10): énfasis SPOFs, race conditions, credentials rotation
- **Escalabilidad** (12 gaps, score 3.5/10): énfasis n8n SQLite, Postgres pool, wa_messages growth
- **Automatización** (21 gaps, score 4/10): énfasis pasos manuales doctora + ops + onboarding campaña
- **Velocidad campaña** (12 gaps, score 5.5/10): énfasis templates Meta, asset reusability, dashboard live

---

## 10. Próximos pasos inmediatos

1. **Usuario revisa este documento** y responde decisiones §7
2. **Si OK** → arrancar Sprint 1 con tareas 1.1-1.6 en orden
3. **Tras Sprint 1** → checkpoint con scores actualizados
4. **Tras Sprint 3** → cierre formal backbone determinístico → sesión estratégica agentes IA habilitada

---

**Documento cerrado:** 2026-05-27
**Próxima revisión:** post-Sprint 1 (esperado 2026-06-10)
**ADR de cierre backbone:** se escribirá tras Sprint 3 (`docs/decisiones/0037-cierre-backbone-deterministico.md`)
