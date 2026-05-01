# Política de Cookies — Livskin

**Última actualización:** 2026-05-01
**Versión:** 1.0

Esta Política de Cookies explica qué son las cookies, cuáles utilizamos en nuestros sitios `livskin.site` y `campanas.livskin.site`, y cómo usted puede gestionar sus preferencias de privacidad.

Esta Política complementa nuestra [Política de Privacidad](privacy-policy.md) y nuestros [Términos de Uso](terms-of-service.md).

---

## 1. Qué son las cookies

Las **cookies** son pequeños archivos de texto que se almacenan en su dispositivo (computadora, smartphone, tablet) cuando visita un sitio web. Las cookies permiten al sitio:

- Recordar sus preferencias y configuración
- Recordar si está logueado/a
- Realizar análisis estadístico de uso del sitio
- Personalizar contenido y anuncios
- Atribuir conversiones a campañas publicitarias

Las cookies pueden ser:
- **Propias** (first-party): generadas por nuestro propio sitio
- **De terceros** (third-party): generadas por servicios externos como Meta, Google, etc.

Por su duración:
- **De sesión**: se borran al cerrar el navegador
- **Persistentes**: permanecen un tiempo determinado (días, semanas, meses)

---

## 2. Categorías de cookies que utilizamos

Clasificamos las cookies en **4 categorías**, gestionadas mediante el banner de consent de Complianz GDPR (configurado bajo estándares LGPD Brasil, equivalente a Ley N° 29733 Perú).

### 2.1 🟢 Esenciales (siempre activas — no requieren consent)

Cookies necesarias para el funcionamiento básico del sitio. **Sin estas cookies el sitio no funciona correctamente** — por ello no requieren su consentimiento.

| Cookie | Propósito | Duración |
|---|---|---|
| `PHPSESSID` | Sesión PHP del servidor (gestión de estado) | Sesión |
| `wordpress_*` | Login WordPress (solo si es admin) | Sesión / 14 días |
| `cf_clearance` | Cloudflare seguridad (anti-bots) | 30 días |
| `cmplz_*` | Estado del banner de cookies (Complianz) | 365 días |

### 2.2 🔵 Funcionales (requieren consent — opt-in)

Mejoran la experiencia pero no son estrictamente necesarias.

| Cookie | Propósito | Duración |
|---|---|---|
| `wp-settings-*` | Preferencias de UI WordPress | 1 año |

### 2.3 📊 Estadísticas (requieren consent — opt-in)

Nos ayudan a entender cómo se usa el sitio para mejorarlo (análisis agregado y anónimo).

| Cookie | Origen | Propósito | Duración |
|---|---|---|---|
| `_ga` | Google Analytics | ID de cliente único | 2 años |
| `_ga_*` | Google Analytics 4 | Identificador de propiedad | 2 años |
| `_gid` | Google Analytics | ID de sesión | 24 horas |

### 2.4 🎯 Marketing y atribución (requieren consent — opt-in)

Permiten medir efectividad de campañas publicitarias y mostrar contenido relevante.

#### 2.4.1 Cookies de Meta (Facebook/Instagram)

| Cookie | Propósito | Duración |
|---|---|---|
| `_fbp` | ID de browser único de Meta Pixel | 90 días |
| `_fbc` | Click ID de anuncio de Meta (cuando llega de un ad) | 90 días |

#### 2.4.2 Cookies propias `lvk_*` (first-party)

Cookies creadas por nosotros para preservar la atribución de su origen:

| Cookie | Propósito | Duración |
|---|---|---|
| `lvk_utm_source` | Fuente de tráfico (facebook, google, etc.) | 90 días |
| `lvk_utm_medium` | Medio (cpc, organic, email, etc.) | 90 días |
| `lvk_utm_campaign` | Campaña específica | 90 días |
| `lvk_utm_content` | Variante creativa del anuncio | 90 días |
| `lvk_utm_term` | Palabra clave (Google Ads) | 90 días |
| `lvk_fbclid` | Click ID de Meta (backup de `_fbc`) | 90 días |
| `lvk_gclid` | Click ID de Google (backup de `gclid`) | 90 días |
| `lvk_event_id` | Identificador único de conversión (deduplicación) | Sesión |
| `lvk_landing_url` | Página de aterrizaje original | 90 días |
| `lvk_consent` | Estado del consentimiento del usuario | 365 días |

**Importante sobre las cookies `lvk_*`:** son **cookies propias (first-party)** generadas en `livskin.site` y compartidas con `campanas.livskin.site`. No son compartidas con terceros directamente — pero sus valores pueden ser enviados a Meta y Google a través de nuestro servidor (Conversions API) en formato hasheado y anónimo.

#### 2.4.3 Cookies de Google Ads (futuro — cuando se activen campañas)

| Cookie | Propósito | Duración |
|---|---|---|
| `_gcl_au` | Atribución de campañas Google Ads | 90 días |

