# Botox — Campaña Día de la Madre 2026

> **Tu lugar centralizado para todos los assets de Botox de esta campaña.**
> Vos dejás los archivos finales en las subcarpetas correspondientes; Claude los integra al sistema técnico.

---

## Estructura

```
botox/
├── README.md (este archivo)
├── copies.md                # ⭐ copies finales de los 3 banners (aprobados)
├── landing.md               # estado: NO se produce landing en esta campaña (Op A)
├── tracking.md              # UTMs específicas de Botox + shortcode [BTX-MAY-FB]
├── banners/                 # ← TÚ dejás banners finales aquí
│   ├── tofu-1x1.png         # 1080×1080 — FB Feed, IG Feed
│   ├── tofu-4x5.png         # 1080×1350 — Mobile Feed
│   ├── tofu-9x16.png        # 1080×1920 — Stories, Reels
│   ├── mofu-1x1.png
│   ├── mofu-4x5.png
│   ├── mofu-9x16.png
│   ├── bofu-1x1.png
│   ├── bofu-4x5.png
│   └── bofu-9x16.png
├── fotos/                   # ← TÚ dejás fotos finales aquí (si necesitás para banners)
└── landing-source/          # NO se usa en esta campaña (Op A — sin landing dedicada)
```

**Total banners requeridos**: 9 (3 ideas × 3 aspect ratios)

---

## Estado actual de los assets

| Asset | Estado | Owner | Próxima acción |
|---|---|---|---|
| Copies (texto) | ✅ Propuesto v1 (`copies.md`) | Claude | Dario revisa + aprueba/ajusta |
| Banner TOFU 1×1 | ⏳ pendiente | Dario en Canva | Producir + dejar en `banners/tofu-1x1.png` |
| Banner TOFU 4×5 | ⏳ pendiente | Dario en Canva | idem |
| Banner TOFU 9×16 | ⏳ pendiente | Dario en Canva | idem |
| Banner MOFU 1×1 | ⏳ pendiente | Dario en Canva | idem |
| Banner MOFU 4×5 | ⏳ pendiente | Dario en Canva | idem |
| Banner MOFU 9×16 | ⏳ pendiente | Dario en Canva | idem |
| Banner BOFU 1×1 | ⏳ pendiente | Dario en Canva | idem |
| Banner BOFU 4×5 | ⏳ pendiente | Dario en Canva | idem |
| Banner BOFU 9×16 | ⏳ pendiente | Dario en Canva | idem |
| Landing | ❌ No aplica (Opción A — todo Click-to-WhatsApp) | — | — |
| Tracking shortcode `[BTX-MAY-FB]` | ✅ Definido | Claude | Doctora informada via cheat sheet |

---

## Brief creativo para los banners (input para Canva)

### Idea 1 — TOFU (Declaración de identidad)

**Mensaje en banner**:
> Este Día de la Madre,
> decide por ti.

**Imagen**:
- Mujer 35-50 años (puede ser foto stock de calidad o paciente real con autorización)
- Mirada con intención (no sonrisa exagerada)
- Expresión tranquila, fondo natural
- Comunica autonomía + control + naturalidad ANTES del texto

**Composición** (ajustar por aspect ratio):
- 1:1 → texto en parte superior 1/3, imagen ocupa 2/3 inferior
- 4:5 → imagen full-bleed con overlay gradient + texto franja inferior
- 9:16 (Stories/Reels) → texto arriba, imagen central, espacio abajo para CTA

**Color**: paleta canónica (rosa `#F4A6BB` para acentos, fondo `#FFFFFF` o `#FCE8EC` wash)

**Tipografía**: Montserrat 300 light para hero (elegante, amplio)

**CTA visible**: "Descubre más →" (suave)

---

### Idea 2 — MOFU (Consideración / explicativo emocional)

**Mensaje en banner**:
> La armonía que
> tú decides.

**Imagen**:
- Misma persona u otra del mismo universo estético (coherencia obligatoria con TOFU)
- Puede ser la doctora si tenés foto profesional aprobada
- Sigue mostrando autonomía + tranquilidad

**Composición**: similar a TOFU pero más cercana (puede ser plano busto)

**CTA**: "Conoce tu enfoque"

---

### Idea 3 — BOFU (Acción concreta)

**Mensaje en banner**:
> Tu hora.
> Tu decisión.

**Imagen**:
- Más íntima, más cercana
- Puede mostrar la doctora en consultorio (humanización)
- O paciente cómoda en clínica
- ❌ NO antes/después comparativos

**Composición**: imagen toma protagonismo, texto sutil

**CTA**: "Agenda tu evaluación"

---

## Reglas duras de la doctrina (aplicar siempre)

### ❌ NUNCA poner en estos banners:
- Palabras prohibidas: "botox", "toxina", "arrugas", "rejuvenecer", "envejecer"
- Precios o "desde S/."
- Promociones / descuentos / urgencia ("¡aprovecha!")
- Modelos artificiales, sonrisas exageradas, piel digital
- Textos largos (max 8 palabras en hero)
- Múltiples CTAs en el mismo banner

### ✅ Sí poner:
- Palabras de poder: decide, elige, define, descubre, conoce, explora, tu
- Espacio en blanco generoso (premium = aire)
- Una idea por banner
- Imagen real (mujer real, no stock genérico)

---

## Checklist 4 preguntas (validar cada banner antes de aprobar final)

Por cada banner:
- [ ] ¿Activa identidad de "madre que decide cuidarse"?
- [ ] ¿Genera permiso interno + tranquilidad? (no urgencia)
- [ ] ¿Sugiere decisión concreta?
- [ ] ¿NO dice: producto / precio / promesa imposible?

Si algún check falla → revisar antes de aprobar.

---

## Workflow operativo (modo CAMPAÑA + BOOTSTRAP)

### Vos en Canva:

1. Abrir Canva con paleta + tipografía Livskin
2. Para cada idea (TOFU/MOFU/BOFU), crear las 3 variantes (1:1, 4:5, 9:16)
3. Aprobar cada banner contra checklist 4 preguntas
4. Exportar como `.png` con naming convencional:
   - `tofu-1x1.png`
   - `tofu-4x5.png`
   - `tofu-9x16.png`
   - (y así para MOFU + BOFU)
5. Dejar en `docs/campaigns/2026-05-dia-madre/botox/banners/`

### Yo (Claude):

1. Verifico que hay 9 banners con naming correcto
2. Pre-validate compliance Meta (claims prohibidas, antes/después, etc.)
3. Si todo OK → archivo en su lugar + listo para subir a Ads Manager
4. Si algo falla compliance → te aviso ANTES de que lo subas

### Vos en Ads Manager (siguiendo `ads-manager-checklist.md`):

1. Subir banners a cada Ad (3 Ads de Botox: TOFU/MOFU/BOFU)
2. Pegar copies de `copies.md`
3. Configurar Customize message con `[BTX-MAY-FB]`
4. Submit

---

## Cross-link

- Brief estratégico: [`../brief.md`](../brief.md)
- Plan operativo: [`../plan.md`](../plan.md)
- Checklist UI manual: [`../ads-manager-checklist.md`](../ads-manager-checklist.md)
- Copies finales: [`copies.md`](copies.md)
- Tracking Botox: [`tracking.md`](tracking.md)
- Doctrina de marca: `docs/brand/`
