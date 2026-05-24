/**
 * Yossie Responder — Tool Dispatcher inline para n8n D1.
 *
 * Recibe: {parsed, cliente, conv_state, referral, original_text}
 * Devuelve: {action_type, response_text, audit_reason, metadata}
 *
 * Doctrina #11: scoring 100% determinístico, NO IA fallback.
 * Sin IA: confidence <0.5 escala a humano.
 *
 * Copy base: docs/brand/voice-v1.md + painpoints-responses.md + catalogo-tratamientos.md
 *
 * Sincronizado con: infra/n8n/lib/wa_parser.js
 */

// ============================================================
// PATTERNS DE DETECCIÓN
// ============================================================

const REFERRAL_PRODUCT_PATTERNS = {
  botox: /\b(botox|toxina|arrugas|expresi[óo]n|tercio)\b/i,
  acido: /(\b(acido|[áa]cido)\s+(hialuronico|hialur[óo]nico)\b)|\bhialur[óo]nico\b|\brinomodelaci[óo]n\b|\bpomulos\b|\blabios\b/i,
  prp: /\b(prp|plasma|plaquetas)\b/i,
  limpieza: /(limpieza\s+facial|facial\s+profunda)/i,
};

const RED_FLAG_PATTERNS = {
  aggressive_negotiation: /\b(reg[áa]l[ao]me?|gratis|invita\s+la\s+casa|b[áa]j[au][lm]e|h[áa]z[mt]e\s+un\s+gran\s+descuento|si\s+no\s+me\s+bajas?|m[áa]s\s+barato\s+que)\b/i,
  competitor_aggressive: /\ben\s+(munay|beysa|valderma).*(mejor|m[áa]s\s+barato)/i,
  serial_canceller: null,  // requires conv history check
  impossible_expectations: /\b(borrar\s+(todas?\s+)?mis?\s+arrugas|c[áa]mbiame\s+la\s+cara|garantizado\s+100|sin\s+ning[úu]n\s+riesgo)\b/i,
  contraindication: /\b(embaraz|gestaci[óo]n|c[áa]ncer|lupus|autoinmune|alergi[ac]\s+grave|lactancia|amamantando|antibi[óo]tic[ao]|anticoagulant|warfarina)\b/i,
  aggressive_language: /\b(idiota|est[úu]pid[oa]|imb[éé]cil|tonta|estafa|fraude|tramposo|ladron|chamuyero)\b/i,
};

const PAINPOINT_PATTERNS = {
  miedo_dolor: /\b(duele|dolor|me\s+va\s+a\s+doler|sufre|sufrir|me\s+arde|adormecimiento|anestesia)\b/i,
  miedo_cambio: /\b(cambiar?\s+la?\s+(rostro|cara)|que\s+me\s+cambies?|me\s+va\s+a\s+cambiar|raro|congelad[ao]|aparecer\s+congelad|gestos|expresi[óo]n\s+rara|natural)\b/i,
  precio_alto: /\b(caro|costoso|muy\s+alto|por\s+el\s+precio|fuera\s+de\s+mi\s+presupuesto|no\s+me\s+alcanza)\b/i,
  desconfianza: /\b(profesional|colegiada|t[íi]tulo|estafa|seguro|certificad|m[ée]dica?\s+real)\b/i,
  inseguridad_social: /\b(pareja\s+note|esposo|que\s+digan|que\s+dir[áa]n|amigas?\s+sepan|familia\s+sepa|verguenza|qu[ée]\s+pensar[áa]n)\b/i,
  timing_edad: /\b(muy\s+joven|muy\s+vieja|edad\s+correcta|mi\s+edad|temprano|tard[ée]?)\b/i,
  falta_tiempo: /\b(no\s+tengo\s+tiempo|trabajo\s+todo|horario|fin\s+de\s+semana|domingo|noche|temprano|fuera\s+de\s+horario)\b/i,
  comparacion: /\b(otra\s+cl[íi]nica|cobran\s+menos|en\s+\w+\s+(es|sale|cobra)\s+m[áa]s\s+barato|vi\s+en\s+internet)\b/i,
  distancia: /\b(vivo\s+en|lejos|viene\s+de|distancia|viajar?|desde\s+lima|desde\s+arequipa|desde\s+afuera)\b/i,
  cuotas: /\b(cr[ée]dito|cuotas|partes|tarjeta\s+cr[ée]dito|pagar\s+despu[ée]s|financiamient)\b/i,
  no_sabe: /\b(no\s+s[ée]\s+qu[ée]|qu[ée]\s+me\s+recomiendas?|cu[áa]l\s+me\s+conviene|qu[ée]\s+necesito|qu[ée]\s+tratamiento|qu[ée]\s+es\s+mejor)\b/i,
  primera_vez: /\b(primera\s+vez|nunca\s+me\s+he\s+hecho|primer\s+tratamiento|nunca\s+he\s+probad)\b/i,
};

