---
name: livskin-ops
description: Operación cross-VPS de Livskin — query estado del sistema, audit log, system map, ejecutar runbooks. Read-only sin auth. Acciones mutating requieren autorización Dario.
version: 1.0.0
allowed-tools:
  - Bash
  - WebFetch
  - Read
authorization_required: partial
authorization_callback: https://erp.livskin.site/api/internal/skill-authorize
mcp_server: https://erp.livskin.site/mcp/livskin-ops  # post-Fase 4
authoritative_docs:
  - docs/sistema-mapa.md
  - docs/audit-events-schema.md
  - docs/runbooks/README.md
---

# Skill: Livskin Ops

Capacidades para operar el sistema Livskin cross-VPS.

## Cuándo usar esta skill

- Dario pregunta "¿cuál es el estado del sistema?"
- Aparece una alerta (disk warning, container crashloop, etc.)
- Necesitás verificar antes de ejecutar acciones (read-only safety)
- Forense: investigar audit_log para entender un incidente

## Cuándo NO usar

- Para deployar código nuevo → usar [livskin-deploy](../livskin-deploy/SKILL.md)
- Para queries de negocio (ventas, clientes) → usar el ERP UI directamente
- Sin contexto de Livskin (es project-specific, no genérico)

## Procedure básico

```
1. ANTES de cualquier acción:
   - Fetch /api/system-map.json para tener contexto del sistema
   - Si necesitás historia: query audit_log de últimas 24h
2. Identificar la categoría de la query/acción
3. Si es READ-ONLY: ejecutar directo
4. Si es MUTATING: invocar authorization_callback, esperar OK de Dario
5. Reportar resultado en forma estructurada
```

## Tools disponibles

### `query_system_state(vps?: str)`
Devuelve snapshot reciente de un VPS (o los 3 si no se especifica).
Read-only, sin auth.

```bash
curl -sf -H "X-Internal-Token: $TOKEN" \
  https://erp.livskin.site/api/internal/system-state | jq
# o el sensor de un VPS específico:
curl -sf -H "X-Internal-Token: $TOKEN" \
  http://10.114.0.2:9100/api/system-state | jq
```

### `query_audit_log(action_filter?: str, limit?: int = 50)`
Lista eventos del audit log con filtros opcionales.

```bash
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  SELECT occurred_at, action, user_username, audit_metadata
  FROM audit_log
  WHERE action LIKE \"infra.%\"
  ORDER BY occurred_at DESC LIMIT 20;
"'
```

### `query_system_map(section?: str)`
Sirve docs/sistema-mapa.md como JSON estructurado.

```bash
curl -sf https://erp.livskin.site/api/system-map.json | jq '.containers[] | select(.vps == "livskin-erp")'
```

### `query_runbooks(trigger_keyword?: str)`
Lista runbooks disponibles, opcionalmente filtra por keyword en `trigger`.

```bash
grep -l "disk_pct >= 85" docs/runbooks/*.md
```

### `trigger_runbook(runbook: str, dry_run?: bool = true)` — RISKY
Ejecuta un runbook. Si `auto_executable=true` ejecuta directo. Si no,
requiere autorización Dario.

```
1. Read runbook YAML frontmatter
2. Validar required_secrets disponibles
3. Ejecutar commands_diagnose (siempre, read-only)
4. Si auto_executable=false: pedir auth Dario
5. Si OK: ejecutar commands_fix
6. Ejecutar commands_verify
7. Reportar a audit_log
```

### `query_backups_status()`
Estado de los backups (último de cada componente, verificación).

```sql
SELECT
  audit_metadata->>'engine' as engine,
  audit_metadata->>'db' as db,
  max(occurred_at) as last_verified
FROM audit_log
WHERE action = 'infra.backup_verified'
GROUP BY 1, 2;
```

## Authorization callback

Cuando se llama una acción RISKY:

```
POST https://erp.livskin.site/api/internal/skill-authorize
{
  "skill": "livskin-ops",
  "action": "trigger_runbook",
  "params": {"runbook": "ssl-cert-expiring"},
  "context": "Cert expira en 5 días, runbook auto_executable=true"
}

→ Endpoint envía a Dario via WhatsApp:
   "Skill livskin-ops quiere ejecutar trigger_runbook(ssl-cert-expiring).
    Razón: <context>. Responde OK o no."

→ Dario responde con "OK <token>" o "no"
→ Endpoint devuelve: {"authorized": true|false, "token": "..."}

→ Agente continúa o aborta
```

## Outputs estructurados

Toda respuesta debe ser machine-readable. Estructura recomendada:

```json
{
  "skill": "livskin-ops",
  "action_executed": "query_system_state",
  "summary": "All 3 VPS healthy. VPS 1 at 92% RAM (warning).",
  "data": {...},
  "anomalies_detected": [
    {"vps": "livskin-wp", "type": "ram_warning", "value": 92}
  ],
  "next_actions_recommended": [
    {"runbook": "disk-full", "priority": "low"}
  ]
}
```

## Limitaciones

- NO puede cambiar configs sin auth
- NO puede ejecutar `doctl compute droplet-action restore` sin auth
- NO puede modificar audit_log (es immutable a nivel DB)
- NO puede acceder a datos de clientes (PII) sin auth bcrypt admin login

## Referencias

- [docs/sistema-mapa.md](../../docs/sistema-mapa.md) — autoritativo de containers/VPS
- [docs/audit-events-schema.md](../../docs/audit-events-schema.md) — schema de eventos
- [docs/runbooks/README.md](../../docs/runbooks/README.md) — runbooks ejecutables
