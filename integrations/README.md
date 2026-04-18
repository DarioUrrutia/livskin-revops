# Integraciones externas

Cada carpeta contiene documentación, configuración (no-secreta) y referencias para un servicio externo al stack Livskin.

## Estructura de cada integración

```
integrations/<proveedor>/
├── README.md         # qué está configurado, IDs, links al panel, estado
├── .env.example      # variables requeridas (sin valores)
└── configs/          # exports de configuración (JSON, XML si aplica)
```

**Secretos reales** viven en `keys/.env.integrations` (gitignored) + respaldo cifrado Bitwarden.

## Integraciones del proyecto

| Carpeta | Proveedor | Estado | Dossiers relacionados |
|---|---|---|---|
| [meta/](meta/) | Meta (Facebook Business, Ads, Pixel, CAPI, WhatsApp Cloud) | ⏳ por configurar | ADR-0019, ADR-0028 |
| [google/](google/) | Google (GA4, GTM, Search Console, Ads futuro) | ⏳ por configurar | ADR-0019 |
| [whatsapp/](whatsapp/) | WhatsApp Cloud API — test number + prod | ⏳ Fase 0 | ADR-0028, ADR-0038 |
| [cloudflare/](cloudflare/) | DNS, SSL, WAF, proxy | ✅ activo 4 subdominios | ADR-0003 |
| [canva/](canva/) | Canva Pro Brand Kit + API | ✅ activo, API por configurar | ADR-0030 |
| [anthropic/](anthropic/) | Claude API (4 agentes) + budget | ⏳ Fase 0 | — |
| [fal-ai/](fal-ai/) | Flux Pro para imágenes conceptuales | ⏳ Fase 0 | ADR-0030 |
| [claude-design/](claude-design/) | Claude Design (research preview) para landing pages y banners | ⏳ Fase 5 | ADR-0045 |

## Principio rector

- Este folder es la **fuente de verdad de "qué está configurado dónde"**.
- Cada README lista: IDs públicos, links al panel, propósito, quién tiene acceso, estado actual.
- Nunca se commitean tokens, passwords, access_tokens, client_secrets.
