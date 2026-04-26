---
runbook: cost-budget-exceeded
severity: high
auto_executable: false
trigger:
  - "evento infra.budget_exceeded en audit_log"
  - "agent_budget_alerts entry tipo 'exceeded'"
  - "WhatsApp alert de monthly spend >100%"
required_secrets:
  - AUDIT_INTERNAL_TOKEN
commands_diagnose:
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c \"SELECT * FROM agent_budget_alerts ORDER BY triggered_at DESC LIMIT 10;\"'"
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c \"SELECT agent_name, SUM(cost_usd) as cost, COUNT(*) as calls, AVG(input_tokens+output_tokens) as avg_tokens FROM agent_api_calls WHERE occurred_at::date = CURRENT_DATE GROUP BY 1;\"'"
  - "# Visitar https://erp.livskin.site/admin/agent-costs"
commands_fix:
  - "# Opción A: aumentar budget temporalmente (con autorización Dario)"
  - "# Opción B: deshabilitar agente temporalmente"
  - "# Opción C: rollback a versión previa del prompt (puede ser bug)"
commands_verify:
  - "# Próximas calls deben can_proceed=true"
  - "curl -sf -H \"X-Internal-Token: $TOKEN\" 'https://erp.livskin.site/api/internal/agent-budget-check?agent_name=conversation' | jq"
escalation:
  if_fail: "WhatsApp inmediato a Dario — costos pueden seguir creciendo si hard_block desactivado"
related_skills:
  - livskin-ops
---

# Cost budget exceeded — agente superó hard limit

## Síntomas
- Audit log tiene `infra.budget_exceeded` reciente
- Dashboard `/admin/agent-costs` muestra agente en rojo
- WhatsApp alert "Daily spend 100%+"
- Llamadas API empezaron a fallar con `outcome=budget_blocked`

## Severidad

🔴 **HIGH** — sin acción, los costos pueden seguir si `hard_block_at_limit` está desactivado.
Si está activado (default): el agente para automáticamente, pero perdemos funcionalidad.

## Diagnóstico

```bash
# 1. Ver alertas recientes
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  SELECT triggered_at, agent_name, alert_type, scope, usd_at_trigger, limit_at_trigger
  FROM agent_budget_alerts
  ORDER BY triggered_at DESC LIMIT 20;
"'

# 2. Ver consumo por agente HOY
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  SELECT
    agent_name,
    SUM(cost_usd) as cost_today,
    COUNT(*) as calls,
    AVG(input_tokens+output_tokens) as avg_tokens,
    AVG(latency_ms) as avg_latency_ms
  FROM agent_api_calls
  WHERE occurred_at::date = CURRENT_DATE
  GROUP BY 1
  ORDER BY 2 DESC;
"'

# 3. Ver outliers — calls extra costosas (probable bug)
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  SELECT occurred_at, agent_name, model, cost_usd, input_tokens, output_tokens, task_id, prompt_template_id
  FROM agent_api_calls
  WHERE occurred_at::date = CURRENT_DATE
  ORDER BY cost_usd DESC LIMIT 10;
"'
```

## Decisión flow

```
¿Es spike legítimo (carga real) o bug?
├── BUG (calls anormalmente caras, loop, prompt mal)
│   → Rollback a prompt previo + fix root cause
│   → No aumentar budget
└── LEGÍTIMO (más leads, más tráfico)
    → Aumentar budget (con autorización Dario)
    → Considerar optimizaciones (cache, modelo más barato)
```

## Fix por causa

### A. Bug en agente (calls runaway)

```bash
# 1. Identificar el agente afectado
# Output del paso 2 del diagnóstico

# 2. Deshabilitar temporalmente
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  UPDATE agent_budgets
  SET active = false, notes = CONCAT(notes, E'\n[paused $(date)] runaway costs')
  WHERE agent_name = '<agent>';
"'

# 3. Investigar logs del agente
ssh livskin-erp 'docker logs --tail=200 <agent-container> | grep -i error'

# 4. Rollback a versión previa del prompt
# (depende de cómo se versione — Fase 4+)

# 5. Reactivar agente con monitoring extra
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  UPDATE agent_budgets
  SET active = true, daily_usd_limit = daily_usd_limit / 2
  WHERE agent_name = '<agent>';
"'
```

### B. Spike legítimo

```bash
# Aumentar budget temporal (con autorización Dario via WhatsApp)
# AUDIT_INTERNAL_TOKEN debe estar disponible
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  UPDATE agent_budgets
  SET daily_usd_limit = 5.00,  -- antes era 3.00
      notes = CONCAT(notes, E'\n[increased $(date)] spike legitimo')
  WHERE agent_name = 'conversation';
"'

# Audit event:
curl -X POST https://erp.livskin.site/api/internal/audit-event \
  -H "X-Internal-Token: $TOKEN" \
  -d '{"action":"admin.budget_changed","entity_id":"conversation","metadata":{"old_daily":3,"new_daily":5,"reason":"spike legitimo confirmado"}}'
```

### C. Optimización para reducir costo recurrente

Cuando el spike NO fue bug pero los costos son altos sostenidos:

1. **Habilitar prompt caching** (90% descuento sobre input cached)
   - Identificar parte estática del prompt (system message, contexto cliente)
   - Marcar con `cache_control: {type: "ephemeral"}`

2. **Cambiar a modelo más barato donde aplica**
   - Classification simple → Haiku 4.5 (5× más barato que Sonnet)
   - Tareas complejas → mantener Sonnet 4.6 / Opus 4.7

3. **Limit max_tokens en respuestas**
   - Si responses promedio son <500 tokens, limitar a 800 para evitar runaway

4. **Batch API para tareas no-realtime**
   - Content generation programada → 50% descuento

## Verificación

```bash
# Después del fix, próximas calls deben passing
curl -sf -H "X-Internal-Token: $TOKEN" \
  "https://erp.livskin.site/api/internal/agent-budget-check?agent_name=<agent>" | jq

# Esperado: {"can_proceed": true, ...}
```

## Por qué este runbook NO es auto_executable

Decisiones que requieren juicio humano:
- ¿Es bug o spike legítimo? (depende del contexto del negocio)
- Aumentar budget tiene impacto financiero
- Deshabilitar agente afecta usuarios

→ Siempre confirmación Dario.

## Post-incidente

- Actualizar `feedback_agent_resource_optimization.md` si emerge un patrón
- Considerar ajustar `alert_threshold_pct` (default 80) si dispara mucho
- Si fue bug: agregar test que detecte el caso edge
- Si fue spike: documentar en `docs/audits/` para forecasting
