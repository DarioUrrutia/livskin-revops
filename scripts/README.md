# scripts/ — Scripts de operación local (laptop)

Scripts Python que corren **desde la laptop de Dario** (no en VPS) para auditar/configurar sistemas externos via API. Distintos de `infra/scripts/` que son scripts shell para operación dentro de los VPS.

## Inventario

| Script | Propósito | Auth requerida |
|---|---|---|
| `google_oauth_setup.py` | OAuth user flow inicial — abre browser, Dario autoriza, guarda refresh token en `keys/google-oauth-token.json` | OAuth Client ID (`keys/google-oauth-client.json`) |
| `google_audit.py` | Audit programático stack Google (GA4 properties + GTM container + tags) — read-only, ~1.500 lines de output | refresh token Google |
| `gtm_inspect_workspace.py` | Lista variables/triggers/tags del workspace GTM actual | refresh token Google con tagmanager.readonly |
| `gtm_build_tracking_engine.py` | Construye Tracking Engine (Custom HTML tag + variables + triggers) en GTM workspace — UTM persistence + form_submit + whatsapp_click + scroll | refresh token Google con tagmanager.edit.containers |
| `gtm_publish_v18.py` | Publica el workspace GTM como nueva versión live | refresh token Google con tagmanager.publish |

## Cuándo correrlos

- **`google_oauth_setup.py`**: una sola vez (o cuando expire refresh token, ~6 meses)
- **`google_audit.py`**: cuando necesites verificar estado actual stack Google (after deploy, debugging, etc.)
- **`gtm_*.py`**: durante setup tracking (mini-bloque 3.2 Fase 3) o cuando rehagamos config

## Pre-requisitos

- Python 3.10+
- `pip install -r requirements.txt` (Google API client + auth libraries)
- `keys/google-oauth-client.json` y `keys/google-oauth-token.json` presentes (gitignored)

## Comparación con `infra/scripts/`

| | `scripts/` (laptop) | `infra/scripts/` (VPS) |
|---|---|---|
| **Lenguaje** | Python | Shell (Bash) |
| **Naming** | `snake_case.py` (PEP 8) | `kebab-case.sh` |
| **Corre en** | Laptop Dario | VPS 1/2/3 |
| **Propósito** | Audit + setup APIs externas | Ops internos VPS (alembic, backups, brain-index) |
| **Auth** | Tokens Google/Meta locales | SSH keys + audit_internal_token |

## Ejemplos

```bash
# Audit completo Google stack (read-only)
python scripts/google_audit.py

# Re-publicar GTM container con nueva config
python scripts/gtm_publish_v18.py

# Re-OAuth (cuando expire token)
python scripts/google_oauth_setup.py
```
