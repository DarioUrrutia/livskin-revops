---
type: runbooks-index
version: 2.0
last_updated: 2026-04-26
authoritative: true
description: Índice de runbooks operativos. Cada runbook tiene frontmatter YAML ejecutable que el 5to agente (Infra+Security) puede consumir como skill MCP.
---

# 📘 Runbooks Operativos — Livskin

## Estructura de cada runbook

Todos los runbooks tienen frontmatter YAML estructurado:

```yaml
---
runbook: <nombre-kebab-case>
severity: low | medium | high | critical
auto_executable: true | false           # ¿el agente puede ejecutar sin autorización?
trigger:
  - "<condición que dispara este runbook>"
required_secrets:                        # qué secretos hace falta tener
  - SECRET_NAME
commands_diagnose:                       # comandos read-only para identificar
  - "comando 1"
commands_fix:                            # comandos que aplican el fix
  - "comando 1"
commands_verify:                         # confirmar que el fix funcionó
  - "comando 1"
escalation:
  if_fail: <quién o qué hacer>
related_skills:                          # skills MCP que usan este runbook
  - skill-name
---
```

## Catálogo Bloque 0.6 + 0.10 (13 runbooks ejecutables)

### Operacional

| # | Runbook | Severity | Auto |
|---|---|---|---|
| 1 | [ssl-cert-expiring](ssl-cert-expiring.md) | medium | ✅ |
| 2 | [disk-full](disk-full.md) | high | ⚠️ partial |
| 3 | [container-crashloop](container-crashloop.md) | high | ⚠️ |
| 4 | [postgres-connections-exhausted](postgres-connections-exhausted.md) | high | ❌ |
| 5 | [n8n-workflow-failing](n8n-workflow-failing.md) | medium | ❌ |
| 6 | [backup-failed](backup-failed.md) | high | ⚠️ |
| 13 | [cost-budget-exceeded](cost-budget-exceeded.md) | high | ❌ (Bloque 0.10) |

### Disaster Recovery

| # | Runbook | Severity | Auto |
|---|---|---|---|
| 7 | [migration-failed-mid-deploy](migration-failed-mid-deploy.md) | critical | ❌ |
| 8 | [vpc-down](vpc-down.md) | critical | ❌ |
| 9 | [disaster-recovery-vps1](disaster-recovery-vps1.md) | critical | ❌ |
| 10 | [disaster-recovery-vps2](disaster-recovery-vps2.md) | critical | ❌ |
| 11 | [disaster-recovery-vps3](disaster-recovery-vps3.md) | critical | ❌ |

### Seguridad

| # | Runbook | Severity | Auto |
|---|---|---|---|
| 12 | [credential-leaked](credential-leaked.md) | critical | ❌ |

## Runbooks históricos (pre-Bloque 0.6)

| Runbook | Estado |
|---|---|
| [obsidian-setup](obsidian-setup.md) | ✅ Fase 1 |

## Cómo el agente IA usa esto

El 5to agente consume estos runbooks así:

1. Recibe alerta (ej: "disk_pct=92% en livskin-wp")
2. Busca runbook con trigger matching
3. Si `auto_executable: true`: ejecuta diagnose → fix → verify, reporta resumen
4. Si `auto_executable: false`: ejecuta solo diagnose, propone fix con autorización pendiente

## Convenciones

- **`required_secrets`** se carga de Bitwarden o GitHub Secrets
- **`commands_diagnose`** debe ser idempotente y read-only
- **`commands_fix`** debe ser idempotente cuando posible
- **`commands_verify`** debe ser determinístico
