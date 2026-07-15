# Index de Decisiones — Livskin RevOps

Este directorio contiene todos los **Architecture Decision Records (ADRs)** del proyecto. Cada decisión estructural importante se documenta como un ADR separado, inmutable una vez aprobado.

**Formato:** ver [_template.md](_template.md).

---

## Leyenda de estados

| Icono | Estado | Significado |
|---|---|---|
| 🔒 | En revisión | Borrador activo, pendiente de aprobación |
| ✅ | Aprobada | Decisión tomada, en implementación o ya implementada |
| 🔄 | Superseded | Reemplazada por otra ADR (ver "supersedida por…") |
| 💤 | Diferida | Decisión consciente de posponer |
| ⏳ | Pendiente | Aún no se ha abordado, reserva de número |
| 📝 | Borrador | Trabajando en el contenido |

---

## ⚠️ Importante (auditoría 2026-05-03 + actualización 2026-05-10)

Este index fue **reescrito el 2026-05-03** tras auditoría integral del proyecto + **actualizado el 2026-05-10** tras ADRs nuevos + cambio de status ADR-0034. La versión legacy listaba ~50 ADRs ✅ pero solo existían 20 archivos físicos — el resto eran números reservados con metadata "✅" engañosa.

Notas históricas relevantes:

- **Conflicto de numeración 0033 / 0034**: el index legacy reservaba 0033 = "Escalación a doctora WhatsApp" y 0034 = "Reactivación 45 días". Ambos números fueron **reasignados** a archivos nuevos durante mayo 2026 (match auto + Conversation Agent IA). Las decisiones legacy reservadas tomarán números futuros (≥0040) cuando se materialicen como archivos físicos.

- **ADRs entre 0004-0010, 0016-0018, 0020, 0022, 0028-0029, 0037-0044** estaban en el index legacy como ✅ pero NO existen como archivo. Si alguna decisión necesita ser ADR formal, se reservará número en el momento de escribir.

- **2026-05-09**: agregado ADR-0035 (Módulo Agenda Mínima ERP) tras implementación Fase 4A.1.
- **2026-05-10**: agregado ADR-0036 (Workflow A2 sync ERP→Vtiger). Status ADR-0034 cambió `💤 Diferida` → `🔄 Supersedida` por doctrina #14 nueva.
- **2026-05-28**: agregados ADR-0037 (Distributed locks Redis SETNX), ADR-0038 (PG streaming replica VPS3→VPS2), ADR-0039 (n8n SQLite→PG migration) — documentación retroactiva de Sprint 1 estabilización backbone (commits `e7a3118`, `488493e`, `4a70211`, `e1faffa`).

---

## ADRs físicos verificados (25 archivos al 2026-05-28)

### Arquitectura y datos (Fase 0-1)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0001](0001-segundo-cerebro-filosofia-y-alcance.md) | Segundo cerebro — filosofía y 6 capas | ✅ | 0 |
| [0002](0002-arquitectura-de-datos-y-3-vps.md) | Arquitectura de datos (3 VPS, 5 DBs) | ✅ | 0 |
| [0003](0003-seguridad-baseline-y-auditorias.md) | Seguridad baseline y auditorías | ✅ | 0 |

### Gobierno de datos (Fase 2)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0011](0011-modelo-de-datos-lead-cliente-venta.md) | Modelo de datos Lead / Cliente / Venta / Pago / Gasto (v1.1) | ✅ | 2 |
| [0012](0012-pipeline-stages-vtiger.md) | Pipeline stages en Vtiger | ✅ | 2 |
| [0013](0013-reglas-de-deduplicacion.md) | Dedup phone anchor + lead_touchpoints + cross-system (v2) | ✅ | 2 |
| [0014](0014-naming-conventions.md) | Naming conventions (códigos, fuentes, UTMs) | ✅ | 2 |
| [0015](0015-source-of-truth-por-dominio.md) | Source of truth por dominio | ✅ | 2 |

### ERP refactor (Fase 2)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0023](0023-erp-refactor-flask-strategy.md) | ERP refactor Flask — estrategia modernización | ✅ | 2 |
| [0024](0024-strangler-fig-render-vps3.md) | Strangler fig (clone + 60d cold standby + cutover on-demand) | ✅ | 2 |
| [0025](0025-backfill-script-rerunable.md) | Backfill script re-ejecutable (Excel/Sheets → Postgres) | ✅ | 2 |
| [0026](0026-auth-bcrypt-2-cuentas.md) | Auth bcrypt + 2 cuentas con roles | ✅ | 2 |
| [0027](0027-audit-log-inmutable.md) | Audit log inmutable (56 eventos canónicos al 2026-05-03) | ✅ | 2 |

