"""Build d1-wa-yossie-v2.json workflow programmatically."""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Load responder v2 JS
with open('c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/infra/n8n/lib/yossie_responder_v2.js', 'r', encoding='utf-8') as f:
    responder_js = f.read()

# Strip module.exports section
responder_js = responder_js.replace(
    """if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    processInbound,
    parseInbound,
    decideNextAction,
    buildHandoffPayloads,
    detectTreatment,
    detectRedFlag,
    TREATMENT_LABELS,
  };
}""",
    "// (module.exports omitido en n8n)"
)

# Master code embedded
yossie_master_code = """// ============================================================================
// YOSSIE MASTER NODE - Workflow d1-wa-handoff-v2
// Doctrina #11 - deterministic backbone first
// ============================================================================

""" + responder_js + """

// ============================================================================
// EXECUTION
// ============================================================================

const META_TOKEN = $env.META_SYSTEM_USER_TOKEN;
const AUDIT_TOKEN = $env.AUDIT_INTERNAL_TOKEN;
const ERP_BASE = 'https://erp.livskin.site';
const A1_WEBHOOK = 'https://flow.livskin.site/webhook/acquisition/form-submit';

if (!META_TOKEN) return [{ json: { error: 'META_SYSTEM_USER_TOKEN env var missing' } }];
if (!AUDIT_TOKEN) return [{ json: { error: 'AUDIT_INTERNAL_TOKEN env var missing' } }];

const webhookBody = $input.first().json.body || {};

const inbound = parseInbound(webhookBody);
if (!inbound) {
  return [{ json: { skipped: true, reason: 'no inbound message (status callback)' } }];
}

let stateRow = null;
try {
  const stateRes = await this.helpers.httpRequest({
    method: 'GET',
    url: ERP_BASE + '/api/internal/wa-state',
    qs: { phone: inbound.phone_e164 },
    headers: { 'X-Internal-Token': AUDIT_TOKEN },
    json: true,
    timeout: 10000,
  });
  stateRow = stateRes && Object.keys(stateRes).length ? stateRes : null;
} catch (e) {
  console.warn('[Yossie] Get state failed:', e.message);
}

const result = processInbound(webhookBody, stateRow);

if (result.decision.action_type === 'no_action') {
  return [{ json: { skipped: true, decision: result.decision, inbound } }];
}

const outboundResults = { sent: [], errors: [] };
let outboundWamid = null;
let outboundError = null;

if (result.wa_outbound) {
  // Delay 2-5s aleatorio para humanizar respuesta al lead (no aplica a notifs internas)
  const delayMs = 2000 + Math.floor(Math.random() * 3000);
  await new Promise((resolve) => setTimeout(resolve, delayMs));

  try {
    const phoneNumberId = inbound.phone_number_id;
    const waRes = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://graph.facebook.com/v21.0/' + phoneNumberId + '/messages',
      headers: { Authorization: 'Bearer ' + META_TOKEN, 'Content-Type': 'application/json' },
      body: result.wa_outbound,
      json: true,
      timeout: 15000,
    });
    outboundWamid = waRes?.messages?.[0]?.id || null;
    outboundResults.sent.push({ type: 'wa_to_lead', delay_ms: delayMs, meta_response: waRes });
  } catch (e) {
    outboundError = e.message;
    outboundResults.errors.push({ type: 'wa_to_lead', error: e.message });
  }
}

try {
  const upsertPayload = {
    phone_lead: result.new_state.phone_lead,
    state: result.new_state.state,
    last_intent: result.new_state.last_intent,
    context_json: result.new_state.context_json,
    last_inbound_text: result.new_state.last_inbound_text,
    increment_inbound_count: true,
    increment_outbound_count: result.wa_outbound ? true : false,
    // Persistir body inbound en wa_messages (fix bug 2026-05-27 — tabla estaba vacia)
    inbound_message: {
      meta_message_id: inbound.message_id || null,
      message_type: inbound.type || 'text',
      body: inbound.text || null,
      intent: result.new_state.last_intent || null,
      meta_payload_raw: {
        from: inbound.from,
        type: inbound.type,
        button_id: inbound.button_id || null,
        list_id: inbound.list_id || null,
        referral_source_id: inbound.referral_source_id || null,
        referral_headline: inbound.referral_headline || null,
        referral_product: inbound.referral_product || null,
      },
    },
  };
  if (result.new_state.escalation_reason) {
    upsertPayload.escalation_reason = result.new_state.escalation_reason;
    upsertPayload.escalation_to = result.new_state.escalation_to;
  }
  if (result.wa_outbound) {
    const outText = result.wa_outbound.type === 'text'
      ? result.wa_outbound.text?.body
      : result.wa_outbound.interactive?.body?.text;
    upsertPayload.last_outbound_text = outText;
    // Persistir body outbound en wa_messages
    upsertPayload.outbound_message = {
      meta_message_id: outboundWamid,
      message_type: result.wa_outbound.type || 'text',
      body: outText || null,
      meta_status: outboundError ? 'failed' : 'sent',
      meta_error_message: outboundError,
    };
  }
  await this.helpers.httpRequest({
    method: 'POST',
    url: ERP_BASE + '/api/internal/wa-state',
    headers: { 'X-Internal-Token': AUDIT_TOKEN, 'Content-Type': 'application/json' },
    body: upsertPayload,
    json: true,
    timeout: 10000,
  });
  outboundResults.state_upserted = true;
} catch (e) {
  outboundResults.errors.push({ type: 'state_upsert', error: e.message });
}

if (result.handoff_payloads) {
  try {
    const a1Res = await this.helpers.httpRequest({
      method: 'POST',
      url: A1_WEBHOOK,
      headers: { 'Content-Type': 'application/json' },
      body: result.handoff_payloads.vtiger_payload,
      json: true,
      timeout: 20000,
    });
    outboundResults.sent.push({ type: 'a1_vtiger_lead', response: a1Res });
  } catch (e) {
    outboundResults.errors.push({ type: 'a1_vtiger_lead', error: e.message });
  }

  // Notificacion a 3 destinatarios via TEMPLATE doctor_lead_notification_v1 (APPROVED)
  // Template NO depende de 24h window — funciona siempre, incluso si destinatario nunca escribio.
  // Template body tiene 6 vars: {{1}} nombre, {{2}} telefono, {{3}} tratamiento, {{4}} experiencia, {{5}} urgencia, {{6}} mensaje
  const recipients = result.handoff_payloads.notif_recipients || [
    { name: 'Dario', phone: result.handoff_payloads.dario_phone || '51982732978' },
  ];
  const tplPayloads = result.handoff_payloads.template_params || {};
  for (const recipient of recipients) {
    try {
      const notifRes = await this.helpers.httpRequest({
        method: 'POST',
        url: 'https://graph.facebook.com/v21.0/' + inbound.phone_number_id + '/messages',
        headers: { Authorization: 'Bearer ' + META_TOKEN, 'Content-Type': 'application/json' },
        body: {
          messaging_product: 'whatsapp',
          recipient_type: 'individual',
          to: recipient.phone,
          type: 'template',
          template: {
            name: 'doctor_lead_notification_v1',
            language: { code: 'es_PE' },
            components: [
              {
                type: 'body',
                parameters: [
                  { type: 'text', text: tplPayloads.nombre || '(sin nombre)' },
                  { type: 'text', text: tplPayloads.telefono || '(sin tel)' },
                  { type: 'text', text: tplPayloads.tratamiento || '(no especificado)' },
                  { type: 'text', text: tplPayloads.experiencia || '(no respondio)' },
                  { type: 'text', text: tplPayloads.urgencia || '(no respondio)' },
                  { type: 'text', text: tplPayloads.mensaje || '(sin mensaje original)' },
                ],
              },
            ],
          },
        },
        json: true,
        timeout: 15000,
      });
      outboundResults.sent.push({ type: 'notif_template_' + recipient.name, phone: recipient.phone, meta_response: notifRes });
    } catch (e) {
      outboundResults.errors.push({ type: 'notif_template_' + recipient.name, phone: recipient.phone, error: e.message });
    }
  }
}

return [{
  json: {
    success: outboundResults.errors.length === 0,
    inbound: { from: inbound.from, text: inbound.text, button_id: inbound.button_id, referral_product: inbound.referral_product },
    decision: result.decision.action_type,
    new_state: result.new_state.state,
    new_progress: result.new_state.context_json?.progress,
    handoff_triggered: !!result.handoff_payloads,
    outbound: outboundResults,
  },
}];
"""

