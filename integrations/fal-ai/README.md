# fal.ai — Flux Pro

Generación de imágenes conceptuales IA. Usado por el Content Agent para visuales artísticos que no requieren template rígido de Brand Kit.

## Uso específico en Livskin

Con Claude Design + Canva cubriendo ~80% de la producción visual on-brand, fal.ai queda para:

- Visuales conceptuales de ads creativos (ej: metáforas, escenas)
- Imágenes hero de landing pages con concepto fuerte
- Mockups editoriales para contenido orgánico

**NO** lo usamos para retratos de pacientes reales (compliance + ética), ni para reemplazar fotos reales de resultados clínicos.

## Modelos usados

| Modelo | Uso | Costo aprox |
|---|---|---|
| Flux Pro | Imágenes fotorealistas de alta calidad | $0.05/imagen |
| Flux Schnell | Iteración rápida de concepto | $0.003/imagen |

## Presupuesto

$20/mes declarado en blueprint. A ritmo Flux Pro: ~400 imágenes/mes = suficiente.

## Variables de entorno

```bash
FAL_KEY=...
FAL_DEFAULT_MODEL=flux-pro
FAL_MONTHLY_BUDGET_USD=20
```

## Referencias

- fal.ai docs: https://fal.ai/
- Flux models: https://fal.ai/models/fal-ai/flux-pro
- ADR-0030 — Content Agent Creative Factory (define cuándo usar fal.ai vs Claude Design vs Canva)
