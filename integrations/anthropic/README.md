# Anthropic — Claude API

Cerebro de los 4 agentes IA del sistema.

## Cuentas y modelos

- **Cuenta personal:** Claude Max 5x (~$100/mes ya pagado) — para Claude Code (esta sesión) + Claude Design
- **Cuenta de API:** console.anthropic.com — **a cargar crédito** en Fase 0

## Modelos usados

| Modelo | Uso | Cost/1M tokens input | Cost/1M tokens output |
|---|---|---|---|
| Claude Opus 4.7 | Conversation Agent (complejidad alta), Growth Agent | ~$15 | ~$75 |
| Claude Sonnet 4.6 | Content Agent (briefs creativos) | ~$3 | ~$15 |
| Claude Haiku 4.5 | Acquisition Engine (decisiones simples), evals LLM-as-judge | ~$0.25 | ~$1.25 |

Estrategia de costo:
- Opus solo para agentes que requieren razonamiento complejo con contexto largo
- Sonnet para generación creativa
- Haiku para tareas simples + evaluación

## Prompt caching

Activado en todos los agentes. Reduce costos hasta 90% en conversaciones con system prompts grandes que se repiten.

## Presupuesto

- **Budget mensual inicial:** $120 USD
- **Budget alerts:** a 50%, 80%, 100%
- **Circuit breaker:** a 100% del budget del día, pausar agentes y alertar

Tracking en DB `analytics.llm_costs` con cadencia por request.

## Variables de entorno

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MONTHLY_BUDGET_USD=120
ANTHROPIC_DAILY_BUDGET_USD=5
ANTHROPIC_MODEL_DEFAULT=claude-opus-4-7
ANTHROPIC_MODEL_SIMPLE=claude-haiku-4-5
ANTHROPIC_MODEL_CREATIVE=claude-sonnet-4-6
```

## Data privacy

**Importante:** verificar en settings de cuenta que los prompts **NO** se usen para entrenamiento (opt-out). Anthropic respeta este setting por default para accounts API.

## Referencias

- Anthropic API docs: https://docs.anthropic.com/
- Pricing: https://www.anthropic.com/pricing
- Claude Code docs: https://docs.claude.com/claude-code
- ADR-0005 — Orquestación agentes (n8n + Agent SDK)
- ADR-0040 — Cost tracking
