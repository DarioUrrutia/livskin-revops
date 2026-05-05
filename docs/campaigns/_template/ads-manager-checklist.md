# Ads Manager Checklist — {{CAMPAIGN_NAME}} (UI manual paso a paso)

> **Para el operador** — clicks paso a paso siguiendo este orden estricto.
> **Pre-requisito:** `campaign-config-final.md` con status `approved`.
> **Tiempo estimado:** 30-60 min según número de ad sets/ads.

---

## 1. Estructura objetivo

(referenciar `campaign-config-final.md` § 1-4)

---

## 2. Pre-flight (Día -1)

### A. Account Quality
1. Abrir https://business.facebook.com/accountquality
2. Account selector → **`{{AD_ACCOUNT}}`**
3. Verificar status:
   - ✅ "Excellent" / "Good" → seguir
   - ❌ "Limited" / "Restricted" → **PARAR**

### B. Pixel funcionando
1. Abrir https://business.facebook.com/events_manager2/list/datasets
2. Seleccionar Pixel `{{PIXEL_ID}}`
3. Verificar última recepción de PageView <24h
4. Smoke test si necesario

### C. FB Page + WhatsApp conectado
1. https://business.facebook.com/settings/pages
2. Page → "Apps and integrations" → confirmar WhatsApp `{{WA_PHONE_E164}}` conectado
3. Si NO → **PARAR**, conectar primero

### D. Método de pago + spending limit
1. https://business.facebook.com/billing
2. Verificar payment method activo
3. Spending limit ≥ S/ {{BUDGET_PEN}}

---

## 3. Crear la campaña

### Paso 1 — Abrir Ads Manager
- https://www.facebook.com/adsmanager/manage/campaigns?act={{AD_ACCOUNT}}
- Verificar arriba a la izquierda dice la cuenta correcta
- Click verde "+ Crear"

### Paso 2 — Buying type + objective
- Buying type: **Auction**
- Campaign objective: **(a llenar — del config)**
- Click "Continuar"

### Paso 3 — Special Ad Categories
- Seleccionar default ("Declarar que NO es categoría especial")
- ⚠️ Si Meta marca Health → **PARAR**, escribir al chat

### Paso 4 — Campaign details
1. Nombre: `{{CAMPAIGN_NAME}}`
2. CBO: TOGGLE ON / OFF (según config)
3. Budget: lifetime S/ {{BUDGET_PEN}}
4. Bid strategy: Mayor volumen
5. A/B test: NO
6. Click "Siguiente"

### Paso 5 — Crear Ad Set 1
(seguir `campaign-config-final.md` § 2 paso a paso)

### Paso 6 — Crear Ads del Ad Set 1
(seguir copies del config-final)

### Paso 7 — Crear Ad Set 2 + ads (si aplica)
(repetir)

### Paso 8 — Crear Ad Set 3 + ads (si aplica)
(repetir)

### Paso 9 — Review + publish
1. Click "Revisar y publicar"
2. Verificar resumen
3. Si todo OK: click "Publicar"
4. Meta envía a review (4-24h)

### Paso 10 — Verificación post-publish
1. Status del Campaign = "Activo" o "Programado"
2. Status de cada Ad
3. Si rechazado: ver razón + ajustar

---

## 4. Smoke test pre-spend significativo

(cuando Meta apruebe pero antes de gastar mucho)

### Acción operador
1. Desde celular (no admin), navegar a FB/IG
2. Buscar manualmente alguno de los ads
3. Click en CTA del ad
4. Verificar destino (URL o WA pre-poblado correcto)
5. **NO mandar mensaje** (evitar ensuciar data)

### Acción Claude
- Verificar Pixel events vía Events Manager
- Confirmar shortcodes correctos en mensaje WA pre-poblado

---

## 5. Daily checks durante campaña (5 min cada mañana)

1. Abrir Ads Manager → seleccionar la campaña
2. Screenshot de:
   - Vista campaña con métricas
   - Cada ad set
   - Top/bottom ads por CTR
3. Pasar al chat
4. Análisis + recomendaciones generadas

---

## 6. Recursos rápidos

- **Ads Manager**: https://www.facebook.com/adsmanager/manage/campaigns?act={{AD_ACCOUNT}}
- **Events Manager**: https://business.facebook.com/events_manager2/list/datasets
- **Account Quality**: https://business.facebook.com/accountquality
- **Audiences**: https://business.facebook.com/asset_library/audiences
- **Page Settings**: https://business.facebook.com/settings/pages
- **Billing**: https://business.facebook.com/billing
- **Runbook técnico Meta UI**: `docs/runbooks/meta-ads-configuracion.md`

---

**Si algo se desvía → parar, screenshot, chat. Cero improvisación.**
