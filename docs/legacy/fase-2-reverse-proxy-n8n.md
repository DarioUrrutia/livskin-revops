# FASE 2 — Reverse Proxy + Cloudflare + n8n

## Estado
FASE 2 completada con despliegue funcional.

## Infraestructura
- VPS DigitalOcean FRA1
- IP: 167.172.97.197
- Usuario: livskin

## Seguridad
- UFW activo
- Puertos abiertos:
  - 22 (SSH)
  - 80 (HTTP)
  - 443 (HTTPS)
- Política:
  - deny incoming
  - allow outgoing

## Nginx
- desplegado en Docker
- expone:
  - 80
  - 443
- actúa como reverse proxy

## Red Docker
- red externa: revops_net
- comunicación interna por nombre de servicio

## n8n
- desplegado en Docker
- no expone puertos al host
- accesible vía Nginx
- volumen persistente:
  - ~/apps/n8n/data

## Cloudflare
- subdominio: flow.livskin.site
- proxy activo
- Always Use HTTPS activo
- modo SSL: Flexible

## Problemas encontrados
1. Nginx fallaba al resolver upstream n8n
2. permisos incorrectos en volumen de n8n
3. error de secure cookie en HTTP
4. error 521 al usar Cloudflare Full sin TLS en origen

## Estado pendiente
- implementar TLS en Nginx
- cambiar Cloudflare a Full (strict)

## Regla clave
Solo Nginx expone puertos.
Servicios internos nunca se exponen directamente.
