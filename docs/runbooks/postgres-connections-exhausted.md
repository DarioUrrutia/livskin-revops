---
runbook: postgres-connections-exhausted
severity: high
auto_executable: false
trigger:
  - "postgres logs muestran 'too many connections'"
  - "erp-flask falla con 'connection pool full'"
required_secrets: []
commands_diagnose:
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -c \"SELECT count(*) FROM pg_stat_activity;\"'"
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -c \"SELECT pid, usename, state, query_start, left(query,80) FROM pg_stat_activity WHERE state != \\\"idle\\\" ORDER BY query_start;\"'"
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -c \"SHOW max_connections;\"'"
commands_fix:
  - "# Identificar conexiones idle viejas y matarlas (con autorización):"
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = \\\"idle\\\" AND state_change < NOW() - INTERVAL \\\"1 hour\\\" AND pid != pg_backend_pid();\"'"
commands_verify:
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -c \"SELECT count(*) FROM pg_stat_activity;\"'"
escalation:
  if_fail: "aumentar max_connections en postgres.conf + restart"
related_skills:
  - livskin-ops
---

# Postgres connections agotadas

## Síntomas
- erp-flask logs: `connection pool full`, `FATAL: too many connections`
- Tests fallan con `psycopg2.OperationalError`
- Containers que usan postgres caen en healthcheck

## Diagnóstico

```bash
# Conexiones actuales vs max
ssh livskin-erp 'docker exec postgres-data psql -U postgres -c "
  SELECT count(*), max_conn
  FROM pg_stat_activity, (SELECT setting::int AS max_conn FROM pg_settings WHERE name=\"max_connections\") s
  GROUP BY max_conn;
"'

# Quién está conectado
ssh livskin-erp 'docker exec postgres-data psql -U postgres -c "
  SELECT pid, usename, application_name, state, state_change, left(query, 80)
  FROM pg_stat_activity
  ORDER BY state_change DESC LIMIT 30;
"'
```

## Fix

### Paso 1: matar conexiones idle viejas (con autorización Dario)

```bash
ssh livskin-erp 'docker exec postgres-data psql -U postgres -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = \"idle\"
    AND state_change < NOW() - INTERVAL \"1 hour\"
    AND pid != pg_backend_pid();
"'
```

### Paso 2: si persiste, restart erp-flask (libera connection pool)

```bash
ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/erp-flask && docker compose restart'
```

### Paso 3: aumentar max_connections (cambio permanente, requiere restart)

```bash
# Editar postgres-data config (mount custom postgres.conf si no hay)
# O via env var en docker-compose:
#   command: postgres -c max_connections=200

ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/postgres-data && docker compose down && docker compose up -d'
```

## Verificación

```bash
ssh livskin-erp 'docker exec postgres-data psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"'
# Debe ser <50 (margen para nuevas conexiones)
```

## Escalación

Si max_connections=200 sigue saturándose → connection leak en algún
service. Buscar en código `Session()` sin context manager.
