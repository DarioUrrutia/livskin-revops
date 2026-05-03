# Landing — Botox — Día de la Madre 2026

## Estado: NO se produce landing dedicada en esta campaña

**Decisión de diseño** (en `brief.md` + `plan.md`): Opción A — todos los ads van a Click-to-WhatsApp directo. **No hay landing de Día de la Madre Botox** en esta campaña.

---

## Razones

1. **Objetivo es maximizar contactos WhatsApp**, no leads de form (decisión Dario 2026-05-04)
2. **Audience chica de Cusco (~10-18K alcanzables)** no soporta dilución de budget entre destinos
3. **Setup más simple** = menos puntos de falla en primera campaña
4. **Doctora cierra mejor en WhatsApp** que post-form (data anecdótica)
5. **A/B landing vs WA directo se valida en próxima campaña** con datos de esta

---

## Landing evergreen actual sigue viva (no se modifica)

La landing de Botox que ya existe sigue funcionando para tráfico orgánico:

- **URL**: https://campanas.livskin.site/botox-mvp/
- **Path técnico**: `infra/landing-pages/botox-mvp/`
- **Estado**: ✅ live y operativa (Mini-bloque 3.6 cerrado 2026-05-01)
- **Uso en esta campaña**: NINGUNO (no se promociona vía ads)

Esta landing evergreen NO se toca durante la campaña. Si hay tráfico orgánico que llega ahí, sigue funcionando con tracking + form → A1 → Vtiger → ERP.

---

## Si en post-mortem decidimos producir landings dedicadas (próxima campaña)

Estructura prevista:

- Slug técnico: `dia-madre-botox-2026` (o similar para campaña próxima)
- URL pública: `https://campanas.livskin.site/dia-madre-botox-2026/`
- Path técnico: `infra/landing-pages/dia-madre-botox-2026/`
- Owner del diseño visual: Dario (en claude.ai/design)
- Owner del adapter técnico: Claude (10 pasos de adaptación al sistema livskin-tracking)

Workflow para producir (cuando sea):

1. Vos producís la landing casi-final en claude.ai/design
2. Dejás los archivos en `landing-source/` (subfolder ya creado, vacío)
3. Yo aplico **review gate** (te pregunto si está lista o necesita cambios)
4. Cuando OK, aplico los **10 pasos de adaptación** (meta tags + livskin-tracking.js + form intercept + Pixel + CAPI + uploads + UTMs + WA links)
5. Push a CF Pages → deploy automático
6. Smoke test post-deploy

**Esto NO se hace en esta campaña.** Queda como referencia futura.

---

## Cross-link

- Decisión Opción A documentada: [`../brief.md`](../brief.md) + [`../plan.md`](../plan.md)
- Landing evergreen Botox actual: `infra/landing-pages/botox-mvp/`
- Conventions del sistema landings: `infra/landing-pages/_shared/conventions.md`
