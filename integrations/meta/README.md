# Meta — Business Manager, Pixel, Conversion API, Ads

Meta es la plataforma central de tracking y adquisición de pacientes para Livskin.

> **Última actualización del inventario:** 2026-05-09 post-audit completo.
> **Detalle del audit + cleanup:** [docs/audits/meta-business-2026-05-09/REPORT.md](../../docs/audits/meta-business-2026-05-09/REPORT.md)

## Componentes

| Componente | Uso | Estado |
|---|---|---|
| Business Manager | Cuenta corporativa de Meta | ✅ existe (3 BMs detectados — ver §Inventario abajo) |
| Facebook Page | Presencia orgánica | ✅ existe (157 seguidores, ownership pendiente) |
| Instagram Business | Presencia orgánica | ✅ existe (56 seguidores) |
| Meta Pixel / Dataset | Tracking client-side + CAPI | ✅ activo (1 dataset moderno + 1 pixel legacy desconectado) |
| **Conversion API (CAPI)** | Tracking server-side (ERP→n8n→Meta) | ✅ live (Mini-bloque 3.4 cerrado 2026-05-01, workflow [G3]) |
| Meta Ads Manager | Campañas publicitarias | ✅ activo, sin campañas históricas relevantes |
| Meta Marketing API | Gestión automatizada de campañas | 💤 diferida por audit 2026-05-03 (Acquisition = scripts, no agente) |
| WhatsApp Cloud API | Mensajería Cloud | ⏳ Fase 4A.2 (próxima sesión, número +51947741117) |
| Business Verification | Requerida para WA prod en futuro | ⏳ pendiente |

---

## §Inventario actualizado (2026-05-09)

### Business Managers (3 detectados)

| BM | Owner real | Contenido | Decisión |
|---|---|---|---|
| **Livskin Perú** | Dario (cuenta actual) | Cuenta publicitaria activa + dataset CAPI + System User CAPI | ✅ BM principal |
| **Livskin Perú Comercial** | Dario (cuenta actual) | Vacío de assets reales (residuales SU/pixel "fantasmas") | 🟡 Eliminación diferida (Meta requiere limpiar dependencias residuales primero) |
| **D'Claudia** | Cuenta vieja Dario perdida + doctora con acceso (rol exacto desconocido) | Hosting Página FB + cuenta Instagram | 🚨 Ownership pendiente — coordinar con doctora (ver REPORT.md §Hallazgos críticos) |

### Cuenta publicitaria

| ID | BM | Status | Personas con acceso |
|---|---|---|---|
| `2885433191763149` | Livskin Perú | ✅ Activa | Dario (Control total) |

### Pixels / Datasets

| Asset | ID | Tipo | Status |
|---|---|---|---|
| **Livksin Pixel 2026** | `4410809639201712` | Dataset moderno (Pixel + CAPI) | ✅ Recibiendo eventos — productivo |
| **Livksin Pixel** (legacy) | `670708374433840` | Pixel legacy | 🟡 Desconectado de cuenta publicitaria 2026-05-09; eliminación final no soportada por Meta UI (zombie inofensivo) |
| **WhatsApp Marketing Message Event Sharing** | — | Dataset placeholder | ⏳ Activar en Fase 4A.2 cuando se conecte WA Cloud API |

> **Nota typo**: ambos pixels tienen "Livksin" en el nombre (no "Livskin") — typo del proyecto original, no afecta funcionalidad.

### Apps Meta for Developers (post-cleanup 2026-05-09)

| App | ID | Estado |
|---|---|---|
| **Conversions API Application** | (sistema Meta interno) | ✅ Keep — usada por SU "Conversions API System User" para CAPI vía n8n [G3] |
| ~~Claude Audit App~~ | ~~`941702218481777`~~ | ✅ Eliminada 2026-05-09 (residual del intento Marketing API 2026-04-27) |
| ~~agent n8n~~ | ~~`2261551344333617`~~ | ✅ Eliminada 2026-05-09 (test app antigua sin uso productivo) |

### System Users (en BM Livskin Perú)

| SU | ID | Rol |
|---|---|---|
| **Conversions API System User** | `61579475681790` | ✅ Legítimo — emite events CAPI |
| **Claude Audit** | `61560721390798` | 🟡 Neutralizado 2026-05-09 (0 activos + 0 tokens). Eliminación final NO soportada por Meta UI — zombie inofensivo |

