# Canva — Brand Kit + API

Producción visual central con consistencia de marca. Usado por el Content Agent.

## Cuenta

- Canva Pro (ya pagado)
- Brand Kit configurado con logos, colores, fuentes

## Integración con Claude Design

Claude Design (claude.ai/design) tiene **export directo a Canva** — un banner generado en Claude Design se envía a Canva fully editable. Esta es la ruta principal del pipeline creativo (ADR-0045).

## API

Canva Connect API (beta/GA — a verificar acceso):
- Endpoints para crear designs programáticamente
- Aplicar Brand Kit
- Exportar en formatos múltiples (PNG, JPG, PDF, MP4)

## Formatos de producción estándar

| Formato | Dimensiones | Uso |
|---|---|---|
| Feed square | 1080×1080 | Instagram/Facebook feed |
| Story vertical | 1080×1920 | Instagram/Facebook stories |
| Reel cover | 1080×1920 | Reels Instagram |
| Web banner | 1200×628 | Facebook ad image, OG image |
| Hero landing | 1920×1080 | Banner header de landing pages |

## Brand Kit inventario (a verificar/completar en Fase 0)

- [ ] Logo principal (versiones: full color, b/n, invertido)
- [ ] Logotipo secundario (si aplica)
- [ ] Isotipo (símbolo solo)
- [ ] Paleta de colores primarios
- [ ] Paleta de colores secundarios
- [ ] Tipografías principales (headline + body)
- [ ] Tipografías secundarias
- [ ] Iconografía standard
- [ ] Plantillas iniciales para ads

## Variables de entorno

```bash
CANVA_API_TOKEN=...            # cuando API esté disponible
CANVA_BRAND_KIT_ID=...
CANVA_TEAM_ID=...
```

## Referencias

- Canva Connect API: https://www.canva.dev/docs/connect/
- Claude Design → Canva export: flujo integrado en ADR-0045
- ADR-0030 — Content Agent Creative Factory
