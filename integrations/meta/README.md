# Meta — Business Manager, Pixel, Conversion API, Ads

Meta es la plataforma central de tracking y adquisición de pacientes para Livskin.

## Componentes

| Componente | Uso | Estado |
|---|---|---|
| Business Manager | Cuenta corporativa de Meta | ✅ existe |
| Facebook Page | Presencia orgánica | ✅ existe |
| Instagram Business | Presencia orgánica | ✅ existe |
| Meta Pixel | Tracking client-side en livskin.site | ✅ activo vía PixelYourSite |
| **Conversion API (CAPI)** | Tracking server-side (n8n → Meta) | ⏳ Fase 3 |
| Meta Ads Manager | Campañas publicitarias | ✅ activo |
| Meta Marketing API | Gestión automatizada de campañas | ⏳ Fase 5 (Acquisition Engine) |
| Meta Ad Library API | Research competencia | ⏳ Fase 5 (Content Agent) |
| Business Verification | Requerida para WhatsApp prod | ⏳ Fase 0 trámite |

## IDs públicos (a llenar en Fase 0)

| Variable | Valor | Dónde encontrarlo |
|---|---|---|
| `META_BUSINESS_ID` | _pendiente_ | Business Manager → Settings → Business Info |
| `META_PIXEL_ID` | _pendiente_ | Events Manager → Pixel → Settings |
| `META_AD_ACCOUNT_ID` | _pendiente_ | Ads Manager → Settings |
| `META_FB_PAGE_ID` | _pendiente_ | Facebook Page → About |
| `META_IG_ACCOUNT_ID` | _pendiente_ | Instagram Business Settings |
| `META_APP_ID` | _pendiente_ | developers.facebook.com/apps |

## Eventos que rastreamos

### Client-side (via PixelYourSite en WP)

- `PageView` — toda visita a livskin.site
- `ViewContent` — vista de página de tratamiento específico
- `Lead` — form submit SureForms
- `InitiateCheckout` — click to WhatsApp desde CTA
- `Schedule` — cita agendada (push desde JS al confirmar)

### Server-side (via Conversion API desde n8n)

- `Lead` — duplicado del client-side para mejor match quality
- `Purchase` — cierre de venta en ERP (con fbclid recuperado del lead original)
- `CompleteRegistration` — cliente nuevo confirmado en Vtiger

## Match quality — estrategia

Server-side CAPI recibe **siempre** que disponibles:
- `fbclid` (capturado del primer contacto)
- Email hasheado SHA256
- Teléfono hasheado SHA256 (formato internacional)
- País (PE)
- Ciudad (Cusco)
- IP (del server que reenvía, no útil para match — ok)
- User agent (si estaba)

Target match quality: **"Good" o mejor** (7/10+).

## Secretos

En `keys/.env.integrations`:

```bash
META_APP_ID=...
META_APP_SECRET=...
META_ACCESS_TOKEN=...             # system user token
META_AD_ACCOUNT_ID=act_...
META_PIXEL_ID=...
META_PIXEL_ACCESS_TOKEN=...       # CAPI specific token
```

## Referencias

- Meta for Developers: https://developers.facebook.com
- Conversion API: https://developers.facebook.com/docs/marketing-api/conversions-api
- ADR-0019 — Tracking architecture
- ADR-0020 — Modelo de atribución (last-touch MVP)
