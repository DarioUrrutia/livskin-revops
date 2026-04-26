---
runbook: disk-full
severity: high
auto_executable: false  # depende del VPS — algunos cleanup son safe, otros no
trigger:
  - "disk_pct >= 85"
  - "evento infra.disk_warning del sensor"
required_secrets: []
commands_diagnose:
  - "ssh livskin-{wp|ops|erp} 'df -h /'"
  - "ssh livskin-{wp|ops|erp} 'du -sh /var/log /var/lib/docker /srv/backups /home 2>/dev/null | sort -h'"
  - "ssh livskin-{wp|ops|erp} 'docker system df 2>/dev/null'"
commands_fix:
  - "ssh livskin-{wp|ops|erp} 'docker system prune -af --volumes' # CUIDADO: borra unused"
  - "ssh livskin-{wp|ops|erp} 'sudo journalctl --vacuum-time=7d'"
  - "ssh livskin-{wp|ops|erp} 'find /var/log -name \"*.log\" -mtime +30 -delete'"
commands_verify:
  - "ssh livskin-{wp|ops|erp} 'df -h /'"
escalation:
  if_fail: "DO panel — resize droplet a plan superior"
related_skills:
  - livskin-ops
---

# Disco lleno (>85%)

## Síntomas
- Sensor reporta `disk_pct >= 85%`
- Containers fallan al escribir
- nginx logs paran de actualizarse
- pg_dump falla

## Diagnóstico

```bash
# 1. Ver uso global
ssh livskin-erp 'df -h /'

# 2. Ver qué directorios consumen más
ssh livskin-erp 'sudo du -sh /var/log /var/lib/docker /srv/backups /home /tmp 2>/dev/null | sort -h'

# 3. Si hay docker — ver imágenes/volúmenes huérfanos
ssh livskin-erp 'docker system df'
```

## Fix por causa común

### A. Logs grandes
```bash
# journald (systemd)
ssh livskin-erp 'sudo journalctl --vacuum-time=7d'

# Logs de docker (rotación)
ssh livskin-erp 'sudo find /var/lib/docker/containers -name "*.log" -size +100M -exec truncate -s 0 {} \;'

# Logs de nginx (>30 días)
ssh livskin-erp 'sudo find /var/log/nginx -name "*.log*" -mtime +30 -delete'
```

### B. Imágenes Docker huérfanas

```bash
# CUIDADO: borra imágenes/networks/volumes no usados.
# NO usar --volumes si tienes data en volumes anonimos!
ssh livskin-erp 'docker image prune -af'
ssh livskin-erp 'docker network prune -f'
```

### C. Backups locales viejos (>30 días)

```bash
ssh livskin-erp 'find /srv/backups/local -maxdepth 1 -type f -mtime +30 -delete'
```

### D. Postgres bloat (autovacuum no funcionó)

```bash
# Verificar bloat
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  SELECT relname, n_dead_tup, n_live_tup
  FROM pg_stat_user_tables
  WHERE n_dead_tup > 1000
  ORDER BY n_dead_tup DESC LIMIT 5;"'

# Si hay tablas con bloat → VACUUM FULL (bloquea, hacer en horario bajo)
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "VACUUM FULL ANALYZE;"'
```

## Verificación

```bash
ssh livskin-erp 'df -h /'  # ahora <80%
```

## Escalación

Si después de cleanup el disco sigue >80%:
- DO panel → resize droplet a plan superior
- O: mover backups a object storage (S3-compatible)

## Por qué este runbook NO es auto_executable

Aunque `docker system prune` y limpieza de logs son SAFE en general, en
casos edge:
- `docker volume prune` puede borrar data de containers detenidos pero válidos
- VACUUM FULL bloquea tablas y puede afectar usuarios activos

→ siempre confirmar con Dario antes de ejecutar.
