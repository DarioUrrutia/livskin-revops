# Mini-bloque 3.1 — Limpieza VPS 1 (2026-04-28)

> Primer mini-bloque ejecutado de Fase 3. Todas las acciones tomadas vía wp-cli + mysql + Google APIs (programmatic, no UI tanteos).

---

## Acciones ejecutadas

### 1. Backup preventivo
- `mysqldump` de tabla `wp_options` → `/tmp/wp_options_backup_2026-04-28.sql` (1.3MB) en VPS 1
- `astra-settings` JSON snapshot → `/tmp/astra_settings_backup_2026-04-28.json` (216KB) en VPS 1

### 2. wp-cli instalado en VPS 1
- Descargado wp-cli.phar oficial → `/usr/local/bin/wp`
- Confirmado funcional con `wp --info`
- Toolchain WordPress ahora disponible para futuras operaciones programáticas

### 3. Plugin **LatePoint desactivado**
```
sudo -u www-data wp plugin deactivate latepoint --path=/var/www/livskin
→ Success
```
Razón: tenía servicios demo (Luxury Spa, Stone Therapy…), no se usaba en producción real.

### 4. Plugin **PixelYourSite desactivado**
```
sudo -u www-data wp plugin deactivate pixelyoursite --path=/var/www/livskin
→ Success
```
**Resultado clave**: resuelve el doble disparo del Pixel `4410809639201712` confirmado en audit del 2026-04-27. GTM queda como única fuente client-side del Pixel + GA4. La validación final será en Meta Events Manager → Diagnóstico (1) debería resolverse en 24-48h.

### 5. Cloudflare Turnstile configurado en SureForms 1569
**Plugin instalado:** `simple-cloudflare-turnstile` (Simple CAPTCHA Alternative with Cloudflare Turnstile, 1.39.0, 100k installs).

**Widget Cloudflare creado:**
- Name: `livskin-site-forms`
- Hostnames: `livskin.site` + `www.livskin.site`
- Mode: **Managed (Recommended)** — Cloudflare decide automáticamente cuándo mostrar challenge
- Pre-clearance: OFF
- Site Key: `0x4AAAAAADFJRFdmUz6wMNnx` (público)
- Secret Key: configurado vía archivo temp seguro (no pasó por chat ni se commiteó)

**Configuración aplicada (en 2 capas para máxima protección):**

a) **Plugin "Simple Cloudflare Turnstile"** — protege wp-login.php + comments + integraciones generales:
   - `cfturnstile_key` = Site Key
   - `cfturnstile_secret` = Secret Key
   - `cfturnstile_login` = 1 (login form protected)
   - `cfturnstile_sureforms` = 0 (deshabilitado para evitar duplicar con SureForms native)

b) **SureForms native Turnstile** — para form 1569 específicamente (más limpio que doble layer):
   - `srfm_security_settings_options.srfm_cf_turnstile_site_key` = Site Key
   - `srfm_security_settings_options.srfm_cf_turnstile_secret_key` = Secret Key
   - `srfm_security_settings_options.srfm_cf_appearance_mode` = `auto`
   - Form 1569 meta: `_srfm_captcha_security_type` = `cf-turnstile`
   - Form 1569 meta: `_srfm_form_recaptcha` = `cf-turnstile`

**Validación HTML:**
```
cf-turnstile div: 2 ocurrencias
challenges.cloudflare.com script: 1 ocurrencia
srfm-cf-sitekey div ID: 1 ocurrencia
Site Key embedido: 1 ocurrencia
Page size: 261520 → 262073 bytes (+553 bytes — widget agregado)
```

**Resultado:** bots ya no pueden submitear el form sin pasar el challenge. El próximo `form_submit` que aparezca en GA4 debería ser humano real.

### 6. Social links del header + footer arreglados (Astra theme)

**Antes**: 3 social icons en `header-social-icons-1` y 2 en `footer-social-icons-1` con `url=""` (vacío). El icono WhatsApp tenía link roto `api.whatsapp.com/send?phone=` sin número.

**Después**:
- WhatsApp: `https://api.whatsapp.com/send?phone=51982732978` (número de la doctora; se cambiará a Cloud API en Fase 4)
- Instagram: `https://www.instagram.com/livskin_medicinaestetica_cusco/`
- Facebook: `https://www.facebook.com/525464061130920` (URL ID-based, garantizada)

