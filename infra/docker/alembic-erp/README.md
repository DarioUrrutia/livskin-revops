# alembic-erp — Migrations para `livskin_erp`

Gemelo de `alembic-brain` pero apuntando a la DB del ERP transaccional.

**Estado actual:** DB vacía (sin tablas). Las migrations empiezan a llenarse en Fase 2 cuando se refactoriza el ERP Flask con SQLAlchemy + Pydantic.

## Uso

Idéntico a alembic-brain — ver su README para comandos detallados.

Desde VPS 3:
```bash
cd /srv/livskin-revops/infra/docker/alembic-erp
docker compose run --rm alembic-erp current
docker compose run --rm alembic-erp upgrade head
docker compose run --rm alembic-erp revision -m "create clientes table"
```

O con el script wrapper:
```bash
/srv/livskin-revops/infra/scripts/alembic-erp.sh current
```

## Primera migration esperada (Fase 2)

Cuando empiece el refactor del ERP, la primera migration probablemente creará:
- `auth_users` (con los 2 usuarios fijos: tú + doctora)
- `clientes`
- `ventas`, `venta_items`
- `pagos`, `pago_asignaciones`
- `gastos`
- `audit_log`
- + índices

Cada cambio posterior = nueva migration.

## Diferencia con alembic-brain

| Aspecto | alembic-brain | alembic-erp |
|---|---|---|
| DB objetivo | `livskin_brain` | `livskin_erp` |
| Env var `ALEMBIC_DB_NAME` | `livskin_brain` | `livskin_erp` |
| Estado actual | Baseline 0001 no-op (schema creado por init scripts) | Vacío — primera migration creará el schema completo |
| Uso | Capas del segundo cerebro (6 tablas con pgvector) | Tablas transaccionales del ERP (Fase 2+) |

## Referencias

- [alembic-brain/README.md](../alembic-brain/README.md) — gemelo con más detalle
- [ADR-0010](../../../docs/decisiones/README.md) — Alembic obligatorio
- [ADR-0002 § 5.3.5](../../../docs/decisiones/0002-arquitectura-de-datos-y-3-vps.md) — schema propuesto para `livskin_erp`