# Build workflow JSON
workflow = {
    "id": "d1-wa-yossie-v2",
    "name": "[D1v2] WA Yossie Master - State Machine + Buttons + Handoff",
    "active": True,
    "isArchived": False,
    "nodes": [
        {
            "id": "n1-webhook-get",
            "name": "Webhook GET (handshake)",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [200, 200],
            "webhookId": "wa-yossie-v2-get",
            "parameters": {
                "httpMethod": "GET",
                "path": "wa-yossie-v2",
                "responseMode": "responseNode",
                "options": {}
            }
        },
        {
            "id": "n2-verify",
            "name": "Verify Handshake",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [420, 200],
            "parameters": {
                "jsCode": "const p = $input.first().json.query || {};\nconst c = p['hub.challenge'] || '';\nconst t = p['hub.verify_token'] || '';\nif (t === 'livskin_wa_webhook_2026' && c) return [{ json: { response: c, statusCode: 200 } }];\nreturn [{ json: { response: 'forbidden', statusCode: 403 } }];"
            }
        },
        {
            "id": "n3-respond-handshake",
            "name": "Respond Handshake",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [640, 200],
            "parameters": {
                "respondWith": "text",
                "responseBody": "={{ $json.response }}",
                "options": {"responseCode": "={{ $json.statusCode }}"}
            }
        },
        {
            "id": "n4-webhook-post",
            "name": "Webhook POST (events)",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [200, 460],
            "webhookId": "wa-yossie-v2-post",
            "parameters": {
                "httpMethod": "POST",
                "path": "wa-yossie-v2",
                "responseMode": "responseNode",
                "options": {}
            }
        },
        {
            "id": "n5-respond-ok",
            "name": "Respond 200 OK",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [420, 460],
            "parameters": {
                "respondWith": "text",
                "responseBody": "OK",
                "options": {"responseCode": 200}
            }
        },
        {
            "id": "n6-yossie-master",
            "name": "Yossie Master",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [640, 600],
            "parameters": {"jsCode": yossie_master_code},
            "continueOnFail": True
        }
    ],
    "connections": {
        "Webhook GET (handshake)": {"main": [[{"node": "Verify Handshake", "type": "main", "index": 0}]]},
        "Verify Handshake": {"main": [[{"node": "Respond Handshake", "type": "main", "index": 0}]]},
        "Webhook POST (events)": {"main": [[
            {"node": "Respond 200 OK", "type": "main", "index": 0},
            {"node": "Yossie Master", "type": "main", "index": 0}
        ]]}
    },
    "settings": {"executionOrder": "v1"},
    "staticData": None,
    "meta": None,
    "pinData": None,
    "versionId": "v2-init",
    "activeVersionId": "v2-init",
    "versionCounter": 1,
    "triggerCount": 2,
    "tags": []
}

out_path = 'c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/infra/n8n/workflows/D-conversation/d1-wa-yossie-v2.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, separators=(',', ':'))

js_len = len(yossie_master_code)
full_len = len(json.dumps(workflow))
print(f"Master code: {js_len} chars")
print(f"Workflow JSON total: {full_len} bytes")
print(f"Saved: {out_path}")