// ============================================================
// COPY REAL (extraído de docs/brand/)
// ============================================================

const COPY = {
  greeting_lead_nuevo_botox: (name, refPrice) =>
    `Hola${name ? ' ' + name : ''} ☺️ Gracias por escribirnos a Livskin.

Soy Yossie, asistente de la Dra. Claudia Delgado.

Te aclaro los precios del Botox:
• S/250 por zona individual (frente, entrecejo, patas de gallo, etc.)
• S/700 tratamiento FULL FACE (todas las zonas — tercio superior + medio + inferior)

La Dra. evalúa qué zonas trabajar según tu caso en la consulta gratuita (30 min, sin compromiso).

¿Quieres agendar?`,

  greeting_lead_nuevo_acido: (name) =>
    `Hola${name ? ' ' + name : ''} ☺️ Gracias por escribirnos a Livskin.

Soy Yossie, asistente de la Dra. Claudia Delgado.

Vi que te interesa el Ácido Hialurónico — sirve para rinomodelación, ojeras, pómulos, labios o mentón. Da volumen, modela y los resultados son inmediatos. Dura 18-24 meses.

El precio se cotiza solo en consulta porque depende de la cantidad de producto. La consulta es gratuita.

¿Agendamos?`,

  greeting_lead_nuevo_prp: (name) =>
    `Hola${name ? ' ' + name : ''} ☺️ Gracias por escribirnos a Livskin.

Soy Yossie, asistente de la Dra. Claudia Delgado.

El PRP (Plasma Rico en Plaquetas) usa tu propia sangre para regenerar la piel. Mejora calidad, grosor, textura.

S/200 solo infiltrado, S/220-250 con Dermapen (microagujas). Son 3 sesiones, una cada mes.

¿Quieres agendar consulta gratuita para evaluar tu caso?`,

  greeting_lead_nuevo_limpieza: (name) =>
    `Hola${name ? ' ' + name : ''} ☺️ Gracias por escribirnos a Livskin.

Soy Yossie, asistente de la Dra. Claudia Delgado.

La Limpieza Facial Profunda parte desde S/70 (básica) hasta S/120 (premium). Dura 45-60 min, sin recuperación, recomendada cada 3-4 semanas.

Es ideal para conocer a la Dra. y mantener tu piel limpia + radiante.

¿Agendamos?`,

  greeting_lead_nuevo_default: (name) =>
    `Hola${name ? ' ' + name : ''} ☺️ Gracias por escribirnos a Livskin.

Soy Yossie, asistente de la Dra. Claudia Delgado.

La Dra. es Médico Cirujano colegiada (CMP 091029) con 10+ años de experiencia en Cusco. Trabaja con cada paciente individualmente, sin protocolos estándar.

¿Qué tratamiento te interesa? Tenemos Botox, Ácido Hialurónico, PRP, Esperma de Salmón, Hilos, Limpieza Facial y más. La consulta es gratuita.`,

  greeting_recurrente: (name) =>
    `Hola${name ? ' ' + name : ''} ☺️ Qué bueno saber de ti.
¿En qué te ayudo?`,

  // Painpoint responses (literales de la doctora)
  painpoint_miedo_dolor:
    `Todo duele un poquito ☺️
Pero los resultados valen la pena — la Dra. usa técnicas suaves y para Botox aplica anestesia local cuando es necesario.

¿Quieres agendar consulta para que te explique mejor según tu caso?`,

  painpoint_miedo_cambio:
    `Esta es una pregunta clave para la Dra. ☺️

Su filosofía es exactamente lo opuesto a "cambiar el rostro": trabaja sobre TUS facciones, devolviendo lo que tenías antes. No cambia estructura, no bloquea gestos.

De hecho, la Dra. usa sus propios productos — ella misma es ejemplo de resultados naturales.

¿Te gustaría conocerla en una consulta gratuita?`,

  painpoint_precio_alto:
    `Sí, los productos médicos certificados tienen un costo ☺️

La Dra. usa marcas como Reach (Botox) y Yvoire (Ácido Hialurónico) — puedes verificar precios online si quieres comparar.

También hay versiones más económicas que te puede ofrecer en consulta — no tienen exactamente el mismo resultado pero pueden funcionar para tu caso. Lo evalúan juntas.`,

  painpoint_desconfianza:
    `Totalmente válida la pregunta ☺️

La Dra. Claudia Delgado es Médico Cirujano colegiada — CMP 091029. Actualmente cursa la Maestría en Medicina Estética en la Universidad Científica del Sur.

10+ años de experiencia, formación intensiva en Argentina (con Dra. Débora Amad), USA y Colombia.

Si quieres, te puedo enviar certificados específicos del tratamiento que te interesa.`,

  painpoint_inseguridad_social:
    `Mira, los varones casi nunca notan nada ☺️
Y si lo notan, tienes suerte.

La filosofía de la Dra. es justo esa — que el cambio se vea natural, sin que parezca que te hiciste algo. Trabaja sobre tus propias facciones para que el resultado sea sutil.

A las amigas sí puede llamar la atención, pero más como "te ves descansada" que "te hiciste algo".`,

  painpoint_timing_edad:
    `La edad ideal depende mucho de tu genética y de cómo gesticulas ☺️

Cada persona envejece distinto — algunas marcan más la frente, otras los ojos, otras el contorno. La Dra. lo evalúa caso por caso.

¿Quieres que la Dra. te haga una evaluación gratuita en consulta?`,

  painpoint_falta_tiempo:
    `La Dra. tiene flexibilidad horaria ☺️

Atiende desde temprano (5-6 am si es necesario) hasta tarde (8-9 pm), incluso domingos previa coordinación.

¿Qué horario te queda mejor? Coordino con ella y te confirmo.`,

  painpoint_comparacion:
    `Cada clínica tiene sus propios productos y precios ☺️

Lo que cambia entre clínicas es: la marca del producto, los años de experiencia de quien lo aplica, y el seguimiento post-tratamiento.

La Dra. Claudia usa marcas médicas certificadas (Reach, Yvoire). Si quieres, la Dra. puede ajustar entre S/20-30 según tu caso (ya lo decide ella en consulta).`,

  painpoint_distancia:
    `La Dra. tiene consideraciones especiales para pacientes que vienen de lejos ☺️

Puede agendar horarios que te acomoden — incluso temprano o tarde, fin de semana, o concentrar varios tratamientos en una sola visita si lo necesitas.

¿De dónde vienes?`,

  painpoint_cuotas:
    `Por ahora el pago es al momento del tratamiento ☺️

Aceptamos Yape, Plin, transferencia y efectivo.

Si te vuelves cliente recurrente y la Dra. te conoce bien, en el futuro puede manejar crédito caso por caso.`,

  painpoint_no_sabe:
    `Entendido ☺️

Para eso es la consulta gratuita — la Dra. evalúa tu caso específico y te recomienda qué tratamientos van mejor con lo que buscas. Dura 30 minutos.

Sin compromiso, sin presión. ¿Quieres agendar?`,

  painpoint_primera_vez:
    `Bienvenida ✨ Es totalmente normal tener dudas si es primera vez.

La Dra. tiene 10+ años de experiencia trabajando con pacientes primerizos. Te explica todo en detalle antes de cualquier decisión.

La consulta es gratuita — sin compromiso de hacer nada ese día. Solo conversar y que tengas info clara.

¿Agendamos?`,

  // Escalations
  escalate_contraindication: (name) =>
    `${name ? name : 'Hola'} ☺️ Este caso lo evalúa directamente la Dra. Claudia.

Cada condición médica requiere análisis individual — algunos tratamientos pueden hacerse con precauciones, otros no.

Le paso tu consulta y te responde apenas pueda. ¿Te parece?`,

  escalate_red_flag: (name) =>
    `${name ? name : ''} ☺️ Te paso con la Dra. Claudia para que coordine directamente contigo.

Te responde en breve.`,

  escalate_ask_human: (name) =>
    `Por supuesto ☺️ Le paso a la Dra. Claudia el contexto y te responde apenas pueda.

Mientras tanto, si quieres adelantarme algo sobre lo que buscas, lo anoto para ella.`,

  escalate_low_confidence: (name) =>
    `${name ? name : ''} ☺️ Para responderte bien esto, te paso directo con la Dra.

Te responde apenas pueda.`,

  // Common
  ask_human_acknowledge:
    `Claro ☺️ Le paso a la Dra. Claudia que vea tu mensaje y te responda directamente.

Mientras tanto, ¿quieres adelantarme algo sobre lo que buscas?`,

  agenda_request_response:
    `La Dra. Claudia atiende previa coordinación con flexibilidad ☺️

Cuéntame qué día y horario te queda mejor — temprano, tarde, fin de semana — y coordino con ella.

📍 Wanchaq, Cusco (Urbanización La Florida O-7)`,

  confirm_acknowledged: (name) =>
    `${name ? 'Listo ' + name : 'Listo'} ☺️
Le paso a la Dra. y te confirmo el horario exacto en breve.`,

  reject_acknowledge:
    `Oki, entendido ☺️
Si más adelante quieres conversar, aquí estoy. Estamos en contacto.`,

  reschedule_request:
    `Tranquila ☺️ ¿Cuándo te queda mejor? La Dra. tiene flexibilidad — temprano, tarde, fin de semana, no hay problema.`,

  cancel_acknowledge:
    `Oki, entendido ☺️
Si más adelante quieres volver a agendar, aquí estoy. Estamos en contacto.`,

  // Operation info
  info_direccion:
    `📍 Estamos en Urbanización La Florida O-7, Wanchaq, Cusco.

Detrás del templo de los Mormones, media cuadra encima.

Hay parking gratis frente al consultorio ☺️`,

  info_pagos:
    `Aceptamos Yape, Plin, transferencia y efectivo ☺️

El pago es al momento del tratamiento.`,

  info_horario:
    `La Dra. atiende previa coordinación con flexibilidad — desde temprano hasta tarde, incluso domingos.

¿Qué día y horario te queda mejor?`,

  // Fallback default cuando intent="unknown" pero NO confianza baja
  default_helpful:
    `Cuéntame un poquito más sobre qué buscas ☺️

¿Es para suavizar líneas, dar volumen, mejorar luminosidad o textura, o algo específico que has notado? Con eso te oriento mejor.`,
};