---

## 3. Cookies de terceros y transferencia de datos

Las cookies de terceros (Meta, Google) implican que **estos terceros pueden recibir información sobre su visita**. Estos servicios:

- Tienen sus propias políticas de privacidad (consultar)
- Pueden estar ubicados fuera del Perú (transferencia internacional)
- Cumplen estándares GDPR/CCPA en sus operaciones globales

**Información compartida con Meta vía Conversions API:**
- Email y teléfono **hasheados** (SHA-256, irreversibles — Meta no puede recuperar el dato original)
- Cookies `_fbc`, `_fbp`
- IP y user-agent
- `event_id` para deduplicación
- Información del evento (tipo: Lead/Schedule/Purchase, valor si aplica)

**Información compartida con Google:**
- Cookie `_ga` (ID de cliente)
- Parámetros UTM
- Página visitada
- Eventos configurados en GTM

---

## 4. Cómo gestionar sus preferencias

### 4.1 Banner de consent (recomendado)

Al visitar nuestro sitio por primera vez, **aparece un banner de cookies** (gestionado por Complianz GDPR) que le permite:

- ✅ **Aceptar todas** las categorías
- ❌ **Rechazar todas** (excepto esenciales)
- 🔧 **Personalizar** — elegir qué categorías acepta

Puede **cambiar su decisión en cualquier momento** haciendo click en el icono de cookies en la esquina inferior izquierda del sitio (el banner reaparece).

### 4.2 Configuración de su navegador

También puede gestionar cookies directamente desde su navegador:

| Navegador | Configuración |
|---|---|
| **Google Chrome** | Configuración → Privacidad y seguridad → Cookies |
| **Mozilla Firefox** | Configuración → Privacidad & Seguridad → Cookies y datos del sitio |
| **Safari** | Preferencias → Privacidad → Cookies |
| **Microsoft Edge** | Configuración → Privacidad → Cookies |

**Importante:** si bloquea **todas las cookies**, algunas funciones del sitio podrían no operar correctamente.

### 4.3 Opt-out específicos de terceros

| Servicio | URL para opt-out |
|---|---|
| Google Analytics | https://tools.google.com/dlpage/gaoptout |
| Meta Pixel | https://www.facebook.com/help/568137493302217 |
| Anuncios personalizados Google | https://adssettings.google.com |
| Anuncios personalizados Meta | https://www.facebook.com/ads/preferences |

---

## 5. Sin consentimiento — qué pasa

Si **NO** otorga consentimiento (o lo retira):

- ✅ **Sí podemos**: usar cookies esenciales (sesión, seguridad, banner consent)
- ❌ **NO usamos**: Google Analytics, Meta Pixel, cookies marketing
- ❌ **NO enviamos**: datos a Meta CAPI ni Google Ads
- ✅ **El sitio sigue funcionando** — pero sin medición ni atribución de campañas

Su decisión es **respetada y registrada**. Si nuestro sitio detecta una conversión sin consent → registramos el lead en nuestro CRM (datos esenciales: nombre, teléfono, email) pero **NO disparamos eventos a plataformas publicitarias**.

---

## 6. Cookies first-party `lvk_*` cross-subdomain

Las cookies `lvk_*` son **propias** (first-party) y se setean con `domain=.livskin.site`. Esto significa que **se comparten entre nuestros subdominios**:

- `livskin.site` (sitio principal)
- `www.livskin.site`
- `campanas.livskin.site` (landings de campañas pagas)
- `crm.livskin.site` (admin Vtiger — interno, no expuesto)
- `dash.livskin.site` (dashboards Metabase — interno)
- `flow.livskin.site` (n8n workflows — interno)
- `erp.livskin.site` (ERP Postgres app — interno)

Esto permite que si usted llega desde un anuncio Meta (con `fbclid`) a una landing y luego vuelve al sitio principal, su atribución se preserva.

**Importante:** los subdominios `crm`, `dash`, `flow`, `erp` son **interfaces internas de administración** — los visitantes públicos NO interactúan directamente con ellos.

---

## 7. Cambios a esta Política

Cualquier cambio en nuestras prácticas de cookies se reflejará actualizando esta Política, con la fecha de modificación al inicio. **Cambios materiales** serán notificados mediante:

- Aviso destacado en el sitio
- Reapertura del banner de consent (deberá renovar su decisión)
- 30 días de antelación

---

## 8. Contacto

Si tiene preguntas sobre nuestro uso de cookies:

- **Email:** daizurma@gmail.com
- **WhatsApp consultas:** +51 980 727 888

Para ejercer sus derechos ARCO sobre datos recolectados via cookies, consulte nuestra [Política de Privacidad](privacy-policy.md).

---

*Esta Política de Cookies cumple con la Ley N° 29733 del Perú y aplica estándares equivalentes a la LGPD Brasil y GDPR EU.*
