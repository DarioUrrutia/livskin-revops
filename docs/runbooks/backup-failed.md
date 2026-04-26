---
runbook: backup-failed
severity: high
auto_executable: true
trigger:
  - "evento infra.backup_failed en audit_log"
  - "cron de backup falló ($? != 0)"
  - "no hay nuevo backup en /srv/backups/* en 25h"
required_secrets:
  - AUDIT_INTERNAL_TOKEN
commands_diagnose:
  - "ssh livskin-erp 'tail -100 /var/log/livskin-backup.log'"
  - "ssh livskin-erp 'ls -la /srv/backups/local/ /srv/backups/vps2/ 2>&1'"
  - "ssh livskin-erp 'docker exec erp-flask psql -U postgres -d livskin_erp -c \"SELECT occurred_at, action, error_detail FROM audit_log WHERE action LIKE \\\"infra.backup_%\\\" ORDER BY occurred_at DESC LIMIT 10;\"'"
commands_fix:
  - "# Re-ejecutar backup script manualmente"
  - "ssh livskin-erp 'sudo -u livskin /srv/livskin-revops/infra/scripts/backups/backup-vps3.sh'"
commands_verify:
  - "ssh livskin-erp 'ls -la /srv/backups/local/livskin_erp-$(date -u +%Y-%m-%d).sql.gz'"
  - "# audit_log debe tener evento infra.backup_completed reciente"
escalation:
  if_fail: "investigar root cause: disco lleno, postgres down, ssh key expirada"
related_skills:
  - livskin-ops
---

# Backup falló

## Síntomas
- Audit log tiene `infra.backup_failed` reciente
- Cron `livskin-backups` falló
- No hay archivo nuevo en `/srv/backups/local/` para hoy

## Diagnóstico

```bash
# 1. Ver log del backup
ssh livskin-erp 'tail -100 /var/log/livskin-backup.log'

# 2. Listar últimos backups
ssh livskin-erp 'ls -laht /srv/backups/local/ | head -10'

# 3. Audit log de los últimos backups
ssh livskin-erp 'docker exec erp-flask psql -U postgres -d livskin_erp -c "
  SELECT occurred_at, action, error_detail, audit_metadata
  FROM audit_log
  WHERE action LIKE \"infra.backup_%\"
  ORDER BY occurred_at DESC LIMIT 10;
"'
```

## Causas comunes

### A. Disco destino lleno
→ ver runbook [disk-full](disk-full.md)

### B. Postgres down (no responde a pg_dump)
→ ver runbook [container-crashloop](container-crashloop.md) o [postgres-connections-exhausted](postgres-connections-exhausted.md)

### C. SSH key cross-VPS expirada / revocada
```bash
# Test SSH key
ssh livskin-erp 'sudo -u livskin ssh -i /root/.ssh/backup-target backup@10.114.0.2 echo OK'
# Si falla → ver runbook credential-leaked (rotar)
```

### D. Permisos del directorio destino
```bash
# Verificar que user backup puede escribir
ssh livskin-ops 'ls -la /srv/backups/'
ssh livskin-ops 'sudo -u backup touch /srv/backups/vps3/.test && rm /srv/backups/vps3/.test'
```

### E. Cron no corrió (systemd-timer roto)
```bash
ssh livskin-erp 'systemctl status cron'
ssh livskin-erp 'cat /etc/cron.d/livskin-backups'
```

## Fix automático (si causa común detectada)

```bash
# Re-ejecutar backup ahora
ssh livskin-erp 'sudo -u livskin /srv/livskin-revops/infra/scripts/backups/backup-vps3.sh'
```

## Verificación

```bash
# Archivo de hoy debe existir
ssh livskin-erp 'ls -la /srv/backups/local/livskin_erp-'"$(date -u +%Y-%m-%d)"'.sql.gz'

# Audit log debe tener infra.backup_completed nuevo
```

## Escalación

Si después de 2 intentos sigue fallando:
- Pingear a Dario via WhatsApp
- Backup manual desde laptop personal:
  ```bash
  ssh livskin-erp 'docker exec postgres-data pg_dump -U postgres livskin_erp' \
    | gzip > backup-emergencia-$(date +%Y%m%d).sql.gz
  ```
