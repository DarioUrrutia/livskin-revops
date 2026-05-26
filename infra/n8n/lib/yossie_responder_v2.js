/**
 * Yossie Responder v2 — bot rule-based con state machine + interactive buttons
 *
 * Reemplaza v1 (handoff genérico). v2 hace filtro inicial calificación:
 *  - Q1: confirmar tratamiento de interés
 *  - Q2: primera vez vs experiencia previa
 *  - Q3: urgencia / timing
 *  - Cierre: handoff a Dario con info estructurada + ubicación clínica
 *
 * Doctrina #11 — deterministic backbone first. No LLM, no IA.
 * Toda info real validada del workbook discovery 2026-05-17.
 *
 * Author: Claude Code (Livskin RevOps) — 2026-05-24
 *
 * INPUT (desde n8n n8n_function_body):
 *   - inbound: { from, profile_name, type, body, button_id, list_id, referral }
 *   - state_row: { state, q1_treatment, q2_first_time, q3_urgency, message_count, ... } | null
 *
 * OUTPUT:
 *   - action_type: 'send_interactive_buttons' | 'send_text' | 'handoff' | 'no_action'
 *   - response_payload: WA API payload (object)
 *   - new_state: estado a UPSERT en wa_conversation_state
 *   - handoff: { triggered, vtiger_payload, notif_to_dario } | null
 */

// ============================================================================
// INTERNAL PHONES — Dario + doctora. El bot IGNORA mensajes inbound de estos
// (no son leads, son operadores internos que reciben notificaciones).
// ============================================================================

const INTERNAL_PHONES = [
  '+51982732978',   // Dario (control)
  '+51910848995',   // Doctora Claudia (1)
  '+51980727888',   // Doctora Claudia (2)
];

function isInternalPhone(phoneE164) {
  if (!phoneE164) return false;
  return INTERNAL_PHONES.includes(phoneE164);
}

// ============================================================================
// DETECCIONES (regex defensivos sobre texto del lead — fallback si no usa botón)
// ============================================================================

const REFERRAL_PRODUCT_PATTERNS = {
  botox: /\b(botox|toxina|arrugas?|expresi[óo]n|entrecejo|patas\s+de\s+gallo|tercio\s+superior)\b/i,
  acido: /\b([áa]cido\s+hialur[óo]nico|hialur[óo]nico|rinomodelaci[óo]n|p[óo]mulos|relleno\s+de\s+labios|ojeras)\b/i,
  prp: /\b(prp|plasma|plaquetas|plasma\s+rico)\b/i,
  limpieza: /\b(limpieza\s+facial|facial\s+profunda|limpieza\s+de\s+rostro)\b/i,
  hilos: /\b(hilos?\s+tensores?|hilos\s+pdo|lifting\s+sin\s+cirug[ií]a)\b/i,
  salmon: /\b(esperma\s+de\s+salm[óo]n|salm[óo]n|polinucle[óo]tidos)\b/i,
  exosomas: /\b(exosomas|p[ée]ptidos|c[ée]lulas\s+madre)\b/i,
};

const RED_FLAG_PATTERNS = {
  embarazo: /\b(embaraz|gestante|encinta|esperando\s+beb|lactan[dt]|amamant)/i,
  cancer: /\b(c[áa]ncer|tumor|quimio|radio\s*terapia|onc[óo]log)/i,
  alergias_serias: /\b(al[ée]rgica?\s+a\s+(anestesia|botulinico|toxina|hialur[óo]nico)|anafil|edema\s+severo)/i,
  medicamentos_criticos: /\b(anticoagul|warfarin|sintrom|isotretino[íi]na|roacut[áa]n|miastenia)/i,
};

const PRICE_OBJECTION_PATTERNS = /\b(cu[áa]nto\s+(cuesta|sale|vale)|precio|costo|tarifa|caro|costoso|cu[áa]nto\s+es|presupuesto|presupuestos|me\s+sale|me\s+cuesta)/i;

const ESCAPE_TO_HUMAN_PATTERNS = /\b(hablar\s+(con|directo)|hablar\s+con\s+(la\s+)?(doctora|m[ée]dico)|saltar\s+preguntas|sin\s+preguntas|ya\s+s[ée]\s+lo\s+que\s+quiero|d[ée]jame\s+hablar|directamente)/i;

// === FOLLOWUP TEMPLATE BUTTONS — texto exacto de lead_waiting_4h_followup_v1 ===
// Meta envía type=button con button.text al clickear quick reply de template
const FOLLOWUP_YES_PATTERNS = /^s[íi]\s*,?\s*sigo\s+interesad/i;
const FOLLOWUP_LATER_PATTERNS = /m[áa]s\s+tarde\s+respondo|m[áa]s\s+tarde|despu[ée]s\s+respondo/i;
const FOLLOWUP_NO_PATTERNS = /^ya\s+no\s*,?\s*gracias|^no\s*,?\s*gracias|ya\s+no\s+me\s+interes/i;

// === OPT-IN MARKETING — respuestas tras "Ya no, gracias" ===
const OPTIN_YES_PATTERNS = /^s[íi]\s*,?\s*mant[ée]n|mant[ée]nme\s+informad|s[íi]\s+a\s+las\s+promociones|me\s+gustar[íi]a/i;
const OPTIN_NO_PATTERNS = /^no\s*,?\s*eliminar|elimina(r|me)?\s+mis\s+datos|borra(r|me)?\s+(mis\s+)?datos|no\s+quiero\s+(m[áa]s|nada)/i;

