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

## ⚠️ Importante (auditoría 2026-05-03)

Este index fue **reescrito el 2026-05-03** tras auditoría integral del proyecto. La versión legacy listaba ~50 ADRs ✅ pero solo existían **20 archivos físicos** — el resto eran números reservados con metadata "✅" engañosa. Removidos.

Notas históricas relevantes:

- **Conflicto de numeración 0033 / 0034**: el index legacy reservaba 0033 = "Escalación a doctora WhatsApp" y 0034 = "Reactivación 45 días". Ambos números fueron **reasignados** a archivos nuevos durante mayo 2026 (match auto + Conversation Agent IA). Las decisiones legacy reservadas tomarán números futuros (≥0035) cuando se materialicen como archivos físicos.

- **ADRs entre 0004-0010, 0016-0018, 0020, 0022, 0028-0029, 0035-0044** estaban en el index legacy como ✅ pero NO existen como archivo. Si alguna decisión necesita ser ADR formal, se reservará número en el momento de escribir.

---

## ADRs físicos verificados (20 archivos al 2026-05-03)

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

### Agentes IA — diferida por audit 2026-05-03

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0034](0034-conversation-agent-foundation.md) | Conversation Agent IA Foundation | 💤 **Diferida** (audit 2026-05-03) | 4 (orig) |

> **Nota sobre ADR-0034**: aprobada el 2026-05-02, diferida al día siguiente tras audit honesto del scope de agentes (memoria 🔥 CRÍTICA `project_agent_scope_audit_2026_05_03.md` + audit formal `docs/audits/agent-scope-audit-2026-05-03.md`). V1 será chatbot rule-based + handoff humano + templates Meta-approved (Fase 4A). Esta ADR será **supersedida** por ADR futura "Conversation Agent v0 rule-based" cuando se construya.

---

## ADRs reservados pero NO escritos (decisiones futuras)

Estas son decisiones que el proyecto va a necesitar formalizar cuando lleguen. **No tienen archivo todavía** y **el número se asigna al escribir, no al reservar** — para evitar conflictos como 0033/0034.

| Concepto | Cuándo se materializa |
|---|---|
| Conversation Agent v0 rule-based | Fase 4A (post-Bridge Episode + módulo Agenda) — supersede ADR-0034 |
| Módulo Agenda mínimo en ERP | Fase 4A (Bloque puente operacional) |
| VPS dedicado de agentes (`agents.livskin.site`) | Fase 4B (cuando se construya Brand Orchestrator) |
| Brand Orchestrator multi-agent (5 subagentes) | Fase 4B post-validación + brand voice consolidado |
| Acquisition synthesizer (script LLM ocasional) | Fase 5 — script con LLM, NO agente formal |
| Growth narrative (script LLM mensual) | Fase 5 — script |
| Cutover ERP Render → VPS 3 | Fase 6 |
| Reactivación 45 días post-visita | Fase 6+ post-cutover |
| Escalación handoff doctora WhatsApp | cuando se construya Conversation Agent v0 |
| Lead scoring v1 rules-based | Fase 4A o 4B según necesidad observada en datos del Bridge Episode |
| Re-introducir staging real (DB separada) | Fase 6 al cutover Render→VPS3 — supersede la Opción A actual de erp-staging eliminado |

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

## Estadísticas (al 2026-05-03)

- **20 ADRs físicos** verificados (físicamente como archivo `.md`)
- **18 ADRs ✅ aprobadas** (operativas)
- **1 ADR 💤 diferida** (0034)
- **1 conflicto de numeración histórico** documentado (0033/0034 vs index legacy)
- **0 ADRs 🔒 en revisión** activos
- **0 ADRs 🔄 superseded** todavía (esperado: 0034 será superseded por ADR Conversation Agent v0)
- **~30 ADRs fantasma** removidos del index legacy (eran números con metadata ✅ pero sin archivo)

---

**Última actualización:** 2026-05-03 (auditoría integral — index reescrito desde verificación física de archivos)
