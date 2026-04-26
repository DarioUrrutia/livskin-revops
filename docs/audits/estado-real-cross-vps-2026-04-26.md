# Audit cross-VPS — estado REAL al 2026-04-26

> Verificado en vivo por SSH + curl + queries directos a las DBs.
> Reemplaza cualquier suposición previa sobre qué está instalado/configurado/operativo.

---

## VPS 1 — livskin-wp (WordPress, 46.101.97.246)

### Plugins instalados (`/var/www/livskin/wp-content/plugins/`)

| Plugin | Activo | Configurado | Operativo | Notas |
|---|---|---|---|---|
| **complianz-gdpr** | ✅ | ✅ parcial | ✅ | Region BR (Brasil GDPR), org="Livskin", email=daizurma2@gmail.com, tel=+51982732978. `compile_statistics=google-tag-manager`. Banner cookies cargando en home. |
| **pixelyoursite** (free 11.2.0.4) | ✅ | ❌ **SIN PIXEL ID** | ❌ | Plugin activo y scripts cargados consent-gated, pero **no hay Pixel ID configurado, no hay CAPI token, no hay GA4**. Solo metadata de versión en wp_options. |
| **sureforms** (2.7.0) | ✅ | ✅ | ⚠️ | 1 form publicado: ID **1569 "Formulario pagina Inicio"** con 5 campos (Nombres, Email, Telefono, Tratamiento dropdown 8 opciones). reCAPTCHA: NONE. **0 entries en wp_srfm_entries**. Email notification → daizurma2@gmail.com. |
| **latepoint** (5.3.2) | ✅ | ⚠️ datos demo | ⚠️ | 4 servicios cargados pero **son demo** (Luxury Spa, Stone Therapy, Aroma Therapy, Skin Treatment). 1 booking. **NO son los servicios reales de Livskin.** |
| **elementor** | ✅ | ✅ | ✅ | Builder activo, render OK. |
| **header-footer-elementor** | ✅ | ✅ | ✅ | Tema Astra integrado. |
| **duplicate-page** | ✅ | n/a | ✅ | Utility plugin. |
| **updraftplus** | ✅ | ⚠️ verificar | ? | Backup plugin — falta confirmar destino de backups. |

### Lo que SÍ está cargando en https://livskin.site/

- **GTM container vivo**: `GTM-P55KXDL6` cargado vía `<script>` directo en `</body>` (verified en HTML rendered).
- **SureForms 1569 visible** en el home (clase `srfm-form-container-1569`).
- **PixelYourSite scripts** cargados pero **consent-gated** (`data-cmplz-src`) y **sin Pixel ID** → no envían eventos.
- **Complianz banner** activo.
- **LatePoint scripts** cargados.
- **Elementor + Astra theme** rendering.
- **WhatsApp link en CTA**: `api.whatsapp.com/send?phone=` ← **número VACÍO. Link roto.**
- **Cloudflare**: confirmed via header `Server: cloudflare` + `CF-RAY`.

### Lo que NO está

- ❌ Meta Pixel ID configurado (PixelYourSite plugin sin ID).
- ❌ CAPI token configurado.
- ❌ GA4 configurado (no `G-XXXXXX` en page).
- ❌ GTM tags publicados ≠ del container (no podemos verificar interno sin acceso al admin GTM).
- ❌ WhatsApp number en CTA del home.
- ❌ Webhook de SureForms hacia Vtiger/ERP — el form solo manda email, no escribe en CRM.
- ❌ Conexión SureForms ↔ formulario-livskin.onrender.com — son sistemas distintos no integrados.
- ❌ LatePoint con servicios reales de Livskin.

### Web server

- nginx + php8.1-fpm
- SSL Letsencrypt + Cloudflare delante
- DocumentRoot: `/var/www/livskin/`
- DB: MariaDB local (`livskin_wp`, user `livskin_user`, password = `livskin` ⚠️ débil)

---

## VPS 2 — livskin-vps-operations (Operations, 167.172.97.197)

### Containers (todos UP)

