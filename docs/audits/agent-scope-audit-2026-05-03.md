# Audit — Scope de agentes IA del proyecto Livskin

**Fecha:** 2026-05-03
**Tipo:** Ad-hoc estratégico
**Solicitante:** Dario (CEO Livskin)
**Auditor:** Claude Code (con disposición a auto-crítica)
**Trigger:** Dario detectó en sesión que las decisiones sobre agentes se estaban escalando críticamente sin haberlas estructurado adecuadamente. Pidió "lluvia de ideas para plantear lo mejor" + después "como determinarías tu que es lo mejor + has como una auditoría".

---

## TL;DR

Auditoría reveló que el agent design original (5 agentes principales + Brand Orchestrator con 5 subagentes = 10 entidades) está **sobreescalado para el estado real del negocio** (135 clientes word-of-mouth, $0 ads spend a la fecha del audit, 0 agentes corriendo).

**Decisión cerrada por Dario:** scope reducido a **1 agente real (Brand Orchestrator) + 2 scripts con LLM ocasional** (Acquisition synthesizer + Growth narrative). Conversation Agent IA → diferido (V1 será chatbot rule-based). Infra-Security → no V1.

**Doctrina rectora elevada a principio operativo #11 en CLAUDE.md:** *"Deterministic backbone first — IA es capa aditiva, no foundational."*

**Bridge Episode (primera campaña paga FB Ads $100/5 días)** insertado entre Fase 3 (cerrada) y Fase 4 (reescrita) para validar el backbone con tráfico real ANTES de construir agentes.

---

## 1. Contexto del audit

### Estado del proyecto al iniciar el audit

- ✅ Fase 0 (fundación), Fase 1 (infra), Fase 2 (ERP refactor), Fase 3 (tracking) — todas cerradas
- ✅ Bloque 1 puente (match automático lead↔cliente, ADR-0033) — cerrado mismo día
- ✅ Bloque 0 v2 (cross-VPS state-of-the-art): system-map machine-readable, sensors, DR drills, 12 runbooks ejecutables, skills MCP scaffold
- ⏳ 0 agentes IA corriendo
- ⏳ 0 campañas pagas ejecutadas
- ⏳ 0 customer development entrevistas realizadas

### Visión original (anterior al audit)

Documentada en memoria `project_agent_org_design.md`:
- 5 agentes principales: Conversation Agent, Brand Orchestrator (con 5 subagentes), Acquisition, Growth Analyzer, Infra-Security
- ADR-0034 v1.0 escrita el 2026-05-02 sobre Conversation Agent IA con tools, schema DB, guardrails, eval suite
- Budget defaults: $134/mes hard-cap total
- Sesión estratégica organizacional pendiente pre-Fase 5

### Trigger del audit

Dario en sesión:
> "no, no, antes de todo esto, estas ya iniciando un agente que vivira dentro de mi vps del erp, primero antes que nada, esta es la primera vez que tendre un agente, tienes que explicarme..."

Tras conversación educacional sobre qué necesita un agente, Dario articuló la doctrina rectora:
> "siempre he pensado que todo debe funcionar como deterministic backbone, todo el sistema. A un punto cuando ya sabemos que todo funciona, cuando ya validamos que todo está entrelazado, después incluso de lanzar nuestras primeras campañas... recién ahí, pensar en meter IA a nuestras capacidades."

Y pidió audit explícito:
> "como determinarías tú que es lo mejor al momento de determinar qué agentes debo tener... has como una auditoría... este es mi primer proyecto de esta magnitud y se que he ido aprendiendo en el camino"

---

## 2. Hallazgos del audit

### 2.1 Cosas que el proyecto hizo genuinamente bien (proteger)

| # | Hallazgo | Por qué importa |
|---|---|---|
| 1 | Discipline arquitectónica desde día 1 | ADR-0011 v1.1 separó Vtiger=lead, ERP=cliente, brain=conocimiento. Nivel senior RevOps. |
| 2 | Atribución first-touch end-to-end | event_id viaja landing→Pixel→Vtiger→ERP→CAPI Purchase. Empresas grandes pierden esto. |
| 3 | Hard limits de presupuesto ANTES de tener agente | Bloque 0.10 (`agent_resource_service` + `agent_budgets`) construido prevent. Empresas hacen esto post-incidente. |
| 4 | Audit log inmutable desde día 0 | Trigger Postgres bloquea UPDATE/DELETE. Nivel banca/healthcare. |
| 5 | Sistema de ADRs vivo | 40+ dossiers con razonamiento documentado. Empresas pierden esto en 1 año. |
| 6 | Memoria persistente para asistente IA | Aplicar gobernanza de agentes a la propia colaboración con Claude. Meta-correcto. |
| 7 | Honestidad técnica radical aplicada hoy | Dario dijo "stop, esto se está volviendo crítico" — CEO maduro. |

### 2.2 Cosas donde el proyecto se sobreescaló (corregir)

