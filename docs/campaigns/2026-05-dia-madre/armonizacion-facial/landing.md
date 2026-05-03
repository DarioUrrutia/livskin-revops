# Landing — Armonización Facial — Día de la Madre 2026

## Estado: ⏳ EN ESPERA — pendiente recibir versión casi-final de Dario

> **Cambio respecto a la decisión inicial**: ahora SÍ se produce 1 landing umbrella "Armonización Facial" (no 0 como Op A original).

---

## Identificación

| Campo | Valor |
|---|---|
| Slug técnico | `dia-madre-armonizacion-2026` |
| URL pública futura | `https://campanas.livskin.site/dia-madre-armonizacion-2026/` |
| Path técnico futuro | `infra/landing-pages/dia-madre-armonizacion-2026/` |
| Frame conceptual | Armonización Facial (umbrella Botox + Ácido Hialurónico) |
| Origen | Versión nueva producida por Dario, basada en botox-mvp existente con copy adaptado |
| Estado deploy | ⏳ pendiente recibir versión casi-final |

---

## Workflow de integración (cuando Dario me pase la landing)

### Paso 1: Recepción

Dario pega la landing en alguno de estos caminos:
- HTML/CSS texto en chat (1 archivo único)
- Múltiples archivos en `landing-source/` (carpeta ya creada)
- Link público de claude.ai/design

### Paso 2: Review gate (yo pregunto, vos decidís)

Antes de inyectar tracking + adaptación técnica, te pregunto:
> *"Recibí la landing. ¿Está lista para producción o necesita cambios primero?"*

NO toco infra/ ni inyecto nada hasta que vos digás "lista".

### Paso 3: Iteración de cambios (si aplica)

Si pedís cambios de copy/estructura, los hago en `landing-source/` (no en infra/) y te muestro diff. Loop hasta que digás "lista".

**Lo que SÍ puedo cambiar en review gate**:
- Copies (aplicando doctrina + checklist 4 preguntas)
- Estructura HTML (mover secciones, agregar/quitar bloques)
- Microcopy (CTAs, form labels)
- Mobile responsive (CSS media queries)
- HTML semántico (h1/h2 jerarquía, alt text)

**Lo que NO toco**:
- Layout visual / colores / tipografía
- Selección o edición de fotos
- Diseño visual desde cero

### Paso 4: 10 pasos de adaptación técnica (cuando vos digás "lista")

1. Crear carpeta `infra/landing-pages/dia-madre-armonizacion-2026/`
2. Inyectar meta tags obligatorios (livskin-treatment, livskin-landing-slug, robots noindex, OG)
3. Inyectar `window.LIVSKIN_CONFIG` + `livskin-tracking.js`
4. Marcar form con `data-livskin-form="true"`
5. Renombrar fields al contrato A1 (`nombre`, `phone`, `email`, `consent_marketing`)
6. Convertir CTAs WhatsApp al formato con shortcode `[ARM-MAY-FB]`
7. Crear `livskin-config.json` con metadata completa
8. Mover fotos de `fotos/` a `infra/landing-pages/dia-madre-armonizacion-2026/uploads/`
9. Refinar copies bajo doctrina (paso final)
10. Smoke test post-deploy

### Paso 5: Diff explicado

Te paso lista de qué cambié + por qué (línea por línea de cambios significativos).

### Paso 6: Tu OK al diff

Vos aprobás explícitamente.

### Paso 7: Push CF Pages → deploy automático

Una vez vos aprobás, push a main → CF Pages deploya en ~3 min.

### Paso 8: Smoke test post-deploy

- `curl https://campanas.livskin.site/dia-madre-armonizacion-2026/` → 200 OK
- Submit form fake con UTMs → verificar lead en Vtiger en <2 min via cron B3 → ERP en <4 min total
- Click WA CTA → verificar mensaje pre-poblado tiene shortcode `[ARM-MAY-FB]`
- Pixel "Lead" event firea en navegador (FB Pixel Helper)

---

## Cambios editorialmente esperados sobre la versión Botox

Ya que vos partís de la landing botox-mvp existente y adaptás a "Armonización Facial":

**Cambios obligatorios (vos los hacés en claude.ai/design / herramienta)**:
- Hero: cambiar "Botox" / "toxina" / etc. por frame umbrella decisional
- Sub-headlines: aplicar doctrina v0.1 (sin nombrar producto en TOFU/MOFU)
- BOFU section: puede mencionar "armonización facial" como concepto (NO "Botox" específico)
- WhatsApp CTAs: shortcode `[ARM-MAY-FB]` (yo te lo configuro en review gate)
- OG image / título: "Armonización Facial — Livskin Día de la Madre" en lugar de "Botox que se ve natural"

**Cambios opcionales** (sugeridos por mí en review gate):
- Reorganización de secciones si la jerarquía no es clara
- Microcopy del form
- Espaciado vertical (premium = aire)

---

## Fotos para la landing

Dario va a pasar fotos **incrementalmente** ("poco a poco") después de tener todo organizado.

**Workflow para cada foto que pase**:
1. Vos drag-drop en chat o dejás en `fotos/` con naming sugerido
2. Yo identifico destino (hero / section-1 / testimonial / etc.) según contexto
3. Muevo a `infra/landing-pages/dia-madre-armonizacion-2026/uploads/<naming-convencional>`
4. Actualizo HTML para usar el path correcto
5. Commit + push → CF Pages re-deploya con la foto nueva
6. Te paso URL para validar visualmente

**Naming convencional** (yo aplico):
- `hero.jpg` — foto principal del hero
- `section-1.jpg`, `section-2.jpg` — secciones secundarias
- `testimonial-<initials>.jpg` — testimoniales
- `og.jpg` — Open Graph (sharing)

---

## Cross-link

- Versión origen: `infra/landing-pages/botox-mvp/` (referencia, NO se modifica — es evergreen)
- Conventions del sistema: `infra/landing-pages/_shared/conventions.md`
- Brief campaña: [`../brief.md`](../brief.md)
- Plan: [`../plan.md`](../plan.md)
- Copies: [`copies.md`](copies.md)
- Tracking: [`tracking.md`](tracking.md)
- Doctrina: `docs/brand/`

---

## Estado de avance (actualizar conforme avancemos)

```
[2026-05-04 17:00] Estructura carpetas reorganizadas a umbrella
[2026-05-04 17:30] Copies v1 propuestos (pendiente aprobación Dario)
[___________] Landing casi-final recibida de Dario
[___________] Review gate ejecutado
[___________] 10 pasos adaptación aplicados
[___________] Push CF Pages (URL live)
[___________] Smoke E2E pre-launch
[___________] Fotos integradas (incremental)
```
