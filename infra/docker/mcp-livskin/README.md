# mcp-livskin — MCP Server

MCP (Model Context Protocol) server que expone las skills `livskin-ops` y
`livskin-deploy` como tools consumibles por agentes IA compatibles con MCP
(Claude Code, Claude Agent SDK, otros).

## Estado

🚧 **Scaffolding** — Bloque 0.9 deja la estructura preparada. Implementación
del server real (TypeScript con `@modelcontextprotocol/sdk` o Python con
`mcp` library) se completa en **Fase 6 / extensión Fase 7** cuando el 5to
agente Infra+Security se construya.

## Rationale

Hoy las skills se cargan via SKILL.md frontmatter (Claude Code y Agent SDK
las soportan así). MCP server agrega:
- Discovery automático para clientes MCP arbitrarios
- Authorization callback estandarizado
- Audit logging de cada tool invocation
- Versionado de tools

## Arquitectura planeada

```
[Agent IA cliente]
       ↓
  HTTPS + Bearer token
       ↓
[mcp-livskin server (puerto 8443)]
       ↓
  ├─ tool: query_system_state    → curl al endpoint correspondiente
  ├─ tool: query_audit_log       → SQL al postgres-data
  ├─ tool: trigger_deploy        → gh workflow run + auth callback
  └─ tool: ... (todos los de tools.json de cada skill)
       ↓
  Response + audit_log entry
```

## Despliegue (post-Fase 6)

Container nuevo en VPS 3:
- Imagen: `livskin/mcp-server:latest` (built local)
- Network: `data_net` (mismo que erp-flask para acceso a postgres-data)
- Puerto: `127.0.0.1:8443` (no expuesto público; via nginx con auth)
- Path nginx: `/mcp/*` → mcp-livskin:8443

## Authorization

Bearer token rotable, scope por skill:
```
Authorization: Bearer <token>
X-Skill: livskin-ops | livskin-deploy
```

Tokens almacenados en `livskin_erp.mcp_tokens` (tabla nueva) con:
- `token_hash` (no plain text)
- `skill` (qué skills puede invocar)
- `actions_whitelist` (subset de tools)
- `created_at`, `expires_at`, `last_used_at`
- `created_by_user_id` (qué admin lo creó)

## Próximos pasos (cuando se implemente)

1. Crear estructura del server (TS o Python)
2. Implementar tool dispatcher leyendo skills/*/tools.json
3. Authorization layer con tokens DB
4. Audit logging de cada tool call
5. Tests E2E
6. Container + docker-compose
7. Routing en nginx-vps3
8. Documentar en sistema-mapa.md

## Mientras tanto

Las skills se consumen directamente por Claude Code/Agent SDK leyendo
`skills/*/SKILL.md` + `tools.json`. El MCP server agrega valor cuando hay
clientes MCP arbitrarios (ej: el 5to agente futuro corriendo en otra
infraestructura).
