# Agentes IA — 4 agentes del sistema Livskin

Cada agente es un sistema construido sobre Claude API + tools + contexto del segundo cerebro, orquestado por n8n.

## Los 4 agentes

| Agente | Propósito | Frecuencia ejecución | Fase construcción | Intervención humana |
|---|---|---|---|---|
| [conversation/](conversation/) | Primera línea atención paciente vía WhatsApp | Tiempo real 24/7 | Fase 4 (semana 6) | ~30 min/día escalaciones |
| [content/](content/) | Generar 12 briefs semanales + Creative Factory | Semanal (domingos) | Fase 5 (semana 7) | 15 min domingo |
| [acquisition/](acquisition/) | Optimización automática campañas Meta | Semanal (lunes) + diario | Fase 5 (semana 8) | 10 min lunes |
| [growth/](growth/) | Análisis continuo + reporte ejecutivo | Diario + semanal | Fase 6 (semana 9) | 1 hora lunes |

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
