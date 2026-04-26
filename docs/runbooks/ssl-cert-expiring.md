---
runbook: ssl-cert-expiring
severity: medium
auto_executable: true
trigger:
  - "cert.days_until_expiry < 14"
  - "evento infra.cert_warning del sensor"
required_secrets:
  - LETSENCRYPT_EMAIL  # solo VPS 1 (certbot)
commands_diagnose:
  - "echo | openssl s_client -connect erp.livskin.site:443 -servername erp.livskin.site 2>/dev/null | openssl x509 -noout -dates"
  - "echo | openssl s_client -connect livskin.site:443 -servername livskin.site 2>/dev/null | openssl x509 -noout -dates"
  - "ssh livskin-wp 'sudo certbot certificates'"
commands_fix:
  - "ssh livskin-wp 'sudo certbot renew --nginx'"
  - "ssh livskin-wp 'sudo systemctl reload nginx'"
commands_verify:
  - "echo | openssl s_client -connect livskin.site:443 -servername livskin.site 2>/dev/null | openssl x509 -noout -enddate"
  - "curl -sI https://livskin.site | grep -i 'HTTP/'"
escalation:
  if_fail: "renovación manual con --manual flag + DNS challenge"
related_skills:
  - livskin-ops
---

# SSL cert expirando

## Síntoma
- Cert TLS de un dominio (livskin.site, erp.livskin.site, etc.) tiene <14 días para expirar
- Sensor `livskin-sensor` reporta evento `infra.cert_warning`
- O Cloudflare alerta sobre cert backend expirando

## Contexto

| VPS | Dominio(s) | Tipo cert | Renovador |
|---|---|---|---|
| VPS 1 | livskin.site, www.livskin.site | Let's Encrypt | certbot (auto-renew) |
| VPS 2 | flow.livskin.site, crm.livskin.site, dash.livskin.site | Cloudflare Origin Cert wildcard | manual (15 años) |
| VPS 3 | erp.livskin.site | Cloudflare Origin Cert wildcard | manual |

## Diagnóstico

```bash
# Ver fechas de expiración
echo | openssl s_client -connect erp.livskin.site:443 -servername erp.livskin.site 2>/dev/null \
  | openssl x509 -noout -dates

# En VPS 1, listar todos los certs
ssh livskin-wp 'sudo certbot certificates'

# Ver cron de auto-renew
ssh livskin-wp 'cat /etc/cron.d/certbot'
```

## Fix

### Caso 1: VPS 1 — Let's Encrypt (auto-renovable)

```bash
# Forzar renovación
ssh livskin-wp 'sudo certbot renew --nginx'

# Reload nginx para usar el nuevo cert
ssh livskin-wp 'sudo systemctl reload nginx'
```

### Caso 2: VPS 2 / VPS 3 — Cloudflare Origin Cert

Estos certs son wildcards `*.livskin.site` válidos por 15 años. Si están
expirando es porque el cert original (creado en setup inicial) llegó a
fin de vida.

```bash
# 1. Crear nuevo Origin Cert en Cloudflare:
#    https://dash.cloudflare.com → SSL/TLS → Origin Server → Create Certificate
#    Hostname: *.livskin.site
#    Validez: 15 años

# 2. Copiar a cada VPS:
scp livskin-origin.crt livskin-ops:/home/livskin/apps/nginx/certs/
scp livskin-origin.key livskin-ops:/home/livskin/apps/nginx/certs/
scp livskin-origin.crt livskin-erp:/srv/livskin-revops/infra/docker/nginx-vps3/certs/
scp livskin-origin.key livskin-erp:/srv/livskin-revops/infra/docker/nginx-vps3/certs/

# 3. Reload nginx en cada VPS:
ssh livskin-ops 'docker exec nginx nginx -s reload'
ssh livskin-erp 'docker exec nginx-vps3 nginx -s reload'
```

## Verificación

```bash
# El cert nuevo debe responder con fecha futura
echo | openssl s_client -connect livskin.site:443 2>/dev/null \
  | openssl x509 -noout -enddate

# El sitio debe responder 200/301
curl -sI https://livskin.site | head -1
```

## Escalación

Si certbot falla en VPS 1:
- Verificar DNS apunta a IP correcta de VPS 1 (`46.101.97.246`)
- Verificar UFW permite puerto 80 (Let's Encrypt usa HTTP-01 challenge)
- Forzar manual: `certbot certonly --manual --preferred-challenges dns -d livskin.site`

Si Cloudflare cert no se puede crear:
- Verificar que el dominio está activo en Cloudflare
- Verificar permisos del API token (necesita `SSL: Edit`)
