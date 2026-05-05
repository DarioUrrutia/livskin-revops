# Template — Cómo arrancar una campaña nueva

> ⚠️ **NO uses este template sin declarar primero MODO CAMPAÑA.**
>
> Lee `CLAUDE.md` principio #12 antes de proceder. Una campaña sin propósito declarado se desvía.

---

## El protocolo en 3 pasos

### Paso 1 — Declarar MODO CAMPAÑA (en voz alta)

Antes de tocar archivos, declarás explícitamente:

```
"Entrando a MODO CAMPAÑA para [SLUG-DE-CAMPAÑA].

Esta campaña existe para [propósito en 1-2 líneas].

Hipótesis principal a validar: [hipótesis testable].

Budget: S/ XXX · Fechas: YYYY-MM-DD a YYYY-MM-DD"
```

Sin esa declaración, **no se ejecuta el script**. Esto NO es burocracia — es la diferencia entre campañas con foco y campañas que se desvían.

### Paso 2 — Ejecutar el script

```bash
python scripts/new-campaign.py
```

El script te va a forzar a articular:
- Slug de la campaña
- Tratamiento canónico
- Propósito (1-2 líneas)
- Hipótesis principal a validar
- Budget en PEN
- Fechas (inicio + fin)
- Shortcode prefix
- Ad Account ID, Pixel ID, WhatsApp E.164

Solo entonces clona los 9 archivos esqueleto a `docs/campaigns/<SLUG>/` con los placeholders rellenados.

### Paso 3 — Revisar el `brief.md` generado

El brief tiene la declaración tuya embebida en el frontmatter YAML como auto-documentación. Revísalo, ajustá si necesitás, commit + push.

---

## Estructura que se genera

```
docs/campaigns/<SLUG>/
├── brief.md                        ← declaración + objetivos + hipótesis
├── plan.md                         ← plan operativo (audience, budget, timeline)
├── campaign-config-final.md        ← config técnico Meta Ads (todo listo para copiar)
├── ads-manager-checklist.md        ← clicks UI Meta paso a paso
├── cheat-sheet-doctora.md          ← imprimible A4 para la doctora
├── tracking-sheet.csv              ← header solo, sin leads
├── tracking-sheet-template.md      ← guía operativa de la doctora
├── _doctrine-feedback.md           ← captura insights del bootstrap
└── post-mortem.md                  ← template para evaluar al cierre
```

---

## Cuándo NO usar este template

- **Si NO estás en modo CAMPAÑA** → trabajá en modo PROYECTO directamente sobre el código/doctrina
- **Si estás en bootstrap activo** y querés hacer feedback bidireccional doctrina ↔ campaña → seguí los principios #12 y #13 de CLAUDE.md
- **Si la campaña no es paga** (ej: contenido orgánico, email blast) → este template está optimizado para campañas pagas Meta Ads. Otros canales requieren plantilla distinta.

---

## Referencias

- `CLAUDE.md` § principio #12 (modo declarado)
- `CLAUDE.md` § principio #13 (modo bootstrap)
- `docs/runbooks/meta-ads-configuracion.md` (comportamientos durables Meta UI)
- `docs/brand/` (doctrina de marca v0.1+)
- Última campaña real ejecutada: `docs/campaigns/2026-05-dia-madre/` (referencia para ver template instanciado)