### Activos orgánicos (Página + Instagram)

| Asset | Datos | BM hosting | Riesgo |
|---|---|---|---|
| **Livskin - Centro Estético Cusco** (FB Page) | 157 seguidores · slug `LivskinCentroEsteticoCusco` · ID `525464061130920` | D'Claudia | 🚨 Cadena de permisos frágil — depende de cuenta vieja Dario perdida + rol doctora desconocido |
| **`@livskin_medicinaestetica_cusco`** (IG Business) | 56 seguidores | Conectada via FB Page (heredado) | 🚨 Mismo riesgo que página |

---

## IDs públicos (env vars)

| Variable | Valor | Dónde encontrarlo |
|---|---|---|
| `META_BUSINESS_ID` | (BM "Livskin Perú" — buscar en BM Settings) | Business Manager → Settings → Business Info |
| `META_PIXEL_ID` | `4410809639201712` | Events Manager → Dataset "Livksin Pixel 2026" |
| `META_AD_ACCOUNT_ID` | `act_2885433191763149` | Ads Manager → Settings |
| `META_FB_PAGE_ID` | `525464061130920` | Facebook Page → About (vive en BM D'Claudia ajeno) |
| `META_IG_ACCOUNT_ID` | _pendiente capturar handle ID numérico_ | Instagram Business Settings |
| `META_APP_ID` | _pendiente_ — ninguna app custom activa, CAPI usa app de sistema "Conversions API Application" | developers.facebook.com/apps |

---

## Eventos que rastreamos

### Client-side (via Tracking Engine GTM en WP)

Movido de PixelYourSite a GTM nativo en Mini-bloque 3.2 (2026-04-28). PixelYourSite **desactivado**.

- `PageView` — toda visita a livskin.site
- `ViewContent` — vista de página de tratamiento específico
- `Lead` — form submit SureForms (con `event_id` único para dedup CAPI)
- `whatsapp_click` — click a CTA WhatsApp (con `event_id` único)
- `Schedule` — cita agendada (cuando aplique en Fase 4)
- `gtm.scrollDepth` 25/50/75/100 — engagement signal

### Server-side (via Conversion API desde n8n [G3])

- `Lead` — duplicado del client-side con `event_id` matching para que Meta deduplique automáticamente
- `Purchase` — cierre de venta en ERP (con fbclid + event_id heredados del lead original via ADR-0033 lead↔cliente match)
- (futuro) `CompleteRegistration` — cliente nuevo confirmado

---

## Match quality — estrategia

Server-side CAPI recibe siempre que disponibles:
- `fbclid` (capturado del primer contacto, persistido en cookie `lvk_*` 90 días)
- `event_id` (UUID único hilo conductor end-to-end — ver memoria `project_attribution_chain_event_id`)
- Email hasheado SHA256
- Teléfono hasheado SHA256 (E.164)
- País (PE), Ciudad (Cusco)
- User agent (si estaba)

Target match quality: **"Good" o mejor** (7/10+).

---

## Secretos

En `keys/.env.integrations`:

```bash
META_APP_ID=...                    # actualmente vacío — no hay app custom (CAPI usa app sistema)
META_APP_SECRET=...                # vacío
META_ACCESS_TOKEN=...              # System User "Conversions API System User" token
META_AD_ACCOUNT_ID=act_2885433191763149
META_PIXEL_ID=4410809639201712
META_PIXEL_ACCESS_TOKEN=...        # CAPI specific token (en n8n credentials también)
```

---

## Referencias

- Meta for Developers: https://developers.facebook.com
- Conversion API: https://developers.facebook.com/docs/marketing-api/conversions-api
- **Audit + cleanup 2026-05-09**: [docs/audits/meta-business-2026-05-09/REPORT.md](../../docs/audits/meta-business-2026-05-09/REPORT.md)
- ADR-0019 v1.0 — CAPI emitida vía ERP→n8n→Meta (Opción B)
- ADR-0020 — Modelo de atribución (last-touch MVP)
- ADR-0021 — UTM persistence + Tracking Engine client-side
- ADR-0033 — Match automático lead↔cliente (mantiene cadena event_id en transición)
