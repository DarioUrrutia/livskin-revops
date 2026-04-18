# Google — GA4, GTM, Search Console

Tracking secundario (Meta es principal). Uso para analítica adicional y posible Ads futuro.

## Componentes

| Componente | Uso | Estado |
|---|---|---|
| Google Analytics 4 (GA4) | Analytics web client-side + server-side | ⏳ Fase 3 |
| Google Tag Manager (GTM) | Contenedor universal de tags | ⏳ Fase 3 |
| Google Search Console | SEO visibility | ✅ existe (a verificar configuración) |
| Google Ads | Posible canal secundario | 💤 fuera MVP |
| Google Business Profile | SEO local | ✅ existe (probable) |

## GA4

### Eventos trackados

Client-side via GTM:
- `page_view` (estándar)
- `view_content` con `item_name` del tratamiento
- `generate_lead` al form submit
- `click_to_whatsapp`

Server-side via Measurement Protocol en n8n:
- `generate_lead` (duplicado para match)
- `purchase` con transaction_id, revenue, items

### Secretos

```bash
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=...  # para Measurement Protocol
```

## GTM

Container con tags:
- Meta Pixel (via PixelYourSite o nativo GTM)
- GA4 configuration tag
- Eventos custom

### Variables

```bash
GTM_CONTAINER_ID=GTM-XXXXXXX
```

## Search Console

- Property: `livskin.site`
- Verificar indexación
- Monitorear queries que traen tráfico orgánico
- Sitemap enviado

## Referencias

- Measurement Protocol: https://developers.google.com/analytics/devguides/collection/protocol/ga4
- GTM docs: https://developers.google.com/tag-manager
- ADR-0019 — Tracking architecture
