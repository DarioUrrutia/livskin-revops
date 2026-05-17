/**
 * wa_parser.js — Parser texto libre WhatsApp para bot-broker Livskin (Fase 4A.3)
 *
 * Detecta intent + fechas/horas propuestas por el lead en texto libre.
 * Usado en n8n Code nodes (workflows D1/D2). NO depende de Claude API.
 * Determinístico — regex + reglas, sin IA.
 *
 * Inputs:
 *   text: string del mensaje inbound del lead (puede ser cualquier idioma/casing/typo)
 *   now: Date opcional (default new Date()) — útil para tests reproducibles
 *   tz_offset_hours: opcional (default -5, Lima/Cusco) — usado para resolver "mañana 4pm" relativo
 *
 * Output:
 *   {
 *     intent: 'propose_date' | 'confirm' | 'reject' | 'ask_price' | 'ask_human'
 *           | 'ask_info' | 'greeting' | 'cancel' | 'reschedule' | 'unknown',
 *     dates: [{ iso, raw, confidence }],  // array vacío si no hay fechas
 *     confidence: 0-1,                     // confianza global del intent
 *     keywords_matched: ['precio', 'agendar', ...],  // debug
 *   }
 *
 * Doctrina: Sprint 2 bot-broker rule-based. Si confidence < 0.5 o intent=unknown,
 * el workflow debería escalar a humano (no responder mal).
 */

// ───────────── Diccionarios ─────────────

const DAYS_OF_WEEK = {
  domingo: 0, dom: 0,
  lunes: 1, lun: 1,
  martes: 2, mar: 2,
  miercoles: 3, miércoles: 3, mie: 3, mié: 3, mier: 3,
  jueves: 4, jue: 4,
  viernes: 5, vie: 5,
  sabado: 6, sábado: 6, sab: 6, sáb: 6,
};

const MONTHS = {
  enero: 1, ene: 1,
  febrero: 2, feb: 2,
  marzo: 3, mar: 3,
  abril: 4, abr: 4,
  mayo: 5, may: 5,
  junio: 6, jun: 6,
  julio: 7, jul: 7,
  agosto: 8, ago: 8,
  septiembre: 9, sep: 9, septiembre: 9, set: 9,
  octubre: 10, oct: 10,
  noviembre: 11, nov: 11,
  diciembre: 12, dic: 12,
};

// Patrones de intent (regex case-insensitive)
const INTENT_PATTERNS = {
  // confirm: palabras de confirmación, opcionalmente con coma o conector + intensificador
  confirm: /^\s*(s[ií]+|ok+|dale|perfecto|confirmo|listo|de\s*acuerdo|me\s*sirve|est[áa]\s*bien|esta\s*perfect|👍|✅)([\s,.!]+(perfecto|listo|claro|excelente|genial|👍|✅))*\s*[.!]*\s*$/i,
  reject: /^\s*(no|no\s*me\s*sirve|no\s*puedo|no\s*podr[ée]|no\s*podemos|❌)\s*[.!]*\s*$/i,
  ask_price: /(cu[áa]nto|precio|costo|cuesta|tarifa|cobr[áa]n|paga[mr]|valor)\b/i,
  // ask_human: cubre "hablar con", "hablar con la", "hablar contigo", "atenderme", "llamarme", etc.
  ask_human: /(hablar\s+(con(\s+la|\s+el)?|al?)\s+(doctora?|m[eé]dica?|humana?|alguien|persona|ti|ud|usted)|atenderme|que\s+me\s+atienda|llam[aoe]r(me)?|tel[eé]fono|hablar\s+contigo|hablar\s+por\s+telefono)/i,
  ask_info: /(qu[ée]\s+es|c[oó]mo\s+(funciona|es|hace)|info|informaci[oó]n|me\s+puede[sn]?\s+(decir|contar|explicar)|necesito\s+saber)/i,
  greeting: /^\s*(hola|buenas|buen\s*d[ií]a|buenas\s*tardes|buenas\s*noches|saludos|hi|hello)\b/i,
  cancel: /(cancel[aoe]r|anul[aoe]r|ya\s*no\s*quiero|no\s*ir[ée]|no\s*podr[ée]\s*ir)\b/i,
  reschedule: /(reagend[aoe]r|reprogram[aoe]r|cambi[aoe]r\s+(fecha|d[ií]a|hora)|otra\s*fecha|otro\s*d[ií]a)\b/i,
};