// ============================================================
// MAIN DISPATCHER
// ============================================================

function detectProductFromText(text) {
  if (!text) return null;
  for (const [product, re] of Object.entries(REFERRAL_PRODUCT_PATTERNS)) {
    if (re.test(text)) return product;
  }
  return null;
}

function extractRefPrice(text) {
  if (!text) return null;
  const m = text.match(/S\/\s*(\d{2,4})/);
  return m ? m[1] : null;
}

function detectRedFlag(text) {
  for (const [tag, re] of Object.entries(RED_FLAG_PATTERNS)) {
    if (re && re.test(text)) return tag;
  }
  return null;
}

function detectPainpoint(text) {
  for (const [tag, re] of Object.entries(PAINPOINT_PATTERNS)) {
    if (re.test(text)) return tag;
  }
  return null;
}

function detectInfoQuery(text) {
  const t = (text || '').toLowerCase();
  if (/(direcci[óo]n|d[óo]nde\s+(est[áa]n|queda|los?\s+encuent)|ubicaci[óo]n|c[óo]mo\s+llegar)/i.test(t)) return 'direccion';
  if (/(pago|forma\s+de\s+pago|yape|plin|tarjeta|efectivo|transferencia)/i.test(t)) return 'pagos';
  if (/(horario|cu[áa]ndo\s+atienden|atienden\s+los\s+(domingos?|s[áa]bados?))/i.test(t)) return 'horario';
  return null;
}

