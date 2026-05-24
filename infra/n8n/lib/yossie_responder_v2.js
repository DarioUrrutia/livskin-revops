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
  return `Hola${safeName} ☺️\n\nSoy Yossie, asistente de la Dra. Claudia Delgado en Livskin Cusco.\n\nLa Dra. es Médico Cirujano colegiada (CMP 091029) con más de 10 años atendiendo en Cusco.\n\nVi que llegas por nuestro anuncio de ${treatment}. ¿Es ese tratamiento el que te interesa, o tienes otra duda?`;
}

function buildGreetingWithoutProduct(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Hola${safeName} ☺️\n\nSoy Yossie, asistente de la Dra. Claudia Delgado en Livskin Cusco.\n\nLa Dra. es Médico Cirujano colegiada (CMP 091029) con más de 10 años atendiendo en Cusco.\n\n¿En qué tratamiento te puedo orientar?`;
}

function buildQ2FirstTime(treatmentKey) {
  const treatment = TREATMENT_LABELS[treatmentKey] || 'este tratamiento';
  return `${treatment} es uno de nuestros tratamientos más pedidos ☺️\n\nCuéntame: ¿es tu primera vez con este tipo de tratamiento, o ya te has hecho antes?`;
}

function buildQ3Urgency() {
  return `Gracias. Una última cosa: ¿cuándo te gustaría empezar?`;
}

function buildClosing(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Listo${safeName} ✨\n\nLe paso ahora tu información a la Dra. Claudia. Ella revisa cada caso personalmente porque cada paciente es distinto.\n\n📍 Estamos en Urb. La Florida O-7, Wanchaq, Cusco\n(Detrás del templo de los Mormones, media cuadra arriba)\n\nApenas la Dra. revise tu info, te escribe por aquí mismo ☺️`;
}

function buildQ4InfoTopics() {
  return `¿Qué te gustaría saber? Cuéntame y le paso toda la info a la Dra. para que te explique mejor.`;
}

function buildClosingWithInfo(name, topics) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  const topicsList = (topics || []).join(', ');
  return `Gracias${safeName} ✨\n\nLe paso a la Dra. Claudia tus inquietudes${topicsList ? ` sobre ${topicsList}` : ''} para que te responda con todo el detalle.\n\n📍 Estamos en Urb. La Florida O-7, Wanchaq, Cusco\n(Detrás del templo de los Mormones, media cuadra arriba)\n\nTe escribe por aquí mismo en breve ☺️`;
}

function buildPriceObjection(name) {
  const safeName = name && name.trim() ? `${name.trim()}, ` : '';
  return `${safeName}los precios varían según la zona, cantidad de producto necesaria y profundidad del tratamiento — cada caso es distinto.\n\nLe paso ahora mismo tus inquietudes a la Dra. Claudia para que pueda explicarte mejor y darte un estimado preciso. Te responde en breve ☺️`;
}

function buildEscapeToHuman(name) {
  const safeName = name && name.trim() ? ` ${name.trim()}` : '';
  return `Por supuesto${safeName} ☺️ La Dra. te escribe en breve.`;
}

function buildRedFlagResponse(name, flagType) {
  const safeName = name && name.trim() ? `${name.trim()}, ` : '';
  return `${safeName}gracias por contarme. Este tipo de caso la Dra. Claudia lo revisa personalmente antes de cualquier paso. Le paso tu info ahora mismo y te responde en breve ☺️`;
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
      // Tratamiento ya conocido → saltar directo a Q2 (primera vez vs experiencia)
      // Pero saludamos primero con confirmación implícita
      return {
        action_type: 'send_interactive_buttons',
        message:
          buildGreetingWithProduct(profile_name, initialTreatment) +
          '\n\n' +
          buildQ2FirstTime(initialTreatment),
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

  // Estado 'escalated' o 'closed' → bot NO responde (humano takes over)
  if (stateName === 'escalated' || stateName === 'closed') {
    return {
      action_type: 'no_action',
      reason: `bot disabled while state=${stateName}`,
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

  return {
    vtiger_payload,
    dario_notif_text,
    dario_phone: '51982732978', // Sin + por Meta API
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
    followup_sent: prevContext.followup_sent || false,
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