### Tracking + atribución (Fase 3)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0019](0019-arquitectura-tracking-2-capas-pixel-capi.md) | Arquitectura tracking 2-capas (GTM client-side + CAPI server-side via n8n) | ✅ | 3 |
| [0021](0021-utms-persistence-y-tracking-engine-client-side.md) | UTMs persistence en localStorage + Tracking Engine | ✅ | 3 |

### Adquisición y landings (Fase 3)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0030](0030-file-naming-conventions-repo.md) | File naming conventions del repo | ✅ | 0 |
| [0031](0031-landings-dedicadas-cloudflare-pages-y-sistema-convenciones.md) | Landings dedicadas Cloudflare Pages + sistema convenciones HTML | ✅ | 3 |
| [0032](0032-metabase-warehouse-architecture-y-etl-strategy.md) | Metabase warehouse architecture + ETL strategy via n8n | ✅ | 3 |

### Datos cross-system (Fase 3 puente)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0033](0033-auto-match-lead-cliente.md) | Match automático lead↔cliente al crear cliente en ERP | ✅ | 3 puente |

### Módulo Agenda + sync bidireccional ERP↔Vtiger (Fase 4A)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0035](0035-modulo-agenda-minima-erp.md) | Módulo Agenda Mínima ERP | ✅ | 4A.1 |
| [0036](0036-workflow-a2-sync-erp-vtiger.md) | Workflow [A2] sync ERP→Vtiger (cierra bidireccional lead lifecycle) | ✅ | 4A.3 (sub) |

### Sprint 1 estabilización backbone (post Fase 4A)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0037](0037-distributed-locks-redis-setnx.md) | Distributed locks Redis SETNX para crons n8n (F1/F2/F3/B3) | ✅ | Sprint 1.3 |
| [0038](0038-postgres-streaming-replica-vps2.md) | Postgres streaming replica VPS3→VPS2 (failover manual) | ✅ | Sprint 1.4 |
| [0039](0039-n8n-backend-postgres-migration.md) | Migración n8n SQLite → Postgres backend | ✅ | Sprint 1.2 |

### Operación continua (post-bootstrap)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0040](0040-correccion-controlada-registros-erp.md) | Corrección controlada de registros ERP (campos no-monetarios + audit trail) + guard CAPI backfill | ✅ | Post-bootstrap |

### Agentes IA — supersedida por doctrina #14 (2026-05-10)

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0034](0034-conversation-agent-foundation.md) | Conversation Agent IA Foundation | 🔄 **Supersedida** (linaje: ✅ 2026-05-02 → 💤 2026-05-03 → 🔄 2026-05-10) | 4 (orig) |