// ───────────── Helpers internos ─────────────

function normalize(text) {
  if (typeof text !== 'string') return '';
  return text.trim().toLowerCase();
}

function stripAccents(s) {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '');
}

// Pasa una fecha JS Date a ISO con tz offset Peru (-05:00).
// No usamos toLocaleString para evitar dependencia del runtime locale.
function isoLocalPeru(date) {
  // date ya es UTC; necesitamos ofsetear -5h y formatear con offset explícito
  const peru = new Date(date.getTime() - 5 * 60 * 60 * 1000);
  const y = peru.getUTCFullYear();
  const mo = String(peru.getUTCMonth() + 1).padStart(2, '0');
  const d = String(peru.getUTCDate()).padStart(2, '0');
  const h = String(peru.getUTCHours()).padStart(2, '0');
  const mi = String(peru.getUTCMinutes()).padStart(2, '0');
  return `${y}-${mo}-${d}T${h}:${mi}:00-05:00`;
}

// Calcula próximo día de la semana desde "now". Si hoy es lunes y se pide "lunes", devuelve PRÓXIMO lunes (no hoy).
function nextDayOfWeek(now, targetDow) {
  const date = new Date(now);
  // Peru offset: corremos +5h para que getUTCDay refleje día Peru
  const peruDate = new Date(date.getTime() - 5 * 60 * 60 * 1000);
  const currentDow = peruDate.getUTCDay();
  let daysToAdd = (targetDow - currentDow + 7) % 7;
  if (daysToAdd === 0) daysToAdd = 7; // si pide el mismo día, asume próxima semana
  peruDate.setUTCDate(peruDate.getUTCDate() + daysToAdd);
  // Re-shift a UTC
  return new Date(peruDate.getTime() + 5 * 60 * 60 * 1000);
}

// Parsea hora del texto. Devuelve {hour, minute} o null.
function parseTime(text) {
  // Match patrones tipo: "10am", "2 pm", "14:30", "10:00", "10h", "2hs", "10 de la mañana"
  const lower = normalize(text);

  // hh:mm (24h)
  let m = lower.match(/\b(\d{1,2}):(\d{2})\b/);
  if (m) {
    const h = parseInt(m[1], 10);
    const mi = parseInt(m[2], 10);
    if (h >= 0 && h <= 23 && mi >= 0 && mi <= 59) return { hour: h, minute: mi };
  }

  // h am/pm
  m = lower.match(/\b(\d{1,2})\s*(am|pm|hs?|h)\b/);
  if (m) {
    let h = parseInt(m[1], 10);
    const suffix = m[2];
    if (suffix === 'pm' && h < 12) h += 12;
    if (suffix === 'am' && h === 12) h = 0;
    if (h >= 0 && h <= 23) return { hour: h, minute: 0 };
  }

  // "10 de la mañana", "5 de la tarde", "8 de la noche"
  m = lower.match(/\b(\d{1,2})\s*(?:de\s+la\s+)?(ma[nñ]ana|tarde|noche)\b/);
  if (m) {
    let h = parseInt(m[1], 10);
    const period = stripAccents(m[2]);
    if (period === 'manana') {
      // mañana = AM (5-11)
      if (h >= 1 && h <= 11) return { hour: h, minute: 0 };
    } else if (period === 'tarde') {
      // tarde = 12-19
      if (h >= 1 && h <= 7) return { hour: h + 12, minute: 0 };
      if (h === 12) return { hour: 12, minute: 0 };
    } else if (period === 'noche') {
      // noche = 19-23
      if (h >= 7 && h <= 11) return { hour: h + 12, minute: 0 };
      if (h === 12) return { hour: 0, minute: 0 };
    }
  }

  return null;
}