// ============================================================================
// CATÁLOGO TRATAMIENTOS (canonical names — valida workbook discovery)
// ============================================================================

const TREATMENT_LABELS = {
  botox: 'Botox',
  acido: 'Ácido Hialurónico',
  prp: 'Plasma Rico en Plaquetas (PRP)',
  limpieza: 'Limpieza Facial Profunda',
  hilos: 'Hilos Tensores',
  salmon: 'Esperma de Salmón',
  exosomas: 'Exosomas',
  otro: 'Otro tratamiento',
};

// ============================================================================
// COPY (mensajes del bot — voice Yossie validada con doctora)
// ============================================================================

function buildGreetingWithProduct(name, treatmentKey) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  const treatment = TREATMENT_LABELS[treatmentKey] || 'medicina estética';
  return `Hola${safeName} ☺️ soy Yossie, asistente de la Dra. Claudia Delgado (CMP 091029) en Livskin Cusco.\n\nVi que llegas por nuestro anuncio de ${treatment}. ¿Es ese el tratamiento que te interesa?`;
}

function buildGreetingWithoutProduct(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Hola${safeName} ☺️ soy Yossie, asistente de la Dra. Claudia Delgado (CMP 091029) en Livskin Cusco.\n\n¿En qué tratamiento te puedo orientar?`;
}

function buildQ2FirstTime(treatmentKey) {
  const treatment = TREATMENT_LABELS[treatmentKey] || 'este tratamiento';
  return `Para que la Dra. te dé la mejor orientación, cuéntame: ¿es tu primera vez con ${treatment}, o ya te lo has hecho antes? ☺️`;
}

function buildGreetingPlusQ2(name, treatmentKey) {
  // Caso: lead escribe "vengo por botox" — saludo + Q2 en UN solo mensaje compacto
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  const treatment = TREATMENT_LABELS[treatmentKey] || 'este tratamiento';
  return `Hola${safeName} ☺️ soy Yossie, asistente de la Dra. Claudia Delgado (CMP 091029) en Livskin Cusco.\n\nCuéntame: ¿es tu primera vez con ${treatment}, o ya te has hecho antes?`;
}

function buildQ3Urgency() {
  return `Genial ☺️ Una última cosa para que la Dra. pueda revisar su agenda contigo: ¿cuándo te gustaría empezar?`;
}

function buildClosing(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Listo${safeName} ✨\n\nLe paso tu información a la Dra. Claudia. Te escribe por aquí en breve para coordinar contigo ☺️\n\n📍 Urb. La Florida O-7, Wanchaq, Cusco`;
}

function buildQ4InfoTopics() {
  return `Claro, antes de pasarte con la Dra. — ¿qué es lo que más te gustaría saber? Así ella te puede explicar con todo el detalle apenas converse contigo ☺️`;
}

function buildClosingWithInfo(name, topics) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  const topicsList = (topics || []).join(', ');
  return `Gracias${safeName} ✨\n\nLe paso a la Dra. Claudia tus inquietudes${topicsList ? ` sobre ${topicsList}` : ''}. Te responde por aquí en breve ☺️\n\n📍 Urb. La Florida O-7, Wanchaq, Cusco`;
}

function buildPriceObjection(name) {
  const safeName = name && name.trim() ? `${name.trim()}, ` : '';
  return `${safeName}los precios varían según la zona, cantidad de producto necesaria y profundidad del tratamiento — cada caso es distinto.\n\nLe paso ahora mismo tus inquietudes a la Dra. Claudia para que pueda explicarte mejor y darte un estimado preciso. Te responde en breve ☺️`;
}

function buildEscapeToHuman(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Por supuesto${safeName} ☺️\n\nLe paso tu interés a la Dra. Claudia. Te escribe por aquí en breve para conversar directamente ✨`;
}

function buildRedFlagResponse(name, flagType) {
  const safeName = name && name.trim() ? `${name.trim()}, ` : '';
  return `${safeName}gracias por contarme. Este tipo de caso la Dra. Claudia lo revisa personalmente antes de cualquier paso. Le paso tu info ahora mismo y te responde en breve ☺️`;
}

// Gap C — handler para media types (image, audio, video, document, location)
function buildMediaReceivedResponse(name, mediaType) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  const labels = {
    image: 'tu foto',
    audio: 'tu mensaje de voz',
    video: 'tu video',
    document: 'tu documento',
    location: 'tu ubicación',
  };
  const label = labels[mediaType] || 'tu mensaje';
  return `Gracias${safeName} ☺️\n\nLe paso ${label} a la Dra. Claudia para que la revise con atención. Ella te responde por aquí en breve con su observación ✨`;
}

// Lead respondió "Sí, sigo interesada" al follow-up — HANDOFF directo
function buildFollowupYesResponse(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Qué bueno${safeName} ✨\n\nLe aviso a la Dra. Claudia que sigues interesada. Ella revisa tu caso personalmente y te escribe por aquí en breve para coordinar contigo ☺️`;
}

