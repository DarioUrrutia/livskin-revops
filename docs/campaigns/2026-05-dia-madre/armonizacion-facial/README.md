# Armonización Facial — Campaña Día de la Madre 2026

> **Tu lugar centralizado para todos los assets de la campaña umbrella "Armonización Facial"** (Botox + Ácido Hialurónico bajo un solo frame conceptual).

---

## Cambio de scope (2026-05-04)

**Decisión Dario**: por presión de tiempo (lanzamiento target 5 may), simplificar la campaña a **un solo frame umbrella "Armonización Facial"** que cubre Botox + Ácido Hialurónico simultáneamente. La doctora decide en consulta presencial qué tratamiento aplicar según evaluación.

**Esto reemplaza** la estructura previa de 2 tratamientos separados (Botox y Acido Hialurónico carpetas).

**Coherencia con doctrina**: el doc de Guidelines explícitamente recomienda "no listar tratamientos en TOFU" y usar frames identitarios. "Armonización Facial" es exactamente ese frame umbrella.

---

## Estructura

```
armonizacion-facial/
├── README.md (este archivo)
├── copies.md                # ⭐ copies del ad bajo doctrina (3 textos: TOFU/MOFU/BOFU)
├── landing.md               # estado de la landing + URL + ref a infra/
├── tracking.md              # UTMs + shortcode [ARM-MAY-FB]
├── banners/                 # ← TÚ dejás 3 banners principales (uno por funnel)
│   ├── tofu.png             #    Vos generás aspect ratio variants en Canva
│   ├── mofu.png             #    y subís directo a FB Ads Manager
│   └── bofu.png
├── fotos/                   # ← TÚ dejás fotos finales para la landing (poco a poco)
└── landing-source/          # ← TÚ dejás versión casi-final de la landing acá
```

**Total banners requeridos**: solo **3 archivos principales** (TOFU/MOFU/BOFU). Las variantes de aspect ratio (1:1, 4:5, 9:16) las producís vos en Canva por separado y subís directo a Meta Ads Manager — yo NO necesito archivarlas.

---

## Estado actual de los assets

| Asset | Estado | Owner | Próxima acción |
|---|---|---|---|
| Copies (texto) | ✅ Propuesto v1 (`copies.md`) | Claude | Dario revisa + aprueba/ajusta |
| Banner TOFU principal | ⏳ pendiente | Dario en Canva | Drag-drop al chat o dejar en `banners/tofu.png` |
| Banner MOFU principal | ⏳ pendiente | Dario en Canva | idem `banners/mofu.png` |
| Banner BOFU principal | ⏳ pendiente | Dario en Canva | idem `banners/bofu.png` |
| Aspect ratio variants (1:1, 4:5, 9:16 por banner) | ⏳ pendiente | Dario en Canva | Generar + subir directo a FB Ads Manager (NO al repo) |
| Landing casi-final | ⏳ pendiente | Dario (versión nueva) | Pegar HTML/CSS en chat o `landing-source/` |
| Fotos para landing | ⏳ incremental | Dario | Pasarme poco a poco; yo las muevo a `infra/landing-pages/<slug>/uploads/` |
| Tracking shortcode `[ARM-MAY-FB]` | ✅ Definido | Claude | Doctora informada via cheat sheet |

---

## Brief creativo para los banners (input para Canva)

Las **3 ideas creativas** del funnel — todas bajo umbrella "Armonización Facial":

### Idea 1 — TOFU (Declaración de identidad)

**Mensaje principal**: "Este Día de la Madre, decide por ti"

**Concepto visual**: mujer 35-50, mirada con intención (NO sonrisa exagerada), expresión tranquila. Fondo natural. La imagen comunica autonomía + naturalidad ANTES del texto.

**Texto sobre imagen** (máximo):
- Hero: `Este Día de la Madre,` / `decide por ti.`
- Sub-mínimo (opcional): `Una hora para ti.`
- CTA visual del banner: `Descubre más →`

