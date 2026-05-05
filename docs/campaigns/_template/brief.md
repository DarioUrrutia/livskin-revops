---
campaign_slug: {{CAMPAIGN_SLUG}}
campaign_name: {{CAMPAIGN_NAME}}
treatment_canonical: {{TREATMENT}}
mode: CAMPAÑA
declared_by: {{DECLARED_BY}}
declared_at: {{DECLARED_AT}}
purpose: |
  {{PURPOSE}}
hypothesis_main: |
  {{HYPOTHESIS}}
hypothesis_secondary:
  - (a llenar)
budget_pen: {{BUDGET_PEN}}
start_date: {{START_DATE}}
end_date: {{END_DATE}}
shortcode_prefix: {{SHORTCODE_PREFIX}}
ad_account: {{AD_ACCOUNT}}
pixel_id: {{PIXEL_ID}}
wa_phone_e164: {{WA_PHONE_E164}}
status: planning
---

# Brief — {{CAMPAIGN_NAME}}

> **Modo:** CAMPAÑA — declarado por {{DECLARED_BY}} el {{DECLARED_AT}}.

---

## 1. Por qué existe esta campaña

{{PURPOSE}}

## 2. Hipótesis principal a validar

{{HYPOTHESIS}}

## 3. Hipótesis secundarias

- (a llenar — qué sub-experimentos correrán dentro de la campaña)

## 4. Audiencia objetivo

- **Geo:** (a llenar)
- **Demo:** (a llenar — edad, género)
- **Idioma:** (a llenar)
- **Custom Audiences:** (a llenar — INCLUDE / EXCLUDE)
- **Intereses:** (a llenar)

## 5. Métricas de éxito

| Métrica | Mínimo aceptable | Objetivo | Excelente |
|---|---|---|---|
| Leads totales (mensajes WA + form) |  |  |  |
| Cost per lead (CPL) |  |  |  |
| Conversion rate lead → cliente |  |  |  |
| Revenue total estimado |  |  |  |

## 6. Restricciones operativas

- (a llenar — bloqueos conocidos, dependencias, restricciones de tiempo, etc.)

## 7. Modo de ejecución

- ☑ **Manual UI** (Dario click-a-click siguiendo `meta-ads-configuracion.md`)
- ☐ **Híbrido** (algunos pasos automatizados)
- ☐ **API Automatizada** (Brand Orchestrator agente)

## 8. Cronograma resumido

| Fecha | Hito |
|---|---|
| {{START_DATE}} | Lanzamiento |
| {{END_DATE}} | Cierre |
| (a llenar) | Post-mortem |

---

**Status del brief:** `planning` → marcar como `approved` cuando esté listo para arrancar producción.
