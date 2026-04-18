# Content Agent — Creative Factory

**Rol:** generar y desplegar contenido para redes sociales y anuncios semanalmente. Resolver el cuello de botella creativo.

**Fase de construcción:** Fase 5 (Semana 7)

## Objetivo

- Research automático de competencia en Meta Ad Library (domingos)
- Análisis de performance del contenido semana anterior
- Generación de **12 briefs completos** (copy + hook + CTA + descripción visual)
- Producción automatizada con Claude Design + Canva + fal.ai
- 4 formatos por brief: feed, story, reel, banner

## Creative Factory — sub-estructuras

Siguiendo el "Momento 08" del blueprint:

| Sub-rol | Qué hace |
|---|---|
| Research | Scrapea Meta Ad Library para competencia (Cusco + clínicas estéticas Perú) |
| Concept | Genera 30 conceptos (propone, evalúa, selecciona 12) |
| Production | Orquesta Claude Design + Canva + fal.ai |
| Testing | Define matriz de testing (parejas variable creativa) |
| Learning Loop | Alimenta creative_memory (L5) con resultados |

## Tools

- `meta_ad_library_search(query, region)` → research competencia
- `meta_ads_get_performance(date_range)` → performance semana anterior
- `brain_get_winning_creatives(treatment, limit=10)` → L5 del cerebro
- `brain_get_learnings(category='creative', limit=5)` → L6 del cerebro
- `canva_create_design_from_brief(brief)` → producción vía API Canva
- `fal_generate_image(prompt, style)` → visual conceptual
- `claude_design_export_to_canva(brief)` → vía Claude Design
- `brain_save_brief(brief)` → guarda brief en L5 con text embedding

## Intervención humana

15 minutos los domingos 22:00 revisando miniaturas:
- Apruebas ✅ / rechazas ❌ / pides ajuste
- Sistema re-genera lo rechazado automáticamente
- Los aprobados pasan al Acquisition Engine el lunes

## Videos testimoniales (protocolo)

Cuando paciente graba video:
1. Sube a Google Drive
2. Whisper transcribe
3. Claude identifica 6 mejores momentos
4. FFmpeg corta clips con subtítulos + branding
5. Resultado: 6 reels listos

## Referencias

- ADR-0030 — Content Agent Creative Factory
- ADR-0045 — Integración Claude Design + Canva + fal.ai
- ADR-0046 — Pipeline landing pages

## Estado actual

⏳ Pendiente — construcción en Fase 5 (Semana 7).
