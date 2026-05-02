---
type: runbooks-index
version: 2.1
last_updated: 2026-05-03
authoritative: true
description: Índice de runbooks operativos. Cada runbook tiene frontmatter YAML ejecutable consumible por skills MCP. Audit 2026-05-03 agregó 5 runbooks que faltaban en el index legacy.
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

## Catálogo (18 runbooks ejecutables al 2026-05-03)

### Operacional

| # | Runbook | Severity | Auto |
|---|---|---|---|
| 1 | [ssl-cert-expiring](ssl-cert-expiring.md) | medium | ✅ |
| 2 | [disk-full](disk-full.md) | high | ⚠️ partial |
| 3 | [container-crashloop](container-crashloop.md) | high | ⚠️ |
| 4 | [postgres-connections-exhausted](postgres-connections-exhausted.md) | high | ❌ |
| 5 | [n8n-workflow-failing](n8n-workflow-failing.md) | medium | ❌ |
| 6 | [backup-failed](backup-failed.md) | high | ⚠️ |
| 7 | [cost-budget-exceeded](cost-budget-exceeded.md) | high | ❌ |

### Disaster Recovery

| # | Runbook | Severity | Auto |
|---|---|---|---|
| 8 | [migration-failed-mid-deploy](migration-failed-mid-deploy.md) | critical | ❌ |
| 9 | [vpc-down](vpc-down.md) | critical | ❌ |
| 10 | [disaster-recovery-vps1](disaster-recovery-vps1.md) | critical | ❌ |
| 11 | [disaster-recovery-vps2](disaster-recovery-vps2.md) | critical | ❌ |
| 12 | [disaster-recovery-vps3](disaster-recovery-vps3.md) | critical | ❌ |
| 13 | [dr-drill-procedure](dr-drill-procedure.md) | low (cadencia semestral/trimestral) | ❌ |

### Seguridad

| # | Runbook | Severity | Auto |
|---|---|---|---|
| 14 | [credential-leaked](credential-leaked.md) | critical | ❌ |

### Procesos de desarrollo (agregados al index 2026-05-03)

| # | Runbook | Severity | Auto |
|---|---|---|---|
| 15 | [preflight-cross-system](preflight-cross-system.md) | informativo | N/A — protocolo obligatorio antes de tocar cross-system |
| 16 | [cierre-sesion](cierre-sesion.md) | informativo | N/A — runbook 11-pasos de cierre de sesión |
| 17 | [vtiger-custom-fields](vtiger-custom-fields.md) | informativo | N/A — referencia cf_NNN ↔ ERP fields |
| 18 | [wordpress-form-livskin-integration](wordpress-form-livskin-integration.md) | informativo | N/A — activar/desactivar/debuggear forms WP |
| 19 | [landing-pages-deploy](landing-pages-deploy.md) | informativo | N/A — Cloudflare Pages deploy de landings |

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