/**
 * Main dispatch function.
 * @param {object} ctx - {parsed, cliente, conv_state, referral, original_text, from}
 * @returns {object} {action_type, response_text, audit_reason, metadata}
 */
function dispatch(ctx) {
  const { parsed, cliente, conv_state, referral, original_text, from } = ctx;
  const text = original_text || '';
  const name = cliente?.primer_nombre || cliente?.nombre?.split(' ')[0] || '';
  const is_recurrente = cliente && (cliente.ventas_historicas || 0) >= 1;
  const is_first_msg_in_conv = !conv_state || conv_state.message_count === 0;

  // === Detección de producto del referral (Click-to-WhatsApp) ===
  let product = null;
  let ref_price = null;
  if (referral) {
    product = detectProductFromText(referral.headline + ' ' + (referral.body || ''));
    ref_price = extractRefPrice(referral.headline + ' ' + (referral.body || ''));
  }
  if (!product) {
    product = detectProductFromText(text);
  }

  // === 1. RED FLAG (prioridad máxima) ===
  const redFlag = detectRedFlag(text);
  if (redFlag === 'contraindication') {
    return {
      action_type: 'escalate_contraindication',
      response_text: COPY.escalate_contraindication(name),
      audit_reason: 'contraindication_medical',
      metadata: { red_flag: redFlag, product },
      escalate: true,
    };
  }
  if (redFlag) {
    return {
      action_type: 'escalate_red_flag',
      response_text: COPY.escalate_red_flag(name),
      audit_reason: `red_flag_${redFlag}`,
      metadata: { red_flag: redFlag, product },
      escalate: true,
    };
  }

  // === 2. Ask human ===
  if (parsed.intent === 'ask_human') {
    return {
      action_type: 'escalate_ask_human',
      response_text: COPY.escalate_ask_human(name),
      audit_reason: 'user_requested_human',
      metadata: { product },
      escalate: true,
    };
  }

  // === 3. Greeting (first message) ===
  if (is_first_msg_in_conv && (parsed.intent === 'greeting' || parsed.intent === 'unknown' || parsed.intent === 'ask_info')) {
    if (is_recurrente) {
      return {
        action_type: 'greeting_recurrente',
        response_text: COPY.greeting_recurrente(name),
        audit_reason: 'greeting_recurrente_match',
        metadata: { product, is_recurrente: true },
      };
    }
    // Lead nuevo — copy por producto
    let copy;
    if (product === 'botox') copy = COPY.greeting_lead_nuevo_botox(name, ref_price);
    else if (product === 'acido') copy = COPY.greeting_lead_nuevo_acido(name);
    else if (product === 'prp') copy = COPY.greeting_lead_nuevo_prp(name);
    else if (product === 'limpieza') copy = COPY.greeting_lead_nuevo_limpieza(name);
    else copy = COPY.greeting_lead_nuevo_default(name);

    return {
      action_type: 'greeting_lead_nuevo',
      response_text: copy,
      audit_reason: `greeting_lead_nuevo_${product || 'default'}`,
      metadata: { product, ref_price, referral_source: referral?.source_id },
    };
  }

  // === 4. Confirmación cita (intent=confirm) ===
  if (parsed.intent === 'confirm') {
    return {
      action_type: 'confirm_acknowledged',
      response_text: COPY.confirm_acknowledged(name),
      audit_reason: 'lead_confirmed_intent',
      metadata: { dates: parsed.dates },
      escalate: parsed.dates.length > 0,  // Si propone fecha + confirma, escalar a doctora para validar
    };
  }

  // === 5. Reject / Cancel ===
  if (parsed.intent === 'reject') {
    return {
      action_type: 'reject_acknowledge',
      response_text: COPY.reject_acknowledge,
      audit_reason: 'lead_rejected',
      metadata: {},
    };
  }
  if (parsed.intent === 'cancel') {
    return {
      action_type: 'cancel_acknowledge',
      response_text: COPY.cancel_acknowledge,
      audit_reason: 'lead_cancelled',
      metadata: {},
      escalate: true,
    };
  }
  if (parsed.intent === 'reschedule') {
    return {
      action_type: 'reschedule_request',
      response_text: COPY.reschedule_request,
      audit_reason: 'lead_reschedule',
      metadata: {},
      escalate: true,
    };
  }

  // === 6. Propose date ===
  if (parsed.intent === 'propose_date') {
    return {
      action_type: 'propose_date_relay',
      response_text: COPY.confirm_acknowledged(name) + '\n\n' + (parsed.dates.length > 0 ? `Anoté: ${parsed.dates[0].raw}.` : ''),
      audit_reason: 'lead_proposed_date',
      metadata: { dates: parsed.dates },
      escalate: true,
    };
  }

  // === 7. Painpoint detection ===
  const painpoint = detectPainpoint(text);
  if (painpoint) {
    const key = `painpoint_${painpoint}`;
    if (COPY[key]) {
      return {
        action_type: key,
        response_text: typeof COPY[key] === 'function' ? COPY[key](name) : COPY[key],
        audit_reason: `painpoint_${painpoint}`,
        metadata: { painpoint, product },
      };
    }
  }

  // === 8. Ask price ===
  if (parsed.intent === 'ask_price') {
    // Si tenemos producto del referral, usar copy específico
    if (product === 'botox') return { action_type: 'price_botox', response_text: `Los precios del Botox son ☺️\n\n• S/250 por zona individual\n• S/700 tratamiento FULL FACE (todas las zonas)\n\nLa Dra. evalúa qué zonas trabajar según tu caso en la consulta gratuita.\n\n¿Quieres agendar?`, audit_reason: 'ask_price_botox', metadata: { product } };
    if (product === 'acido') return { action_type: 'price_acido', response_text: `El Ácido Hialurónico se cotiza solo en consulta ☺️\n\nEs porque el precio depende mucho de la cantidad de producto que cada persona necesita.\n\nLa consulta con la Dra. es gratuita y dura 30 min. ¿Agendamos?`, audit_reason: 'ask_price_acido', metadata: { product } };
    if (product === 'prp') return { action_type: 'price_prp', response_text: `El PRP está en S/200 (solo infiltrado) o S/250 con Dermapen (microagujas) ☺️\n\nSon 3 sesiones, una cada mes.\n\n¿Te gustaría agendar consulta gratuita?`, audit_reason: 'ask_price_prp', metadata: { product } };
    if (product === 'limpieza') return { action_type: 'price_limpieza', response_text: `La Limpieza Facial parte desde S/70 (básica) hasta S/120 (premium) ☺️\n\nDura 45-60 min, recomendada cada 3-4 semanas.\n\n¿Agendamos?`, audit_reason: 'ask_price_limpieza', metadata: { product } };
    // Default
    return {
      action_type: 'ask_price_default',
      response_text: `Te cuento los rangos ☺️\n\n• Botox: S/250 por zona / S/700 full face\n• Ácido Hialurónico: solo en consulta (depende cantidad)\n• PRP: S/200-250\n• Limpieza Facial: S/70-120\n• Esperma de Salmón: S/250-500\n• Exosomas: S/250-600\n\nLa consulta con la Dra. es gratuita. ¿Quieres conocer alguno en detalle?`,
      audit_reason: 'ask_price_default',
      metadata: { product: null },
    };
  }

  // === 9. Info queries (dirección/pagos/horario) ===
  const infoType = detectInfoQuery(text);
  if (infoType === 'direccion') return { action_type: 'info_direccion', response_text: COPY.info_direccion, audit_reason: 'info_direccion', metadata: {} };
  if (infoType === 'pagos') return { action_type: 'info_pagos', response_text: COPY.info_pagos, audit_reason: 'info_pagos', metadata: {} };
  if (infoType === 'horario') return { action_type: 'info_horario', response_text: COPY.info_horario, audit_reason: 'info_horario', metadata: {} };

  // === 10. Low confidence → escalate ===
  if (parsed.confidence < 0.5) {
    return {
      action_type: 'escalate_low_confidence',
      response_text: COPY.escalate_low_confidence(name),
      audit_reason: 'confidence_low',
      metadata: { confidence: parsed.confidence, intent: parsed.intent },
      escalate: true,
    };
  }

  // === 11. Default fallback (intent="unknown" but conf >= 0.5 — rare) ===
  return {
    action_type: 'default_helpful',
    response_text: COPY.default_helpful,
    audit_reason: 'default_fallback',
    metadata: { intent: parsed.intent, confidence: parsed.confidence },
  };
}

// Export for use in n8n Code node (Inline copy approach)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { dispatch, COPY, REFERRAL_PRODUCT_PATTERNS, RED_FLAG_PATTERNS, PAINPOINT_PATTERNS };
}
