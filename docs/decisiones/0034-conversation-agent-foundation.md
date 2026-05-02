# ADR-0034 — Conversation Agent Foundation (Fase 4 arranque) — 💤 DIFERIDA POR AUDIT 2026-05-03

> **⚠️ ESTADO ACTUALIZADO 2026-05-03:** Esta ADR fue aprobada el 2026-05-02 pero al día siguiente, en sesión estratégica, Dario y Claude Code ejecutaron audit honesto que reveló sobreescalamiento del agent design. El Conversation Agent IA fue **diferido**. V1 será **chatbot rule-based + handoff humano + templates Meta-approved** (deterministic backbone first — principio operativo #11 nuevo en CLAUDE.md). Esta ADR queda en histórico documentando la dirección original; será **supersedida por ADR futura "Conversation Agent v0 rule-based"** cuando se construya en Fase 4A post-Bridge Episode (primera campaña paga). Lo que aporta este documento sigue siendo útil como referencia: schema DB de conversaciones, guardrails post-LLM (válidos cuando llegue agent IA), eval suite design, setup Meta App. NO ejecutar la implementación descrita acá hasta tener data real de campaña + brand voice consolidado + decisión explícita de avanzar con agente IA. **Doctrina rectora**: memoria `feedback_deterministic_backbone_first.md`. **Audit completo**: memoria `project_agent_scope_audit_2026_05_03.md` + `docs/audits/agent-scope-audit-2026-05-03.md`.

**Estado:** 💤 **Diferida** (originalmente ✅ Aprobada 2026-05-02 → diferida 2026-05-03 tras audit)
**Fecha:** 2026-05-02 · **Diferida:** 2026-05-03
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Originalmente Fase 4 IA — ahora diferida hasta Fase 4B post-validación
**Workstream:** Agentes · WhatsApp · Datos

---

## 1. Contexto

Cerrado el Bloque 1 (Match automático lead↔cliente, ADR-0033) la atribución end-to-end queda lista pero **falta el agente que recibe los mensajes en WhatsApp y enriquece el lead con phone real + extrae intent + escala a doctora**. Sin Conversation Agent, los click-to-WhatsApp leads (Op B) no se enriquecen y la doctora tiene que atender manualmente cada conversación entrante.

**Decisión estratégica de Dario 2026-05-02:** arrancar Fase 4 **sin esperar al WhatsApp Business API approval oficial**. Razón: la arquitectura del Cloud API es idéntica entre número de test y producción — solo cambian env vars (phone_number_id + access_token). Construir contra test number ahora permite cerrar la foundation y pasar a producción con switch de variables el día del cutover.

**Constraint operacional:** la doctora opera Vtiger + ERP via UI manualmente; el chatbot **no la reemplaza**, la **complementa**: responde preguntas de bajo riesgo (info tratamientos, horarios, ubicación) y agenda cita preliminar en `appointments` (módulo aún por construir). Operaciones de riesgo (cobrar, modificar precio, confirmar agenda) escalan handoff.

**WhatsApp test number:** `+393514918531` (provisorio, italiano por residencia de Dario en Milán).

**Referencias:**
- Memoria `project_whatsapp_architecture.md` — Opción A: número dedicado Cloud API
- Memoria `project_acquisition_flow.md` — Conversation Agent roles (5 funciones) + scoring v1
- Memoria `project_attribution_chain_event_id.md` — event_id es primary correlation key end-to-end
- Memoria `feedback_agent_governance.md` — 5 principios duros: procesos antes de libertad, anti-hallucination, humano al mando, hard limits, eval suite continua
- Memoria `project_agent_org_design.md` — Conversation Agent monolítico inicial (subagentes solo si justifica)
- ADR-0033 — match automático lead↔cliente al crear cliente en ERP
- Bloque 0.10 — `agent_resource_service` + `agent_budgets` (infra hard-limit ya existente)

---

## 2. Opciones consideradas

### Opción A — Conversation Agent monolítico en ERP, n8n sólo bridge

Receiver webhook en n8n (signature verification + normalización). Forward al ERP `/api/whatsapp/incoming`. ERP llama a `services/conversation_agent.py` (Claude API + tools). Respuesta vuelve a n8n que llama a Meta Graph API para enviar el mensaje.

### Opción B — Conversation Agent dentro de n8n (LangChain agent node)

n8n tiene un nodo "Agent" que orquestra Claude API + tools sin pasar por ERP. Más simple en superficie, pero pierde el control de guardrails + audit log + budget tracking (que viven en ERP).

### Opción C — Servicio Python dedicado separado del ERP

Microservicio nuevo `conversation-agent` containerizado aparte. Más overhead de infra (otro contenedor, otra DB connection, otro deploy), beneficio cero en este momento.

---

## 3. Análisis de tradeoffs

| Dimensión | A (ERP monolítico) ✅ | B (n8n agent node) | C (microservicio) |
|---|---|---|---|
| Reuso `agent_resource_service` (hard limits) | Directo | Requiere bridge | Requiere bridge |
| Audit log canónico | Directo | Externo | Externo |
| Eval suite (pytest + golden set) | Directo | Difícil | Posible |
| Reversibilidad | Alta (feature flag) | Media | Baja |
| Complejidad implementación | Media | Baja | Alta |
| Complejidad mantenimiento | Baja | Alta (lógica en JSON nodes) | Alta (deploy adicional) |
| Costo infra | $0 (ya hay ERP) | $0 | +1 contenedor |
| Test number → prod swap | env vars only | env vars only | env vars only |
| Alineación gobernanza | Alta | Baja (lógica esparcida) | Media |

---

## 4. Recomendación

**Opción A — Conversation Agent monolítico en ERP, n8n como bridge transparente.** Razones:

1. **Reuso directo de infra Bloque 0.10**: `agent_resource_service.create_call()` aplica hard-limit por daily/monthly budget (memoria `feedback_agent_governance` punto 4). En Opción B/C tendríamos que duplicar la lógica.
2. **Audit log atómico**: cada turn del agent emite `agent.api_call_completed` + eventos `conversation.*` en la misma DB transaction.
3. **Tests pytest existentes**: el patrón TDD (conftest.py + db_session + monkeypatch) corre sin agregar infra. Eval suite vive como `tests/agents/conversation/`.
4. **Tools determinísticos al alcance**: las tools que el agent invoca son funciones Python que ya existen (`cliente_service`, `lead_service` futuro, etc.) — sin cruce de red.
5. **Test number → producción es UN SOLO env var swap** en cualquiera de las 3 opciones — no diferencia.

Tradeoff aceptado: ERP container crece (más memoria + más lógica). Mitigación: si memoria sube >2GB, extraer a microservicio (decisión reabrible).

---

## 5. Decisión

**Elección:** Opción A — Conversation Agent monolítico en ERP, n8n bridge.

**Fecha de aprobación:** 2026-05-02 por Dario.

**Razonamiento:**
> "podemos hacerlo usando un numero de test, hasta tener el numero oficial, y ya pasamos a produccion con todo lo que tenemos solo cambiando el numero de telefono en facebook" — la arquitectura debe permitir swap test→prod con cambio de env vars únicamente.

---

## 6. Arquitectura

### 6.1 Flujo end-to-end

```
[Lead en WhatsApp Cloud API] ─────────► +393514918531
       │
       ▼ POST x-hub-signature-256 (HMAC SHA256 con app_secret)
[n8n F1 webhook receiver]  https://flow.livskin.site/webhook/whatsapp/incoming
       │  - GET handshake (hub.verify_token) → 200 + hub.challenge
       │  - POST mensaje:
       │      verifica firma Meta
       │      normaliza payload {from, text, message_id, timestamp, profile_name}
       │      audit n8n log
       │
       ▼ POST X-Internal-Token + JSON normalizado
[ERP Flask] /api/whatsapp/incoming
       │  - valida token (settings.audit_internal_token)
       │  - audit_log: webhook.whatsapp_received
       │  - upsert lead/conversation_turn en DB
       │  - llama conversation_agent_service.handle_incoming(turn)
       │       │
       │       ▼
       │       [agent_resource_service.create_call(agent="conversation")]
       │            ├─ check daily/monthly budget hard-limit
       │            ├─ Claude API (sonnet-4-5) con tools
       │            │   tools_v1:
       │            │     • vtiger_search_lead_by_event_id(event_id)
       │            │     • vtiger_search_lead_by_phone(phone_e164)
       │            │     • catalogo_lookup(tipo, query)  [deterministic]
       │            │     • erp_cliente_search_by_phone(phone_e164)
       │            ├─ tool execution loop (max 5 rounds)
       │            ├─ response → guardrails check
       │            │   ✗ menciona precio inexistente → bloquear
       │            │   ✗ promete tratamiento no en catálogo → bloquear
       │            │   ✗ confirma cita sin pasar por handoff → bloquear
       │            └─ audit_log: agent.api_call_completed (cost_usd, tokens, outcome)
       │       ▼
       │       structured response:
       │         {action:"send_message", text:"...", to:"+51..."}
       │       o {action:"handoff", reason:"score>=70", to_doctora:true}
       │       o {action:"silent", reason:"agent_locked_for_human"}
       │
       ▼ JSON response
[n8n F2] envía respuesta via Meta Graph API o ejecuta handoff
```

### 6.2 Setting nuevos (config.py)

```python
# Fase 4 — WhatsApp Cloud API
wa_phone_number_id: str = ""           # Meta-assigned ID (no el número real)
wa_access_token: str = ""              # System User Token (no expira) o App Token (60 days)
wa_verify_token: str = "livskin-verify-2026"   # webhook handshake — definimos nosotros
wa_app_secret: str = ""                # firma X-Hub-Signature-256 (Meta App Secret)
wa_test_number_e164: str = "+393514918531"     # provisorio test
wa_n8n_send_webhook_url: str = "https://flow.livskin.site/webhook/whatsapp/send"

# Fase 4 — Conversation Agent
conversation_agent_enabled: bool = True       # feature flag global
conversation_agent_model: str = "claude-sonnet-4-6"
conversation_agent_max_tokens: int = 1500
conversation_agent_tool_loop_max: int = 5     # max iteraciones tool-call
conversation_agent_locked_actions: list[str] = ["confirm_appointment", "quote_price"]
```

Secrets reales viven en `keys/.env.integrations` (gitignored) y se montan al container vía docker-compose.

### 6.3 Schema DB (nuevas tablas — Alembic 0007)

**conversations** (1 fila por phone-side conversation entera)

| col | tipo | nota |
|---|---|---|
| id | bigint PK | |
| cod_conversation | text unique | LIVCONV0001+ |
| phone_e164 | text indexed | anchor |
| profile_name_wa | text | profile name from Meta |
| started_at | timestamptz | primer mensaje |
| last_turn_at | timestamptz | última actividad |
| state | text | `agent_active` / `handoff_pending` / `human_active` / `closed` |
| score | int | 0-100, recalculado cada turn |
| intent_level | text | `investigando` / `evaluando` / `listo_comprar` |
| cod_lead_vinculado | text FK leads.cod_lead | si encontramos via event_id/phone |
| event_id_at_capture | text | pre-poblado en WA href desde landing |
| handed_off_at | timestamptz nullable | |
| handed_off_reason | text nullable | score≥70 / explicit_request / agent_locked |
| audit_metadata | jsonb | freeform |

**conversation_turns** (1 fila por mensaje individual, agent + lead)

| col | tipo | nota |
|---|---|---|
| id | bigint PK | |
| cod_conversation | text FK conversations | |
| sender | text | `lead` / `agent` / `doctora` |
| message_text | text | |
| message_id_wa | text unique | id del mensaje en Meta (idempotencia) |
| timestamp | timestamptz | |
| tool_calls_json | jsonb nullable | si fue agent turn con tools, qué tools llamó |
| cost_usd | numeric(10,6) nullable | si fue agent turn, costo del LLM call |
| tokens_input | int nullable | |
| tokens_output | int nullable | |
| guardrails_blocked | bool default false | si guardrail bloqueó → texto no enviado |

**agent_tool_calls** (1 fila por tool invocation, para audit + debugging)

| col | tipo | nota |
|---|---|---|
| id | bigint PK | |
| cod_conversation | text FK conversations | |
| turn_id | bigint FK conversation_turns | |
| tool_name | text | `vtiger_search_lead_by_event_id`, etc. |
| input_json | jsonb | |
| output_json | jsonb nullable | null si erroró |
| latency_ms | int | |
| outcome | text | `success` / `error` / `timeout` |
| error_detail | text nullable | |
| occurred_at | timestamptz | |

### 6.4 Tools v1 — first 4

Cada tool es una función Python con JSON schema declarado. Se invocan por nombre desde el tool-calling loop. Ninguna tool toca operaciones de riesgo (cobros, agenda firme — solo agenda **propuesta**, doctora confirma).

**T1: `vtiger_search_lead_by_event_id`**
```json
{
  "name": "vtiger_search_lead_by_event_id",
  "description": "Busca lead en Vtiger/ERP por event_id_at_capture (UUID generado por landing). Útil para enriquecer un WA-click lead con phone real.",
  "input_schema": {
    "type": "object",
    "properties": {"event_id": {"type": "string"}},
    "required": ["event_id"]
  }
}
```
Handler: `select * from leads where event_id_at_capture = :id` — retorna `{cod_lead, vtiger_id, nombre, fuente, tratamiento_interes, fecha_captura}` o `{found: false}`.

**T2: `vtiger_search_lead_by_phone`**
Similar pero por `phone_e164`. Útil para leads que nos contactan organicamente sin pasar por ad.

**T3: `catalogo_lookup`**
```json
{
  "name": "catalogo_lookup",
  "description": "Busca info de tratamientos en el catálogo del ERP. Para responder preguntas sobre qué tratamientos hacemos, categorías, áreas. NO devuelve precios — los precios se cotizan caso por caso por la doctora.",
  "input_schema": {
    "type": "object",
    "properties": {"tipo": {"type": "string", "enum": ["tratamiento", "producto", "area"]}, "query": {"type": "string"}},
    "required": ["tipo"]
  }
}
```

**T4: `erp_cliente_search_by_phone`**
Verifica si el lead ya es cliente existente. Si sí → respuesta personalizada ("Hola Sofia, qué bueno saber de ti"). Si no → flow nuevo lead.

**Tools NO incluidas en v1** (futuras decisiones, ADRs separadas):
- `appointment_propose` (espera ADR Bloque puente Agenda)
- `quote_price` (LOCKED — explícito en `conversation_agent_locked_actions`)
- `notify_doctora` (espera setup notification channel)

### 6.5 Guardrails (post-LLM, pre-envío)

Validación determinística sobre el text del response **antes de retornar `{action: send_message}`**:

| Check | Regla | Acción si trigger |
|---|---|---|
| `precio` o `costo` o `S/.` numéricos | Regex `S\/\.?\s*\d+` o palabras `precio|costo|tarifa` | bloquear, audit `guardrail.price_mention`, replace con "Para cotizarte el precio exacto necesito que la doctora te atienda" + handoff |
| Tratamiento fuera de catálogo | Lookup en `catalogos.area` + tratamientos conocidos | bloquear, audit, fallback "déjame consultar con la doctora" |
| Fecha de cita en pasado o `hoy` sin appointment tool | Parser de fecha en text | bloquear, escalation |
| Confirmación de cita sin pasar por handoff | text contiene "tu cita está confirmada" | bloquear, audit, replace |
| URL externa | regex http(s):// | bloquear (anti-phishing impersonation) |

Cada guardrail dispara `conversation.guardrail_triggered` audit event.

### 6.6 Eval suite

Carpeta `tests/agents/conversation/golden/` con 30 conversaciones simuladas (input → expected behavior class). Categorías:
- `intent_botox_basic` (5)
- `intent_unknown_treatment` (3)
- `price_question_handled` (5) — esperan handoff
- `appointment_request_no_tool` (3) — esperan polite-decline + handoff
- `attribution_enrichment_event_id` (5) — esperan tool call vtiger_search_lead_by_event_id
- `attribution_enrichment_phone` (3) — esperan tool call vtiger_search_lead_by_phone
- `returning_cliente` (3) — esperan tool call erp_cliente_search_by_phone con personalized greeting
- `objection_handling_basic` (3)

Eval check: structural (¿llamó la tool esperada? ¿guardrail triggered?) + LLM-judge (Claude Haiku) sobre tone+factual accuracy.

### 6.7 Audit events nuevos (51 → 57)

Categoría `conversation.*` (NUEVA):
- `conversation.started` — primer mensaje de un phone nuevo
- `conversation.turn_received` — mensaje del lead recibido
- `conversation.turn_sent` — agente envió mensaje
- `conversation.tool_invoked` — agent llamó una tool
- `conversation.guardrail_triggered` — output bloqueado por guardrail
- `conversation.handoff_to_doctora` — score≥70 o explicit request

(`webhook.whatsapp_received` ya existe en KNOWN_ACTIONS desde Bloque 0.8.)

### 6.8 Feature flag + reversibilidad

`settings.conversation_agent_enabled = True`. Si `False`:
- `/api/whatsapp/incoming` devuelve 200 + queue silencioso (sin invocar agent)
- n8n F2 manda mensaje fallback "En unos minutos te atiende la doctora" + audit handoff explícito
- Sistema queda en modo "passthrough manual" — la doctora atiende todo manualmente

### 6.9 Setup en Meta (paso a paso para Dario)

Documento separado: `docs/runbooks/whatsapp-cloud-api-test-setup.md`. Resumen:

1. **developers.facebook.com** → app Livskin → Add Product → WhatsApp
2. **WhatsApp → Quickstart** → "Get Phone Number" → registrar `+393514918531` (verificación SMS)
3. **WhatsApp → API Setup** → copiar:
   - `Phone number ID` → `WA_PHONE_NUMBER_ID`
   - `Access Token` (temporary 24h primero, después generamos System User Token)
4. **App Settings → Basic** → copiar `App Secret` → `WA_APP_SECRET`
5. **WhatsApp → Configuration** → Webhook:
   - Callback URL: `https://flow.livskin.site/webhook/whatsapp/incoming`
   - Verify Token: `livskin-verify-2026` (o cualquiera, ponerlo en `WA_VERIFY_TOKEN`)
   - Subscribe a campo `messages`
6. **System User en Meta Business Manager** → asignar app → generar token permanente con permiso `whatsapp_business_messaging` → reemplaza el temporary

Una vez los secrets en `keys/.env.integrations`, redeploy ERP + n8n y el flow está vivo.

---

## 7. Consecuencias

### Desbloqueado por esta decisión
- Smoke E2E "Hola → bot responde con info catálogo" en test number
- Tool ecosystem para todos los agentes futuros (mismo patrón JSON schema + Python handler)
- Foundation para Bloque puente Agenda (cuando esté el módulo `appointments`, agrega tool `appointment_propose`)
- Pasaje a producción es swap de 2 env vars (`WA_PHONE_NUMBER_ID` + `WA_ACCESS_TOKEN`)

### Bloqueado / descartado
- Opción B (n8n agent node) — descartada por gobernanza (lógica + budgets dispersos)
- Opción C (microservicio dedicado) — postpuesta a futuro si memoria ERP supera 2GB
- Tools de operaciones de riesgo (cobrar, modificar precio) — explícitamente LOCKED hasta sesión estratégica organizacional

### Cuándo reabrir
- Memoria ERP container >2GB → considerar microservicio
- Volumen >1000 conversaciones/mes → optimizar (rate limit + cache catálogo)
- Eval suite degrada >5% en regression → pause deploy, debugging
- Cambios en Meta Cloud API pricing/limits

---

## 8. Changelog

- 2026-05-02 — v1.0 — Creada y aprobada por Dario. Test number `+393514918531` provisorio.

---

**Notas:** ADR alive — los detalles de tools v1 + guardrails + eval suite se refinarán iterativamente sin re-superseder esta decisión. Las Tablas 6.3 y la lista de tools 6.4 son la base mínima; expansiones futuras (T5+, tablas 4-5) se documentan en este ADR como sub-secciones nuevas o nueva ADR si el cambio es estructural.
