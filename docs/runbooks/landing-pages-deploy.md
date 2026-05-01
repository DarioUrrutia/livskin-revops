---
runbook: landing-pages-deploy
severity: medium
auto_executable: false
trigger:
  - "Crear nueva landing dedicada para campaña paga"
  - "Modificar landing existente"
  - "Debugging si tracking de landing no funciona"
required_secrets:
  - CLOUDFLARE_API_TOKEN (GitHub Actions secret)
  - CLOUDFLARE_ACCOUNT_ID (GitHub Actions secret)
  - AUDIT_INTERNAL_TOKEN (GitHub Actions secret)
related_skills:
  - livskin-deploy
---

# Runbook — Crear / actualizar / debugear landing pages

## Arquitectura (resumen)

```
Claude Design (UI design)
   ↓ export zip
infra/landing-pages/<slug>/  (en repo)
   ↓ git push to main
GitHub Actions deploy-landings.yml
   ↓ wrangler pages deploy
Cloudflare Pages (livskin-campanas project)
   ↓ DNS CNAME proxied
campanas.livskin.site/<slug>/  (live, edge global)
```

---

## A. Crear landing nueva

### A.1 Diseñar en Claude Design

1. Abrí claude.ai/design
2. Crea nueva página/proyecto
3. Diseñá secciones libremente (hero, beneficios, antes/después, form, etc.)
4. **CRÍTICO — respetar las convenciones HTML** documentadas en `infra/landing-pages/_shared/conventions.md`:
   - `<form data-livskin-form="true">` para forms a interceptar
   - `<input name="nombre">`, `<input name="phone">`, `<input name="email">`, `<input name="consent_marketing" type="checkbox">`
   - `<a data-livskin-wa="true" href="https://wa.me/...">` para links WhatsApp
   - `<meta name="livskin-treatment" content="Botox">` en `<head>`
   - `<meta name="livskin-landing-slug" content="<slug>">`
   - `<meta name="robots" content="noindex,nofollow">`
   - Footer con links Privacy + Terms + Cookies + disclaimer "resultados varían"

### A.2 Exportar de Claude Design

1. Botón Share → "Export as standalone HTML" o "Download project as .zip"
2. Descomprimí el zip localmente

### A.3 Copiar al repo

```bash
# Slug en kebab-case (ADR-0030 file naming)
# Ejemplo: botox-mar2026, prp-promo, hilos-cusco
SLUG="prp-mar2026"

# Crear folder de la landing nueva
mkdir -p "infra/landing-pages/$SLUG"

# Copiar contenido del export descomprimido
cp -r ~/Downloads/<export-folder>/* "infra/landing-pages/$SLUG/"

# Verificar que el HTML principal se llame index.html
# (CF Pages busca index.html por default)
ls infra/landing-pages/$SLUG/
# Si el HTML se llama landing.html o similar:
mv "infra/landing-pages/$SLUG/landing.html" "infra/landing-pages/$SLUG/index.html"
```

### A.4 Crear `livskin-config.json` de la landing

Copia el template y ajusta:

```bash
cp infra/landing-pages/_template/livskin-config.json \
   infra/landing-pages/$SLUG/livskin-config.json

# Editar valores específicos:
# - slug
# - treatment_canonical_label (debe coincidir con livskin-config-master.json → treatments[].label)
# - og.title, og.description, og.image
# - wa_message_template (con {{treatment}} placeholder)
```

### A.5 Inyectar livskin-tracking.js + meta tags al index.html

**Si Claude Design siguió las convenciones exactas → el build CI/CD inyecta automáticamente.**

**Si NO siguió convenciones perfectamente:** edit manual del `index.html`:

```html
<head>
  <!-- ... contenido existente ... -->

  <!-- AGREGAR estas líneas: -->
  <meta name="livskin-treatment" content="Botox" />
  <meta name="livskin-landing-slug" content="prp-mar2026" />
  <meta name="livskin-conventions-version" content="1.0" />
  <meta name="robots" content="noindex,nofollow" />

  <!-- OG -->
  <meta property="og:title" content="..." />
  <meta property="og:description" content="..." />
  <meta property="og:image" content="/uploads/og-image.jpg" />

  <!-- Tracking config + script -->
  <script>
    window.LIVSKIN_CONFIG = {
      pixel_id: '4410809639201712',
      webhook_url: 'https://flow.livskin.site/webhook/acquisition/form-submit'
    };
  </script>
  <script src="/livskin-tracking.js" defer></script>
</head>
```

