# Sesión 2026-04-21 — Fase 2: ADRs de gobierno de datos + refactor conceptual del modelo

**Duración:** ~8 horas (aprox, con pausas)
**Tipo:** estratégica + ejecución (definición intensa de modelo + escritura de 5 ADRs + corrección arquitectónica importante)
**Participantes:** Dario + Claude Code
**Fase del roadmap:** Fase 2 — Gobierno de datos (semanas 3-4) — ARRANCAMOS HOY

---

## Objetivo de la sesión

Iniciar Fase 2 escribiendo los dossiers ADR de gobierno de datos (0011-0014) + cerrar la definición conceptual del modelo de datos que sustenta el ERP refactorizado y el flujo de adquisición digital.

## Principios aplicados durante la sesión

Dario estableció al inicio (importante, guardado en memoria para futuras sesiones):
- **MVP-speed**: producir ADRs en versión mínima viable, no detallados. Iterar después de ver flujos reales. Principio 1 (ejecutable > ideal).
- **Plumbing-first**: ERP refactor primero estructura, después data real. Plumbing listo antes de Fase 3.
- **Frontend preservado**: comerciales mantienen UX actual; todo cambio es backend.
- **Base 100% word-of-mouth**: los 135 clientes existentes nunca tocaron canal digital.
- **Escalable pero no over-engineered**: profesional RevOps sin complejidad innecesaria.

## Trabajo realizado

### Fase 1 de la sesión — ADRs iniciales (v1 MVP)

Escritura de 4 ADRs de gobierno (versión MVP, basados en análisis del Excel + Flask en Render):

