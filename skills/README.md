# 🤖 Livskin Skills

Capacidades declarativas que cualquier agente IA (Claude Code, Claude Agent
SDK, MCP-compatible client) puede invocar para operar el sistema Livskin.

## Estructura de cada skill

```
skills/
├── livskin-ops/
│   ├── SKILL.md           # frontmatter + instrucciones para el agente
│   ├── tools.json         # tool definitions (tool_use compatible)
│   └── runbook-refs/      # mapeo skill → runbooks
└── livskin-deploy/
    ├── SKILL.md
    └── tools.json
```

## SKILL.md format

```yaml
---
name: <skill-name>
description: <para qué sirve, una línea>
allowed-tools:
  - Bash
  - WebFetch
  - <tool específico>
authorization_required: true | false
authorization_callback: <URL del endpoint que autoriza>
mcp_server: <opcional, URL del MCP server que provee tools custom>
---

# Skill body
Instrucciones para el agente sobre cómo usar esta skill...
```

## Skills disponibles

| Skill | Descripción | Auth Dario |
|---|---|---|
| [livskin-ops](livskin-ops/SKILL.md) | Operación cross-VPS: query state, ejecutar runbooks, ver audit log | partial (read-only sin auth) |
| [livskin-deploy](livskin-deploy/SKILL.md) | Disparar deploys autorizados via GHA workflow_dispatch | yes (siempre) |

## Cómo usarlos

### Desde Claude Code (CLI)
```bash
# El skill se carga automáticamente si está en skills/
# Tools disponibles:
@livskin-ops query_system_state
@livskin-ops query_audit_log "infra.deploy_completed last 7 days"
@livskin-deploy trigger_vps3_redeploy --dry-run
```

### Desde Claude Agent SDK
```python
from anthropic import Anthropic
from livskin_skills import load_skill

client = Anthropic()
skill = load_skill("livskin-ops")
response = client.messages.create(
    model="claude-opus-4-7",
    tools=skill.tools,
    messages=[...]
)
```

### Desde MCP-compatible clients
- Conectar a `https://erp.livskin.site/mcp/livskin-ops` (cuando esté
  desplegado el MCP server)
- Tools auto-descubiertos
- Authorization via Bearer token (rotable)

## Authorization model

**Acciones SAFE (read-only):**
- `query_system_state` — sin auth
- `query_audit_log` — sin auth
- `query_system_map` — sin auth
- `list_skills` — sin auth

**Acciones RISKY (mutating):**
- `trigger_deploy` — auth Dario via WhatsApp / Signal callback
- `trigger_runbook` (auto_executable=false) — auth Dario
- `restore_snapshot` — auth Dario + confirmación timestamp
- `rotate_credential` — auth Dario + Bitwarden update verificado

**Implementación auth callback:**
```
1. Agente intenta acción RISKY
2. Llama a authorization_callback URL con:
   - skill: "livskin-deploy"
   - action: "trigger_vps3_redeploy"
   - context: "...razón..."
3. Endpoint envía notificación a Dario (WhatsApp / Signal)
4. Dario responde "OK <token>" o "no"
5. Agente recibe respuesta y ejecuta o aborta
```

## Para el 5to agente futuro (Infra+Security)

Estas skills son su **base operacional**. El agente:
1. Consume `livskin-ops` para read state
2. Detecta anomalías (cross-checking sensors + audit_log)
3. Cuando aplica, ejecuta runbook auto_executable=true sin pedir auth
4. Cuando es risky, usa `livskin-deploy` o `livskin-ops` con auth callback
5. Reporta acciones tomadas via WhatsApp daily summary

## Versioning

Cada skill versiona en su `SKILL.md` con `version: X.Y.Z`:
- `version: X` mayor = cambio breaking en tool signatures
- `version: Y` minor = feature nueva backward compatible
- `version: Z` patch = bug fix

## Roadmap

- [x] Bloque 0.9: skills livskin-ops + livskin-deploy iniciales
- [ ] Fase 4: skill `livskin-conversation-agent` (gestión leads)
- [ ] Fase 5: skill `livskin-content-agent` (creativos Meta Ads)
- [ ] Fase 6+: agente Infra+Security usa todos los skills via MCP server
