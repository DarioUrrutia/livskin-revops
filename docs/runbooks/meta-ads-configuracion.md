---
name: meta-ads-configuracion
description: Comportamientos durables de Meta Ads UI descubiertos durante setup. Reusable para cualquier campaña futura.
type: runbook
mode: PROYECTO (durable)
created: 2026-05-04
last_validated: 2026-05-04 (campaña Día de la Madre 2026)
---

# Runbook — Configurar campaña Meta Ads paso a paso (UI manual)

> **Este runbook captura comportamientos del software Meta Ads que NO son evidentes en docs oficiales pero que son **durables** y aplican a cualquier campaña.** Distinto del `campaign-config-final.md` (efímero, específico de una corrida) y de la doctrina de marca (ortogonal al software). Acá vive lo técnico operativo de Meta UI.

---

## 1. Comportamientos no obvios de Meta Ads UI

### 1.1 "Público Advantage+" NO permite EXCLUDE de Custom Audiences

**Comportamiento observado**: cuando el ad set tiene "Público Advantage+" activo (default en cuentas modernas), la sección de "Públicos personalizados" solo muestra opciones de INCLUDE. El botón "Agregar exclusiones" aparece **solo después** de cambiar a modo "Limitar aún más el alcance de tus anuncios".

**Cuándo importa**: en estructuras Cold/Warm separadas donde el Cold debe EXCLUIR las CAs históricas para evitar canibalización.

**Cómo cambiar**:
1. En el bloque "Público Advantage+" buscar link **"Cambiar a las opciones de público original"**
2. Meta muestra modal con 3 opciones:
   - "Conservar configuración actual" (sigue Advantage+)
   - "Aplicar reglas de valor con Advantage+ activado"
   - **"Limitar aún más el alcance de tus anuncios"** ← seleccionar esta
3. Click "Continuar"
4. Ahora aparece el botón "Agregar exclusiones" en Públicos personalizados

**Trade-off**: Meta advierte que esto puede reducir performance ~10%. Aceptable cuando control > optimización (audiencias chicas, budget bajo, intentar prospección limpia).

---

### 1.2 Objetivo de campaña "Tráfico" NO permite optimizar por "Conversaciones"

**Comportamiento observado**: si la campaña tiene objetivo Tráfico, los ad sets pueden tener Conversion Location = "Aplicaciones de mensajería → WhatsApp", PERO la "Performance goal" solo ofrece:
- Maximizar visitas a página de destino
- Maximizar clics en el enlace
- Maximizar impresiones
- Maximizar personas únicas que ven los anuncios

**NO disponible**: "Maximizar conversaciones" (esa solo aparece cuando objetivo de campaña es Engagement → Messaging).

**Implicación**: si querés mezclar destinos (algunos ads → Landing, otros ads → WhatsApp directo), **objetivo Tráfico es la única opción** y todos los ad sets deben optimizar por **Link Clicks**. La atribución a mensajes reales se hace por shortcode manual, no por la métrica de Meta.

**Alternativas**:
- **2 campañas separadas**: 1 Tráfico (landing) + 1 Engagement (WA). Pierde CBO unificado.
- **Engagement → Messaging único**: todos los ads van a WA, perdés el experimento landing.
- **Tráfico con Link Clicks** (recomendado para escalas chicas): unifica + acepta pérdida de optimización.

---

### 1.3 Al duplicar Ad Set, modal vuelve a aplicar Advantage+

**Comportamiento observado**: cuando duplicás un ad set vía 3 puntos → "Duplicar", Meta muestra modal con:
- ☑ Llegar a las personas interesadas en tus lugares (expansión geográfica)
- ☑ Usar el público Advantage+

**Estos checks vienen marcados por default**, aunque el ad set original tuviera ambos desactivados. Si presionás "Duplicar" sin desmarcar, Meta re-aplica Advantage+ al duplicado y rompe la configuración cuidadosa que hiciste.

**Cómo evitar**: SIEMPRE desmarcar los checks del modal antes de "Duplicar". Hacer hábito.

---

### 1.4 Geo-targeting tiene radio mínimo regional auto-aplicado

**Comportamiento observado**: al seleccionar una ciudad (ej: "Cusco"), Meta auto-asigna radio mínimo según la región. Para Cusco fue **17 km** (no permite menos). Esto incluye distritos no deseados (San Jerónimo, Saylla, etc.).

