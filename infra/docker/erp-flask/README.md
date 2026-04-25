# erp-flask — ERP Livskin refactorizado

ERP refactorizado de Livskin (era Flask + Google Sheets en Render → ahora Flask + Postgres en VPS 3).

## Estado

🚧 **En construcción** (Fase 2 implementación). Schema definido (12 tablas), models SQLAlchemy en `models/`, routes/services se agregan progresivamente.

**No es producción aún** — vive en dormant standby per ADR-0024.

## Estructura

```
erp-flask/
├── app.py                  # Flask init
├── config.py               # Pydantic Settings (lee env vars)
├── models/                 # SQLAlchemy declarative models (12 tablas)
├── schemas/                # Pydantic v2 (request/response) — futuro
├── services/               # Business logic — futuro
├── routes/                 # Flask blueprints — futuro
├── middleware/             # Auth, audit, errors — futuro
├── templates/              # HTML (formulario.html preservado del Render) — futuro
├── tests/                  # pytest, coverage ≥75% — futuro
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Modelos definidos

Ver `models/` — cada archivo es una entidad:

| Archivo | Tabla | ADR origen |
|---|---|---|
| `cliente.py` | `clientes` | 0011 v1.1 |
| `lead.py` | `leads` | 0011 v1.1 + 0013 v2 |
| `lead_touchpoint.py` | `lead_touchpoints` | 0011 v1.1 + 0013 v2 |
| `venta.py` | `ventas` | 0011 v1.1 |
| `pago.py` | `pagos` | 0011 v1.1 |
| `gasto.py` | `gastos` | 0011 v1.1 |
| `catalogo.py` | `catalogos` | 0011 v1.1 + 0014 |
| `dedup_candidate.py` | `dedup_candidates` | 0013 v2 |
| `form_submission.py` | `form_submissions` | 0011 v1.1 |
| `user.py` | `users` | 0026 |
| `user_session.py` | `user_sessions` | 0026 |
| `audit_log.py` | `audit_log` | 0027 |

## Comandos típicos

**Build:**
```bash
docker compose build
```

**Generar migration desde models** (vía alembic-erp container):
```bash
cd ../alembic-erp
docker compose run --rm alembic-erp revision --autogenerate -m "descripción"
```

**Aplicar migrations:**
```bash
cd ../alembic-erp
docker compose run --rm alembic-erp upgrade head
```

**Run app local (dev):**
```bash
docker compose up
```

## Referencias

- ADR-0023 (estrategia refactor)
- ADR-0011 v1.1 (modelo de datos)
- ADR-0026 (auth)
- ADR-0027 (audit log)
- Memoria `project_erp_migration` (principios)
