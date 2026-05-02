# Agentes IA — scope reducido por audit 2026-05-03

> **⚠️ ACTUALIZACIÓN 2026-05-03:** este README conserva los subdirs originales (`conversation/`, `content/`, `acquisition/`, `growth/`) como **placeholders de organización**, pero el audit 2026-05-03 redujo drásticamente el scope V1.
>
> **Doctrina rectora**: principio operativo #11 — *"Deterministic backbone first — IA es capa aditiva, no foundational"*. Memorias 🔥 CRÍTICAS: `feedback_deterministic_backbone_first.md` + `project_agent_scope_audit_2026_05_03.md`.
>
> **Antes de aprobar agente nuevo**: aplicar **filtro de 6 checks** (memoria audit). Sin pasarlo → tools determinísticas, no agente.

Cada agente futuro será un sistema construido sobre Claude API + tools + contexto del segundo cerebro, orquestado por n8n.

## Scope V1 post-audit 2026-05-03

| Subdir | Status V1 | Plan |
|---|---|---|
| [conversation/](conversation/) | ⏸️ **Diferido** | V1 será chatbot rule-based en ERP (state machine Python, NO IA). Reabrir agente IA cuando volumen WA >100 conv/día sostenido |
| [content/](content/) | ⏳ **Brand Orchestrator** (único agente IA V1) | Caso canónico subagent pattern (research/concept/copy/visual/implementation). Construcción Fase 4B post-validación + brand voice consolidado |
| [acquisition/](acquisition/) | 🔧 **Script con LLM ocasional**, no agente | Meta API + Google API readers determinísticos + 1 LLM call para narrativa de reporte semanal. Fase 5 |
| [growth/](growth/) | 🔧 **Script con LLM ocasional**, no agente | SQL determinístico cohorts + 1 LLM call para narrativa mensual. Fase 5 |

## Estructura común

```
agents/<agent_name>/
├── README.md                 # rol, tools, dependencias, estado
├── prompts/                  # versionados con semver
│   ├── v1.0-system.md
│   ├── v1.1-system.md
│   └── CHANGELOG.md
├── tools/                    # especificaciones JSON de tool use
│   ├── vtiger_get_lead.json
│   └── ...
├── evals/                    # golden set + criterios
│   ├── golden_set.jsonl
│   ├── criteria.md
│   └── results/
│       └── YYYY-MM-DD-<model>-<promptv>.md
└── docs/
    └── runbook.md            # cómo operar, debuggear, rollback
```

## Principios de diseño

1. **Prompt versionado en git.** Cada cambio es un PR. Langfuse trackea qué versión corrió.
2. **Tools con JSON schema estricto.** Nada de ambigüedad.
3. **Segundo cerebro obligatorio.** Antes de decidir, consultar capas relevantes.
4. **Escalación a humano definida.** Cada agente sabe cuándo NO decidir solo.
5. **Observabilidad total.** Langfuse captura cada ejecución.
6. **Costos trackeados por agente.** Tabla `analytics.llm_costs` con atribución.
7. **Rate limiting propio.** No confiar solo en protección de Claude API.

## Orquestación

**Default:** n8n ejecuta flows que llaman Claude API vía HTTP Request node con tool use. Simple, versionable, debuggeable.

**Agent SDK:** reservado para agentes que requieran razonamiento multi-step dentro de una sola decisión (ej: Growth Agent analizando 10 fuentes antes de concluir). Se evalúa caso por caso. Ver ADR-0005.

## Referencias

- ADR-0005 — Orquestación agentes (n8n + Agent SDK híbrido)
- ADR-0029 — Conversation Agent
- ADR-0030 — Content Agent + Creative Factory
- ADR-0031 — Acquisition Engine
- ADR-0032 — Growth Agent
- ADR-0033 — Escalación doctora
- ADR-0036 — Prompt versioning
- ADR-0039 — Evals LLM-as-judge