**Workaround**: usar **marcador manual** en el mapa en lugar de seleccionar la ciudad por nombre.

**Cómo**:
1. En "Lugares" → click en el mapa para fijar pin manualmente
2. Ajustar radio (acepta valores menores como 4-5 km)
3. Eliminar la selección automática de la ciudad por nombre

**Cuándo importa**: campañas hyper-locales (clínicas, restaurantes, retail físico) donde el alcance debe ser <10 km.

---

### 1.5 Editor de Chats — Mensaje predefinido tiene límite 80 caracteres

**Comportamiento observado**: en ads de Click-to-WhatsApp, el "Mensaje predefinido" (lo que el usuario envía al hacer click) tiene **límite de 80 caracteres**.

**Implicación para shortcodes de tracking**:
- Mensaje base: "Hola, vengo del aviso de Livskin Día de la Madre" = 49 chars
- Shortcode tipo "[ARM-MAY-FB-MOFU-COLDWA]" = 24 chars
- **Total: 73/80 chars** ✅ apenas entra

**Si usás campañas con shortcodes más largos** (ej: incluir tratamiento + mes + ad variant + audience tag), reducí el mensaje base o usar shortcodes más compactos.

---

### 1.6 Mejoras esenciales del Advantage+ vienen ON por default y modifican el copy

**Comportamiento observado**: dentro del editor de contenido del ad, hay una sección "Mejoras esenciales (6/6)" que viene **activada por default**. Estas mejoras incluyen:
- Mostrar resúmenes
- Comentarios relevantes
- Mejorar llamada a la acción
- Otros

**Implicación**: Meta puede modificar tu copy/CTA con AI sin avisarte (el AB test es opaco). Para preservar el copy exacto que diseñaste según doctrina, **desactivar manualmente las 6 mejoras**.

**Cómo**:
1. Editor de contenido del ad → bajar a "Mejoras esenciales (6/6)"
2. Click "Editar"
3. Desactivar los 6 toggles
4. Guardar

---

### 1.7 Spend limits del ad set son la única forma de forzar distribución bajo CBO

**Comportamiento observado**: con CBO (Campaign Budget Optimization), Meta distribuye automáticamente entre ad sets según performance. **Sin intervención**, gasta 70-80% del budget en el ad set con mejor CPM (típicamente Warm con CAs históricas).

**Para forzar distribución entre Cold/Warm** (estrategia profesional con audiences chicas):
1. En cada ad set → "Presupuesto y calendario" → "Límites de gasto del conjunto de anuncios"
2. Setear mínimo y máximo en moneda de la cuenta
3. Meta operará dentro del rango forzado

**Trade-off**: Meta muestra warning "podrías obtener mejor performance sin límites". Es real pero aceptable cuando diversificación > optimización.

---

### 1.8 Identifier confusión — Pixel ID vs Ad Account ID vs Business Manager ID

**Riesgo común**: confundirse entre los 3 IDs principales:

| ID | Formato | Dónde vive | Para qué |
|---|---|---|---|
| **Pixel ID** | 16 dígitos | Events Manager | Tracking client-side + CAPI |
| **Ad Account ID** | 16 dígitos | Ads Manager | Donde corren las campañas |
| **Business Manager ID** | 16 dígitos | Business Settings | Contenedor de assets |

**Síntoma**: durante setup, Dario tenía 3 contenedores (2 BMs + cuenta personal). Solo `2885433191763149` (BM Livskin Perú) es operativa. La cuenta personal `2130672884136872` está vacía pero genera confusion.

**Recomendación**: documentar todos los IDs activos al inicio de cada campaña en `campaign-config-final.md`. Diagrama opcional en `docs/integrations/meta/account-architecture.md`.

---

## 2. Account Quality + Status de campañas — chequeos pre-lanzamiento

### 2.1 Account Quality dashboard

```
URL: https://business.facebook.com/accountquality
```

Estados:
- ✅ "Excellent" / "Good" → seguir
- ⚠️ "Needs improvement" → seguir con cuidado
- ❌ "Limited" / "Restricted" → **PARAR**, resolver primero

### 2.2 Estado de delivery de los ads

Por default en columnas "Rendimiento Jean" no se muestra. Para verlo:
1. Click en "Columnas: Rendimiento Jean" arriba a la derecha
2. Cambiar a vista que incluya "Estado de entrega"