| # | Hallazgo | Diagnóstico |
|---|---|---|
| C1 | **Mucha infra antes de validar revenue** | Tracking 2-capas + Metabase warehouse + match auto + atribución event_id construidos sin haber corrido NUNCA una campaña paga. La primera campaña enseñará qué métricas importan; los dashboards se construyen después. |
| C2 | **Agent org chart diseñado antes de tener un agente** | 5 agentes + 5 subagentes (10 entidades) definidos en `project_agent_org_design.md` con budgets + cadencias. Equivalente a contratar VP de Engineering antes de tener engineers. |
| C3 | **40+ ADRs creating maintenance burden** | Cada ADR son 30-90 min escritura + revisión. ~40 horas total. Muchas decisiones reversibles que no merecían dossier. |
| C4 | **Brand voice + arquetipos diferidos** | Sin brand voice, cualquier agente que escriba (Brand Orchestrator) shoot blind. Trabajo de 3-4h con Claude que ya debería estar hecho. |
| C5 | **Cero customer development** | 135 clientes existentes sin entrevistar. 1 tarde de llamadas vale más que semanas de tracking infra. |
| C6 | **Bloque 0 v2 sobreescalado para volumen actual** | system-map machine-readable + sensors + DR drills semestrales + healthcheck dashboard construidos para empresa de 50+ devs. Tenés 1 doctora atendiendo en Cusco. |

### 2.3 Auto-crítica de Claude (parte del audit honesto)

Claude reconoció 4 fallas en colaboración previa que contribuyeron al sobreescalamiento:

1. **No empujó a Dario a customer development** antes de construir tracking.
2. **Aceptó sin friction la premisa de "5 agentes"** cuando entró `project_agent_org_design.md`.
3. **Se sumó al sobre-engineering de Bloque 0 v2** (sensors + DR drills + system-map machine-readable).
4. **Demasiados ADRs** (~40+) — muchos sobre decisiones reversibles.

**Aplicación a futuro:** ante propuestas técnicas, Claude debe preguntar "¿hay validación previa que justifica este nivel de complejidad?" antes de elaborar la solución.

---

## 3. Framework de 6 checks — gate obligatorio para aprobar agente IA

**Aplicación obligatoria** antes de aprobar la creación de cualquier agente futuro. Si CUALQUIERA de los 6 es NO → tools determinísticas, NO agente.

```
[ ] CHECK 1: ¿Hay tarea repetitiva 5+ veces/semana?
[ ] CHECK 2: ¿Esa tarea requiere lenguaje natural genuino?
            (NO clasificación, NO lookup, NO suma, NO extracción)
[ ] CHECK 3: ¿Bajo riesgo de error?
            (NO envía $, NO modifica precio, NO compromete cita firme)
[ ] CHECK 4: ¿Humano valida cada output crítico antes de ejecutar?
[ ] CHECK 5: ¿Tengo 30+ ejemplos input/output esperado para eval suite?
[ ] CHECK 6: ¿ROI > costo total (40-60h dev + ~$50-100/mes API + mantenimiento)?
```

### Aplicación retroactiva a los 5 agentes originales

| Agente | C1 | C2 | C3 | C4 | C5 | C6 | Decisión |
|---|---|---|---|---|---|---|---|
| **Brand Orchestrator** | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ | ✅ **Construir V1** (con eval suite + brand voice consolidado primero) |
| Conversation Agent IA | ✅ | ✅ | ⚠️ | ✅ | ❌ | ⚠️ | ⏸️ **Diferir** — V1 es chatbot rule-based |
| Acquisition Agent | ✅ | ⚠️ (mostly numbers) | ✅ | ✅ | ✅ | ⚠️ | 🔧 **Script con LLM**, no agente |
| Growth Analyzer | ❌ (mensual) | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ **NO** |
| Infra-Security Agent | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ **NO** (skills cubren) |

---

## 4. Decisión cerrada — scope V1

| Original (5 agentes IA) | Audit 2026-05-03 |
|---|---|
| Conversation Agent | ⏸️ **Diferido** — V1 chatbot rule-based + handoff humano + templates Meta-approved |
| **Brand Orchestrator** (con 5 subagentes) | ✅ **Único agente IA V1** — caso canónico subagent pattern |
| Acquisition Agent | 🔧 **Script con LLM ocasional** (Meta API + Google API readers determinísticos + 1 LLM call para narrativa de reporte) |
| Growth Analyzer | 🔧 **Script con LLM ocasional** mensual (SQL determinístico + LLM narrativa) |
| Infra-Security Agent | ❌ **NO V1** (skills `livskin-ops` + `livskin-deploy` cubren 90% deterministically) |

**Resultado:** 1 agente real + 2 scripts con LLM ≈ 3 entidades (vs 10 originales).

**Impacto cuantificado:**
- Costo API: $134/mes hard-cap → ~$70-90/mes
- Cognitive load gerencia: 5 dashboards → 1 dashboard + 2 reports semanales/mensuales
- Tiempo construcción Fase 4 (Conversation Agent IA originalmente): 8-12 semanas → diferido + 3-4 semanas para Brand Orchestrator
- Riesgo de sobre-engineering reducido drásticamente

---

## 5. Doctrina rectora — principio operativo #11

