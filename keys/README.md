# keys/ — Claves SSH y configuración

Este directorio contiene material sensible (claves privadas, tokens). **Casi todo está gitignored** con excepciones específicas versionadas.

## Qué SÍ se versiona (en git)

| Archivo | Propósito |
|---|---|
| `README.md` | Este archivo |
| `ssh_config` | Aliases SSH para los 3 VPS. No contiene secretos (IPs y paths). |

## Qué NO se versiona (gitignored)

| Archivo | Por qué |
|---|---|
| `claude-livskin`, `claude-livskin.pub` | Claves SSH Ed25519 de Claude Code (privada obviamente no) |
| `livskin-do.ppk` | PuTTY private key para VPS 1 (WordPress) |
| `livskin-vps-operations.ppk` | PuTTY private key para VPS 2 (Operations) |
| `livskin-vps-erp.ppk` | PuTTY private key para VPS 3 (ERP) |
| `livskin-vps-erp.pub` | (opcional) pública respaldada como texto |
| `.env.integrations` | Tokens API de Meta, Anthropic, WhatsApp, fal.ai, Canva, Cloudflare |
| `known_hosts` | Huellas dactilares SSH aprendidas localmente |

## Setup en una máquina nueva

Cuando clones el repo en otra laptop (ej: trabajo):

1. `git clone https://github.com/DarioUrrutia/livskin-revops.git`
2. Los archivos `*.ppk` y `claude-livskin*` y `.env.integrations` **no estarán** (gitignored)
3. Bajar `.env.integrations` desde Bitwarden
4. Las `.ppk` de PuTTY: transferencia manual entre máquinas (USB, email cifrado, o regenerar)
5. La key `claude-livskin` de Claude Code: regenerar con `ssh-keygen -t ed25519 -f keys/claude-livskin -C "claude-code@<machine>"` y **agregar su pub key al authorized_keys de cada VPS** (mismo flow que hicimos con la original)

## Rotación de keys

Programada trimestralmente según ADR-0003. Ver runbook `docs/runbooks/key-rotation.md` (pendiente).

## Conectar con ssh_config

```bash
ssh -F keys/ssh_config livskin-wp    # VPS 1 WordPress
ssh -F keys/ssh_config livskin-ops   # VPS 2 Operations
ssh -F keys/ssh_config livskin-erp   # VPS 3 ERP
```

Ver memoria `vps_access.md` para detalles de IPs y credenciales.
