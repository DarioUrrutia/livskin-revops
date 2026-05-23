# Plan flujos n8n — Bot Yossie WhatsApp end-to-end

**Doctrina:** TODOS los syncs cross-system pasan por n8n para tener recorrido visual (memoria `project_n8n_orchestration_layer.md`).

**URL n8n:** `flow.livskin.site` (VPS2)

**Estado actual (2026-05-23):**
- ✅ **[D1] WA Inbound + Parser** deployed (parser intent 10 categorías + fechas tolerante)
- ✅ **[A2] sync ERP→Vtiger** deployed (bidireccional cerrado)
- ⏳ **[D2] WA Send Outbound** — pendiente
- ⏳ **[D3] Conversation Manager cron** — pendiente
- ⏳ **[D4] Doctora Inbound Handler** — pendiente
- ⏳ **[D5] Reengagement sequence cron** — pendiente
- ⏳ **[D6] Reminders cron** — pendiente

---

## Mapa visual end-to-end

```
                    ┌──────────────────────────┐
LEAD WhatsApp ─────►│  [D1] WA Inbound + Parser│
+51 947 741 117     │  - signature verify       │
                    │  - parse intent/fechas    │
                    │  - upsert wa_messages     │
                    │  - upsert wa_conversation │
                    └───────────┬───────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │  [D1.5] Tool Dispatcher  │
                    │  decide acción según:    │
                    │  - intent + confidence    │
                    │  - cliente_id ERP lookup  │
                    │  - state actual conv      │
                    │  - red flag patterns     │
                    └─────┬──────────┬─────────┘
                          │          │
              SIMPLE      │          │ COMPLEJO / ESCALATE
                          ▼          ▼
            ┌───────────────────┐   ┌──────────────────────────┐
            │ [D2] WA Send      │   │ Notif doctora WA personal│
            │ Outbound          │   │ (template w/ contexto)   │
            │ - Yossie copy     │   │ + audit: handed_to_doctor│
            │ - template Meta   │   └──────────────────────────┘
            │   o texto libre    │
            │ - update wa_msgs  │
            └───────────────────┘
                                                  
                                                  
   ┌──────────────────────────┐   ┌──────────────────────────┐
   │ [D3] Conv Manager (cron) │   │ [D4] Doctora Inbound     │
   │ every 5min               │   │  Handler (webhook)       │
   │ - latency check          │   │ - doctora responde en SU │
   │ - escalation triggers    │   │   WA personal            │
   │ - reengagement queue     │   │ - Yossie relaya al lead  │
   │ - templates si >24h      │   │ - confirma appointment   │
   └──────────────────────────┘   │   en ERP                  │
                                  └──────────────────────────┘

   ┌──────────────────────────┐   ┌──────────────────────────┐
   │ [D5] Reengagement (cron) │   │ [D6] Reminders (cron)    │
   │ every 1h                 │   │ every 30min              │
   │ - D1 48h tras silencio   │   │ - T-24h reminder         │
   │ - D2-D6 secuencia        │   │ - T-3h reminder          │
   │ - perdido a 14d sin resp │   │ - skip si lead pidió NO  │
   └──────────────────────────┘   └──────────────────────────┘
```

---

## [D1] WA Inbound + Parser (✅ deployed)

**Trigger:** Webhook POST `/webhook/wa-inbound`
**Estado:** activo, deployed VPS2 sprint 2.2

**Próximas mejoras** (sprint 2.3):
1. **Step nuevo "Lookup ERP cliente"** — query `livskin_erp.clientes WHERE telefono LIKE %{phone_last8}%` para flag `is_recurrente` + `total_ventas_historicas`
2. **Step nuevo "Get conv state"** — lectura `wa_conversation_state` para context
3. **Step "Tool Dispatcher"** — router central a [D2] o escalación

---

## [D1.5] Tool Dispatcher (nuevo, dentro de D1 ampliado)

**Lógica (rule-based, NO IA):**