| Container | Status | Volumes |
|---|---|---|
| `n8n` | Up 2 weeks | `/home/livskin/apps/n8n/data:/home/node/.n8n` |
| `vtiger` | Up 2 weeks | `/home/livskin/apps/vtiger/data:/var/www/html` |
| `vtiger-db` | Up 2 weeks | (volumen named) |
| `metabase` | Up 10 days | (volumen named, NO host bind) |
| `postgres-analytics` | Up 10 days | (volumen named) |
| `nginx` | Up 2 weeks | configs en /etc/nginx |
| `livskin-sensor` | Up 7 hours (healthy) | port 9100 |

### Estado real de cada servicio

#### n8n (flow.livskin.site)
- ✅ Container vivo, accessible.
- ❌ **0 workflows** (`SELECT COUNT(*) FROM workflow_entity` → 0). Ningún automation creado todavía.

#### Vtiger (crm.livskin.site)
- ✅ Container vivo.
- ✅ DB `livskin_db` existe.
- ⚠️ **VIRGEN**: 0 leads, 0 contacts, 0 opportunities. 1 user (admin).
- ⚠️ Credenciales débiles: root/livskin/livskin/livskin todas iguales a `livskin`.

#### Metabase (dash.livskin.site)
- ✅ `GET /api/health` → 200 OK.
- Datos en docker volume named, no en host bind → migrate-from-home.sh **no necesita migrar metabase data**.
- Estado de dashboards no verificado (requiere login UI).

#### postgres-analytics
- ✅ DB `analytics`, user `analytics_user`.
- ✅ 4 tablas: `crm_stages`, `events`, `leads`, `opportunities`.
- ❌ **Todas con 0 filas**. Ningún ETL ha corrido.

### Migración pendiente (`migrate-from-home.sh`)

- Compose files NUEVOS en `/srv/livskin-revops/infra/docker/vps2-ops/{n8n,vtiger,metabase,postgres-analytics,nginx}/` ← creados pero **NO en uso**.
- Containers actuales siguen montando volúmenes desde `/home/livskin/apps/`.
- **Workflow `deploy-vps2.yml` está deshabilitado** (push trigger off) hasta ejecutar migración manualmente.

---

## VPS 3 — livskin-vps-erp (ERP + Brain, 139.59.214.7)

### Containers (4, todos healthy)

| Container | Status |
|---|---|
| `erp-flask` | Up 31 minutes (healthy) |
| `nginx-vps3` | Up 5 days (healthy) |
| `embeddings-service` | Up 5 days (healthy) |
| `postgres-data` | Up 5 days (healthy) |

### Postgres (3 DBs lógicas)

#### `livskin_erp` — 17 tablas, datos reales cargados
| Tabla | Filas |
|---|---|
| clientes | **134** (backfill desde Sheets) |
| catalogos | **88** |
| ventas | **88** |
| pagos | **84** |
| audit_log | **8** (incluye `infra.deploy_completed` post-fix) |
| user_sessions | 5 |
| agent_budgets | 5 |
| infra_snapshots | 3 |
| users | 2 |
| gastos | 1 |
| **leads, lead_touchpoints, agent_api_calls** | 0 (esperado — no operativo todavía) |
| form_submissions, dedup_candidates, agent_budget_alerts | 0 |

#### `livskin_brain` — schema listo, vacío
- 7 tablas: `clinic_knowledge`, `conversations`, `creative_memory`, `embedding_runs`, `learnings`, `project_knowledge` + alembic_version.
- Extensión **pgvector 0.8.2** instalada ✅.
- Extensión **pgcrypto** ✅.
- Sin contenido todavía (no se ha ejecutado el ingest).

#### `livskin_erp_test`
- Existe, vacía, para tests.

### Endpoints externos

- ✅ `https://erp.livskin.site/` → 302 (redirect login OK).
- ✅ `https://erp.livskin.site/api/internal/health` → 200 OK JSON.

### Block 0 v2 — confirmado completado
Los 9 sub-bloques deployados, validados end-to-end (`workflow e50b0f9 SUCCESS`), tag `v0.foundation` push. Audit cross-VPS funcionando (deploy event registrado). 5 incidentes resueltos en cadena (DO_API_TOKEN whitespace, image:create scope, SNAP_ID stdout/stderr split, INET multi-IP, install-doctl retry).

---

## Cuentas externas (verificación parcial — requiere confirmación de Dario)

