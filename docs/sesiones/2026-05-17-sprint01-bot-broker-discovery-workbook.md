---
fecha: 2026-05-16 → 2026-05-17 (sesión maratónica multi-fase, ~14h continuas)
duracion: ~14h
modo: PROYECTO (#12)
participantes: Dario + Claude Code
fase: Sprint 0 + Sprint 1 + cleanup masivo + Sprint 2 parte 1-2 + Interludio Discovery
estado: 2 commits ya mergeados (`9f533c5`, `d159e2d`) + 1 commit nuevo pendiente push (sprint 2 + workbook)
---

# Sesión 2026-05-16/17 — Sprint 0 + Sprint 1 WhatsApp + Sprint 2 parte 1-2 + Interludio Discovery

## Resumen ejecutivo

Sesión más larga del proyecto a la fecha (~14h continuas). Cerramos **4 sprints técnicos + cleanup masivo + producto cualitativo** (workbook discovery para encuentro con la doctora). Hito gigante en el camino al backbone determinístico cerrado.

**Hilo conductor**: arrancamos asumiendo "construyamos el bot-broker técnicamente" → en el medio de Sprint 2 Dario corrige: "esto va a ser scaffold sin contenido, parece mediocre" → pivote estratégico a producir el documento de discovery que permitirá llenar el bot con CONTENIDO real (brand voice, customer journey, painpoints, precios) extraídos de la doctora en encuentro de 3-4h. **Doctrina #14 confirmada**: el interludio estratégico (Fase 4A.6) es PARTE del backbone determinístico, no algo posterior.

## Cronología de la sesión (4 bloques)

### Bloque 1 (~2h): Sprint 0 + Sprint 1 cimientos Meta + WhatsApp

**Sprint 0 — System User token Meta** (~1.5h):
- Reciclado System User "Claude Audit" (creado 2026-05-09 sin uso) → renombrado a "Claude Automation"
- Ampliado token Cloudflare con `Email Routing Addresses:Edit` + `Email Routing Rules:Edit` (era prerequisito anterior cuando arrancamos día)
- Agregados 4 use cases a app "Livskin Integraciones" (App ID `807721865486018`):
  1. WhatsApp Business Platform (ya existía)
  2. Marketing API — Crear y administrar anuncios (`ads_management` Listo para la prueba ✅)
  3. Marketing API — Medir rendimiento (`ads_read` Listo)
  4. Manage everything on your Page (`pages_*` Listo)
- Permissions agregadas opcionales: `pages_manage_ads`, `business_asset_user_profile_access`, `pages_manage_metadata`, `read_insights`, `pages_manage_engagement`, `pages_manage_posts`, `pages_read_user_content`
- 15 activos asignados al System User (1 Page + 1 Ad Account + 1 App + 1 Dominio + 8 WABAs + 2 Conjuntos de datos)
- Token generado con **15 scopes granted**, formato `EAAL...`
- Validado con 4 Graph API tests: /me, /me/permissions (15 OK), BM Livskin Perú accesible, Ad Account `act_2885433191763149` accesible currency PEN
- App Secret `META_APP_SECRET` agregado al `.env.integrations`

**Sprint 1 — WhatsApp Cloud API con +51 947 741 117** (~2h):
- API call directo `POST /1320785723325168/phone_numbers` con cc=51 + phone_number=947741117 + verified_name=Livskin → response `phone_number_id=1071476852722953`
- SMS verification disparado a SIM nuevo doctora — código `857326` ingresado vía API
- Register en CLOUD_API platform con 2FA PIN aleatorio `395609`
- Estado final: **+51 947 741 117 GREEN quality, STANDARD throughput, verified_name "Livskin" approved sin review**
- Webhook workflow `[D0] WA Inbound Receiver` creado en n8n via CLI import + activado vía SQL UPDATE workflow_entity active=1 + activeVersionId=versionId + restart container (patrón heredado del workflow A2 fix)
- Webhook subscription en Meta App configurada con App Access Token (= `${APP_ID}|${APP_SECRET}`): callback_url + verify_token + fields `messages,message_template_status_update`
- WABA productiva suscrita al app via `POST /1320785723325168/subscribed_apps`
- Smoke test E2E completo: outbound text message a +51982732978 OK, inbound test message recibido en n8n executions (id 24096-24113), Dario validó visualmente que llegó a su WA personal con remitente "Livskin"
- Business profile completado por Dario (foto, dirección Wanchaq, email info@livskin.site, sitio web, vertical=BEAUTY) + Claude corrigió typo "Cestrno Estetico" → "Centro Estético" via API
- WABA review status: "Aprobada" → ahora "Revisión en curso" (normal, trigger automático por agregar phone nuevo, 24-72h)

### Bloque 2 (~3h): Cleanup masivo Meta + smoke data residual

**Cleanup WABAs duplicadas Meta**:
- Audit identificó 8 WABAs en BM Livskin Perú (1 prod + 1 test + 6 duplicadas/legacy del 2026-02-23)
- Las 6 candidatas: 0 phone numbers, 0 apps suscritas, 0 templates custom — safe to delete
- Meta NO permite delete WABAs via API (confirmado con tests `/v21.0/{waba}` DELETE rejected y `POST /{waba} name=...` "Application does not have capability") — solo UI manual
- Dario eliminó las 6 vía WhatsApp Manager UI nueva en `business.facebook.com/wa/manage/accounts/`
- Estado final: 2 WABAs (productiva `1320785723325168` Livskin + test `1627699161819695` Test WhatsApp Business Account)

**Cleanup smoke data residual cross-system** (4 sistemas):
- ERP livskin_erp: 1 lead smoke residual `LIVLEAD0001 SMOKE_A2 Test` (eliminado via SQL DELETE en TX + audit_log event id=242)
- Analytics warehouse `analytics`: 4 leads smoke (`SMOKE_A2_LEAD`, `LIVLEAD_TEST_001/002`, `LIVLEAD0001`) + 10 opportunities smoke (`LIVCLIENT_TEST_VTA TEST_SMOKE` x10 + `LIVCLIENT0136 TEST_DEBUG`). Diagnóstico clave: workflows E1/E2 son UPSERT-only, no DELETE cascade — orphan data en analytics cuando se borra en ERP
- Vtiger MariaDB livskin_db: 68 leads soft-deleted (deleted=1) purgados físicamente vía SQL en cascada (vtiger_leadscf, vtiger_leadaddress, vtiger_leadsubdetails, vtiger_modtracker_basic, vtiger_leaddetails, vtiger_crmentity) — total 543 filas eliminadas
- Brain pgvector: 91 chunks mencionan "smoke" pero son **falsos positivos** (docs del proyecto que hablan de smoke tests, no data residual)
- Validación final: 0 smoke residual en ERP/Analytics/Vtiger, consistencia ERP-ventas=88 ↔ Analytics-opportunities=88 ✅

### Bloque 3 (~3h): Sprint 2 parte 1-2 (Migration + Parser)

**Sprint 2.1 — Migration 0008 `wa_conversation_state` + `wa_messages`** (~1h):
- Diseño: tabla state con UNIQUE PARTIAL (`phone_lead WHERE state != 'closed'` — permite múltiples conversaciones cerradas + 1 activa por phone) + tabla messages con UNIQUE constraint en `meta_message_id` (defensa idempotency contra reentregas Meta)
- 26 columnas en state (lead_id FK, vtiger_lead_id, agent_paused, escalation_*, proposed_dates JSONB, context_json JSONB, lifecycle timestamps)
- 19 columnas en messages (conversation_id FK, direction, message_type, body, template_*, meta_status, intent, parsed_dates, meta_payload_raw)
- 9 indices total + 5 check constraints
- Hiccup: copia inicial al VPS3 dejó archivo duplicado (con y sin prefijo fecha) — alembic detectó "Revision present more than once" → corregido eliminando duplicado + cache `__pycache__`
- `alembic upgrade head` ejecutado en VPS3 → migration aplicada exitosamente

**Sprint 2.2 — Parser intent + fechas regex** (~2h):
- Creado `infra/n8n/lib/wa_parser.js` (~250 líneas) — librería pura JS sin dependencias
- Detecta 10 intents: `confirm`, `reject`, `ask_price`, `ask_human`, `ask_info`, `greeting`, `cancel`, `reschedule`, `propose_date`, `unknown`
- Parser de fechas tolerante: días semana (con/sin acentos), días relativos (hoy/mañana/pasado mañana), fechas numéricas (11/05, 11/05/2026), fechas con mes textual (5 de junio), horas (5pm, 14:30, "de la mañana/tarde/noche"), múltiples opciones por mensaje (lunes o martes)
- Timezone Lima (-05:00) con conversión correcta UTC ↔ local
- **24/24 tests pass** en suite local: greetings, precios, ask_human, confirm/reject, cancel/reschedule, propose_date con todas las variantes de fechas
- 3 bugs encontrados y arreglados durante testing: regex ask_human no aceptaba "con la doctora", confirm no aceptaba combinaciones con coma ("sí, perfecto"), parseDates "hoy" sumaba 1 día por bug timezone shift
- Inline-eado en workflow n8n `[D1] WA Inbound + Parser` (reemplazo de D0) y validado E2E con mensajes WhatsApp reales de Dario: "Hola" → greeting 0.80, "Precio botox" → ask_price 0.90, "hola, podria agendar el martes 3pm?" → propose_date 0.80 con fecha martes 19-may 15:00 detectada correctamente

### Bloque 4 (~6h): Pivote a Interludio Discovery + Workbook iterativo

**Pivote estratégico — Dario corrige el rumbo**:
Tras Sprint 2.2 completo, Claude proponía seguir a Sprint 2.3 (Workflow D1 completo con tools dispatcher + Vtiger sync + Meta send). Dario detectó que era **scaffolding sin contenido**:
- "Hay cosas que pides tener que tú ya las tienes" (datos del sistema)
- "Cómo se presentará la estructura, es bueno empezar siempre con esperar respuestas, o como debe actuar el robot después del primer contacto"
- "Cuando la gente busca precios y le damos respuesta genérica pueden perder el interés"
- "Esto tiene que ser top de gama"

Auto-crítica de Claude: estaba construyendo el chasis del bot sin el manual de conducta. Reconocimiento del gap conceptual: faltaba el **Interludio Estratégico (Fase 4A.6)** del master plan — brand voice + arquetipos + posicionamiento + customer journey + copy real del bot.

**Outputs producidos en este bloque**:
1. `docs/brand/interludio-discovery.md` (~600 líneas) — Bitácora narrativa explicativa con marcos conceptuales (postura A vs B del bot, 4 estrategias de precios, 6 escenarios drop-off, sistema global de captación)
2. `docs/brand/interludio-discovery-workbook.html` (89KB) — Workbook **interactivo digital** con auto-save, sidebar navegación, progress bar, export Markdown/JSON

**Iteraciones del workbook (3 versiones)**:
- v1 (60KB): HTML print-friendly. Dario corrigió: "mejor interactivo en pantalla, voy a llenarlo durante el encuentro + grabar conversación"
- v2 (79KB): Convertido a interactivo con inputs/textareas/checkboxes editables + auto-save localStorage cada 500ms + export Markdown/JSON + 13 bloques con sidebar
- v3 (89KB, final): Tres mejoras solicitadas por Dario:
  1. **Datos del sistema pre-cargados** (sección "📊 Datos del sistema" al inicio): 134 clientes, 88 ventas Sep-Nov 2025, S/35,995 revenue, ticket promedio S/409, top categorías reales (Botox 50.1%, HA 15.9%, Hilos 11.1%, Esperma de Salmón 7.1%, PRP 2.5%), distribución pagos (Efectivo 44%, Yape 38%, Plin 12%, Giro 5%), catálogo 21 tratamientos del ERP con flag ¿vendido?, campañas Bridge + Día Madre stats, fototipo análisis 2/134 con fecha nacimiento
  2. **Top 6 tratamientos pre-llenados** como fichas verdes (Botox, HA, Hilos, Esperma Salmón, PRP, Limpieza Facial) con ventas + revenue + ticket avg + marcas sugeridas (Allergan/Galderma/Juvederm/PDO) + áreas comunes
  3. **💡 Hints visibles** debajo de cada pregunta importante con ejemplos concretos de respuesta esperada (cajas amarillas con icono lightbulb)

**Refinamientos finales**:
- "Cusco-específicos" reescrito a **"Contexto local Cusco — painpoints que un cliente de Cusco siente y un cliente de Lima/costa NO"** con tip explicativo + 6 puntos (clima altura, aceptación cultural, turista nacional, cliente extranjero, soroche/altitud, fototipo andino) + 2 slots libres
- **Botón "➕ Agregar otro tratamiento"** dinámico — al click genera ficha 11+, persiste contador en localStorage, botón "🗑 Eliminar" por ficha extra
- **Upload fotos antes/después** en cada caso de éxito: input file → resize Canvas 600px máx → JPEG 70% compresión → preview thumbnail con borde verde + tamaño KB + botón eliminar → base64 guardado en localStorage → incluido en export JSON
- Restauración previews + extras al cargar página (no se pierde nada al cerrar browser)

## Hitos del día (resumen)

| Hito | Estado |
|---|---|
| Sprint 0 — System User token Meta (15 scopes) | ✅ |
| Sprint 1 — WhatsApp Cloud API +51 947 741 117 + webhook n8n + Meta subscription + business profile | ✅ |
| Cleanup 6 WABAs duplicadas | ✅ (6 → 2) |
| Cleanup smoke data residual (ERP + analytics + Vtiger, 543 filas) | ✅ |
| Sprint 2.1 — Migration 0008 (wa_conversation_state + wa_messages, 45 cols total) | ✅ |
| Sprint 2.2 — Parser intent + fechas JS (24/24 tests, validado E2E) | ✅ |
| Workbook discovery interactivo doctora (89KB, 13 bloques, auto-save, upload fotos, dinámico) | ✅ |
| Bitácora discovery doctrina (600 líneas) | ✅ |
| Sprint 2.3 — Workflow D1 completo (tools + Vtiger sync + Meta send) | ⏳ post-encuentro |
| Sprint 3 — D2 + D3 + escalation | ⏳ |
| Sprint 4 — Smoke E2E + recordatorios | ⏳ |

## Decisiones tomadas

1. **Bot guía activo SUTIL** (postura B), no pasivo reactivo. El bot avanza al objetivo (agendar consulta) en cada interacción.
2. **Estrategia de precios B (rango con disclaimer + consulta gratuita)** — top de gama. No "te lo dice la doctora privado" (escapa) ni precio fijo público (commodity).
3. **NO bajar precios como respuesta a "es caro"** — devalúa. Agregar VALOR adicional (kit cuidado, seguimiento gratis).
4. **NUNCA Claude Haiku como Capa 2 del parser** (doctrina #11). Si parser confidence < 0.5 → escalar a humano (doctora), no IA.
5. **Interludio Estratégico (Fase 4A.6) PRIMERO, después Sprint 2.3** (workflow D1 completo). Codear sin contenido era mediocre.
6. **App "Livskin Integraciones" en Development Mode** se queda así — los scopes `ads_management`/`ads_read`/`whatsapp_*` funcionan para nuestros propios assets (BM Livskin Perú) sin App Review formal.
7. **Tabla `wa_conversation_state` con UNIQUE PARTIAL** (no UNIQUE simple) en phone_lead para permitir history de conversaciones cerradas.
8. **Templates Meta a submitir post-encuentro** (4-6 templates definidos por copy real): `new_lead_appointment_request`, `lead_confirmed_appointment`, `lead_rejected_proposal`, `lead_waiting_4h`, reminders T-24h/T-3h.

## Hallazgos no obvios

1. **Meta NO permite delete/rename WABAs via API** — política de seguridad. Solo UI manual. (rejected con `Application does not have capability` incluso con app token + System User admin).
2. **Workflows ETL E1/E2 son UPSERT-only, no DELETE cascade** — orphan data en analytics warehouse cuando se borra en ERP. Smoke data residual era de aquí. Patrón a considerar al rediseñar sync.
3. **Vtiger 8.2 community no purga soft-deletes automático** — leads quedan en DB con `deleted=1` indefinidamente. Purga física requiere SQL en cascada en 6+ tablas (`leadscf`, `leadaddress`, `leadsubdetails`, `modtracker_basic`, `leaddetails`, `crmentity`).
4. **Webhook config en Meta App requiere APP ACCESS TOKEN** (= `{app_id}|{app_secret}`) — System User token NO alcanza para POST `/{app-id}/subscriptions`. PERO WABA subscription al app funciona con System User.
5. **Meta `name_status: AVAILABLE_WITHOUT_REVIEW`** = display name aprobado sin esperar review humano (fast path). Sucedió con "Livskin" porque ya estaba autorizado por un setup previo.
6. **WABA review status fluctúa** — pasó de APPROVED → PENDING tras agregar phone number nuevo (trigger automático Meta, 24-72h re-review esperada).
7. **Parser "hoy 8pm" bug** — el timezone shift naive `+5h` causaba overflow de día. Fix: usar peruDate calculation con offset explícito a +5h después de setear horas.
8. **localStorage tiene límite ~5-10MB** — fotos antes/después en base64 deben comprimirse (canvas resize a 600px + JPEG 70%) para que 12 fotos (6 casos × 2) caben en ~1.2MB.

## Errores cometidos por Claude (autocrítica)

1. **Construcción técnica sin contenido de negocio**: arrancamos Sprint 2 codeando tablas + parser + workflow sin haber diseñado primero el customer journey + copy del bot + scoring rules. Dario detectó y corrigió. Lección: **mapa conceptual antes que código** para componentes con alta carga de contenido (bot, email marketing, ads copy).
2. **Mediocridad escondida en plan**: inicialmente propuse "Sprint B holístico" pero con muchas cosas resueltas con "subset simplificado" donde se necesitaba versión seria. Dario detectó: *"parece muy mediocre tu visión"*. Lección: cuando el bloque importa estratégicamente, **versión seria desde día 1** o explícitamente diferir hasta tener data para hacerla bien.
3. **Información ya disponible en el sistema pero pedida a Dario**: en primer draft del workbook le pedía "traer 134 clientes segmentados, top 5 tratamientos" cuando YO los tengo via SQL. Lección: **antes de pedirle info al usuario, verificar si está en mi acceso programático**.
4. **Codificación sin verificar UI real**: cuando pedí a Dario "ir a `business.facebook.com/wa/manage/accounts/`" pensé que era URL standard, no había verificado que carga. URL no cargaba. Lección: **dar URLs directas solo cuando las he validado en sesión actual** o decir explícitamente "URL aproximada, si no carga avisame".
5. **Iteración v1→v2→v3 del workbook** — primera versión era print-friendly (HTML estático). Lección: **preguntar formato al inicio** antes de producir 60KB de HTML en vano. ¿Imprimir o llenar en pantalla?

## Doctrinas confirmadas / refinadas

- **Doctrina #11 (deterministic backbone first)**: confirmada — sustituimos Claude Haiku Capa 2 por escalar-a-humano cuando confidence < 0.5
- **Doctrina #14 (interludio estratégico es PARTE del backbone)**: confirmada — pivote a interludio antes de Sprint 2.3 con código
- **Doctrina #8 (cero pago sin aprobación)**: confirmada — todo el día $0 nuevo, free tier Meta + n8n existente
- **Doctrina nueva implícita**: "Cuando el componente tiene alta carga de CONTENIDO (no solo lógica), diseñar mapa conceptual + capturar voice/personas/copy ANTES de codear scaffold". Esto debería articularse formal en próxima sesión como Principio Operativo #15 (a discutir con Dario).

## Próxima sesión propuesta

**Encuentro doctora (3-4h, presencial)** — Dario lleva laptop con `docs/brand/interludio-discovery-workbook.html` abierto en Chrome. Pasos:

1. Pre-encuentro (1h antes): Dario:
   - Manda cuestionario corto a doctora día previo (anexo del bitácora)
   - Pide 15 screenshots de chats reales doctora (anonimizados)
   - Pide fotos clínica + foto profesional + logo + brand colors
   - Pide reseñas Google
   - Investiga 5-10 clínicas competencia Cusco

2. Durante el encuentro:
   - Workbook abierto en pantalla (auto-save activo, exportar JSON cada 30-60min como backup)
   - Audio recorder en celular (con permiso)
   - Llenar 13 bloques con doctora
   - Subir fotos antes/después de casos de éxito si tiene

3. Post-encuentro (~6h con Claude Code):
   - Importar export Markdown del workbook
   - Codificar los 12 outputs digitales: `docs/brand/voice-v1.md`, `personas.md`, `journey-map.md`, `catalogo-tratamientos.md`, `precios-strategy.md`, `painpoints-responses.md`, `diferenciacion.md`, `operacion.md`, `casos-exito.md`, `reengagement.md`, `scoring-rules.md`, `captacion-global.md`
   - Articular eventualmente Principio Operativo #15 si la sesión lo cristaliza

4. Después: arrancar Sprint 2.3 (Workflow D1 completo) con COPY REAL en cada response del bot, no placeholders.

## Files creados/modificados en esta sesión

**Nuevos** (commit pendiente push):
- `infra/docker/alembic-erp/migrations/versions/2026_05_16_1930-0008_wa_conversation.py` — Migration tablas wa_conversation_state + wa_messages
- `infra/n8n/lib/wa_parser.js` — Parser intent + fechas regex (250 líneas, 24/24 tests)
- `infra/n8n/workflows/D-conversation/d1-wa-inbound-parser.json` — Workflow n8n D1 con parser inline
- `docs/brand/interludio-discovery.md` — Bitácora narrativa discovery (600 líneas)
- `docs/brand/interludio-discovery-workbook.html` — Workbook interactivo (89KB)
- `docs/sesiones/2026-05-17-sprint01-bot-broker-discovery-workbook.md` — Este session log

**Modificados** (gitignored):
- `keys/.env.integrations` — agregado `META_SYSTEM_USER_ID/TOKEN`, `META_APP_SECRET`, `META_WEBHOOK_VERIFY_TOKEN`, `META_WA_PROD_*` (5 keys), Brevo SMTP (de sesión previa)

**Modificados en VPS3** (deploy):
- ERP livskin_erp DB: migration 0008 aplicada, tablas wa_conversation_state + wa_messages creadas

**Modificados en VPS2** (deploy):
- n8n: workflow `d0-wa-inbound-receiver` reemplazado con `[D1] WA Inbound + Parser` (mismo workflowId, mismo webhook URL)

**Operaciones API ejecutadas (no en repo)**:
- Meta App "Livskin Integraciones": agregados 3 use cases (Marketing API Ads + Analytics + Pages)
- BM Livskin Perú: System User "Claude Audit" → renombrado "Claude Automation" + 15 activos asignados
- WABA Livskin (`1320785723325168`): phone +51 947 741 117 registrado en CLOUD_API, business profile completado
- Meta App subscription: callback_url + verify_token + fields `messages, message_template_status_update`
- Cleanup: 6 WABAs duplicadas eliminadas UI manual
- Cleanup smoke data: 543 filas eliminadas cross-system (ERP + analytics + Vtiger purge físico)