// Extrae todas las fechas mencionadas en el texto.
function parseDates(text, now) {
  const found = [];
  const lower = normalize(text);
  const lowerNoAccents = stripAccents(lower);

  // 1) "hoy", "mañana", "pasado mañana"
  if (/\bhoy\b/.test(lowerNoAccents)) {
    const peruDate = new Date(now.getTime() - 5 * 60 * 60 * 1000);
    const time = parseTime(text) || { hour: 10, minute: 0 };
    peruDate.setUTCHours(time.hour, time.minute, 0, 0);
    const utc = new Date(peruDate.getTime() + 5 * 60 * 60 * 1000);
    found.push({ iso: isoLocalPeru(utc), raw: 'hoy', confidence: 0.85 });
  }

  if (/\bma[nñ]ana\b/.test(lower) && !/pasado\s+ma[nñ]ana/.test(lower)) {
    const date = new Date(now);
    const peruDate = new Date(date.getTime() - 5 * 60 * 60 * 1000);
    peruDate.setUTCDate(peruDate.getUTCDate() + 1);
    const time = parseTime(text) || { hour: 10, minute: 0 };
    peruDate.setUTCHours(time.hour, time.minute, 0, 0);
    const utc = new Date(peruDate.getTime() + 5 * 60 * 60 * 1000);
    found.push({ iso: isoLocalPeru(utc), raw: 'mañana', confidence: 0.9 });
  }

  if (/pasado\s+ma[nñ]ana/.test(lower)) {
    const date = new Date(now);
    const peruDate = new Date(date.getTime() - 5 * 60 * 60 * 1000);
    peruDate.setUTCDate(peruDate.getUTCDate() + 2);
    const time = parseTime(text) || { hour: 10, minute: 0 };
    peruDate.setUTCHours(time.hour, time.minute, 0, 0);
    const utc = new Date(peruDate.getTime() + 5 * 60 * 60 * 1000);
    found.push({ iso: isoLocalPeru(utc), raw: 'pasado mañana', confidence: 0.9 });
  }

  // 2) Días de la semana ("lunes", "martes 5pm", etc.)
  for (const [dayName, dow] of Object.entries(DAYS_OF_WEEK)) {
    const re = new RegExp(`\\b${stripAccents(dayName)}\\b`);
    if (re.test(lowerNoAccents)) {
      const dateUtc = nextDayOfWeek(now, dow);
      const peruDate = new Date(dateUtc.getTime() - 5 * 60 * 60 * 1000);
      const time = parseTime(text) || { hour: 10, minute: 0 };
      peruDate.setUTCHours(time.hour, time.minute, 0, 0);
      const utc = new Date(peruDate.getTime() + 5 * 60 * 60 * 1000);
      found.push({ iso: isoLocalPeru(utc), raw: dayName, confidence: 0.85 });
    }
  }

  // 3) Fechas numéricas dd/mm o dd/mm/yyyy
  const numericRe = /\b(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?\b/g;
  let m;
  while ((m = numericRe.exec(text)) !== null) {
    const d = parseInt(m[1], 10);
    const mo = parseInt(m[2], 10);
    let y;
    if (m[3]) {
      y = parseInt(m[3], 10);
      if (y < 100) y += 2000;
    } else {
      // Sin año explícito: usar año actual o próximo si la fecha ya pasó
      const peruNow = new Date(now.getTime() - 5 * 60 * 60 * 1000);
      y = peruNow.getUTCFullYear();
      const test = new Date(Date.UTC(y, mo - 1, d, 15, 0, 0));
      if (test < peruNow) y++;
    }
    if (d >= 1 && d <= 31 && mo >= 1 && mo <= 12) {
      const time = parseTime(text) || { hour: 10, minute: 0 };
      const peruDate = new Date(Date.UTC(y, mo - 1, d, time.hour, time.minute, 0));
      const utc = new Date(peruDate.getTime() + 5 * 60 * 60 * 1000);
      found.push({ iso: isoLocalPeru(utc), raw: m[0], confidence: 0.9 });
    }
  }

  // 4) "5 de junio", "11 de mayo de 2026"
  const monthRe = /\b(\d{1,2})\s+de\s+(enero|feb|febrero|mar|marzo|abr|abril|may|mayo|jun|junio|jul|julio|ago|agosto|sep|set|septiembre|oct|octubre|nov|noviembre|dic|diciembre)(?:\s+de\s+(\d{4}))?\b/gi;
  while ((m = monthRe.exec(lower)) !== null) {
    const d = parseInt(m[1], 10);
    const mo = MONTHS[m[2]] || MONTHS[stripAccents(m[2])];
    let y;
    if (m[3]) {
      y = parseInt(m[3], 10);
    } else {
      const peruNow = new Date(now.getTime() - 5 * 60 * 60 * 1000);
      y = peruNow.getUTCFullYear();
      const test = new Date(Date.UTC(y, mo - 1, d, 15, 0, 0));
      if (test < peruNow) y++;
    }
    if (d >= 1 && d <= 31 && mo >= 1 && mo <= 12) {
      const time = parseTime(text) || { hour: 10, minute: 0 };
      const peruDate = new Date(Date.UTC(y, mo - 1, d, time.hour, time.minute, 0));
      const utc = new Date(peruDate.getTime() + 5 * 60 * 60 * 1000);
      found.push({ iso: isoLocalPeru(utc), raw: m[0], confidence: 0.9 });
    }
  }

  // Dedup por iso
  const seen = new Set();
  return found.filter(f => {
    if (seen.has(f.iso)) return false;
    seen.add(f.iso);
    return true;
  });
}

// Detecta intent. Order matters: detección más específica primero.
function detectIntent(text) {
  const keywords = [];
  let intent = 'unknown';
  let confidence = 0;

  // Checks específicos primero (ask_price, ask_human) porque pueden coexistir con greeting
  if (INTENT_PATTERNS.ask_price.test(text)) {
    intent = 'ask_price'; confidence = 0.9; keywords.push('precio');
  } else if (INTENT_PATTERNS.ask_human.test(text)) {
    intent = 'ask_human'; confidence = 0.9; keywords.push('humano');
  } else if (INTENT_PATTERNS.cancel.test(text)) {
    intent = 'cancel'; confidence = 0.85; keywords.push('cancelar');
  } else if (INTENT_PATTERNS.reschedule.test(text)) {
    intent = 'reschedule'; confidence = 0.85; keywords.push('reagendar');
  } else if (INTENT_PATTERNS.confirm.test(text)) {
    intent = 'confirm'; confidence = 0.95; keywords.push('confirmacion');
  } else if (INTENT_PATTERNS.reject.test(text)) {
    intent = 'reject'; confidence = 0.9; keywords.push('rechazo');
  } else if (INTENT_PATTERNS.ask_info.test(text)) {
    intent = 'ask_info'; confidence = 0.7; keywords.push('info');
  } else if (INTENT_PATTERNS.greeting.test(text)) {
    intent = 'greeting'; confidence = 0.8; keywords.push('saludo');
  }

  return { intent, confidence, keywords };
}

// ───────────── API pública ─────────────

function parseMessage(text, opts = {}) {
  const now = opts.now ? new Date(opts.now) : new Date();
  const intentInfo = detectIntent(text);
  const dates = parseDates(text, now);

  // Si hay fechas detectadas Y el intent es desconocido o débil, asumir propose_date
  let intent = intentInfo.intent;
  let confidence = intentInfo.confidence;
  if (dates.length > 0 && (intent === 'unknown' || intent === 'greeting' || intent === 'ask_info')) {
    intent = 'propose_date';
    confidence = Math.max(confidence, 0.75);
  }

  return {
    intent,
    dates,
    confidence,
    keywords_matched: intentInfo.keywords,
  };
}

// Export para Node.js (también funciona en n8n Code node como global module.exports o return)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { parseMessage, parseDates, detectIntent, parseTime };
}

// Para usar en n8n Code node (copy-paste el contenido sin module.exports, llamar parseMessage($input.first().json.text))