### A.6 Validar localmente (opcional pero recomendado)

```bash
# Abrir en browser local
cd infra/landing-pages/$SLUG/
python3 -m http.server 8080
# Visitar: http://localhost:8080
# Verificar:
# - Form fields tienen name="nombre", name="phone", etc.
# - Footer tiene links privacy/terms/cookies
# - Console no muestra errors

# Lighthouse local check
npx lighthouse http://localhost:8080 --only-categories=performance --form-factor=mobile
```

### A.7 Commit + push

```bash
git add infra/landing-pages/$SLUG/
git status

# Mensaje commit con detalle
git commit -m "feat(landings): nueva landing $SLUG para campaña <descripcion>

- Treatment: <Botox|PRP|...>
- Período campaña: <YYYY-MM a YYYY-MM>
- Convenciones HTML: aplicadas via livskin-tracking.js

Co-Authored-By: <quien>"

# Push triggers GitHub Actions deploy
git push origin main
```

### A.8 Verificar deploy

```bash
# 1. GitHub Actions ejecutándose:
# https://github.com/DarioUrrutia/livskin-revops/actions

# 2. Cloudflare Pages dashboard:
# https://dash.cloudflare.com → Pages → livskin-campanas → Deployments

# 3. URL live (después de ~2-3 min):
curl -sI "https://campanas.livskin.site/$SLUG/" | head -5
# Esperado: HTTP/2 200

# 4. Verificar tracking script carga:
curl -s "https://campanas.livskin.site/livskin-tracking.js" | head -10
# Esperado: contenido del script (no 404)
```

---

## B. Modificar landing existente

```bash
# Editar archivos en infra/landing-pages/<slug>/
# Pueden ser: copy, imágenes, JSON config, layout

git add infra/landing-pages/<slug>/
git commit -m "fix(landings): <descripción>"
git push origin main
# CI/CD redeploy automatic ~2 min
```

**Para rollback rápido a versión anterior:**

```bash
# 1. Git revert del commit problemático
git revert <commit-sha>
git push origin main

# 2. O via Cloudflare Pages dashboard:
# Deployments → seleccionar deploy anterior → "Rollback to this deployment"
```

---

## C. Test E2E lead via landing → Vtiger → ERP → CAPI

### C.1 Submit form en landing live

```bash
# Visitar la landing en browser
https://campanas.livskin.site/<slug>/?utm_source=test&utm_campaign=runbook-test

# Llenar form con datos identificables:
# - Nombre: "Runbook Test Lead"
# - Phone: +51999000<XX> (único)
# - Email: runbook-test@example.com
# - Aceptar consent_marketing checkbox

# Click submit
```

### C.2 Verificar lead en n8n [A1] execution log

```bash
ssh -F keys/ssh_config livskin-ops 'sqlite3 /home/livskin/apps/n8n/data/database.sqlite \
  "SELECT id, status, startedAt FROM execution_entity WHERE workflowId=\"a1-form-submit-vtiger-lead\" ORDER BY id DESC LIMIT 3;"'
```

Debe mostrar execution con status=success en el último minuto.

### C.3 Verificar Lead en Vtiger

```bash
ssh -F keys/ssh_config livskin-ops 'docker exec vtiger-db mysql -u livskin -plivskin livskin_db \
  -e "SELECT ld.leadid, ld.firstname, ld.lastname, ld.email, lcf.cf_853 utm_source, lcf.cf_871 event_id, lcf.cf_875 tratamiento \
      FROM vtiger_leaddetails ld \
      LEFT JOIN vtiger_leadscf lcf ON lcf.leadid=ld.leadid \
      LEFT JOIN vtiger_crmentity c ON c.crmid=ld.leadid \
      WHERE c.deleted=0 ORDER BY ld.leadid DESC LIMIT 3;"'
```

### C.4 Verificar lead en ERP (después de cron [B3], ~2 min)

```bash
ssh -F keys/ssh_config livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp \
  -c "SELECT id, vtiger_id, nombre, phone_e164, utm_source_at_capture, event_id_at_capture \
      FROM leads ORDER BY id DESC LIMIT 3;"'
```

### C.5 Verificar evento Meta CAPI

