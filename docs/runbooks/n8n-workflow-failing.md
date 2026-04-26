---
runbook: n8n-workflow-failing
severity: medium
auto_executable: false
trigger:
  - "n8n logs muestran 'Workflow execution failed' >5 veces en 1h"
  - "Webhooks reciben payload pero no hay registro en analytics.events"
required_secrets: []
commands_diagnose:
  - "ssh livskin-ops 'docker logs --tail=200 n8n 2>&1 | grep -iE \"error|failed\"'"
  - "# Visitar https://flow.livskin.site → Executions → ver últimos errores"
  - "ssh livskin-ops 'docker exec n8n n8n list:workflow'"
commands_fix:
  - "# Acceso UI: https://flow.livskin.site → identificar workflow en error"
  - "# Click en execution fallida → ver step que falló → re-ejecutar"
commands_verify:
  - "ssh livskin-ops 'docker logs --tail=50 n8n 2>&1 | grep -i workflow'"
  - "# UI muestra última execution como 'success'"
escalation:
  if_fail: "rollback workflow a versión previa via n8n UI"
related_skills:
  - livskin-ops
---

# n8n workflow falla repetidamente

## Síntomas
- n8n UI muestra executions en rojo
- SureForms enviado pero no aparece lead en Vtiger
- Tracking eventos no llegan a analytics.events

## Diagnóstico

1. UI: https://flow.livskin.site → Executions → filtrar por "failed"
2. Identificar workflow + step donde falla
3. Inspeccionar input data + error message

```bash
# Logs de docker n8n
ssh livskin-ops 'docker logs --tail=200 n8n 2>&1 | grep -iE "error|failed"'
```

## Causas comunes

### A. Endpoint externo cambió (Meta CAPI, GA4 MP)
- Verificar URL + estructura del request
- Meta puede deprecar API versions

### B. Credencial expiró (Meta access token)
- n8n UI → Credentials → renovar token

### C. Schema de input cambió (SureForms agregó campo nuevo)
- Workflow no maneja campo nuevo → lo ignora o falla

### D. Cross-VPS connectivity (cae erp-flask)
- Verificar `curl https://erp.livskin.site/ping` desde VPS 2
- Si falla → revisar runbook `container-crashloop` en VPS 3

## Fix

1. Identificar causa via UI
2. Editar workflow → fix step → save
3. Re-ejecutar manualmente para validar
4. Si volume alto → re-ejecutar batch failed via UI

## Verificación

UI muestra última execution del workflow como `success`.

```bash
# Logs limpios sin errores recientes
ssh livskin-ops 'docker logs --tail=50 n8n 2>&1'
```

## Escalación

Si workflow está roto >24h:
- n8n permite versionado de workflows → revertir a versión previa
- Considerar pausar workflow temporalmente y replay manual de payloads
  desde `n8n.executions_table` (sqlite en `/home/livskin/apps/n8n/data/`)