Aplicado vía Python script + `wp option update astra-settings --format=json`. Cache transients purgada (11 transients borrados).

**Validación HTML:**
```
href="" aria-label="(WhatsApp|Instagram|Facebook)" → 0 ocurrencias (todos los links rellenos)
```

### 7. Pixel legacy `670708374433840` — saltado
Decisión Dario: dejarlo abandonado. Tiene 1053 días sin actividad, 0 sitios conectados, 0 integraciones, 0 events. Meta ya no expone opción de archivar/eliminar Pixels desde UI. Inocuo dejarlo como está.

---

## Estado del stack post-cleanup

### Plugins activos VPS 1 (después de cleanup)
| Plugin | Estado | Rol |
|---|---|---|
| complianz-gdpr | ✅ activo | Banner cookies + consent management |
| duplicate-page | ✅ activo | Utility (admin) |
| elementor | ✅ activo | Page builder |
| header-footer-elementor | ✅ activo | Tema |
| sureforms | ✅ activo | Form 1569 con Turnstile |
| updraftplus | ✅ activo | Backups |
| simple-cloudflare-turnstile | ✅ activo (NUEVO) | Login + comments protection |
| ~~latepoint~~ | ❌ desactivado | (era servicios demo) |
| ~~pixelyoursite~~ | ❌ desactivado | (resolvía doble disparo Pixel) |

### Tracking client-side (homepage HTML)
| Componente | Estado |
|---|---|
| GTM container `GTM-P55KXDL6` | ✅ disparando (live version 17) |
| GTM tag `GA - Config` (GA4) | ✅ activo |
| GTM tag `Pixel Meta - Config` (Meta) | ✅ activo (única fuente Pixel ahora) |
| PixelYourSite scripts | ✅ ELIMINADOS (0 referencias en HTML) |
| LatePoint scripts | ✅ ELIMINADOS (0 referencias en HTML) |
| SureForms form 1569 | ✅ visible + Turnstile habilitado |
| Complianz cookie banner | ✅ activo |

### Eventos GA4 últimas 48h (post audit re-run)
```
page_view:        21    (9 users)
user_engagement:  15    (6 users)
scroll:           10    (4 users)
session_start:     9    (8 users)
first_visit:       6    (6 users)
form_start:        1    (1 user) ← último bot probable, antes de Turnstile
form_submit:       1    (1 user) ← último bot probable, antes de Turnstile
```

Tráfico orgánico real evidente (9 unique users). El form_submit detectado fue probablemente el último bot — desde ahora con Turnstile activo no debería pasar.

---

## Validación pendiente (24-48h)

1. **Meta Events Manager → Diagnóstico (1) del Pixel 2026** debe resolverse a 0 (al cesar el doble disparo).
2. **GA4 form_submit count** debe quedar en 0 hasta que llegue un humano real.
3. **Turnstile Analytics en Cloudflare** dashboard → empezarán a aparecer challenges + verifications.

---

## Backup y reversibilidad

Todas las acciones son reversibles:
- **Plugins desactivados** → re-activar con `wp plugin activate <name>` (1 comando)
- **Pixel viejo abandonado** → permanece en Meta como estaba (no se tocó)
- **Turnstile** → desactivar con `wp plugin deactivate simple-cloudflare-turnstile` + revertir post meta `_srfm_form_recaptcha` a `none`
- **Social links** → restaurar de backup `astra_settings_backup_2026-04-28.json`

Para revertir TODO el cleanup (escenario nuclear):
```bash
mysql ... < /tmp/wp_options_backup_2026-04-28.sql
wp plugin activate latepoint pixelyoursite
wp plugin deactivate simple-cloudflare-turnstile
```

Backup vive en `/tmp/` de VPS 1 — efímero (se borra en reboot). Si necesitamos preservar más tiempo, hay que copiar a `/srv/backups/` o similar.

---

**Generado:** Claude Code · 2026-04-28
**Tiempo total mini-bloque 3.1:** ~75 min
**Snapshot DO de VPS 1 antes:** ❌ no se hizo (workflow `deploy-vps1.yml` deshabilitado, no hicimos snapshot manual). Backup wp_options fue suficiente para esta clase de cambios reversibles.
