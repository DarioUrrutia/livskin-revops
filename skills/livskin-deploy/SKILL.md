---
name: livskin-deploy
description: Disparar deploys autorizados a los 3 VPS de Livskin via GitHub Actions workflow_dispatch. SIEMPRE requiere autorización Dario.
version: 1.0.0
allowed-tools:
  - Bash
  - WebFetch
authorization_required: true
authorization_callback: https://erp.livskin.site/api/internal/skill-authorize
authoritative_docs:
  - .github/workflows/deploy-vps1.yml
  - .github/workflows/deploy-vps2.yml
  - .github/workflows/deploy-vps3.yml
  - docs/runbooks/migration-failed-mid-deploy.md
---

# Skill: Livskin Deploy

Capacidad para disparar deploys controlados a los 3 VPS via GitHub Actions.

**TODA acción requiere autorización Dario.** Ningún deploy es auto_executable.

## Procedure

```
1. Verificar contexto:
   - Es horario adecuado (no madrugada Italia / no horario operativo Cusco)?
   - El último deploy de este VPS fue exitoso? (audit_log)
   - Hay backups recientes verificados? (último <24h)

2. Si todo OK → request authorization

3. Si Dario aprueba → trigger workflow

4. Monitor del workflow (poll cada 30s):
   - Snapshot DO created?
   - Pull + compose up?
   - Verify endpoints OK?
   - Tests passed (si VPS 3)?

5. Si todo verde → reportar success
   Si verify falla → workflow rolleó al snapshot pre-deploy → reportar
```

## Tools disponibles

### `trigger_deploy(vps: str, branch?: str = "main", skip_snapshot?: bool, skip_tests?: bool)` — RISKY

Dispara workflow_dispatch del workflow correspondiente.

```bash
gh workflow run deploy-vps3.yml \
  --ref main \
  -f skip_snapshot=false \
  -f skip_tests=false
```

### `monitor_deploy(workflow_run_id: str)`

Polling del run hasta que termine.

```bash
gh run view <run-id> --log-failed
gh run watch <run-id>
```

### `request_rollback(vps: str, snapshot_id?: str)` — VERY RISKY

Restaura un VPS desde snapshot DO. Snapshot por default = el más reciente
con tag `pre-deploy`.

**Equivale al runbook [migration-failed-mid-deploy](../../docs/runbooks/migration-failed-mid-deploy.md).**

```bash
SNAP_ID=$(bash .github/scripts/do-snapshot.sh latest livskin-vps-erp pre-deploy)
bash .github/scripts/do-snapshot.sh restore livskin-vps-erp "$SNAP_ID"
```

### `list_recent_deploys(limit?: int = 10)`

Audit log de deploys recientes (mejor que `gh run list` porque incluye
contexto del audit log post-deploy).

```sql
SELECT
  occurred_at,
  audit_metadata->>'vps' as vps,
  audit_metadata->>'sha' as sha,
  audit_metadata->>'actor' as actor,
  audit_metadata->>'outcome' as outcome,
  result
FROM audit_log
WHERE action LIKE 'infra.deploy_%'
ORDER BY occurred_at DESC LIMIT 10;
```

## Authorization template

```
POST /api/internal/skill-authorize
{
  "skill": "livskin-deploy",
  "action": "trigger_deploy",
  "params": {
    "vps": "livskin-vps-erp",
    "branch": "main",
    "skip_snapshot": false,
    "skip_tests": false
  },
  "context": "Hot fix de bug en venta_service.py — commit abc123. Riesgo: bajo (test coverage 81%).",
  "estimated_duration": "8 minutes"
}
```

Mensaje a Dario via WhatsApp:
```
🚀 Skill livskin-deploy quiere ejecutar:

Acción: trigger_deploy
VPS: livskin-vps-erp (ERP)
Branch: main
Razón: Hot fix bug venta_service.py (abc123)
Duración estimada: 8 min
Snapshot pre-deploy: SÍ (rollback automático si falla)
Tests post-deploy: SÍ

¿OK? Responde "OK <token>" o "no <razón>"
```

## Reglas de seguridad

🛑 **NUNCA disparar deploys**:
- Sin snapshot DO pre-deploy (excepto en hotfixes urgentes confirmados)
- Sin tests passing en main (verificar último GHA run del PR)
- En horarios de tráfico alto (verificar last_login_at de usuarios)
- Si el último deploy del mismo VPS falló (investigar primero)
- Si hay deploy concurrent del mismo VPS (concurrency lock en workflows)

✅ **OK disparar**:
- Cambios mergeados a main con tests passing
- Snapshot reciente (<24h)
- Horario apropiado (madrugada UTC)
- Dario autoriza con razón clara

## Outputs estructurados

```json
{
  "skill": "livskin-deploy",
  "action": "trigger_deploy",
  "vps": "livskin-vps-erp",
  "workflow_run_id": 12345,
  "started_at": "2026-04-26T11:30:00Z",
  "snapshot_id": "snap-abc123",
  "outcome": "success" | "failed" | "rolled_back",
  "duration_s": 480,
  "audit_log_event_id": 9876,
  "next_actions_recommended": []
}
```

## Limitaciones

- Solo workflows definidos en `.github/workflows/deploy-vps[1|2|3].yml`
- No puede modificar el workflow mismo (eso requiere PR review)
- No puede deployar branches != main sin autorización extra
- No puede skipear snapshot DO en producción (skip_snapshot=true requiere
  autorización adicional explícita)

## Referencias

- [.github/workflows/](../../.github/workflows/) — workflows de los 3 VPS
- [.github/scripts/do-snapshot.sh](../../.github/scripts/do-snapshot.sh) — wrapper doctl
- [docs/runbooks/migration-failed-mid-deploy.md](../../docs/runbooks/migration-failed-mid-deploy.md) — qué hacer si rollback necesario