// Lead respondió "Más tarde respondo" — snooze 24h
function buildFollowupLaterResponse(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Perfecto${safeName} ☺️\n\nTe escribimos mañana para retomar la conversación cuando tengas más tiempo. Quedamos atentas a tu respuesta ✨`;
}

// Lead respondió "Ya no, gracias" — pregunta opt-in marketing
function buildOptInQuestion(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Entendido${safeName}, gracias por avisarnos ☺️\n\nUna última cosa: ¿prefieres que te enviemos promociones ocasionales en el futuro, o prefieres que eliminemos tus datos de nuestra base?`;
}

// Lead aceptó recibir promociones futuras
function buildOptInYesResponse(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Perfecto${safeName} ✨\n\nQuedas en nuestra lista para avisarte de promociones y novedades. ¡Hasta pronto! ☺️`;
}

// Lead pidió que eliminemos sus datos
function buildOptInNoResponse(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Listo${safeName}, eliminaremos tus datos de nuestra base ☺️\n\nRespetamos tu decisión. Gracias por habernos escrito y te deseamos lo mejor ✨`;
}

// Gap K — Lead vuelve a escribir post-escalado (state=escalated, nueva conversacion)
function buildLeadReturnedResponse(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `¡Qué bueno que hayas vuelto${safeName}! ✨\n\nLe aviso a la Dra. Claudia que retomas tu interés. Como ya conoce tu caso, te responde por aquí muy en breve para continuar contigo ☺️`;
}

// ============================================================================
// INTERACTIVE BUTTONS PAYLOADS
// ============================================================================

function buildInteractiveButtons(phoneE164, bodyText, buttons) {
  return {
    messaging_product: 'whatsapp',
    recipient_type: 'individual',
    to: phoneE164.startsWith('+') ? phoneE164.slice(1) : phoneE164,
    type: 'interactive',
    interactive: {
      type: 'button',
      body: { text: bodyText },
      action: {
        buttons: buttons.map((b) => ({
          type: 'reply',
          reply: { id: b.id, title: b.title.slice(0, 20) },
        })),
      },
    },
  };
}

function buildTextMessage(phoneE164, bodyText) {
  return {
    messaging_product: 'whatsapp',
    recipient_type: 'individual',
    to: phoneE164.startsWith('+') ? phoneE164.slice(1) : phoneE164,
    type: 'text',
    text: { preview_url: false, body: bodyText },
  };
}

// ============================================================================
// HELPER: detectar tratamiento del referral o del texto libre
// ============================================================================

function detectTreatment(text) {
  if (!text) return null;
  for (const [key, regex] of Object.entries(REFERRAL_PRODUCT_PATTERNS)) {
    if (regex.test(text)) return key;
  }
  return null;
}

function detectRedFlag(text) {
  if (!text) return null;
  for (const [flag, regex] of Object.entries(RED_FLAG_PATTERNS)) {
    if (regex.test(text)) return flag;
  }
  return null;
}

// ============================================================================
// PARSE INBOUND — extrae lo útil del webhook payload Meta
// ============================================================================

function parseInbound(webhookBody) {
  const body = webhookBody || {};
  const entries = body.entry || [];

  for (const entry of entries) {
    for (const change of entry.changes || []) {
      const value = change.value || {};
      const messages = value.messages || [];
      if (!messages.length) continue;
      const contacts = value.contacts || [];

      for (const msg of messages) {
        const from = msg.from;
        const messageId = msg.id;
        const timestamp = msg.timestamp;
        const type = msg.type;
        const contact = contacts.find((c) => c.wa_id === from) || {};
        const profileName = contact.profile?.name || '';
        const phoneE164 = from.startsWith('+') ? from : '+' + from;
        const phoneNumberId = value.metadata?.phone_number_id;

        let text = '';
        let buttonId = null;

        if (type === 'text') {
          text = msg.text?.body || '';
        } else if (type === 'interactive') {
          if (msg.interactive?.button_reply) {
            buttonId = msg.interactive.button_reply.id;
            text = msg.interactive.button_reply.title || '';
          } else if (msg.interactive?.list_reply) {
            buttonId = msg.interactive.list_reply.id;
            text = msg.interactive.list_reply.title || '';
          }
        } else if (type === 'button') {
          text = msg.button?.text || '';
          buttonId = msg.button?.payload || null;
        } else if (type === 'image') {
          text = '[imagen]' + (msg.image?.caption ? ' ' + msg.image.caption : '');
        } else if (type === 'audio') {
          text = '[audio]';
        } else if (type === 'video') {
          text = '[video]' + (msg.video?.caption ? ' ' + msg.video.caption : '');
        } else if (type === 'document') {
          text = '[documento]' + (msg.document?.filename ? ' ' + msg.document.filename : '');
        } else if (type === 'location') {
          text = `[ubicación] ${msg.location?.latitude || ''},${msg.location?.longitude || ''}`;
        } else if (type === 'sticker') {
          text = '[sticker]';
        }

        const referral = msg.referral || msg.context?.referral || null;
        const referralProduct = referral
          ? detectTreatment((referral.headline || '') + ' ' + (referral.body || ''))
          : null;

        return {
          from,
          phone_e164: phoneE164,
          phone_number_id: phoneNumberId,
          profile_name: profileName,
          message_id: messageId,
          timestamp,
          type,
          text,
          button_id: buttonId,
          referral_product: referralProduct,
          referral_source_id: referral?.source_id || null,
          referral_source_url: referral?.source_url || null,
          referral_headline: referral?.headline || null,
        };
      }
    }
  }
  return null;
}