**Aspect ratios necesarios** (los hacés vos en Canva):
- 1:1 (1080×1080) — Feed
- 4:5 (1080×1350) — Mobile Feed
- 9:16 (1080×1920) — Stories/Reels

### Idea 2 — MOFU (Consideración / explicativo emocional)

**Mensaje principal**: "La armonía que tú decides"

**Concepto visual**: misma persona u otra del mismo universo estético. Coherencia visual con TOFU obligatoria.

**Texto sobre imagen**:
- Hero: `La armonía que` / `tú decides.`
- Sub: `Aplicación médica con criterio.`
- CTA: `Conoce tu enfoque`

### Idea 3 — BOFU (Acción concreta)

**Mensaje principal**: "Tu hora, tu decisión / Agenda evaluación"

**Concepto visual**: más cercana, más directa. Puede mostrar la doctora en consultorio (humanización del servicio).

**Texto sobre imagen**:
- Hero: `Tu hora.` / `Tu decisión.`
- Sub: `Evaluación médica con la doctora.`
- CTA: `Agenda tu evaluación`

---

## Reglas duras de la doctrina (aplicar en CADA banner)

### ❌ NUNCA poner:
- "Botox", "ácido hialurónico", "rellenos", "toxina", "inyección"
- "Arrugas", "envejecer", "rejuvenecer"
- Precios o "desde S/."
- Promociones / descuentos / urgencia ("¡aprovecha!")
- Modelos artificiales, sonrisas exageradas, piel digital
- Textos largos (max 8 palabras en hero)
- Múltiples CTAs en el mismo banner

### ✅ SÍ poner:
- Palabras de poder: decide, elige, define, descubre, conoce, explora, tu
- Espacio en blanco generoso (premium = aire)
- Una idea por banner
- Imagen real (mujer real, no stock genérico)

---

## Checklist 4 preguntas (cada banner antes de aprobar final)

- [ ] ¿Activa identidad de "madre que decide cuidarse"?
- [ ] ¿Genera permiso interno + tranquilidad? (no urgencia)
- [ ] ¿Sugiere decisión concreta?
- [ ] ¿NO dice: producto / precio / promesa imposible?

---

## Workflow operativo

### Vos en Canva (en paralelo con mi trabajo):

1. Producir 3 banners principales (TOFU/MOFU/BOFU) usando los copies de `copies.md`
2. Para cada uno, producir las variantes de aspect ratio (1:1, 4:5, 9:16) en Canva
3. Pasar los 3 principales a Claude (drag-drop chat o carpeta `banners/`)
4. Subir las 9 variantes (3 ideas × 3 aspect ratios) directo a FB Ads Manager siguiendo `../ads-manager-checklist.md`

### Yo (Claude) — paralelo:

1. Reorganizar carpetas + reescribir docs (en proceso)
2. Esperar landing casi-final que vas a pegar
3. Aplicar review gate + 10 pasos adaptación + push CF Pages
4. Cuando pases banners principales: archivo en `banners/` + verificar compliance Meta
5. Cuando pases fotos (poco a poco): mover a `infra/landing-pages/dia-madre-armonizacion-2026/uploads/` + actualizar HTML

### Vos en Ads Manager (cuando todo esté listo):

1. Seguir checklist UI manual (`../ads-manager-checklist.md`)
2. Configurar 1 campaign + 1 ad set + 3 ads
3. Cada ad con sus 3 aspect ratio variants (Asset customization)

---

## Cross-link

- Brief estratégico: [`../brief.md`](../brief.md)
- Plan operativo: [`../plan.md`](../plan.md)
- Configuración técnica: [`../campaign-config-draft.md`](../campaign-config-draft.md)
- Checklist UI manual: [`../ads-manager-checklist.md`](../ads-manager-checklist.md)
- Copies finales: [`copies.md`](copies.md)
- Tracking: [`tracking.md`](tracking.md)
- Estado landing: [`landing.md`](landing.md)
- Doctrina de marca: `docs/brand/`