| Servicio | Estado verificable | Pendiente confirmar |
|---|---|---|
| **Cloudflare** | ✅ activo (proxying livskin.site) | Acceso al dashboard, WAF rules, Turnstile. |
| **GTM** | ✅ container `GTM-P55KXDL6` LIVE en livskin.site | ¿Tags publicados dentro? ¿Triggers? ¿Variables? |
| **Meta Business** | ❓ no verificable desde fuera | ¿Hay BM creado? ¿Hay Pixel ID generado? ¿Token CAPI generado? |
| **GA4** | ❌ NO cargado en livskin.site | ¿Hay propiedad GA4 creada? ¿Measurement ID? |
| **WhatsApp Business API** | ❌ link en home con phone vacío | ¿Trámite Meta iniciado? ¿Test number activo? |
| **Render** (formulario-livskin) | ✅ vivo y respondiendo, SIN tracking | ¿Sigue siendo el SoT real de leads o ya fue reemplazado por SureForms? |
| **Google Sheets** (DB leads) | n/a (asumido vivo per master plan) | ¿Cuántos leads tiene actualmente? Confirmar timestamp último export. |

---

## Contradicción crítica encontrada (requiere decisión Dario)

**Dos sistemas de captura de leads coexisten:**

1. **SureForms 1569** en `https://livskin.site/` — visible en home, envía email a daizurma2@gmail.com, **0 submissions registradas en DB**.
2. **formulario-livskin.onrender.com** — vivo, escribe a Google Sheets (per master plan), pero **NO está enlazado desde livskin.site**.

**Pregunta abierta:** ¿Los leads reales del último mes vinieron por (a) SureForms vía email, (b) Render form vía link directo (Instagram bio, WhatsApp, ads), o (c) ambos?

Esta respuesta cambia drásticamente cómo abordamos la integración tracking + CRM.

---

## Gaps reales para Fase 3 (tracking + observabilidad)

Después de este audit, la lista NO es "instalar Pixel/GTM/GA4". Es:

### Marketing tech (lo que existe pero está incompleto)
1. **Configurar Meta Pixel ID** en plugin PixelYourSite (Pixel YA está creado o falta? — Dario confirma)
2. **Generar y configurar token CAPI** en PixelYourSite
3. **Crear propiedad GA4** + agregar Measurement ID al sitio (vía GTM, no plugin separado)
4. **Configurar tags GTM**: pageview GA4, evento form_submit, evento booking_created, evento whatsapp_click
5. **Conectar Complianz consent-mode** → Pixel + GA4 (hoy compile_statistics=GTM pero consent-mode=no)
6. **Reparar link WhatsApp CTA** del home (phone vacío) o reemplazar con n8n webhook
7. **Decidir SoT formulario**: SureForms vs Render → migrar uno hacia el otro
8. **Conectar form (cualquiera) → Vtiger + ERP** vía webhook (hoy no hay integración)
9. **UTMs persistence**: hidden fields en form + cookie de primera visita

### Observabilidad
10. **Langfuse** instalación (n8n container o nuevo) — no existe todavía
11. **Metabase dashboards reales** — login y crear dashboards (hoy 0 según verificación parcial)
12. **postgres-analytics ETL** — conectar source DBs y poblar las 4 tablas vacías

### Pre-requisitos NO técnicos
- A. Decidir form SoT (SureForms vs Render).
- B. Confirmar existencia/credenciales en Meta Business, GA4, GTM (Dario en UI).
- C. Estado del trámite WhatsApp Business API (5-10 días Meta).

---

## Próximo paso recomendado (post-audit)

Antes de ejecutar nada, sesión corta de 15-20 min con Dario para:

1. Resolver la contradicción form SureForms vs Render (cuál es el real SoT operativo).
2. Confirmar qué cuentas externas existen ya (Meta Business, GA4, GTM admin).
3. Confirmar si hay Pixel ID generado pero no aplicado, vs Pixel ID por crear.
4. Definir si Fase 3 prioriza marketing-tech (Pixel/GA4/CAPI) o integraciones (form→Vtiger→ERP).

Este audit elimina toda suposición. Cualquier propuesta posterior parte de la base verificada arriba.