// ============================================================================
// STATE MACHINE — decide próxima acción según state actual + input
// ============================================================================

function decideNextAction(inbound, state) {
  const { phone_e164, profile_name, text, button_id, referral_product } = inbound;
  const stateName = state?.state || 'new';
  // Progress dentro del estado 'qualifying' — guardado en context_json.progress
  const progress = state?.context_json?.progress || null;

  // === MEDIA TYPES — image/audio/video/document/location → HANDOFF a doctora ===
  // Stickers se ignoran (common WA quirk). Texto puro sigue flow normal.
  const mediaTypes = ['image', 'audio', 'video', 'document', 'location'];
  if (mediaTypes.includes(inbound.type)) {
    return {
      action_type: 'media_handoff',
      message: buildMediaReceivedResponse(profile_name, inbound.type),
      new_state_name: 'escalated',
      handoff: {
        triggered: true,
        flag: `lead_sent_${inbound.type}`,
        urgency: 'MEDIUM',
      },
    };
  }
  if (inbound.type === 'sticker') {
    // Sticker: ignorar sin responder (common quirk, evitar spam)
    return {
      action_type: 'no_action',
      reason: 'sticker ignored',
    };
  }

  // === RESPUESTAS AL TEMPLATE FOLLOWUP — interceptar ANTES de state machine normal ===
  // Solo aplica si followup_sent=true y state aun qualifying (no escalated/closed)
  const followupSent = state?.context_json?.followup_sent === true;
  if (followupSent && stateName === 'qualifying') {
    // (1) Lead respondió "Sí, sigo interesada" → HANDOFF directo a doctora
    if (FOLLOWUP_YES_PATTERNS.test(text)) {
      return {
        action_type: 'followup_yes_handoff',
        message: buildFollowupYesResponse(profile_name),
        new_state_name: 'escalated',
        handoff: {
          triggered: true,
          flag: 'followup_yes_interested',
          urgency: 'HIGH',
        },
      };
    }
    // (2) Lead respondió "Más tarde respondo" → snooze 24h, state queda qualifying
    if (FOLLOWUP_LATER_PATTERNS.test(text)) {
      const snoozeUntil = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
      return {
        action_type: 'followup_snooze_24h',
        message: buildFollowupLaterResponse(profile_name),
        new_state_name: 'qualifying',
        new_progress: progress, // mantiene Q1/Q2/Q3 donde se quedó
        snoozed_until: snoozeUntil,
        reset_followup_sent: true, // F1 podrá reenviar tras snooze
      };
    }
    // (3) Lead respondió "Ya no, gracias" → preguntar opt-in marketing
    if (FOLLOWUP_NO_PATTERNS.test(text)) {
      return {
        action_type: 'send_interactive_buttons',
        message: buildOptInQuestion(profile_name),
        buttons: [
          { id: 'q5_optin_yes', title: 'Sí, mantenme' },
          { id: 'q5_optin_no', title: 'No, eliminar' },
        ],
        new_state_name: 'qualifying',
        new_progress: 'q5_optin',
      };
    }
  }

  // === RESPUESTAS AL OPT-IN (Q5) — tras "Ya no, gracias" ===
  if (stateName === 'qualifying' && progress === 'q5_optin') {
    let optInMarketing = null;
    if (button_id === 'q5_optin_yes') optInMarketing = true;
    else if (button_id === 'q5_optin_no') optInMarketing = false;
    else if (OPTIN_YES_PATTERNS.test(text)) optInMarketing = true;
    else if (OPTIN_NO_PATTERNS.test(text)) optInMarketing = false;

    if (optInMarketing === true) {
      return {
        action_type: 'closed_optin_yes',
        message: buildOptInYesResponse(profile_name),
        new_state_name: 'closed',
        opt_in_marketing: true,
        handoff: {
          triggered: true,
          flag: 'closed_opt_in_marketing',
          urgency: 'LOW',
        },
      };
    }
    if (optInMarketing === false) {
      return {
        action_type: 'closed_optin_no',
        message: buildOptInNoResponse(profile_name),
        new_state_name: 'closed',
        opt_in_marketing: false,
        request_data_deletion: true,
        handoff: {
          triggered: true,
          flag: 'closed_opt_out_delete_data',
          urgency: 'LOW',
        },
      };
    }
    // No matcheó — repreguntar
    return {
      action_type: 'send_interactive_buttons',
      message: 'No te entendí bien ☺️ ¿Prefieres recibir promociones ocasionales o eliminar tus datos?',
      buttons: [
        { id: 'q5_optin_yes', title: 'Sí, mantenme' },
        { id: 'q5_optin_no', title: 'No, eliminar' },
      ],
      new_state_name: 'qualifying',
      new_progress: 'q5_optin',
    };
  }

  // RED FLAGS — siempre escalar inmediato, en cualquier state
  const redFlag = detectRedFlag(text);
  if (redFlag) {
    return {
      action_type: 'escalate_red_flag',
      message: buildRedFlagResponse(profile_name, redFlag),
      new_state_name: 'escalated',
      handoff: {
        triggered: true,
        flag: `red_flag_${redFlag}`,
        urgency: 'HIGH',
      },
    };
  }

  // PRICE OBJECTION — en cualquier turno, intercepta + handoff
  if (PRICE_OBJECTION_PATTERNS.test(text)) {
    return {
      action_type: 'price_objection',
      message: buildPriceObjection(profile_name),
      new_state_name: 'escalated',
      handoff: {
        triggered: true,
        flag: 'price_objection',
        urgency: 'MEDIUM',
      },
    };
  }

  // ESCAPE TO HUMAN — lead pide hablar directo con doctora
  if (ESCAPE_TO_HUMAN_PATTERNS.test(text) && stateName !== 'new') {
    return {
      action_type: 'escape_to_human',
      message: buildEscapeToHuman(profile_name),
      new_state_name: 'escalated',
      handoff: {
        triggered: true,
        flag: 'lead_requested_human',
        urgency: 'MEDIUM',
      },
    };
  }

  // === STATE MACHINE ===

  // Estado 'new' → primera interacción
  if (stateName === 'new') {
    // Prioridad detección tratamiento: referral del ad > texto libre del mensaje
    const detectedFromText = detectTreatment(text);
    const initialTreatment = referral_product || detectedFromText;

    if (initialTreatment) {
      // Tratamiento ya conocido → saludo compacto + Q2 directo (un solo mensaje)
      return {
        action_type: 'send_interactive_buttons',
        message: buildGreetingPlusQ2(profile_name, initialTreatment),
        buttons: [
          { id: 'q2_first_time', title: 'Primera vez' },
          { id: 'q2_repeat', title: 'Ya me he hecho' },
          { id: 'q1_other', title: 'Otro tratamiento' },
        ],
        new_state_name: 'qualifying',
        new_progress: 'q2',
        q1_treatment: initialTreatment,
      };
    } else {
      // Vino sin contexto → menú top 3 + otro
      return {
        action_type: 'send_interactive_buttons',
        message: buildGreetingWithoutProduct(profile_name),
        buttons: [
          { id: 'q1_botox', title: 'Botox' },
          { id: 'q1_acido', title: 'Ácido Hialurónico' },
          { id: 'q1_otro', title: 'Otro tratamiento' },
        ],
        new_state_name: 'qualifying',
        new_progress: 'q1',
        q1_treatment_hint: null,
      };
    }
  }

  // Estado 'qualifying' progress=q1 → procesando respuesta a Q1 → Q2
  if (stateName === 'qualifying' && progress === 'q1') {
    // Detectar tratamiento del botón clickeado o del texto libre
    let treatmentKey = null;

    if (button_id) {
      if (button_id.startsWith('q1_yes_')) {
        treatmentKey = button_id.replace('q1_yes_', '');
      } else if (button_id === 'q1_botox') treatmentKey = 'botox';
      else if (button_id === 'q1_acido') treatmentKey = 'acido';
      else if (button_id === 'q1_otro' || button_id === 'q1_other') {
        // Lead quiere otro → handoff con flag
        return {
          action_type: 'handoff_other_treatment',
          message: buildEscapeToHuman(profile_name),
          new_state_name: 'escalated',
          handoff: {
            triggered: true,
            flag: 'wants_other_treatment',
            urgency: 'MEDIUM',
          },
        };
      } else if (button_id === 'q1_question') {
        // Lead tiene duda → Q4 painpoints
        return {
          action_type: 'send_interactive_buttons',
          message: buildQ4InfoTopics(),
          buttons: [
            { id: 'q4_precios', title: 'Precios' },
            { id: 'q4_ubicacion', title: 'Ubicación' },
            { id: 'q4_otro', title: 'Otra duda' },
          ],
          new_state_name: 'qualifying',
          new_progress: 'q4',
        };
      }
    } else {
      // No clickeó botón, parsea texto libre
      treatmentKey = detectTreatment(text);
    }

    if (!treatmentKey) {
      // No pudimos parsear → handoff con flag
      return {
        action_type: 'handoff_unparseable',
        message: buildEscapeToHuman(profile_name),
        new_state_name: 'escalated',
        handoff: {
          triggered: true,
          flag: 'lead_response_unparseable',
          urgency: 'MEDIUM',
        },
      };
    }

    // Tratamiento confirmado → Q2 primera vez
    return {
      action_type: 'send_interactive_buttons',
      message: buildQ2FirstTime(treatmentKey),
      buttons: [
        { id: 'q2_first_time', title: 'Primera vez' },
        { id: 'q2_repeat', title: 'Ya me he hecho' },
      ],
      new_state_name: 'qualifying',
      new_progress: 'q2',
      q1_treatment: treatmentKey,
    };
  }

  // Estado 'qualifying' progress=q2 → procesando respuesta a Q2 → Q3
  if (stateName === 'qualifying' && progress === 'q2') {
    let firstTime = null;
    if (button_id === 'q2_first_time') firstTime = true;
    else if (button_id === 'q2_repeat') firstTime = false;
    else if (/primera\s+vez/i.test(text)) firstTime = true;
    else if (/ya\s+(me\s+he\s+hecho|he\s+(hecho|tenido))/i.test(text)) firstTime = false;

    // Si no pudimos parsear → handoff
    if (firstTime === null) {
      return {
        action_type: 'handoff_q2_unparseable',
        message: buildEscapeToHuman(profile_name),
        new_state_name: 'escalated',
        handoff: {
          triggered: true,
          flag: 'q2_unparseable',
          urgency: 'LOW',
        },
      };
    }

    // → Q3 urgencia
    return {
      action_type: 'send_interactive_buttons',
      message: buildQ3Urgency(),
      buttons: [
        { id: 'q3_asap', title: 'Lo antes posible' },
        { id: 'q3_2_3_weeks', title: 'En 2-3 semanas' },
        { id: 'q3_averiguando', title: 'Averiguando' },
      ],
      new_state_name: 'qualifying',
      new_progress: 'q3',
      q2_first_time: firstTime,
    };
  }

  // Estado 'qualifying' progress=q3 → procesando respuesta a Q3
  if (stateName === 'qualifying' && progress === 'q3') {
    let urgency = null;
    if (button_id === 'q3_asap') urgency = 'asap';
    else if (button_id === 'q3_2_3_weeks') urgency = '2_3_weeks';
    else if (button_id === 'q3_averiguando') urgency = 'just_browsing';
    else if (/antes\s+posible|esta\s+semana|urgente|ya|ya\s+mismo/i.test(text)) urgency = 'asap';
    else if (/2-3\s+semanas|pr[óo]ximas\s+semanas|en\s+(un|una)\s+(mes|semanas)/i.test(text)) urgency = '2_3_weeks';
    else if (/averig|solo\s+(pregunto|pregunta|consult)|info|informaci/i.test(text)) urgency = 'just_browsing';

    // Si lead solo está averiguando → preguntar Q4 painpoints en lugar de cerrar
    if (urgency === 'just_browsing') {
      return {
        action_type: 'send_interactive_buttons',
        message: buildQ4InfoTopics(),
        buttons: [
          { id: 'q4_precios', title: 'Precios' },
          { id: 'q4_ubicacion', title: 'Ubicación' },
          { id: 'q4_otro', title: 'Otra duda' },
        ],
        new_state_name: 'qualifying',
        new_progress: 'q4',
        q3_urgency: urgency,
      };
    }

    // Caso ASAP o 2-3 semanas → cierre + handoff directo (lead listo)
    return {
      action_type: 'close_and_handoff',
      message: buildClosing(profile_name),
      new_state_name: 'escalated',
      q3_urgency: urgency || 'unknown',
      handoff: {
        triggered: true,
        flag: 'qualified_lead',
        urgency: urgency === 'asap' ? 'HIGH' : 'MEDIUM',
      },
    };
  }

  // Estado 'qualifying' progress=q4 → procesando respuesta a Q4 painpoints → CIERRE + HANDOFF
  if (stateName === 'qualifying' && progress === 'q4') {
    let topics = [];
    if (button_id === 'q4_precios') topics = ['precios'];
    else if (button_id === 'q4_ubicacion') topics = ['ubicacion'];
    else if (button_id === 'q4_otro') topics = ['otro'];
    else {
      // texto libre — parseo simple
      const t = (text || '').toLowerCase();
      if (/precio|costo|cu[áa]nto|tarifa|caro/.test(t)) topics.push('precios');
      if (/ubicaci|d[oó]nde|direcci[oó]n|local|consultorio|c[oó]mo\s+llegar/.test(t)) topics.push('ubicacion');
      if (/disponibilidad|horario|cu[áa]ndo\s+(puedo|atienden|atienden)/.test(t)) topics.push('disponibilidad');
      if (/duele|dolor|molest|incomod/.test(t)) topics.push('dolor');
      if (/dura|cu[áa]nto\s+tiempo|resultados|cu[áa]nto\s+vale.*tiempo/.test(t)) topics.push('duracion');
      if (/seguro|peligros|riesgo|efectos|contraindic|embaraz/.test(t)) topics.push('seguridad');
      if (topics.length === 0) topics.push('otro');
    }

    // Cierre + handoff con info topics
    return {
      action_type: 'close_with_info',
      message: buildClosingWithInfo(profile_name, topics.map((t) => ({
        precios: 'precios',
        ubicacion: 'ubicación y horarios',
        disponibilidad: 'disponibilidad',
        dolor: 'dolor y molestias',
        duracion: 'duración y resultados',
        seguridad: 'seguridad',
        otro: 'tu duda',
      }[t] || t))),
      new_state_name: 'escalated',
      info_topics: topics,
      handoff: {
        triggered: true,
        flag: 'qualified_lead_info_request',
        urgency: 'MEDIUM',
      },
    };
  }

  // Gap K — Lead vuelve a escribir post-escalado (state=escalated)
  // En lugar de ignorar: bot responde con saludo cordial + notif a humanos
  // destacando que es LEAD RETURNANTE (no es lead nuevo).
  if (stateName === 'escalated') {
    return {
      action_type: 'lead_returned_handoff',
      message: buildLeadReturnedResponse(profile_name),
      new_state_name: 'escalated', // se mantiene escalated
      handoff: {
        triggered: true,
        flag: 'lead_returned_after_escalation',
        urgency: 'HIGH',
      },
    };
  }
  // state=closed: lead pidió no contactar más → bot NO responde
  if (stateName === 'closed') {
    return {
      action_type: 'no_action',
      reason: 'bot disabled while state=closed (lead opted out previously)',
    };
  }

  // Default — no debe llegar aquí
  return {
    action_type: 'no_action',
    reason: `unknown state: ${stateName}`,
  };
}