Estados que verás:
- **"Procesando"** → estado intermedio, pasa a "En revisión" en minutos
- **"En revisión"** → Meta aprobando (4-24h)
- **"Programado"** → ya aprobado, esperando schedule de inicio
- **"Activo - en circulación"** → corriendo
- **"Rechazado"** → revisar razón en columna o click ad

---

## 3. Verificar que el Pixel está midiendo correctamente

### 3.1 Verificación técnica desde el filesystem (cuando hay acceso al código)

Si la landing tiene `livskin-tracking.js` instalado:

```bash
# Confirmar que el script se sirve correctamente
curl -s -L -o /dev/null -w "HTTP %{http_code}\n" "https://campanas.livskin.site/livskin-tracking.js"

# Verificar Pixel ID correcto en el JS servido
curl -s -L "https://campanas.livskin.site/livskin-tracking.js" | grep -E "pixel_id|fbq.*init"

# Confirmar que el HTML del landing tiene el script tag
curl -s -L "https://campanas.livskin.site/<landing-slug>/" | grep "livskin-tracking.js"
```

### 3.2 Verificación funcional desde Events Manager

```
URL: https://business.facebook.com/events_manager2/list/datasets
```

1. Click en el Pixel
2. Pestaña "Resumen" → ver gráfico de eventos
3. Verificar que la "Última recepción" del PageView sea **<1 hora** durante campaña activa
4. Si hay pico visible en el gráfico → tráfico de ads está disparando eventos

### 3.3 Tasa esperada de click→PageView

**Rango realista con consent modal + AdBlockers + LATAM mobile:** **40-70%**.

Causas del leak (todas esperadas):
- Rechazo de consent modal: ~30% del leak
- AdBlockers (uBlock, AdBlock Plus): 15-20%
- Bounce inmediato pre-script: ~10%
- Conexiones lentas: ~5%

**No es un bug. Es trade-off de compliance.**

---

## 4. Revisión final antes de "Publicar"

Modal "Revisar borradores" muestra **solo cambios pendientes**. Si un ad set/ad tiene status diferente (auto-publicado por modal de "Guardar plantilla" en Editor de Chats, etc.), **no aparece** en la review pero sí está en la campaña.

**Diagnóstico**:
- Si el modal muestra menos ad sets/ads que los que ves en sidebar → algunos ya están publicados/activos individualmente. Está OK.
- Verificar el **número (X)** del botón "Revisar y publicar (X)" — son cambios pendientes específicos.

**Warnings vs Errores**:
- Warnings (amarillos) = sugerencias de Meta para mejor performance. NO bloquean publicación. Aceptables si la decisión es consciente (ej: forzar spend limits para diversificar).
- Errores reales = bloquean publicación. Si los hay, Meta los identifica claramente con "Corregir error" link.

---

## 5. Post-publish — qué esperar

### Timeline típico

| T+ | Evento |
|---|---|
| 0 | Click "Publicar" → ads van a "Procesando" |
| +5 min | "Procesando" → "En revisión" |
| +4-24h | "En revisión" → "Programado" o "Rechazado" |
| Schedule start | "Programado" → "Activo - en circulación" |
| +30 min post-activo | Primeros eventos en Events Manager |

### Si un ad queda en "Rechazado"

1. Click en el ad → ver razón
2. Razones comunes en medicina estética:
   - Imágenes "before/after" demasiado contrastadas (bot detecta como anuncio engañoso)
   - Promesas absolutas en copy ("garantizado", "100%")
   - Ads de Health requieren disclosure especial (a veces auto-detectan)
3. Ajustar + resubmit (no necesita re-publicar toda la campaña)

---

## 6. Cuándo NO usar este runbook

- Si tenés Marketing API token funcional → usá automatización vía API (más rápido y reproducible)
- Si la campaña es >$1.000 USD → considerar Advantage+ Audience completo (Meta tiene data para optimizar bien)
- Si la audiencia es masiva (>500K personas) → Advantage+ + reglas de valor probablemente superan al control manual

---

## Changelog

- **2026-05-04** (v1.0): documento creado durante setup de campaña Día de la Madre 2026. Captura 8 comportamientos durables descubiertos.
- **(futuro)** v1.1: refinar después de post-mortem cuando tengamos data de performance + comparación con runs futuros.
