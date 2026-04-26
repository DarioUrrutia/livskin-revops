---
runbook: vpc-down
severity: critical
auto_executable: false
trigger:
  - "cross-VPS calls timeouts (10.114.0.x unreachable)"
  - "metabase no carga data desde livskin_erp"
  - "sensor recolector reporta error en los 3 VPS"
required_secrets: []
commands_diagnose:
  - "ssh livskin-erp 'ping -c 3 10.114.0.2'"
  - "ssh livskin-erp 'ping -c 3 10.114.0.3'"
  - "ssh livskin-ops 'ping -c 3 10.114.0.4'"
  - "doctl compute droplet list --format ID,Name,PrivateIPv4"
  - "# Verificar status DO: https://status.digitalocean.com"
commands_fix:
  - "# DO VPC down → no podemos arreglarlo, pero hay fallbacks:"
  - "# 1. Cambiar metabase a usar IP pública de VPS 3 (cross-VPS via internet)"
  - "# 2. Cambiar n8n → erp-flask call para usar URL pública (https://erp.livskin.site)"
commands_verify:
  - "ssh livskin-erp 'ping -c 3 10.114.0.2'"
  - "# Latencia <10ms inter-VPS"
escalation:
  if_fail: "abrir ticket a DigitalOcean support"
related_skills:
  - livskin-ops
---

# DigitalOcean VPC inaccesible

## Síntomas
- `ping 10.114.0.x` desde otro VPS → timeout
- Cross-VPS queries de metabase a postgres-data fallan
- Sensors no pueden pollear cross-VPS
- Backups cross-VPS fallan

## Contexto

VPC `10.114.0.0/20` Frankfurt aloja:
- 10.114.0.2 — livskin-vps-operations (VPS 2)
- 10.114.0.3 — livskin-wp (VPS 1)
- 10.114.0.4 — livskin-vps-erp (VPS 3)

Si VPC está caída, los servicios públicos siguen funcionando (HTTPS via
Cloudflare) pero pierden:
- Cross-VPS queries
- Backups cross-VPS
- Sensors recolección
- (Pre-Fase 6) replicación postgres

## Diagnóstico

```bash
# 1. Ping cross-VPS
ssh livskin-erp 'ping -c 3 10.114.0.2'  # debe responder <2ms
ssh livskin-erp 'ping -c 3 10.114.0.3'

# 2. Confirmar que IPs privadas siguen asignadas
doctl compute droplet list --format ID,Name,PrivateIPv4

# 3. Status oficial DO
curl -s https://status.digitalocean.com/api/v2/status.json | jq

# 4. Test desde VPS 1 → 3
ssh livskin-wp 'ping -c 3 10.114.0.4'
```

## Fix

VPC down es problema de infraestructura DigitalOcean — **no podemos
arreglarlo**, pero podemos mitigar:

### Mitigación 1: usar URLs públicas en lugar de IPs privadas

Para servicios críticos cross-VPS:

```yaml
# Antes (interno VPC):
# metabase database connection: jdbc:postgresql://10.114.0.4:5432/livskin_erp

# Después (público vía Cloudflare):
# metabase database connection: jdbc:postgresql://erp-data.livskin.site:5432/livskin_erp
```

Requiere:
1. Crear DNS `erp-data.livskin.site` → IP pública VPS 3
2. Abrir UFW puerto 5432 desde IP pública VPS 2
3. Postgres pg_hba.conf permitir IP pública VPS 2
4. ⚠️ **WARNING**: postgres expuesto público. Solo aceptable temporalmente.

### Mitigación 2: pausar servicios non-critical

- Pausar cron de sensors (no son críticos para operación)
- Pausar backups cross-VPS hasta que vuelva VPC

## Verificación

```bash
# Cuando VPC vuelva
ssh livskin-erp 'ping -c 3 10.114.0.2'  # debe responder
```

## Escalación

1. Status page DO: https://status.digitalocean.com
2. Si está down a nivel regional → ticket a soporte (priority 2)
3. Si problema solo del VPC tuyo → ticket urgente (priority 1)
4. Documentar incidente: tiempo de inicio + impacto

## Post-incidente

- Revertir mitigaciones (cerrar puertos públicos, etc.)
- Documentar en `docs/audits/`
- Considerar segundo VPS de backup en otra región
