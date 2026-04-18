# Cloudflare — DNS, SSL, WAF, Proxy

Puerta pública única del sistema. Todo el tráfico externo pasa por Cloudflare.

## Zonas gestionadas

- `livskin.site` — zona principal

## DNS records (estado actual)

| Subdominio | Tipo | Destino | Proxy |
|---|---|---|---|
| `livskin.site` | A | 46.101.97.246 | ✅ proxied |
| `www.livskin.site` | CNAME | `livskin.site` | ✅ |
| `flow.livskin.site` | A | 167.172.97.197 | ✅ |
| `crm.livskin.site` | A | 167.172.97.197 | ✅ |
| `dash.livskin.site` | A | 167.172.97.197 | ✅ |
| `erp.livskin.site` | A | _pendiente VPS 3_ | ✅ (Fase 1) |
| `erp-staging.livskin.site` | A | _pendiente VPS 3_ | ✅ (Fase 1) |

Registros MX / SPF / DKIM / DMARC — revisar en Fase 0 trimestral.

## SSL / TLS

- **Mode:** Full (Strict) — valida cert en origen
- **Edge cert:** Universal SSL (gratis Cloudflare)
- **Origin cert:** Cloudflare Origin Cert (15 años) en VPS 2 y 3 — wildcard para `*.livskin.site`
- **Minimum TLS:** 1.2
- **Always Use HTTPS:** Activo
- **HSTS:** Activo (max-age 6 meses, includeSubDomains)

VPS 1 usa **Let's Encrypt** directo (no origin cert CF) porque es la zona raíz livskin.site — conviene tener cert público independiente. Auto-renewal vía certbot.

## WAF

- Managed Rules: OWASP Core Ruleset activado
- Rate Limiting: configurar reglas en Fase 3 para endpoints críticos (login, form submit)
- Bot Fight Mode: activo
- Challenge Passage: 30 min

## Page Rules (a configurar)

Pendiente Fase 3:
- Cache aggressive en `livskin.site/wp-content/uploads/*`
- Bypass cache en `flow.livskin.site/*` (webhooks)
- Bypass cache en `erp.livskin.site/*` y `erp-staging.livskin.site/*`

## Variables de entorno

```bash
CF_API_TOKEN=...       # scoped a zona livskin.site, permisos mínimos
CF_ZONE_ID=...
CF_ACCOUNT_ID=...
```

## Referencias

- Cloudflare docs: https://developers.cloudflare.com/
- ADR-0003 — Seguridad baseline (sección S1 Red externa)
- ADR-0004 — Comunicación entre VPS (DO VPC — complementaria a Cloudflare público)
