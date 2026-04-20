# alembic-brain — Migrations para `livskin_brain`

Sistema de versionado de schema para la DB del segundo cerebro. Cada cambio al schema (agregar columna, renombrar tabla, crear índice) se representa como un archivo Python numerado en `migrations/versions/` — reversible, auditable, reproducible.

## Cómo usar

**Desde VPS 3 (o cualquier máquina con acceso al `data_net`):**

Método largo:
```bash
cd /srv/livskin-revops/infra/docker/alembic-brain
docker compose run --rm alembic-brain <comando>
```

Método corto (script wrapper):
```bash
/srv/livskin-revops/infra/scripts/alembic-brain.sh <comando>
```

## Comandos frecuentes

| Qué quieres hacer | Comando |
|---|---|
| Ver en qué revision está el DB | `current` |
| Ver historial completo | `history` |
| Aplicar todas las migrations pendientes | `upgrade head` |
| Aplicar la siguiente (una a una) | `upgrade +1` |
| Revertir la última | `downgrade -1` |
| Crear nueva migration (vacía, llenar a mano) | `revision -m "descripcion corta"` |
| Marcar como aplicada sin ejecutar | `stamp head` |
| Generar SQL sin aplicar (dry-run) | `upgrade head --sql` |

## Setup inicial (hecho 2026-04-20)

1. Migration `0001_baseline_brain_schema.py` creada (no-op)
2. DB marcada como "en 0001" con:
   ```bash
   docker compose run --rm alembic-brain stamp head
   ```
3. Cualquier cambio futuro = migration numerada en `versions/`

## Flujo típico para un cambio de schema

Ejemplo: agregar columna `duration_minutes` a `clinic_knowledge`.

1. **Crear archivo de migration vacío:**
   ```bash
   docker compose run --rm alembic-brain revision -m "add duration_minutes to clinic_knowledge"
   ```
   Alembic crea `migrations/versions/<fecha>-<rev>_add_duration_minutes_to_clinic_knowledge.py`.

2. **Editar el archivo:**
   ```python
   def upgrade() -> None:
       op.add_column(
           "clinic_knowledge",
           sa.Column("duration_minutes", sa.Integer(), nullable=True),
       )

   def downgrade() -> None:
       op.drop_column("clinic_knowledge", "duration_minutes")
   ```

3. **Commit + push:**
   ```bash
   git add migrations/versions/<nueva migration>.py
   git commit -m "feat(brain): add duration_minutes column"
   git push
   ```

4. **Aplicar en VPS 3** (hoy manual, futuro automatizado por CI/CD):
   ```bash
   docker compose run --rm alembic-brain upgrade head
   ```

5. **Verificar:**
   ```bash
   docker compose run --rm alembic-brain current
   # Muestra la nueva revision como HEAD
   ```

## Conexión

Conecta a `postgres-data:5432/livskin_brain` como usuario `postgres` (superuser — necesario para DDL amplio).

Password leído de `../postgres-data/.env` (gitignored).

Si ves error "POSTGRES_SUPERUSER_PASSWORD no seteado":
- Verifica que `/srv/livskin-revops/infra/docker/postgres-data/.env` existe en el VPS
- Si no existe, fue olvidado copiarlo durante el setup inicial

## Estructura del directorio

```
alembic-brain/
├── Dockerfile              # image con alembic + psycopg2 + sqlalchemy
├── docker-compose.yml      # servicio oneshot (profile "oneshot")
├── alembic.ini             # config alembic (logging, script location)
├── migrations/
│   ├── env.py              # lee env vars, construye DB URL, conecta
│   ├── script.py.mako      # template de nuevas migrations
│   └── versions/
│       └── 0001_baseline_brain_schema.py   # baseline no-op
└── README.md               # este archivo
```

## Referencias

- [Alembic docs](https://alembic.sqlalchemy.org/)
- [ADR-0010](../../../docs/decisiones/README.md) — Alembic obligatorio desde día 1
- [ADR-0001 § 7](../../../docs/decisiones/0001-segundo-cerebro-filosofia-y-alcance.md) — schema del cerebro
- [infra/docker/alembic-erp/](../alembic-erp/) — gemelo para `livskin_erp`
