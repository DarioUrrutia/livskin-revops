# 2026-05-03 — Pivot estratégico + plan primera campaña paga

## Contexto inicial

Sesión arrancó como continuación de Bloque 1 (match automático lead↔cliente) cerrado el 2026-05-02. Plan original: implementar Bloque 2 (Conversation Agent IA con tools, según ADR-0034 v1.0 escrita el día anterior). Dario interrumpió con preocupación legítima: "esta es la primera vez que tendré un agente, tienes que explicarme qué cosas se necesitan, qué infraestructura, cuáles son las opciones, todo esto necesito saber".

Lo que arrancó como educacional terminó siendo el **pivot estratégico más importante del proyecto**.

## Lo que pasó (4 movimientos encadenados)

### Movimiento 1 — Pausa antes de implementar agente

Dario detuvo la implementación inmediata. Pidió comprender qué es un agente, qué necesita, qué opciones de infra hay. Claude respondió con explicación de 7 componentes (modelo, prompt, memoria, tools, guardrails, observabilidad, budget) + 4 paths de infraestructura (in-process / microservicio / SaaS / n8n agent node).

### Movimiento 2 — Articulación de doctrina rectora

Dario respondió:
> "estoy pensando que por el momento necesitamos usar un chatbot para whatsapp, no un de inteligencia artificial, si no más bien uno de esos donde hay ya caminos establecidos de conversación... que tenga también la oportunidad de agendar citas, responder las preguntas principales, enseñar servicios, antes y después"

Después fue más lejos:
> "siempre he pensando que todo debe funcionar como deterministic backbone, todo el sistema. A un punto cuando ya sabemos que todo funciona, cuando ya validamos que todo está entrelazado, después incluso de lanzar nuestras primeras campañas, entender, pulir, refinar, y establecer la estructura total, recién allí, pensar en meter IA a nuestras capacidades."

Esta articulación fue elevada a **principio operativo #11 en CLAUDE.md**: *"Deterministic backbone first — IA es capa aditiva, no foundational."*

### Movimiento 3 — Audit honesto del scope agentes

Dario pidió audit explícito:
> "como determinarías tú que es lo mejor al momento de determinar qué agentes debo tener... has como una auditoría... este es mi primer proyecto de esta magnitud y se que he ido aprendiendo en el camino"

Claude ejecutó audit honesto incluyendo auto-crítica:

**Cosas bien hechas (proteger):**
- Discipline arquitectónica (Vtiger=lead, ERP=cliente, brain=conocimiento)
- Atribución first-touch end-to-end vía event_id
- Hard limits de presupuesto antes de tener agente
- Audit log inmutable desde día 0
- Memoria persistente para asistente IA

**Cosas sobreescaladas (corregir):**
- Mucha infra antes de validar revenue (tracking + warehouse + match auto sin haber corrido NUNCA campaña paga)
- Agent org chart de 5 agentes diseñado antes de tener un agente corriendo
- ~40 ADRs (overhead grande para 1 founder + Claude)
- Brand voice + arquetipos diferidos pero son input crítico de cualquier agente
- Cero customer development (135 clientes existentes sin entrevistar)
- Bloque 0 v2 sobreescalado para volumen actual

**Auto-crítica de Claude:** 4 fallas reconocidas (no empujar customer development, aceptar premisa "5 agentes" sin friction, sumarse al sobre-engineering Bloque 0 v2, demasiados ADRs).

**Framework de 6 checks** definido como gate para aprobar agente futuro:
1. Tarea repetitiva 5+ veces/semana
2. Requiere lenguaje natural genuino (no clasificación/lookup/suma)
3. Bajo riesgo de error
4. Humano valida cada output crítico
5. 30+ ejemplos para eval suite
6. ROI > costo total

**Aplicado retroactivamente:**
| Agente original | Decisión audit |
|---|---|
| Brand Orchestrator | ✅ V1 (caso canónico subagentes) |
| Conversation Agent IA | ⏸️ Diferido — V1 chatbot rule-based |
| Acquisition | 🔧 Script con LLM, no agente |
| Growth Analyzer | ❌ NO V1 |
| Infra-Security | ❌ NO V1 (skills cubren) |

Resultado: 5 agentes → 1 agente real + 2 scripts. Costo $134/mes → ~$70-90/mes.

### Movimiento 4 — Decisión campaña paga manual mañana

Dario decidió:
> "quisiera que mañana armemos una campaña, aunque sea manualmente, para que la lancemos y así tener data de la cual aprender. Como podemos optimizar para tener al menos el chat activo, porque lanzaría campañas que en su mayoría irían a un chat, al número de la doctora..."

Bridge Episode acordado: FB Ads $100/5 días, 3 destinos (landing botox-mvp + landing prp-mvp nueva + WhatsApp directo doctora con shortcodes manuales). Captura data real para informar Fase 4 con datos, no hipótesis.

