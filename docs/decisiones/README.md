# Index de Decisiones — Livskin RevOps

Este directorio contiene todos los **Architecture Decision Records (ADRs)** del proyecto. Cada decisión estructural importante se documenta como un ADR separado, inmutable una vez aprobado.

**Formato:** ver [_template.md](_template.md).

---

## Leyenda de estados

| Icono | Estado | Significado |
|---|---|---|
| 🔒 | En revisión | Borrador activo, pendiente de aprobación |
| ✅ | Aprobada | Decisión tomada, en implementación o ya implementada |
| 🔄 | Superseded | Reemplazada por otra ADR |
| 💤 | Diferida | Decisión consciente de posponer |
| ⏳ | Pendiente | Aún no se ha abordado, reserva de número |
| 📝 | Borrador | Trabajando en el contenido |

---

## Índice por workstream

### Arquitectura y datos

| ADR | Título | Estado | Fase |
|---|---|---|---|
| [0001](0001-segundo-cerebro-filosofia-y-alcance.md) | Segundo cerebro — filosofía y 6 capas | ✅ | 0 |
| [0002](0002-arquitectura-de-datos-y-3-vps.md) | Arquitectura de datos (3 VPS, 5 DBs) | ✅ | 0 |
| [0003](0003-seguridad-baseline-y-auditorias.md) | Seguridad baseline y auditorías | ✅ | 0 |
| 0004 | Comunicación entre VPS — DigitalOcean VPC | ✅ **Implementada** 2026-04-19 (VPC 10.114.0.0/20, latencia <2ms verificada) | 1 |
| 0005 | Orquestación agentes — n8n único orquestador + Claude API con tool use (Agent SDK diferido) | ✅ | 4 |
| 0006 | Embeddings — multilingual-e5-small self-hosted | ✅ | 1 |
| 0007 | Observabilidad — Langfuse desde Fase 3 | ✅ | 3 |
| 0008 | Staging environment — mismo VPS 3 con compose separado | ✅ | 1 |
| 0009 | CI/CD — GitHub Actions → SSH → docker compose | ✅ | 1 |
| 0010 | Alembic migrations obligatorias desde día 1 | ✅ | 1 |

### Gobierno de datos

| ADR | Título | Estado | Fase |
|---|---|---|---|
| 0011 | Modelo de datos Lead / Cliente / Venta | ⏳ | 2 |
| 0012 | Pipeline stages en Vtiger | ⏳ | 2 |
| 0013 | Reglas de deduplicación (email + teléfono) | ⏳ | 2 |
| 0014 | Naming conventions (campañas, fuentes, medios) | ⏳ | 2 |
| 0015 | Source of truth por dominio | ✅ | 2 |
| 0016 | Time zones — UTC DB, local UI | ✅ | 0 |
| 0017 | Consent mode Complianz (reject-or-accept MVP) | ⏳ | 3 |
| 0018 | Schema detallado del segundo cerebro | ⏳ | 1 |

### Tracking y atribución

| ADR | Título | Estado | Fase |
|---|---|---|---|
| 0019 | Arquitectura tracking (Meta CAPI + GA4 MP + GTM) | ✅ | 3 |
| 0020 | Modelo de atribución — last-touch para MVP | ✅ | 3 |
| 0021 | UTMs persistence en localStorage | ⏳ | 3 |
| 0022 | Consent mode Complianz | ✅ | 3 |

### ERP

| ADR | Título | Estado | Fase |
|---|---|---|---|
| 0023 | ERP — refactor Flask (no rewrite) | ✅ | 2 |
| 0024 | Migración strangler fig (Render → VPS 3) | ✅ | 2 |
| 0025 | Backfill histórico (74 ventas + 135 clientes) | ⏳ | 2 |
| 0026 | Auth ERP — 2 cuentas fijas sin concurrencia | ✅ | 2 |
| 0027 | Audit log ERP (tabla inmutable) | ✅ | 2 |
| 0028 | Flujo de citas WhatsApp → Vtiger (sin LatePoint) | ✅ | 4 |