```javascript
// Pseudocódigo del dispatcher
function dispatch(parsed, conv_state, cliente_erp) {
  // 1. Escalación inmediata si:
  if (parsed.confidence < 0.5) return "escalate_low_confidence";
  if (parsed.intent === "ask_human") return "escalate_user_request";
  if (cliente_erp && cliente_erp.ventas_historicas >= 3) return "escalate_recurrente";

  // 2. Red flags (scoring rules)
  const redFlagPatterns = [
    /m[áa]s barato|descuento|negociaci[oó]n|rebaja|baja precio/i,
    /(otra cl[íi]nica|munay|beysa|valderma).*(mejor|m[áa]s barato)/i,
    /cancel(o|amos|a) (otra vez|de nuevo)/i,
    /borrar todas? mis arrugas|cambiarme la cara|que me cambies/i,
    /embarazada|gestaci[oó]n|cancer/i,  // contraindicación → SIEMPRE escalate
  ];
  if (redFlagPatterns.some(re => re.test(parsed.original_text))) {
    return "escalate_red_flag";
  }

  // 3. Caminos automáticos según intent
  switch (parsed.intent) {
    case "greeting": return "send_welcome_yossie";
    case "ask_price": return "send_price_range_with_disclaimer";
    case "ask_info": return "send_info_treatment";
    case "confirm": return "confirm_appointment_with_doctora";
    case "reject": return "send_followup_or_close";
    case "cancel": return "cancel_appointment";
    case "reschedule": return "send_reschedule_request_to_doctora";
    case "propose_date": return "relay_proposal_to_doctora";
    default: return "escalate_unknown";
  }
}
```

**Output:** action_name → siguiente nodo n8n route correspondiente.

---

## [D2] WA Send Outbound

**Trigger:** llamado por D1.5 dispatcher o D3 cron
**Input:** `{phone, action_type, params, template_name_or_text}`

**Lógica:**
1. Check si ventana 24h activa (`wa_conversation_state.last_inbound_at < NOW() - 24h`?)
2. Si dentro de ventana → enviar texto libre
3. Si fuera de ventana → usar template Meta-approved
4. Si template no aprobada aún → audit `wa_send_blocked_no_template` + notif doctora

**Endpoint Meta:** `POST /v21.0/{phone_id}/messages`

**Templates a usar** (ver `integrations/whatsapp/templates/drafts-v1.md`):
- `new_lead_appointment_request` → primer contacto
- `lead_confirmed_appointment` → cita confirmada
- `lead_proposed_alternatives` → doctora propone alternativas
- `lead_waiting_4h_followup` → silencio 4h
- `appointment_reminder_24h` → T-24h
- `appointment_reminder_3h` → T-3h
- `reengagement_inactive_30d` → inactividad 30d

---

## [D3] Conversation Manager (cron 5min)

**Trigger:** cron `*/5 * * * *`

**Pasos:**
1. Query `wa_conversation_state WHERE state NOT IN ('closed', 'won')`
2. Para cada conversación:
   - **Si `waiting_doctora` >4h** → notif doctora "lead X esperando hace 4h"
   - **Si `waiting_doctora` >24h** → notif Dario alerta
   - **Si `waiting_lead` >48h** → trigger D5 reengagement (paso D1)
   - **Si `negotiating` >7d** → marcar `lost_silence`
3. Audit cada acción

---

## [D4] Doctora Inbound Handler

**Trigger:** webhook desde **WhatsApp PERSONAL doctora** (cuando ella responde via su número habitual)

**Reto técnico:** la doctora usa SU número personal. Cloud API solo captura mensajes del número Livskin oficial `+51 947 741 117`. ¿Cómo capturamos lo que ella escribe en su WA personal?

**Opciones a evaluar:**
- **Opción A — Manual via Yossie**: doctora le dice a Yossie via WA Livskin "confirma cita Maria viernes 6pm" → Yossie lo relaya al lead. Doctora NO escribe directo al lead.
- **Opción B — App WhatsApp Business Multi-dispositivo**: imposible, su número personal NO está conectado a la API Cloud (sería suspender su WA personal).
- **Opción C — Bridge via ERP**: doctora marca en ERP "respuesta a Maria: viernes 6pm OK" → ERP emite evento → n8n relaya al lead via Cloud API. Esto requiere ERP UI para que doctora responda inline.

**Recomendación inicial:** **Opción A + C híbrida**.
- Opción A para casos simples y conversacionales (doctora chatea con Yossie como si fuera asistente humano)
- Opción C para confirmaciones formales (botones en ERP "confirmar cita / proponer alternativas")

→ **Decisión a Dario en próxima micro-sesión** post-encuentro doctora pre-Sprint 2.3.

---

## [D5] Reengagement Sequence (cron 1h)

**Trigger:** cron `0 */1 * * *`

