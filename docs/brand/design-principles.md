---
type: brand-doctrine-design
version: 0.1
status: BORRADOR
parent: brand-system.md
---

# Principios de Diseño — Livskin

> **v0.1 BORRADOR** (modo bootstrap principio #13).

---

## Los 5 principios

### 1. Espacio en blanco = lujo

**Mientras más aire:**
- Más percepción premium
- Más credibilidad
- Más respiración para la decisión

**Regla operativa:** mínimo 1.5x altura de fuente como espaciado entre bloques principales.

**Anti-patrón:** llenar pantalla "porque hay espacio". El espacio no es desperdicio, es valor.

### 2. Jerarquía clara — siempre el mismo orden

```
1. Idea principal (declaración de identidad)
2. Imagen (refuerzo emocional)
3. Acción (CTA)
```

**Regla operativa:** una sección = una idea = un CTA. Si hay 2 ideas, son 2 secciones.

### 3. NO saturar — error crítico

**El error que rompe todo:**
> Titular + Subtítulo + Beneficios + Lista + CTA todos juntos en una sección

**Regla operativa:**
- Máximo 3 elementos por bloque visual: encabezado + 1 elemento de soporte + CTA
- Si necesitás más → es 2 bloques

### 4. Color controlado

**Paleta canónica:**

| Token | Valor | Uso |
|---|---|---|
| `--brand-pink` | `#F4A6BB` | CTA primario (hot pink — actual) |
| `--brand-pink-soft` | `#FCE8EC` | Wash de sección, fondos suaves |
| `--brand-pink-d` | `#E88AA2` | Estados hover |
| `--brand-red` | `#8B1F1F` | Acentos editoriales puntuales |
| `--brand-blue` | `#5BB5D6` | Acentos secundarios (uso restringido) |
| `--ink` | `#1F1A1A` | Texto principal (cuasi-negro, NO negro puro) |
| `--ink-soft` | `#4A4441` | Texto secundario |
| `--ink-mute` | `#8A847F` | Texto terciario / labels |
| `--bg` | `#FFFFFF` | Fondo base |

**Reglas duras del rosa:**
- ✅ Suave, desaturado
- ❌ NUNCA promocional (el rosa NO grita "SALE")
- ❌ NUNCA saturado puro tipo neón

**Reglas duras del negro:**
- ✅ `#1F1A1A` (cuasi-negro)
- ❌ `#000000` (negro puro = se ve barato en pantallas)

### 5. Tipografía

**Sistema:**
- **Montserrat** (300/500/600/700) → titulares + UI
  - 300 (light) → headlines display
  - 500 (medium) → eyebrows, labels
  - 600 (semibold) → display-bold (sub-titulares)
- **Open Sans** (400-700) → body text + descripciones

**Reglas:**

| Elemento | Font | Weight | Letter-spacing | Notas |
|---|---|---|---|---|
| Headline display | Montserrat | 300 | `0.01em` | Light + amplio = elegante |
| Display-bold (sub) | Montserrat | 600 | `0.02em` | Más afirmativo |
| Eyebrow / labels | Montserrat | 500 | `0.32em` UPPERCASE | Tracking amplio |
| Body | Open Sans | 400 | normal | Lectura cómoda |
| CTA button | Montserrat | 500-600 | `0.05em` | Sans afirmativo |

**Anti-patrón:** Comic Sans, Arial, Times New Roman, Helvetica vanilla — tipografías genéricas rompen el código premium.

---

## Reglas de layout

### Mobile-first (obligatorio)

Todas las landings DEBEN ser mobile-first. Stats reales: ~70% del tráfico de ads Meta llega desde mobile.

```
Mobile (default) → Tablet (>720px) → Desktop (>1024px)
```

### Vertical rhythm

Variables del sistema (definidas en `infra/landing-pages/_shared/conventions.md`):

```css
--sp-y: 88px (mobile) / 112px (tablet) / 128px (desktop)  /* padding vertical sección */
--sp-x: 20px (mobile) / 32px (tablet) / 48px (desktop)    /* padding horizontal */
--gap-block: 40-56px                                       /* entre header y content */
```

### Hero / contenido orden

- **Mobile:** texto arriba, imagen abajo (orden de lectura natural)
- **Desktop:** imagen + texto en grid 2 columnas

---

## Componentes reutilizables (referencia futura)

Los siguientes patterns existen en `infra/landing-pages/botox-mvp/` y deberían extraerse a `infra/landing-pages/_shared/components/` cuando llegue el refactor:

- `<PinkCTA>` — botón primario rosa pill
- `<SectionHeader>` — eyebrow + display headline + sub
- `<Testimonial>` — quote + nombre + opcional rol
- `<HeroSplit>` — grid 2-col hero
- `<ProcessGrid>` — pasos del proceso 1-2-3
- `<BeneficiosTrio>` — 3 columnas de propuesta de valor
- `<Booking>` — form + WhatsApp CTA combinados

---

## Anti-patrones (qué nunca hacer)

| ❌ Anti-patrón | Por qué rompe |
|---|---|
| Botones grandes tipo "BUY NOW" | Estética e-commerce barata |
| Colores agresivos (rojo neón, amarillo SALE) | Rompe código premium |
| Tipografía genérica (Comic Sans, Arial) | Rompe código premium |
| Pop-ups inmediatos | Fricción + ansiedad |
| Countdown timers | Urgencia fabricada |
| "100% guaranteed" badges | Genera desconfianza |
| Stock photos genéricas (modelos sonriendo en fondo blanco) | Rompe código de naturalidad |
| Animaciones complejas (parallax exagerado, auto-play video) | Distrae de la decisión |

---

## Cómo aplicar en cada pieza

1. Diseñar mobile-first
2. Aplicar paleta canónica + tipografía exacta
3. Verificar jerarquía: idea → imagen → acción (siempre en ese orden)
4. Revisar saturación: contar elementos por bloque (max 3)
5. Validar espacio en blanco generoso
6. Pasar por checklist de 4 preguntas (`brand-system.md` § 6)

---

## Changelog

- **v0.1** (2026-05-04): destilado de Guidelines + paleta extraída de botox-mvp/index.html actual.