- **ADR-0011 v1.0** — Modelo de datos Lead/Cliente/Venta/Pago/Gasto (flat 1-venta-1-item preservando Flask)
- **ADR-0012** — Pipeline stages Vtiger (5 stages simples: nuevo → contactado → agendado → cliente / perdido)
- **ADR-0013 v1.0** — Reglas de deduplicación (jerarquía phone > email > nombre+dob)
- **ADR-0014** — Naming conventions (LIVXXXX####, UTMs, canales)

### Fase 2 de la sesión — correcciones arquitectónicas importantes

Durante la sesión Dario identificó varias inconsistencias que forzaron revisiones:

#### Corrección 1: Timing de cutover (v1.2 master plan)

Originalmente el master plan asumía cutover al final de Fase 2. Dario clarificó:
- VPS 3 permanece en **dormant standby** durante Fases 2-5 con data sintética
- Render sigue siendo producción real sin cambios
- Cutover real ocurre en Fase 6 cuando el sistema completo está validado
- Backfill script debe ser re-runable (sintético en Fase 2-5, real en Fase 6)

**Cambios aplicados**:
- Memoria nueva `project_cutover_strategy.md`
- Master plan § 11.4 re-escrita (Fase 2 exit criteria)
- Master plan § 11.8 (Fase 6 con cutover explícito como hito + 7 pasos operativos)
- Master plan changelog v1.2

#### Corrección 2: Alcance narrow de Vtiger (v1.3 master plan)

Dario clarificó que Vtiger es específicamente para **adquisición digital**, no master de todos los clientes:
- Vtiger = master del **lead digital** solamente
- ERP Postgres = master del **cliente** (incluyendo 135 históricos)
- Doctora's personal WA = out of scope del sistema automatizado
- Número para WA Cloud API = nuevo número dedicado (Opción A)

**Cambios aplicados**:
- 3 memorias nuevas:
  - `project_whatsapp_architecture.md` — Opción A + test→prod timing + handoff mechanics
  - `project_acquisition_flow.md` — 2 canales, scoring v1 rules, handoff, nurture, remarketing
  - `project_vtiger_erp_sot.md` — SoT corregido explícito
- ADR-0013 **reescrita a v2** — identity graph con 2 canales + phone anchor + `lead_touchpoints` + cross-system dedup
- ADR-0011 **actualizada a v1.1** — corrige SoT + agrega columnas scoring/intent/handoff + nuevas tablas
- ADR-0015 **escrita** (era orphan del índice) — oficializa SoT por dominio con tabla canónica 13 dominios + 6 flujos de sync
- CLAUDE.md, README.md, master-plan § 5.2: corrección "Vtiger master identidad cliente" → "Vtiger master del lead digital"
- Master plan changelog v1.3

### Flujo completo de adquisición clarificado

Dario articuló la visión completa end-to-end, que Claude capturó en diagrama:

```
Meta Ads + Google Ads (con tracking completo)
    → Landing pages (una por tratamiento, 5 iniciales: Botox, Esperma de Salmón, PRP, Ác. Hialurónico, Hilos)
        → 2 CTAs: Form submit O Click-to-WhatsApp
            → Ambos convergen en WhatsApp Business Cloud API (número nuevo dedicado)
                → Conversation Agent (Claude en n8n):
                   - Detecta intent + tratamiento
                   - Asigna score 0-100 (rules-based v1)
                   - Categoriza intent: investigando / evaluando / listo_comprar
                   - Si score ≥ 70 → HANDOFF a doctora (WA notif + dashboard badge)
                   - Si < 70 → NURTURE via WA drip + remarketing Google/Meta Ads
                → Cita agendada (Vtiger calendar)
                    → Día de cita: cliente llega (o no_show)
                    → Tratamiento en persona (doctora)
                    → Pago + registro en ERP
                        → ***BRIDGE DIGITAL→FÍSICO***
                        → ERP hace lookup por phone: match Vtiger Lead → convert auto
                        → Meta CAPI Purchase event fires con fbclid original
                        → Attribution loop closes
```

### Scoring v1 rules-based (aprobado)

| Señal | Peso |
|---|---|
| Tiempo respuesta < 1h | +15 |
| Menciona tratamiento específico | +20 |
| Pregunta precio | +15 |
| Pregunta disponibilidad | +20 |
| >3 mensajes | +10 |
| Fuente = Google Search | +10 |
| consent_marketing=true | +5 |
| Edad en rango target | +5 |
| Keywords "mañana/hoy/cita" | +15 |
| Silencio >48h | -15 |
| Objeciones ("caro", "después") | -10 |

Umbrales: ≥70 handoff, 40-69 nurture, <40 frío.

## Decisiones cerradas en sesión

1. **Frontend preservado estricto** — cambios solo en backend
2. **Flat 1-venta-1-item** — preserva lógica Flask, no normalizar en MVP
3. **Phone E.164 como anchor universal** para dedup cross-channel y cross-system
4. **5 landings iniciales** (una por tratamiento top-revenue)
5. **Nurture = WhatsApp drip**, NO email marketing en MVP
6. **Remarketing = Google Ads Customer Match + Meta Custom Audiences**
7. **Handoff = WA notif + dashboard badge** (combinación)
8. **Opción A WhatsApp**: número nuevo dedicado para Cloud API, doctora conserva su número
9. **Test number en Fases 2-5, producción en Fase 6 cutover**
10. **SoT: Vtiger=lead digital only, ERP=cliente + transacciones, Brain=conocimiento**
11. **Landings pages con 2 CTAs obligatorios** (form + WA button)
12. **Los 135 clientes históricos** nunca entran a Vtiger — se quedan en ERP con `fuente='organico'`

## Estado del repo al cierre

### Archivos nuevos creados (ADRs)

- `docs/decisiones/0011-modelo-de-datos-lead-cliente-venta.md` (v1.1, ~11KB)
- `docs/decisiones/0012-pipeline-stages-vtiger.md` (v1.0, ~5KB)
- `docs/decisiones/0013-reglas-de-deduplicacion.md` (v2.0, ~10KB — reemplaza v1.0 de la misma sesión)
- `docs/decisiones/0014-naming-conventions.md` (v1.0, ~5KB)
- `docs/decisiones/0015-source-of-truth-por-dominio.md` (v1.0, ~8KB — era orphan, ahora escrita)

### Archivos modificados

- `CLAUDE.md` (stack table: Vtiger scope fix)
- `README.md` (stack table: Vtiger scope fix)
- `docs/decisiones/README.md` (0011-0014 marked ✅)
- `docs/master-plan-mvp-livskin.md` (§ 5.2 Vtiger scope, § 11.4 Fase 2 re-encuadrada, § 11.8 Fase 6 cutover explícito, changelogs v1.2 + v1.3)

### Memorias Claude Code nuevas (en `~/.claude/projects/.../memory/`)

- `project_cutover_strategy.md` — timing del cutover
- `project_whatsapp_architecture.md` — Opción A + handoff + timing
- `project_acquisition_flow.md` — flujo completo end-to-end
- `project_vtiger_erp_sot.md` — SoT corregido
- `project_erp_migration.md` — principios de migración (frontend preservado, base word-of-mouth, profesional RevOps escalable)
- `MEMORY.md` índice actualizado

## Lo que quedó pendiente para mañana

### ADRs "huérfanos" del índice que hay que escribir (marcados ✅ sin archivo)

Prioridad para cerrar definición completa de Fase 2:

1. **ADR-0023** — ERP refactor Flask (estrategia de refactor, SQLAlchemy + Pydantic + service layer + tests)
2. **ADR-0024** — Strangler fig (ahora "clone + parallel standby + cutover on-demand" tras clarificación de timing)
3. **ADR-0025** — Backfill re-runable (modo sintético para Fases 2-5, modo real pull desde Sheets live en cutover)
4. **ADR-0026** — Auth 2 cuentas bcrypt (Dario + doctora)
5. **ADR-0027** — Audit log inmutable (tabla append-only)

Estimado: 1.5-2h en total a MVP-speed.

### Después de esos 5 ADRs

Arranque de implementación Fase 2 en código:
- Alembic `alembic-erp/versions/0001_initial_schema.py` (crea 9 tablas del ADR-0011 v1.1)
- Refactor del Flask `app.py` a SQLAlchemy + Pydantic + service layer
- Endpoint `/api/client-lookup?phone=X` (crítico para bridge digital→físico)
- Tests (pytest, cobertura ≥70% lógica de negocio)
- Deploy a VPS 3 en dormant standby

## Próxima sesión (mañana)

Orden propuesto:
1. Yo leo CLAUDE.md + memoria + backlog + este session log al arrancar
2. Te propongo: "Arrancamos con los 5 ADRs huérfanos (0023-0027) — cerramos definición de Fase 2. Después implementación."
3. Escribo los 5 a MVP-speed (~30-45 min cada uno)
4. Commit final de gobierno de datos completo
5. Si queda energía, empezamos `alembic-erp/versions/0001_initial_schema.py`

## Estadísticas de la sesión

- **~8 horas** trabajadas (con pausas)
- **5 ADRs** escritos (4 v1 + 1 rewrite v2 + 1 orphan cerrada)
- **5 memorias nuevas** creadas para persistencia
- **3 docs raíz actualizados** (CLAUDE.md, README.md, master-plan)
- **2 correcciones arquitectónicas** importantes aplicadas (cutover timing + Vtiger scope)
- **~15 decisiones estructurales** cerradas
- **0 líneas de código** (esta fue sesión 100% de definición; implementación mañana)

---

**Firma del log:** Claude Code + Dario · 2026-04-21

**Estado cierre**: Fase 2 arrancada, 4/9 ADRs de Fase 2 completos (0011 v1.1, 0012, 0013 v2, 0014) + 1 fundacional aprovechada (0015). 5 ADRs huérfanos para mañana (0023-0027).