Dario también pidió organización profunda:
> "esto es como algo que está surgiendo en medio, no puedes perder la hilación o empezar a alucinar y confundir este episodio con la integridad total del proyecto, ni con los aprendizajes que tenemos, ni las decisiones que debemos de tomar con respecto al sobredimensionamiento de los agentes, por favor organízame todo de manera que esté controlado todo. por favor hazlo bien, hazlo detallado..."

## Lo que se construyó hoy (organización durable)

**Memorias 🔥 CRÍTICAS nuevas:**
- `feedback_deterministic_backbone_first.md` — doctrina rectora del proyecto
- `project_agent_scope_audit_2026_05_03.md` — operacionalización + framework 6 checks

**Memoria efímera:**
- `project_first_paid_campaign_2026_05_03.md` — episodio Bridge, archivar tras post-mortem

**Memorias actualizadas con header de supersedimiento:**
- `project_agent_org_design.md` — visión "CEO + empleados" sigue válida; alcance V1 reducido
- `project_roadmap.md` — Bridge Episode + Fase 4/5 reescritas

**Index actualizado:**
- `MEMORY.md` — nueva categoría "Doctrina rectora" en 🔥 CRÍTICAS + sección "Episodios efímeros"

**Documentos del proyecto:**
- `CLAUDE.md` — principio operativo #11 agregado + estado al 2026-05-03 + roadmap revisado
- `docs/decisiones/0034-conversation-agent-foundation.md` — marcada 💤 Diferida con header explicativo
- `docs/audits/agent-scope-audit-2026-05-03.md` — audit formal con framework + supersedimientos
- `docs/sesiones/2026-05-03-strategic-pivot-and-first-campaign.md` — este archivo
- `docs/campaigns/2026-05-first-campaign/plan.md` — plan táctico campaña Bridge (próximo)
- `docs/campaigns/2026-05-first-campaign/tracking-sheet-template.md` — cheat sheet doctora (próximo)
- `docs/master-plan-mvp-livskin.md` — update con Bridge Episode + scope reducido (próximo)

## Decisiones tomadas (vinculantes)

1. **Doctrina rectora**: deterministic backbone first → principio operativo #11
2. **Scope agentes V1**: 1 agente real (Brand Orchestrator) + 2 scripts con LLM (Acquisition synth + Growth narrative)
3. **Conversation Agent IA**: diferido. V1 será chatbot rule-based + handoff humano + templates Meta-approved
4. **ADR-0034 v1.0**: marcada 💤 Diferida; será supersedida por ADR Conversation Agent v0 rule-based en Fase 4A
5. **Framework de 6 checks**: gate obligatorio para aprobar agente futuro
6. **Bridge Episode insertado** entre Fase 3 (cerrada) y Fase 4 (reescrita)
7. **Bloque 1 commit `60b609d`** (match automático lead↔cliente) — encaja con doctrina nueva, push pendiente aprobación explícita

## Push status

**Pendiente:** Bloque 1 commit `60b609d` (14 archivos, 1225 líneas) — encaja perfecto con doctrina backbone-first (es 100% determinístico). Push pendiente aprobación explícita de Dario.

## Hallazgos relevantes para futuras sesiones

- **Patrón observado**: Dario tiene capacidad de pause-and-redirect que muchos founders no tienen. Su frase "no, no, antes de todo esto" salvó al proyecto de 4-8 semanas más de sobre-engineering.
- **Anti-patrón observado**: Claude tiende a elaborar técnicamente sobre cualquier premisa que el usuario propone. Sin push back explícito, las propuestas se vuelven especificaciones implementables. El reto a futuro: Claude debe preguntar "¿hay validación previa que justifica este nivel de complejidad?" antes de elaborar la solución.
- **Doctrina #11 aplicada como filtro**: cualquier propuesta futura de agente IA pasa por los 6 checks. Si falla cualquiera → tools determinísticas en su lugar.

## Lo que queda pendiente

**Inmediato (hoy noche, 2-3h):**
- Verificar end-to-end del botox-mvp landing con UTMs
- Crear landing PRP duplicando botox-mvp
- Generar 3 links WhatsApp con shortcodes
- Setup tracking sheet template

**Mañana (3-4h):**
- Setup Facebook Ads Manager
- Crear creatividades (3-4 ads, vos + Claude, sin Brand Orchestrator)
- Cheat sheet impreso/digital para doctora
- Lanzar campaña

**Día 5-9:**
- Campaña corre, chequeo diario Ads Manager
- Doctora llena tracking sheet WA

**Día 9-10:**
- Post-mortem con data real
- Aprendizajes durables → memorias permanentes
- Decisión informada de próxima fase (chatbot WA primero o Brand Orchestrator primero)

## Próxima sesión propuesta

**Esta misma noche o mañana mañana**: ejecutar Tareas 1-4 del plan campaña (verificación + landing PRP + links WA + B3 fix opcional). Tactical, ~2-3h.

Después de eso, **Día 1 de la campaña**: setup FB Ads + lanzamiento.

**Después de la campaña corrida**: post-mortem con data real informa la decisión de Fase 4.
