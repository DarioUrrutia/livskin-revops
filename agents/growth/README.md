# Growth Agent

**Rol:** análisis continuo del sistema completo y generación de recomendaciones estratégicas.

**Fase de construcción:** Fase 6 (Semana 9)

## Objetivo

- Pulls diarios de Meta Ads + Vtiger + WordPress + ERP + brain
- Cálculo automático: CAC, LTV emergente, conversión por etapa, ROI por creativo
- Detección de anomalías (alertas)
- Ejecución automática de decisiones low-risk (ajustes menores de budget)
- Evaluación de calidad del Conversation Agent cada 100 conversaciones
- **Reporte semanal ejecutivo vía WhatsApp cada lunes**

## Reporte semanal

Estructurado, <500 palabras, llega a tu WhatsApp los lunes 09:00:

```
📊 LIVSKIN — SEMANA {N}

Financieros:
- Revenue: S/.X (Δ vs semana anterior)
- CAC: S/.Y
- Conversión lead→venta: Z%
- Tickets promedio: S/.W

Top 3 insights:
1. ...
2. ...
3. ...

Top 3 decisiones recomendadas (análisis riesgo):
1. Acción: ... · Impacto estimado: ... · Riesgo: bajo/medio/alto
2. ...
3. ...

Comparativa vs últimas 4 semanas: [mini-gráfico ASCII]

Auto-ejecutadas esta semana: N decisiones (ver dashboard).
Acción requerida tuya: [X] o "ninguna".
```

## Tools

- `analytics_query(sql)` → queries parametrizadas a warehouse
- `brain_get_conversations_sample(limit=20, random)` → para evals Conversation Agent
- `brain_save_learning(hypothesis, evidence, outcome, confidence)` → L6
- `meta_ads_auto_adjust(rule_set)` → solo si low-risk
- `whatsapp_send_report(markdown)` → envío del reporte
- `llm_evaluate(conversations, rubric)` → LLM-as-judge con Haiku

## Evals del Conversation Agent

Cada 100 conversaciones:
1. Sample 20 random
2. Evaluar con LLM-as-judge (Claude Haiku) contra rúbrica
3. Rúbrica: empatía, precisión, escalación correcta, cierre, brand voice
4. Resultado guardado en L6 (learnings) como "quality score" semanal
5. Si score < umbral: alertar + proponer ajuste de prompt

## Detección de anomalías

Reglas iniciales (simples, sin ML):

- Ventas de un día < 50% del promedio móvil 7 días → alerta
- CPL > 2× promedio último mes → alerta
- Conversión < 50% del baseline → alerta
- Conversación "muerta" >24h sin respuesta cuando debería cerrar → alerta
- Cost Claude API >150% del daily avg → alerta

## Referencias

- ADR-0032 — Growth Agent
- ADR-0039 — Evals LLM-as-judge
- ADR-0034 — Reactivación 45 días
- ADR-0040 — Cost tracking

## Estado actual

⏳ Pendiente — construcción en Fase 6 (Semana 9).
