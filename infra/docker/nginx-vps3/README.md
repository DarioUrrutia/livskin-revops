# nginx-vps3 — Reverse proxy VPS 3

Termina TLS con Cloudflare Origin Cert wildcard y proxy-pasa a servicios internos en `data_net`.

## Qué sirve

| Host | Upstream actual | Upstream futuro (Fase 2) |
|---|---|---|
| `erp.livskin.site` | maintenance page estática | `http://erp-flask:5000` (ERP refactorizado) |
| `erp-staging.livskin.site` | maintenance page estática | `http://erp-staging-flask:5000` |
| Cualquier otro host | 444 (connection close) | 444 |

## Estructura

```
nginx-vps3/
├── docker-compose.yml
├── nginx.conf              # config main + Cloudflare real_ip + SSL defaults
├── sites/
│   ├── 00-default.conf     # catch-all 444
│   ├── erp.livskin.site.conf
│   └── erp-staging.livskin.site.conf
├── html/
│   ├── prod/index.html     # maintenance page prod
│   └── staging/index.html  # maintenance page staging (banner naranja)
└── certs/                  # gitignored
    ├── livskin-origin.crt
    └── livskin-origin.key
```

## Cert

Cloudflare Origin Cert wildcard `*.livskin.site + livskin.site`, válido hasta 2041-04-01. Reutilizado de VPS 2 (mismo cert; generar uno nuevo sería desperdicio).

**Rotación:** cuando se acerque expiración (~2040 😅). No es relevante para el MVP.

## Cloudflare real_ip

El `nginx.conf` tiene la lista de IP ranges de Cloudflare en `set_real_ip_from`. Los logs muestran la IP real del cliente (header `CF-Connecting-IP`) en vez de la IP de Cloudflare.

Lista mantenida en https://www.cloudflare.com/ips/ — actualizar cada 6 meses o si aparece traffic "desconocido" en logs.

## Deploy

```bash
cd /srv/livskin/nginx
docker compose up -d
docker compose logs -f nginx-vps3
```

## Verificación

```bash
# Desde internet (laptop de Dario):
curl -v https://erp.livskin.site
curl -v https://erp-staging.livskin.site

# Desde el host VPS 3 (direct, bypassing Cloudflare):
curl -k -v https://localhost/nginx-health
# → "ok" (pero con cert warning porque CF Origin Cert no es trusted fuera de CF)

# Hit directo a la IP sin Host header:
curl -k -v https://139.59.214.7
# → 444 connection close
```

## Cuando se despliegue ERP Flask (Fase 2)

Editar `sites/erp.livskin.site.conf`:

```nginx
# Reemplazar el block `location /` con:
location / {
    proxy_pass http://erp-flask:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $cf_connecting_ip;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
}
```

El root / try_files se borra. El maintenance page `html/prod/index.html` queda como fallback por si el ERP está caído.

## Referencias

- [ADR-0003](../../../docs/decisiones/0003-seguridad-baseline-y-auditorias.md) — headers de seguridad baseline
- [Cloudflare IP ranges](https://www.cloudflare.com/ips/)
- [VPS 2 nginx config](../nginx/) — referencia de estructura