### Agentes IA

| ADR | Título | Estado | Fase |
|---|---|---|---|
| 0029 | Conversation Agent — prompts, tools, golden set | ⏳ | 4 |
| 0030 | Content Agent — Creative Factory + Claude Design | ⏳ | 5 |
| 0031 | Acquisition Engine — testing matrix | ⏳ | 5 |
| 0032 | Growth Agent — reporte semanal ejecutivo | ⏳ | 6 |
| 0033 | Escalación a doctora — WhatsApp personal | ✅ | 4 |
| 0034 | Reactivación 45 días v1 | ✅ | 6 |
| 0035 | Lead scoring v1 — rules-based | ✅ | 4 |
| 0036 | Prompt versioning — git + Langfuse | ✅ | 4 |
| 0037 | Embedding model versioning | ✅ | 1 |
| 0038 | WhatsApp test number Meta (sandbox) | ✅ | 0 |

### Observabilidad y calidad

| ADR | Título | Estado | Fase |
|---|---|---|---|
| 0039 | Evals LLM-as-judge con Haiku | ⏳ | 6 |
| 0040 | Cost tracking Claude API | ⏳ | 3 |

### Operativa

| ADR | Título | Estado | Fase |
|---|---|---|---|
| 0041 | Backups escalonados por fase | ✅ | 2 |
| 0042 | ETL schedule (polling 5min + Meta hourly) | ✅ | 4 |
| 0043 | Gestión de secretos — .env.integrations + Bitwarden | ✅ | 0 |
| 0044 | Git workflow — main + feature branches | ✅ | 0 |

### Creatividad

| ADR | Título | Estado | Fase |
|---|---|---|---|
| 0045 | Integración Claude Design + Canva + fal.ai | ⏳ | 5 |
| 0046 | Pipeline landing pages (Claude Design → WP) | ⏳ | 5 |

---

## Diferimentos explícitos

Decisiones conscientes de NO abordar en el MVP. Documentadas para evitar re-apertura inconsciente.

| ADR | Título | Estado | Trigger para reabrir |
|---|---|---|---|
| 0099 | SUNAT / comprobantes electrónicos | 💤 | Cuando se decida formalizar facturación |
| 0100 | IGV inclusive/exclusive | 💤 | Junto con 0099 |
| 0101 | Inventario de productos | 💤 | Si retail se vuelve significativo |
| 0102 | Historial clínico del paciente | 💤 | Post-MVP con la doctora |
| 0103 | PDFs / impresión | 💤 | Si el equipo reporta necesidad |
| 0104 | Offline mode ERP | 💤 | Si cortes de internet reportados frecuentes |
| 0105 | Computer vision clínica (antes/después) | 💤 | Mes 4-6 con volumen de fotos |
| 0106 | Multi-touch attribution | 💤 | Cuando volumen lo justifique |
| 0107 | Fine-tuning modelos propios | 💤 | 10k+ conversaciones históricas |

---

## Cómo proponer una nueva decisión

1. Copia `_template.md` → nuevo archivo con próximo número disponible
2. Completa contexto + opciones + tradeoffs (sin recomendación final aún)
3. Claude Code puede redactar la propuesta pero **la decisión final es de la usuaria**
4. Actualiza este index con la nueva entrada (status 🔒)
5. Discusión en sesión estratégica
6. Al aprobar: status pasa a ✅, se registra fecha y razonamiento en el ADR

## Cómo cambiar una decisión aprobada

**NO editar la ADR original.** Crear nueva ADR que la supersede:
1. Nueva ADR explica el cambio de contexto
2. Lista qué aspectos de la ADR anterior ya no aplican
3. Marca la anterior con 🔄 Superseded por ADR-NNNN
4. El index refleja ambas

---

**Última actualización:** 2026-04-18 (v1.0 — Fase 0)
