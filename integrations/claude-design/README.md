# Claude Design

Herramienta de Anthropic lanzada el **2026-04-17** (research preview). Powered by Claude Opus 4.7.

URL: https://claude.ai/design

## Capacidades

- Generar mockups, prototipos, diapositivas, one-pagers, banners, diseños visuales
- Edición por prompt + sliders custom para elementos específicos del diseño
- Design system aprendido desde codebase o archivos de diseño subidos
- **Export directo a Canva** (fully editable)
- **Export directo a Claude Code** (código HTML/CSS/React)
- Export PDF, URL pública, PPTX

## Acceso

Incluido en **Claude Max** (ya pagado por Dario). Sin costo adicional.

## Uso planificado en Livskin

### Pipeline de banners (Content Agent — Fase 5)

```
Content Agent genera brief (copy + concepto visual)
    │
    ▼
Claude Design crea mockup on-brand
    │ (iteración por sliders/prompts)
    ▼
Export a Canva
    │ (Canva aplica Brand Kit final, genera variantes de formato)
    ▼
Acquisition Engine publica en Meta Ads
    │
    ▼
Performance tracking → creative_memory en segundo cerebro
```

### Pipeline de landing pages (Fase 5)

```
Tú describes "landing para Botox Wanchaq" a Claude Design
    │
    ▼
Claude Design genera visual + copy
    │
    ▼
Export a Claude Code (yo)
    │ (convierto a HTML Tailwind o WP template)
    ▼
Deploy a livskin.site/landing/botox-wanchaq
    │
    ▼
Tracking PixelYourSite + GTM automático
```

### Pitch decks y one-pagers (ad-hoc)

- One-pager para pacientes VIP con paquete facial completo
- Pitch deck de revisión trimestral de resultados
- Presentaciones para posibles partnerships

## Integración práctica

1. Al onboarding de Claude Design, subir: logos + paleta + tipografías + screenshots actuales de livskin.site
2. Claude Design aprende el design system
3. Cada brief del Content Agent se puede procesar vía Claude Design con un prompt estándar
4. Los diseños generados se guardan en `creative_memory` del segundo cerebro

## Limitaciones conocidas (research preview)

- No hay API programática aún (uso es humano vía claude.ai/design)
- Puede cambiar features mientras esté en preview
- No reemplaza Canva para producción masiva de variantes de formato

## Cuándo usar Claude Design vs Canva vs fal.ai

| Necesidad | Herramienta |
|---|---|
| Concepto visual nuevo con brand awareness | **Claude Design** → Canva |
| Variantes de formato masivas de un diseño aprobado | **Canva API** |
| Imagen conceptual/artística sin brand rígido | **fal.ai Flux** |
| Landing page como código | **Claude Design** → Claude Code (yo) |

## Referencias

- Claude Design launch: https://www.anthropic.com/news/claude-design-anthropic-labs
- Get started: https://support.claude.com/en/articles/14604416-get-started-with-claude-design
- ADR-0045 — Integración Claude Design + Canva + fal.ai
- ADR-0046 — Pipeline landing pages
