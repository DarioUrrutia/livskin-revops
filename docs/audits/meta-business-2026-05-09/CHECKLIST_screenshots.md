# Audit Meta Business — checklist de screenshots

**Para Dario** — abrir cada URL, navegar a la sección indicada, tomar screenshot full-page (`Ctrl+Shift+I` para fit window si hace falta), guardar en `docs/audits/meta-business-2026-05-09/` con el nombre exacto.

> Si una URL te lleva a "selecciona Business Manager" arriba: capturá la lista que aparezca (te pide elegir cuál).

---

## 🏢 1. Business Managers (general)

### A1. Lista de todos los BMs
- **URL**: https://business.facebook.com/overview
- **Captura**: la lista de "Business accounts" que aparece arriba (donde elegís cuál)
- **Nombre archivo**: `01-bm-list.png`
- **Buscamos**: cuántos BMs tenés, sus nombres, IDs

### A2. Settings del BM principal Livskin
- **URL**: https://business.facebook.com/settings/info
- **Captura**: pantalla "Información del negocio"
- **Nombre archivo**: `02-bm-info-livskin.png`
- **Buscamos**: nombre oficial, ID del BM, verificación

---

## 💰 2. Cuentas publicitarias (ad accounts)

### B1. Lista de ad accounts
- **URL**: https://business.facebook.com/settings/ad-accounts
- **Captura**: tabla completa con todas las cuentas (activas + inactivas)
- **Nombre archivo**: `03-ad-accounts.png`
- **Buscamos**: IDs, status, gasto histórico, asignaciones

### B2. Detalle ad account principal (Livskin Perú)
- **URL**: https://business.facebook.com/settings/ad-accounts/2885433191763149?business_id=...
- **Captura**: la pestaña "People assigned" + "Apps" + "Pixels"
- **Nombre archivo**: `04-ad-account-livskin-detail.png`
- **Buscamos**: quién tiene acceso, apps conectadas, pixels asignados

### B3. Detalle ad account personal/legacy
- **URL**: similar pero ID `2130672884136872`
- **Captura**: misma pantalla
- **Nombre archivo**: `05-ad-account-personal-detail.png`
- **Buscamos**: confirmar si está vacía o tiene data residual

---

## 🎯 3. Pixels

### C1. Lista de pixels
- **URL**: https://business.facebook.com/settings/pixels
- **Captura**: tabla completa
- **Nombre archivo**: `06-pixels-list.png`
- **Buscamos**: pixel activo (`4410809639201712`) + legacy a archivar (`670708374433840`)

---

## 📱 4. Apps Meta for Developers

### D1. Lista de apps
- **URL**: https://developers.facebook.com/apps/
- **Captura**: tabla con todas las apps (incluyendo "Claude Audit App" del intento previo)
- **Nombre archivo**: `07-developer-apps-list.png`
- **Buscamos**: apps existentes, sus permisos, App Review status

### D2. Si hay app Livskin existente: detalle
- **URL**: https://developers.facebook.com/apps/<APP_ID>/dashboard/
- **Captura**: dashboard + Settings → Basic
- **Nombre archivo**: `08-livskin-app-dashboard.png` y `09-livskin-app-settings.png`
- **Buscamos**: permisos, productos activados (WhatsApp, Marketing API, etc.)

---

## 📞 5. WhatsApp Business

### E1. WhatsApp Business Manager
- **URL**: https://business.facebook.com/wa/manage/home/
- **Captura**: si te pide seleccionar BM, captura esa pantalla. Si entras directo, captura la home con phone numbers list.
- **Nombre archivo**: `10-wa-business-home.png`
- **Buscamos**: si ya hay algún número conectado, si hay templates aprobados

### E2. WhatsApp accounts en BM Settings
- **URL**: https://business.facebook.com/settings/whatsapp-business-accounts
- **Captura**: lista
- **Nombre archivo**: `11-wa-accounts-list.png`

---

## 📄 6. Páginas Facebook

### F1. Lista de páginas conectadas al BM
- **URL**: https://business.facebook.com/settings/pages
- **Captura**: tabla
- **Nombre archivo**: `12-pages-list.png`
- **Buscamos**: cuáles son oficiales Livskin, cuáles legacy

---

## 👥 7. Usuarios + System Users

### G1. People (usuarios humanos)
- **URL**: https://business.facebook.com/settings/people
- **Captura**: lista
- **Nombre archivo**: `13-bm-people.png`

### G2. System Users
- **URL**: https://business.facebook.com/settings/system-users
- **Captura**: lista — incluye "Claude Audit System User" del intento previo
- **Nombre archivo**: `14-bm-system-users.png`

---

## ⚡ 8. Información del Pixel activo

### H1. Detalle Pixel activo (en Events Manager)
- **URL**: https://business.facebook.com/events_manager2/list/pixel/4410809639201712/overview
- **Captura**: overview + recent events (últimas 24h)
- **Nombre archivo**: `15-pixel-events-overview.png`
- **Buscamos**: si pixel está recibiendo events, qué events está disparando

---

## 📋 Resumen

Total: **15 screenshots**. Estimado: 15-20 min en navegar + capturar.

Cuando termines, dejá los archivos en `docs/audits/meta-business-2026-05-09/` y avisame. Yo analizo + documento estructura + plan de cleanup.

Si alguna URL te da error o "no tengo acceso", anótalo (es información útil — significa que el BM no tiene esa cosa).