```bash
# Audit log de capi events
ssh -F keys/ssh_config livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp \
  -c "SELECT occurred_at, action, metadata FROM audit_log \
      WHERE action LIKE '\''tracking.capi%'\'' ORDER BY id DESC LIMIT 3;"'

# O en Meta Events Manager → Probar eventos
# https://business.facebook.com/events_manager2/list/dataset/4410809639201712
```

### C.6 Cleanup test data

```bash
# Vtiger: borrar lead test (vía REST API o UI)
# ERP: DELETE FROM leads WHERE phone_e164 = '+51999000XX'
```

---

## D. Troubleshooting

### "Lead no aparece en Vtiger después de submit"

```bash
# 1. Verificar tracking script carga
# Browser DevTools → Network tab → buscar livskin-tracking.js (200 OK)

# 2. Verificar que el form tiene data-livskin-form="true"
# Browser DevTools → Inspector → buscar atributo en <form>

# 3. Verificar consent_marketing checkbox checked
# Sin checkbox marcado → POST no se dispara (HTML5 required validation)

# 4. Verificar POST a webhook en Network tab
# Filtrar por "form-submit"
# Esperado: POST 200

# 5. Si POST falla con CORS error:
# Verificar nginx CORS config en VPS 2:
ssh livskin-ops 'cat /home/livskin/apps/nginx/sites/n8n.conf | grep -A 3 acquisition'
# Debe incluir: Access-Control-Allow-Origin: https://campanas.livskin.site

# 6. Verificar n8n [A1] activo
ssh livskin-ops 'sqlite3 /home/livskin/apps/n8n/data/database.sqlite \
  "SELECT name, active FROM workflow_entity WHERE id=\"a1-form-submit-vtiger-lead\";"'
```

### "Banner de cookies no aparece"

```bash
# Verificar en Browser DevTools que <div data-livskin-banner="true"> existe en DOM
# Verificar window.LivskinTracking.getConsent() === 'pending'
# Si es 'accepted_all' o 'rejected_all', limpiar cookie:
document.cookie = 'lvk_consent=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=.livskin.site';
location.reload();
```

### "Pixel no dispara"

```bash
# Solo dispara si user dio consent marketing
# Verificar:
window.LivskinTracking.hasMarketingConsent()  # Debe ser true

# Verificar window.fbq existe y se inicializó
window.fbq  # debe ser function

# Test manual:
window.LivskinTracking.fireEvent('PageView', {})
# Network tab debe mostrar request a connect.facebook.net
```

### "Lighthouse score < 60"

Ver `infra/landing-pages/_shared/conventions.md` § 7 checklist + considerar:
- Optimizar imágenes (WebP, lazy loading)
- Eliminar fonts innecesarias o subset
- Minificar CSS/JS si Claude Design genera versión development

---

## E. Versionado de campañas

Cada campaña en su propio folder con sufijo de período:

```
infra/landing-pages/
├── botox-mar2026/      # Marzo 2026
├── botox-jul2026/      # Julio 2026 (versión nueva)
├── prp-launch-2026/    # PRP launch
└── ...
```

**Vieja URL → redirect 301 a nueva** (configurar en Cloudflare Pages → Redirects o `_redirects` file en root del build):

```
# infra/landing-pages/_shared/_redirects
/botox-mar2026/* /botox-jul2026/:splat 301
```

---

## F. Cuándo reabrir este runbook

- Si Claude Design cambia formato de export
- Si Cloudflare Pages cambia su API o build process
- Si convenciones HTML evolucionan (new mandatory tags)
- Si volumen >20 landings y necesitamos process automation
- Cuando Brand Orchestrator F5 esté activo y genere landings auto

---

## G. Cross-references

- ADR-0031 — Landings hosting CF Pages + sistema convenciones
- `infra/landing-pages/_shared/conventions.md` — markup HTML contract
- `infra/landing-pages/_shared/livskin-tracking.js` — script standalone
- `infra/landing-pages/_shared/livskin-config-schema.json` — schema validador
- `livskin-config-master.json` — single source of truth datos negocio
- `.github/workflows/deploy-landings.yml` — CI/CD workflow
- `docs/legal/privacy-policy.md` — privacy policy linkeada en footer
- `docs/legal/terms-of-service.md` — terms linkeados en footer
- `docs/legal/cookie-policy.md` — cookies linkeada en banner consent