**Lógica (drop-off D1-D6 del workbook):**

```sql
-- Detectar leads silenciosos
SELECT * FROM wa_conversation_state WHERE
  state IN ('waiting_lead', 'open')
  AND last_outbound_at < NOW() - INTERVAL '48 hours'
  AND last_inbound_at IS NULL OR last_inbound_at < last_outbound_at
  AND reengagement_attempts < 4;
```

**Secuencia:**
| Touch | Trigger | Template | Si no responde →  |
|---|---|---|---|
| D1 | 48h sin respuesta | `lead_waiting_4h_followup` (reusable) | wait 24h → D2 |
| D2 | 24h después D1 | "Mayor contenido" (a definir) | wait 24h → D3 |
| D3 | 24h después D2 | "Preguntar dudas + ofrecer agendar" | wait 24h → D4 |
| D4 | 24h después D3 | "Proponer nueva cita" | wait 7d → D5 |
| D5 | 7d después D4 | "Enviar discusión + agendar" | mark lost_silence |
| D6 | 14d+ después D5 | template `reengagement_inactive_30d` | one-shot, mark perdido |

**Touches máximos:** 4 (después → `lost_silence`)
**Días silencio total → perdido:** 30d (D6 es one-shot final)

---

## [D6] Reminders (cron 30min)

**Trigger:** cron `*/30 * * * *`

**Lógica:**
1. Query `appointments WHERE estado='programada' AND fecha_hora BETWEEN NOW()+2h AND NOW()+3h30min AND reminder_3h_sent=false`
2. Enviar template `appointment_reminder_3h`
3. Marcar `reminder_3h_sent=true`
4. Similar para T-24h con `appointment_reminder_24h`

**Skip si:**
- Cliente marcó "no recordatorios" en preferencias (futura feature ERP)
- Cliente ya confirmó asistencia hoy

---

## Stack de tablas Postgres ERP usadas

- `wa_conversation_state` (creada migration 0008)
- `wa_messages` (creada migration 0008)
- `clientes` + `clientes_venta` (lookup para detectar recurrente)
- `appointments` (cuando se construya migration 0009 — pendiente Sprint 4)
- `audit_log` (todos los eventos `wa.*`, `conversation.*`, `appointment.*`)

---

## Audit events nuevos canónicos (a registrar en `docs/audit-events-schema.md`)

| Event | Cuándo |
|---|---|
| `wa.message_received` | Cada inbound D1 |
| `wa.message_sent` | Cada outbound D2 (texto libre o template) |
| `wa.template_used` | Outbound via template Meta |
| `wa.send_blocked_no_template` | Out of 24h window, no template aprobada |
| `conversation.escalated_to_doctora` | Trigger escalación (red flag, recurrente, etc.) |
| `conversation.intent_detected` | Cada vez que parser classifica |
| `conversation.intent_unknown` | Confidence < 0.5 |
| `conversation.reengagement_sent` | Cron D5 envió touch |
| `conversation.marked_lost` | Touches máx alcanzados |
| `appointment.confirmed_via_bot` | Yossie confirmó cita |
| `appointment.proposed_alternatives` | Doctora propuso slots distintos |
| `appointment.reminder_sent_24h` | Recordatorio T-24h |
| `appointment.reminder_sent_3h` | Recordatorio T-3h |

---

## Orden de implementación sugerido (Sprint 2.3 + Sprint 3)

**Sprint 2.3 (~6-8h, post-12-outputs)** — workflow D1 ampliado:
1. Añadir Lookup ERP cliente a D1 (paso nuevo)
2. Añadir Tool Dispatcher (D1.5) inline
3. Building [D2] WA Send con templates
4. Smoke E2E: lead nuevo → Yossie saluda + propone consulta

**Sprint 3 (~8-12h)**:
5. [D3] Conversation Manager cron
6. [D4] Doctora Inbound Handler (decisión arquitectónica A vs C primero)
7. Migration 0009 — `appointments` table
8. Smoke E2E completo: anuncio → form → Yossie → cita → doctora confirma → reminders → asistencia → cliente

**Sprint 4 (~4-6h)**:
9. [D5] Reengagement cron + sequence completa
10. [D6] Reminders cron
11. CAPI emit hooks (Lead + Schedule + Purchase con event_id full-funnel)
12. Smoke E2E con reengagement validado

---

**Fin plan n8n bot Yossie — 2026-05-23**