> **Nota sobre ADR-0034 — linaje completo**:
> 1. **2026-05-02**: ✅ Aprobada (escrita Claude, decisión Dario)
> 2. **2026-05-03**: 💤 Diferida tras audit honesto (memoria 🔥 `project_agent_scope_audit_2026_05_03.md` + audit `docs/audits/agent-scope-audit-2026-05-03.md`). Conversation Agent IA reducido a "diferir hasta validación con data real".
> 3. **2026-05-10**: 🔄 Supersedida por **Principio Operativo #14** + memoria `feedback_sesion_estrategica_agentes_dedicada.md` (Dario clarificó que V1 NO será LLM monolítico — V1 es **chatbot rule-based** de Fase 4A.3). Razón del cambio: "Diferida" implicaba pause de la decisión IA monolítica; "Supersedida" refleja la realidad de cambio de arquitectura.
>
> **Será reemplazada por ADR-0037 "Conversation Agent v0 rule-based"** cuando se construya formalmente en la sesión estratégica de agentes IA (post-backbone cerrado per principio #14). Conversation Agent IA real reabriría SOLO si volumen WhatsApp >100 conv/día sostenido por 7+ días.

---

## ADRs reservados pero NO escritos (decisiones futuras)

Estas son decisiones que el proyecto va a necesitar formalizar cuando lleguen. **No tienen archivo todavía** y **el número se asigna al escribir, no al reservar** — para evitar conflictos como 0033/0034.

| Concepto | Cuándo se materializa | Notas (post-doctrina #14) |
|---|---|---|
| **Conversation Agent v0 rule-based** | Sesión estratégica agentes IA post-backbone cerrado | Supersede ADR-0034. Documenta arquitectura formal del rule-based de Fase 4A.3. Número se asigna al escribir (≥0040) |
| **Brand Orchestrator V0 BOOTSTRAP** | Si excepción Brand Orchestrator V0 BOOTSTRAP se ejecutó durante backbone | Documenta lecciones aprendidas + scope refinado + herramientas validadas |
| **Brand Orchestrator V1 multi-agent** | Sesión estratégica agentes IA post-backbone | 5 subagentes formal (research/concept/copy/visual/implementation) |
| ADR Acquisition synthesizer script | Sesión estratégica agentes IA | Script con LLM ocasional, NO agente formal |
| ADR Growth narrative script | Sesión estratégica agentes IA | Script con LLM mensual |
| ADR Infra+Security agent | Sesión estratégica agentes IA — timing construcción Fase 7 | Diferido — skills cubren V1 |
| ADR VPS dedicado agentes (`agents.livskin.site`) | Sesión estratégica agentes IA | Decisión arquitectónica formal |
| Cutover ERP Render → VPS 3 | Fase 6 | |
| Reactivación 45 días post-visita | Fase 6+ post-cutover | |
| Lead scoring v1 rules-based | Fase 4A o 4B según necesidad | |
| Re-introducir staging real (DB separada) | Fase 6 al cutover Render→VPS3 | Supersede Opción A erp-staging eliminado |

---

## Diferimentos explícitos del MVP

Decisiones conscientes de NO abordar en el MVP. Documentadas para evitar re-apertura inconsciente. **Sin número asignado** hasta que se materialicen.

| Concepto | Trigger para reabrir |
|---|---|
| SUNAT / comprobantes electrónicos | Cuando se decida formalizar facturación |
| IGV inclusive/exclusive | Junto con SUNAT |
| Inventario de productos | Si retail se vuelve significativo |
| Historial clínico del paciente | Post-MVP con la doctora |
| PDFs / impresión | Si el equipo reporta necesidad |
| Offline mode ERP | Si cortes de internet reportados frecuentes |
| Computer vision clínica (antes/después) | Mes 4-6 con volumen de fotos |
| Multi-touch attribution | Cuando volumen lo justifique |
| Fine-tuning modelos propios | 10k+ conversaciones históricas |
| Conversation Agent IA monolítico (post-diferimiento ADR-0034) | Volumen WhatsApp >100 conv/día sostenido |

---

## Cómo proponer una nueva decisión

1. **NO reservar número anticipadamente.** Asignar en el momento de escribir.
2. Copia `_template.md` → nuevo archivo con el siguiente número físico libre (verificar con `ls *.md | sort` o glob `0*.md`).
3. Completa contexto + opciones + tradeoffs (sin recomendación final aún).
4. Claude Code puede redactar la propuesta pero **la decisión final es de la usuaria**.
5. Actualiza este index con la nueva entrada.
6. Discusión en sesión.
7. Al aprobar: status pasa a ✅, se registra fecha y razonamiento en el ADR.

## Cómo cambiar una decisión aprobada

**NO editar la ADR original.** Crear nueva ADR que la supersede:

1. Nueva ADR explica el cambio de contexto.
2. Lista qué aspectos de la ADR anterior ya no aplican.
3. Marca la anterior con 🔄 Superseded por ADR-NNNN (con header explícito en el archivo).
4. El index refleja ambas (con nota cruzada).

---

## Estadísticas (al 2026-05-28)

- **26 ADRs físicos** verificados (físicamente como archivo `.md`)
- **23 ADRs ✅ aprobadas** (operativas)
- **0 ADRs 💤 diferidas** (0034 ya pasó a 🔄 Supersedida 2026-05-10)
- **1 ADR 🔄 supersedida** (0034 por doctrina #14)
- **1 conflicto de numeración histórico** documentado (0033/0034 vs index legacy)
- **0 ADRs 🔒 en revisión** activos
- **3 ADRs documentación retroactiva Sprint 1** (0037, 0038, 0039 — implementados 2026-05-28, ADRs escritos misma sesión)
- **~30 ADRs fantasma** removidos del index legacy (eran números con metadata ✅ pero sin archivo)

---

**Última actualización:** 2026-07-15 (ADR-0040 corrección controlada registros ERP + guard CAPI backfill)