// ============================================================================
// BUILD HANDOFF PAYLOADS (Vtiger Lead create + Dario notif)
// ============================================================================

function buildHandoffPayloads(inbound, state, decision) {
  const { phone_e164, profile_name, referral_product, referral_source_id, referral_source_url, referral_headline, text } = inbound;

  // Tratamiento final: prioridad - decision (acabamos de detectarlo) > context_json (state previo) > referral
  // BUG FIX 2026-05-24: state.q1_treatment NO existe top-level, vive en state.context_json.q1_treatment
  const ctx = state?.context_json || {};
  const treatmentKey =
    decision?.q1_treatment || ctx.q1_treatment || referral_product || ctx.referral_product || null;
  const treatmentLabel = treatmentKey ? TREATMENT_LABELS[treatmentKey] : 'Otro / No detectado';

  // Vtiger payload (para A1 webhook → Lead create)
  const vtiger_payload = {
    phone: phone_e164,
    nombre: profile_name || `Lead WA ${phone_e164.slice(-4)}`,
    email: '',
    _source: 'wa-inbound',
    utm_source: referral_source_id ? 'facebook' : 'wa-direct',
    utm_medium: referral_source_id ? 'cpc' : 'organic',
    utm_campaign: referral_source_id || 'wa-direct-may26',
    utm_content: treatmentKey || 'unknown',
    event_id: referral_source_id || inbound.message_id,
    landing_url: referral_source_url || '',
    tratamiento_interes: treatmentLabel,
  };

  // Construir notif a Dario
  const urgencyEmoji = decision.handoff?.urgency === 'HIGH' ? '🔥' : decision.handoff?.urgency === 'MEDIUM' ? '⚡' : '💛';
  const flagLine = decision.handoff?.flag ? `\n⚠️ Flag: ${decision.handoff.flag}` : '';

  const q1 = treatmentKey;
  const q2 = decision?.q2_first_time != null ? decision.q2_first_time : ctx.q2_first_time;
  const q3 = decision?.q3_urgency || ctx.q3_urgency;
  const infoTopics = decision?.info_topics || ctx.info_topics || [];

  const urgencyLabel = {
    asap: 'Lo antes posible (esta semana)',
    '2_3_weeks': 'En 2-3 semanas',
    just_browsing: 'Solo averiguando',
    unknown: 'No respondió',
  }[q3] || 'No respondió';

  const firstTimeLabel = q2 === true ? 'Primera vez' : q2 === false ? 'Ya se ha hecho antes' : 'No respondió';

  const adSourceLine = referral_source_id
    ? `🔗 Ad: "${referral_headline || referral_source_id}"`
    : '🔗 Contacto directo (no via ad)';

  const infoTopicsLabel = {
    precios: 'Precios',
    ubicacion: 'Ubicación / horarios',
    disponibilidad: 'Disponibilidad agenda',
    dolor: 'Dolor / molestias',
    duracion: 'Duración / resultados',
    seguridad: 'Seguridad / contraindicaciones',
    otro: 'Otra duda',
  };
  const infoTopicsLine = infoTopics.length > 0
    ? `\n❓ Dudas que mencionó: ${infoTopics.map((t) => infoTopicsLabel[t] || t).join(', ')}`
    : '';

  const dario_notif_text =
    `${urgencyEmoji} LEAD ${decision.handoff?.flag === 'qualified_lead' ? 'CALIFICADO' : 'NUEVO'} — Livskin\n\n` +
    `👤 ${profile_name || '(sin perfil)'} (${phone_e164})\n` +
    `🎯 Tratamiento: ${treatmentLabel}\n` +
    `🔁 Experiencia previa: ${firstTimeLabel}\n` +
    `⏱️ Urgencia: ${urgencyLabel}` +
    `${infoTopicsLine}\n` +
    `${adSourceLine}${flagLine}\n\n` +
    `💬 Mensaje original:\n"${text || '(botón)'}"\n\n` +
    `👉 wa.me/${phone_e164.replace('+', '')}`;

  // Lista de phones que reciben la notif (sin +, formato Meta API)
  // Dario: control. Doctoras 1 y 2: las que responden al lead.
  const notif_recipients = [
    { name: 'Dario (control)', phone: '51982732978' },
    { name: 'Doctora Claudia (1)', phone: '51910848995' },
    { name: 'Doctora Claudia (2)', phone: '51980727888' },
  ];

  // Template params para doctor_lead_notification_v1 (APPROVED)
  // Body: "Hola Dra. Claudia, llegó un nuevo lead:\n\nNombre: {{1}}\nTeléfono: {{2}}\nTratamiento de interés: {{3}}\nExperiencia previa: {{4}}\nUrgencia: {{5}}\n\nMensaje original del lead:\n\"{{6}}\""
  // Las variables NO pueden tener saltos de linea, asi que aplanamos el texto del mensaje
  const flattenText = (t) => (t || '').replace(/\n+/g, ' ').replace(/\s+/g, ' ').slice(0, 250).trim();

  // Gap K — si lead volvió post-escalado, MARCAR FUERTE en TODAS las variables
  // para que doctora distinga al instante (header del template dice "nuevo lead" hardcoded
  // pero cada line del body grita RETURNANTE)
  const isReturning = decision.handoff?.flag === 'lead_returned_after_escalation';

  const template_params = isReturning ? {
    nombre: `🔄 ${profile_name || `Lead WA ${phone_e164.slice(-4)}`} (YA HABLO ANTES)`,
    telefono: phone_e164,
    tratamiento: `🔄 RETURNANTE — ${treatmentLabel}`,
    experiencia: `🔄 LEAD QUE VOLVIO (ya conversaba antes)`,
    urgencia: `🔄 ALTA — retomar conversacion`,
    mensaje: `🔄 [VOLVIO] ${flattenText(text) || '(sin mensaje)'}`,
  } : {
    nombre: profile_name || `Lead WA ${phone_e164.slice(-4)}`,
    telefono: phone_e164,
    tratamiento: treatmentLabel,
    experiencia: firstTimeLabel,
    urgencia: urgencyLabel,
    mensaje: flattenText(text) || '(sin mensaje)',
  };

  return {
    vtiger_payload,
    dario_notif_text,    // backward-compat (texto libre, legacy)
    dario_phone: '51982732978',  // legacy
    notif_text: dario_notif_text,
    notif_recipients,
    template_params,    // NUEVO: usado por Yossie Master para envio via template doctor_lead_notification_v1
  };
}

