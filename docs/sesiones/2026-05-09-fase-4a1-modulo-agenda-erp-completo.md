---
fecha: 2026-05-09
duracion: ~10h (sesión muy larga)
modo: PROYECTO (#12)
participantes: Dario + Claude Code
fase: 4A.1 — Modulo Agenda Minima ERP
estado: ✅ COMPLETO + mergeado a main (commit c84ff37)
---

# Sesión 2026-05-09 — Fase 4A.1 Módulo Agenda Mínima ERP

## Resumen ejecutivo

Sesión larga de implementación + iteración UX intensa. Resultado: **Sub-bloque 4A.1 completo y mergeado a main**, incluyendo backend + UI mobile-first + tests E2E reales del pipeline (lead → Vtiger → cron B3 → ERP → card automática en Agenda).

Bonus: arquitectura del **bot-broker bidireccional** (Fase 4A.3) discutida y documentada en memoria 🔥.

## Lo construido

### Backend Agenda (ADR-0035)
- Migration Alembic 0007 — tabla `appointments` + 5 índices + CHECK constraints (subject + status enum)
- Modelo SQLAlchemy con 6 estados (`scheduled` / `confirmed` / `attended` / `no_show` / `cancelled` / `rescheduled`)
- Service `appointment_service.py` con 9 métodos: create, get_by_cod, list_with_filters, update, confirm, mark_attended, mark_no_show, cancel, reschedule
- **Workflow crítico mark_attended**: si lead.id presente y phone no matchea cliente existente → crea cliente con `cod_lead_origen` heredado (ADR-0033) + UTMs; si phone matchea → vincula al cliente existente
- **Auto-transiciones lead.estado_lead**: `mark_attended → cliente`, `mark_no_show → contactado` (re-nurturing)
- Blueprint `api_appointments.py` con 9 endpoints REST + auth bcrypt
- Feature flag `AGENDA_FEATURE_ENABLED` (default OFF)
- 53/53 tests passing (29 service + 21 routes + 3 cliente recurrente). Coverage del service: **98%**.

### UI mobile-first
- Pestaña Agenda con **2 secciones**:
  1. **"Esperando agendar fecha"** — leads activos sin appointment activa. Cards `.lead-card` con: nombre + estado pill + phone tappable + cod_lead + tratamiento + campaña + fecha llegada + botón verde "📅 Agendar fecha"
  2. **"Próximas citas"** — appointments scheduled/confirmed con cards `.agenda-card`
- Header refactor: logo + nombre user + botón **"⏻ Salir"** prominente + menú **"⚙️"** colapsable con audit log/system health/agent costs/cambiar password/cerrar sesión
- Tabs scrolleables horizontalmente (7+ pestañas con `overflow-x: auto`)
- Sticky submit bottom en 3 forms (Venta, Pago, Gasto) para mobile <720px
- Tablas Dashboard: `width: auto` + wrappers `overflow-x: auto`, classes `.num` (nowrap right tabular-nums), `.fecha` (nowrap left)
- Decimales formateados: `fmtPct()` (1 decimal), `fmtFecha()` (dd-mm-yyyy)
- Zona discreta italic debajo de categoría en "Atenciones Recientes"

### Tests + Audit (Playwright headed iPhone 15 393×852)
- `scripts/erp_full_audit.py` — audit visual con detección de overflow (filtra elementos en contenedores scrolleables)
- `scripts/erp_smoke_e2e.py` — flow E2E Agenda: 22/22 PASS (login + 7 pestañas + workflow Confirmar→Vino→crea cliente + No vino + logout)
- `scripts/erp_smoke_ventas_pagos.py` — ventas via UI + validación trigger DEBE recálculo (V1, V2, V3 OK + DEBE 100→160→300 verificado paso a paso vía SQL)
- `scripts/smoke_pipeline_lead_to_agenda.py` — **E2E real del pipeline**: POST simulated form → n8n A1 → Vtiger Lead (10x68) → cron B3 (~90s) → ERP `LIVLEAD0001` → card "Esperando agendar" automática
- `scripts/quick_screenshot_agenda.py` — helper para captura rápida iPhone 15
- `scripts/cleanup_smoke_data.sql` — script idempotente para limpiar TODOS los TEST_SMOKE

### Memorias 🔥 nuevas (8)
- `feedback_no_redeclarar_js_globals_formulario_html` — antes de `const X` en formulario.html legacy, grepear (un SyntaxError rompe TODO el JS)
- `feedback_docker_compose_restart_no_recarga_env` — toggles de feature flags requieren `up -d --force-recreate`, no `restart`
- `feedback_doctora_solo_erp_vtiger_automatico` — doctrina operacional: doctora opera SOLO ERP, transiciones lead se sincronizan a Vtiger via workflow async
- `feedback_smoke_test_leads_audit_log` — `audit_log.lead.synced_from_vtiger > leads.count` = SMOKE TESTS limpiados, NO regresión
- `feedback_no_revisiones_a_medias` — barrer todos los formatos antes de afirmar "X no existe" (.html + .jsx + .tsx + configs.d/, sshd -T no grep manual)
- `feedback_mobile_targets_layout_rules` — viewports CSS ~393px (iPhone 15/16 + Xiaomi 14T Pro). Tablas: nombres natural / precios+fechas nowrap
- `feedback_validar_ui_con_playwright_obligatorio` — capturar screenshot iPhone 15 + ver visualmente ANTES de declarar listo
- `project_chatbot_broker_architecture` — arquitectura bot-broker bidireccional aprobada para Fase 4A.3

## Iteraciones UX significativas

Sesión de **mucho push-pull** con Dario sobre layout. Errores y correcciones progresivas:

1. ❌ Modal "+ Nueva cita" pedía pegar códigos `LIVCLIENT####` — UX inutilizable
2. ✅ Refactorizado a dropdowns con datalist (radios "Lead" vs "Cliente existente")
3. ❌ "Cliente existente" era flujo confuso (Dario clarificó: solo lead-only)
4. ✅ Modal lead-only + auto-rellenar tratamiento + badge recurrente
5. ❌ Botón "+ Nueva cita" como acción primaria contra el modelo objetivo
6. ✅ Degradado a "+ manual" gris secundario (chatbot crea citas en futuro)
7. ❌ Cards usaban tabla 5-cols con botones cortados en mobile
8. ✅ Cards mobile-first responsive (1 col mobile / 3 col desktop)
9. ❌ Bug overlay del seccion-resumen-pago — falso positivo de Playwright timing
10. ✅ Sticky submit bottom + script con `force=True`
11. ❌ Reglas wrap CSS demasiado agresivas (max-width + line-clamp + ellipsis)
12. ✅ Solo `.num` y `.fecha` con nowrap, resto wrap natural
13. ❌ Leads escondidos en dropdown del modal (Dario: "no deberian aparecerme automaticamente los cards?")
14. ✅ Sección "Esperando agendar fecha" arriba de "Próximas citas"
15. ❌ Card "Esperando agendar" usando `.agenda-card` no optimizado mobile
16. ✅ `.lead-card` rediseñada compacta + nombre wrap natural sin ellipsis

## Decisiones arquitectónicas tomadas

### Doctrina operacional (Dario 2026-05-09)
- **La doctora opera SOLO el ERP** — jamás toca Vtiger
- **WhatsApp personal de la doctora se mantiene** — no migra a Cloud API
- **Bot-broker bidireccional** (Fase 4A.3): bot media entre lead y doctora con su WhatsApp habitual
- **Devices target**: iPhone 15/16 + Xiaomi 14T Pro (~393px CSS)
- **Reglas wrap tablas**: nombres natural / precios+fechas nowrap (no truncar con ellipsis)

### Bot-broker (Fase 4A.3)
- Lead propone fecha → bot pasa a doctora vía WhatsApp personal
- Doctora responde texto libre ("confirmo" o "mejor lunes 5pm o martes 11am")
- Bot transmite al lead, parsea respuesta, loop hasta acuerdo
- Bot crea appointment en ERP cuando hay match
- 4 niveles de latencia automáticos (15min / 30min / 4h / 24h)
- Sin tabla de horarios fijos (doctora flexible incluyendo fines de semana)
- Documentado en memoria `project_chatbot_broker_architecture.md`

## Bugs encontrados y arreglados

1. **JS SyntaxError** por redeclaración de `const CLIENTES_CODIGOS` (rompía toda la página)
2. **Docker compose restart no recarga env_file** (feature flag quedaba cacheado)
3. **Pestaña Agenda no aparecía** post-toggle del flag
4. **Overflow horizontal mobile** por 7ma pestaña (tabs no scrolleables)
5. **Dashboard tablas overflow 21px** en iPhone 15
6. **Decimales sin formatear** (tasa cobro 95.34567%)
7. **Header opciones absolute superpuestas al logo** en mobile
8. **Nombre lead truncado con ellipsis** (overflow-wrap missing)

## Smoke E2E real validado

```
[POST simulated form] → HTTP 200 {"vtiger_lead_id":"10x68"}
       ↓ (~8s)
[Vtiger crea lead]
       ↓ (cron B3 ~90s)
[ERP livskin_erp.leads]: LIVLEAD0001 con UTMs + fbclid + event_id heredados
       ↓ (views.py construye leads_sin_cita)
[Pestaña Agenda card automática]: "TEST_SMOKE_E2E_FORM" visible sin acción humana
```

**Attribution chain end-to-end preservada**: utm_campaign, fbclid, event_id, fecha_captura.

## Commits del día (28 en feat/agenda-module-4a1, 1 merge a main)

```
c84ff37 Merge: Fase 4A.1 — Modulo Agenda Minima ERP (en main)
d44d7b0 chore: cleanup smoke data + backlog 4A.3 bot-broker
9918e97 fix: nombre lead wrap completo
842d255 fix: card 'Esperando agendar' mobile-first
42b8832 feat: sección 'Esperando agendar' (leads automáticos como cards)
324c805 feat: fecha dd-mm-yyyy + zona debajo categoría
af01f25 fix: tablas ancho auto + scroll horizontal + decimales formateados
1656d19 fix: reglas wrap por columna (.num + .fecha)
140cc27 fix: viewports devices reales + reglas wrap diferenciadas
85d10a6 fix: tabla-rec ancho reducido + wrappers :has()
b1c3764 fix: dashboard tablas scrolleables horizontal
ff620e8 fix: botón submit sticky en mobile + script smoke robusto
a639f96 fix: ignorar overflow dentro contenedores scrolleables
a48f998 fix: tabs horizontalmente scrolleables en mobile
e203bc7 feat: UI mobile-first cards + Playwright headed test
9177c56 feat: v2 lead-only + cliente recurrente + auto-transiciones
870e637 fix(runbook): agenda-mantenimiento up -d --force-recreate
029c3ee fix CRITICO: redeclaracion CLIENTES_CODIGOS
4a8c62b fix(agenda-ui): dropdowns en vez de pegar códigos
0d53398 docs(agenda): runbook + ADR-0035 IMPLEMENTADA
7b64635 feat(erp): UI pestaña AGENDA en formulario.html
8805c1a fix(erp): sanitize Pydantic ValidationError
0c1968e feat(erp): backend modulo Agenda Fase 4A.1
... (+ commits prep)
```

## Estado al cierre

| Sistema | Estado |
|---|---|
| ERP `erp.livskin.site` | ✅ Funcionando, feature flag Agenda ON |
| Migration 0007 | ✅ Aplicada en VPS3 |
| 7/7 pestañas mobile audit | ✅ CLEAN sin overflow |
| Tests | ✅ 53/53 passing |
| DB ERP | ✅ 0 rows test_smoke |
| Vtiger | ✅ smoke leads marked deleted=1 |
| Branch feat/agenda-module-4a1 | ✅ Mergeado a main (c84ff37) |

## Próxima sesión propuesta

**Fase 4A.2 — WhatsApp Cloud API test number** (~2-3h)
- Pre-check: cuenta Meta for Developers
- Crear app + WhatsApp product + test number
- Webhook a n8n
- Smoke: enviar/recibir mensaje
- Documentar en `integrations/whatsapp/setup.md`

Después: **Fase 4A.3 — Bot-broker rule-based** (~8-10h en 2 sesiones).