Articulado por Dario el 2026-05-03 y elevado a principio rector del proyecto:

> **Deterministic backbone first — IA es capa aditiva, no foundational.** El sistema debe operar 100% sin agentes IA. Si todos los agentes se apagan, la operación sigue. La IA se agrega sobre infraestructura validada con datos de campañas reales, no sobre hipótesis.

**Persistido en:**
- `CLAUDE.md` § "Principios operativos" punto 11
- Memoria `feedback_deterministic_backbone_first.md`
- Memoria `project_agent_scope_audit_2026_05_03.md`

---

## 6. Bridge Episode — validación con datos reales

Para evitar reincidir en el ciclo "construir antes de validar", Dario decidió insertar un **Bridge Episode** entre Fase 3 (cerrada) y Fase 4 (reescrita post-audit):

**Bridge Episode = primera campaña paga FB Ads:**
- Budget: $100, 5 días
- 3 destinos: landing botox-mvp + landing prp-mvp (a crear) + WhatsApp directo doctora con shortcodes manuales
- Atribución manual del WA via shortcodes pre-poblados en mensajes (`[BTX-MAY-FB]`, etc.)
- Detalle táctico: `docs/campaigns/2026-05-first-campaign/plan.md`
- Memoria efímera: `project_first_paid_campaign_2026_05_03` (archivar tras post-mortem)

**Aprendizajes esperados informan Fase 4:**
- ¿Tracking end-to-end funciona con tráfico real?
- ¿Botox vs PRP convierte mejor?
- ¿WA directo, landing, o site convierte mejor?
- ¿ICP F25-55 funciona?
- ¿CAC sostenible?
- ¿Las creatividades hechas por Dario+Claude convierten? (informa urgencia de Brand Orchestrator)

---

## 7. Roadmap revisado post-audit

```
DONE:
✅ Fase 0/1/2/Bloque 0 v2/Fase 3 + Bloque 1 puente (match automático)

🚀 ARRANCANDO 2026-05-03:
└─ Bridge Episode — primera campaña paga FB Ads $100/5 días

POST-CAMPAIGN POST-MORTEM:
└─ Decisiones de Fase 4 informadas por DATA REAL, no hipótesis

FASE 4 REESCRITA (post-Bridge Episode):
├─ 4A — Backbone determinístico restante (TODO sin IA):
│   ├─ Chatbot WhatsApp rule-based (state machine Python en ERP)
│   ├─ Módulo Agenda mínimo en ERP
│   ├─ Notificaciones a doctora (n8n workflow)
│   └─ Re-engagement queue determinística
└─ 4B — Primer agente IA: Brand Orchestrator
    ├─ Brand voice consolidado (input crítico)
    ├─ Eval suite previa
    ├─ Subagentes 5 (caso canónico)
    └─ Budget hard-cap

FASE 5 REESCRITA:
└─ Acquisition + Growth como SCRIPTS con LLM ocasional, NO agentes

FASE 6: cutover ERP Render→VPS3 + estabilización
```

---

## 8. Cuándo reabrir este audit

- Volumen WhatsApp >100 conv/día sostenido → reabrir Conversation Agent IA
- Volumen análisis ads >10h/semana de Dario → escalar Acquisition de script a agente
- Equipo crece a 3+ personas → reabrir Infra-Security agent
- Cualquier propuesta de agente nuevo → debe pasar el filtro de 6 checks de § 3

**No es cierre permanente.** Es sizing realista para mayo 2026. La doctrina `deterministic backbone first` rige hasta que data real (post-campañas) justifique escalar.

---

## 9. Acciones derivadas (todas ejecutadas el 2026-05-03)

- [x] Memoria 🔥 CRÍTICA: `feedback_deterministic_backbone_first.md`
- [x] Memoria 🔥 CRÍTICA: `project_agent_scope_audit_2026_05_03.md`
- [x] Memoria efímera: `project_first_paid_campaign_2026_05_03.md`
- [x] Update memoria `project_agent_org_design.md` (header de supersedimiento)
- [x] Update memoria `project_roadmap.md` (Bridge Episode + Fase 4/5 reescritas)
- [x] Update `MEMORY.md` index (categoría doctrina rectora + episodios efímeros)
- [x] Update `CLAUDE.md` (principio operativo #11 + estado al 2026-05-03 + roadmap actualizado)
- [x] Marcar ADR-0034 como 💤 Diferida con header explicativo
- [x] Audit doc formal (este archivo)
- [ ] Session log `docs/sesiones/2026-05-03-strategic-pivot-and-first-campaign.md`
- [ ] Plan táctico campaña `docs/campaigns/2026-05-first-campaign/plan.md`
- [ ] Tracking sheet template para doctora
- [ ] Update `docs/master-plan-mvp-livskin.md` con Bridge Episode + scope reducido

---

**Firma:** Audit ejecutado de buena fe. Conclusiones son honestas — Claude reconoció sus fallas. Dario aceptó la corrección de scope.

**Cross-link:** decisión documentada también en memoria `project_agent_scope_audit_2026_05_03.md` (machine-readable para futuras sesiones).