// ============================================================================
// MAIN — entry point para n8n Code node
// ============================================================================

function processInbound(webhookBody, stateRow) {
  const inbound = parseInbound(webhookBody);
  if (!inbound) {
    return { action_type: 'no_action', reason: 'no inbound message (probably status callback)' };
  }

  // Bot IGNORA mensajes inbound de los 3 phones internos (Dario + 2 doctora).
  // No crea lead, no responde, no envia notifs. Es solo proteccion contra loops.
  if (isInternalPhone(inbound.phone_e164)) {
    return {
      action_type: 'no_action',
      reason: `internal phone ignored (${inbound.phone_e164})`,
      inbound: { from: inbound.from, phone_e164: inbound.phone_e164, text: inbound.text },
    };
  }

  const decision = decideNextAction(inbound, stateRow);

  // Build context_json mergiendo state previo + decisión nueva
  const prevContext = stateRow?.context_json || {};
  const newContext = {
    progress: decision.new_progress || prevContext.progress || null,
    profile_name: inbound.profile_name || prevContext.profile_name || '',
    q1_treatment: decision.q1_treatment || prevContext.q1_treatment || null,
    q2_first_time:
      decision.q2_first_time != null ? decision.q2_first_time : prevContext.q2_first_time,
    q3_urgency: decision.q3_urgency || prevContext.q3_urgency || null,
    info_topics: decision.info_topics || prevContext.info_topics || [],
    referral_source_id: inbound.referral_source_id || prevContext.referral_source_id || null,
    referral_source_url: inbound.referral_source_url || prevContext.referral_source_url || null,
    referral_headline: inbound.referral_headline || prevContext.referral_headline || null,
    referral_product: inbound.referral_product || prevContext.referral_product || null,
    // followup_sent: si decision pide reset (snooze 24h) -> false, sino mantener
    followup_sent: decision.reset_followup_sent ? false : (prevContext.followup_sent || false),
    // snoozed_until: tras "Más tarde respondo" — F1 NO debe reenviar antes de esta fecha
    snoozed_until: decision.snoozed_until || prevContext.snoozed_until || null,
    // opt_in_marketing: respuesta del lead a Q5 (true=acepta promos, false=pide eliminacion)
    opt_in_marketing: decision.opt_in_marketing != null ? decision.opt_in_marketing : prevContext.opt_in_marketing,
    // request_data_deletion: bandera para que ops elimine datos PII de este lead
    request_data_deletion: decision.request_data_deletion === true ? true : prevContext.request_data_deletion,
  };

  const result = {
    inbound,
    decision,
    new_state: {
      phone_lead: inbound.phone_e164,
      state: decision.new_state_name || stateRow?.state || 'new',
      last_intent: newContext.q1_treatment,
      context_json: newContext,
      last_inbound_text: inbound.text || '',
      escalation_reason: decision.handoff?.flag || null,
      escalation_to: decision.handoff?.triggered ? 'dario' : null,
    },
  };

  // Si hay handoff triggered, construye payloads
  if (decision.handoff?.triggered) {
    result.handoff_payloads = buildHandoffPayloads(inbound, stateRow, decision);
  }

  // Si hay respuesta a enviar, construye WA payload
  if (decision.action_type !== 'no_action' && decision.message) {
    if (decision.buttons) {
      result.wa_outbound = buildInteractiveButtons(
        inbound.phone_e164,
        decision.message,
        decision.buttons,
      );
    } else {
      result.wa_outbound = buildTextMessage(inbound.phone_e164, decision.message);
    }
  }

  return result;
}

// Export para n8n Code node (return `processInbound(...)`)
// En n8n: const result = processInbound($input.first().json.body, $('Get State').first().json);
//         return [{ json: result }];

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    processInbound,
    parseInbound,
    decideNextAction,
    buildHandoffPayloads,
    detectTreatment,
    detectRedFlag,
    TREATMENT_LABELS,
  };
}
