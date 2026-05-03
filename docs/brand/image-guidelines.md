---
type: brand-doctrine-images
version: 0.1
status: BORRADOR
parent: brand-system.md
---

# Guía Visual de Imágenes — Livskin

> **v0.1 BORRADOR** (modo bootstrap principio #13).

---

## Principio rector

**La imagen DEBE comunicar autonomía, control y naturalidad ANTES de que el visitor lea el texto.**

El copy solo refuerza. Si la imagen contradice el mensaje, la imagen gana siempre — el texto no recupera la conexión rota.

---

## Qué SÍ usar

✅ **Mujeres reales** (no modelos profesionales con piel artificial)
✅ **Seguridad tranquila** en la mirada
✅ **Expresión neutra o leve sonrisa** — nunca sonrisa exagerada
✅ **Mirada con intención** — la persona sabe lo que decidió, no busca aprobación
✅ **Edad acorde al segmento** (35-55 para Día de la Madre, 28-50 para genéricos)
✅ **Diversidad sutil** — Cusco/Lima → rasgos andinos/mestizos representados
✅ **Iluminación natural / suave** — no flash duro, no estudio sobreproducido
✅ **Fondos neutros o ambientes reales** (clínica, casa, espacios cotidianos premium)

---

## Qué NO usar (lista negra)

❌ **Modelos irreales** con piel "perfecta" digital
❌ **Sonrisas exageradas** ("¡aleluya, me hice botox!")
❌ **Piel perfecta artificial** (suavizado obvio, retoques excesivos)
❌ **Stock photos genéricas** ("woman smiling at camera in white background")
❌ **Antes/después visibles en TOFU/MOFU** (genera ansiedad, rompe narrativa decisional)
❌ **Manos médicas con jeringas** (lenguaje clínico frío)
❌ **Productos en primer plano** (botellas, ampollas)
❌ **Texto sobre la imagen saturando** (deja respirar la cara)

---

## Por etapa del funnel

### TOFU — declaración de identidad

**Qué busca la imagen:**
- Comunicar autonomía pre-texto
- Mirada directa, sin necesidad de aprobación
- Respiración visual amplia

**Crop preferido:** retrato medio (hombros + rostro), espacio negativo a un lado

**Ejemplos canónicos:**
- Mujer mirando hacia el horizonte, expresión tranquila
- Mujer en su casa, luz natural de ventana
- Retrato cuasi-editorial, sin photoshop visible

### MOFU — consideración

**Qué busca la imagen:**
- Coherencia visual con TOFU (misma estética, no cambiar de universo)
- Puede ser la misma persona en otro contexto
- Sigue sin mostrar tratamiento

**Anti-patrón:** mostrar manos del doctor con jeringa (rompe la narrativa).

### BOFU — conversión

**Qué busca la imagen:**
- Más cercana, más íntima
- Puede mostrar resultados sutiles (ej: rostro bien iluminado en clínica) — pero NO antes/después comparativos
- O puede ser la doctora en su consultorio (humanización del servicio)

---

## Convenciones de naming + ubicación

### Estructura de carpetas

```
infra/landing-pages/<slug>/uploads/
├── hero-<slug>.jpg              # foto principal del hero
├── section-<slug>-1.jpg         # secciones secundarias (numeradas si hay varias)
├── section-<slug>-2.jpg
├── testimonial-<initials>-<slug>.jpg  # testimoniales con foto (opcional)
├── doctora-<context>.jpg        # foto de la doctora si aplica
└── og-<slug>.jpg                # imagen de Open Graph (sharing)
```

**Reglas de naming:**
- Todo lowercase
- Sin tildes ni eñes (URL-safe)
- Slug coincide con el de la landing
- Sin espacios → guiones
- Extensión `.jpg` para fotos, `.png` para gráficos con transparencia, `.webp` permitido para optimización

### Tamaños recomendados

| Uso | Resolución mínima | Aspect ratio |
|---|---|---|
| Hero mobile | 800x1000 | 4:5 (portrait) |
| Hero desktop | 1600x900 | 16:9 |
| Section secundaria | 1200x800 | 3:2 |
| OG sharing | 1200x630 | 1.91:1 |
| Testimonial avatar | 400x400 | 1:1 |

---

## Mecánica de upload (modo bootstrap actual)

Dario tiene 3 caminos para enviar fotos:

### A. Drag-drop en chat con Claude (rápido, ad-hoc)

1. Pega la foto directamente en el mensaje
2. Indica destino: *"esta para hero de la landing día-de-la-madre"*
3. Claude:
   - Guarda en `infra/landing-pages/<slug>/uploads/<naming-convencional>`
   - Edita HTML/JSX para usarla
   - Commit + push → CF Pages auto-deploy en ~3 min
   - Pasa URL para validar

### B. Carpeta `_pending-uploads/` (batches, gitignored)

1. Dario deja archivos en `_pending-uploads/` cuando tiene tiempo libre
2. Naming sugerido: `<slug-hint>-<descripcion-corta>.jpg`
3. Al inicio de sesión, Claude lista qué hay nuevo
4. Pregunta destino de cada uno
5. Procede idéntico a (A)

### C. Generación AI (cuando no hay foto disponible)

1. Dario solicita: *"genera hero para landing X con estos criterios..."*
2. Claude genera prompt para fal.ai / Claude Design respetando guidelines
3. Imágenes generadas DEBEN pasar por aprobación de Dario antes de ir a producción
4. Marcar metadata: `generated_by_ai: true` en config (para trazabilidad)

---

## Checklist pre-upload

Antes de subir cualquier imagen a una landing, verificar:

```
[ ] ¿La imagen pasa la prueba de "comunica antes que el texto"?
[ ] ¿Mujer real, no modelo artificial?
[ ] ¿Mirada con intención, no de aprobación?
[ ] ¿Expresión neutra/leve sonrisa, no exagerada?
[ ] ¿Sin texto encima saturando?
[ ] ¿Sin antes/después visibles (excepto BOFU explícito)?
[ ] ¿Naming convencional respetado?
[ ] ¿Optimizada (<300KB para hero, <100KB para secciones)?
[ ] ¿Aspect ratio correcto para el uso?
[ ] ¿Aprobada por Dario antes de commit?
```

---

## Si la imagen NO califica

**Política dura:** mejor sin imagen que con imagen mala.

Si la foto rompe el código (modelo artificial, sonrisa exagerada, stock genérica) y no hay alternativa:
- Usar fondo de color con tipografía editorial
- O usar imagen abstracta (textura, color block)
- Esperar foto correcta antes de publicar

**No publicar landings con stock photo genérica.** Eso rompe la inversión completa de la campaña.

---

## Changelog

- **v0.1** (2026-05-04): destilado de Guidelines + convención de naming + 3 mecánicas de upload definidas.
