# Scoring Rules — Bot Yossie v1.0

**Fuentes:** workbook (high-value signals + problemáticos) + audio + observación chats
**Consume:** Bot Yossie [D1.5 Tool Dispatcher], n8n routing, audit log

---

## Filosofía

**Doctrina #11:** scoring 100% determinístico. NO IA / NO Claude Haiku.
Si confidence parser <0.5 → escalar a humano, no agregar fallback IA.

**3 niveles de prioridad:**
1. **HIGH-VALUE** — atender preferentemente, escalación rápida si aplica
2. **NORMAL** — flow estándar bot Yossie
3. **RED FLAG / LOW-PRIORITY** — escalación a doctora para que decida si atender

---

## Reglas de clasificación

### HIGH-VALUE — triggers (cualquiera de estos)

| Trigger | Detección | Acción |
|---|---|---|
| **Cliente recurrente ERP** ≥3 ventas | Lookup `clientes_venta` by phone | Tag `high_value_recurrent`, skip intro, acceso precio directo, crédito permitido |
| **High ticket histórico** ≥S/1000 promedio | `AVG(clientes_venta.monto_venta) >= 1000` | Tag `high_value_ticket`, tono premium |
| **Recurrencia frecuente** ≥3 visitas/año | `COUNT(clientes_venta WHERE año = current)` ≥3 | Tag `high_value_loyalty`, acceso preferente agenda |
| **Migra de otra clínica** (lead nuevo) | Mensaje contiene contexto técnico de tratamientos previos | Tag `high_value_migrant`, tono experto |

**Pattern detection "migra de otra clínica" (regex):**
```javascript
const migrantPatterns = [
  /me hago.{0,30}(botox|hialur|hilos|prp) hace/i,
  /usualmente uso.{0,20}(marca|producto)/i,
  /antes me lo hacía en/i,
  /quería cambiar de cl[íi]nica/i,
];
```

**Comportamiento bot Yossie con HIGH-VALUE:**
- Greeting personalizado (usa nombre + skip "Soy Yossie, asistente de...")
- Acceso a precios directos sin disclaimer
- Tono más experto (asume conocimiento previo)
- Opción de crédito mencionada si aplica (recurrente)
- Escalación a doctora más ágil (no esperar 4h)
- Acceso preferente a horarios atípicos (fuera 8am-8pm)

---

### NORMAL — leads estándar

**Default cuando NO hay triggers high-value ni red flag.**

**Características:**
- Primera interacción
- Sin historial ERP
- Pregunta general sobre tratamientos
- Sin patterns negativos

**Comportamiento bot Yossie:**
- Flow estándar (greeting completo Yossie + ofrecer consulta gratuita)
- Painpoint handling estándar (ver `painpoints-responses.md`)
- Reengagement secuencia D1-D6 si silencia
- Sin friction inusual

---

### RED FLAG — triggers (cualquiera de estos)

| Trigger | Detección | Acción |
|---|---|---|
| **Negocia precio agresivamente** | Pattern regex (ver abajo) | Escalación + audit `red_flag_aggressive_negotiation` |
| **Compara obsesivamente con competencia** | Mensaje menciona ≥2 clínicas + "más barato" | Escalación + audit `red_flag_competitor_comparison` |
| **Cancela última hora repetidamente** | ≥2 cancelaciones día-de en últimos 60 días | Tag `red_flag_serial_canceller`, sin auto-confirmación de futuras citas |
| **Espera resultados imposibles** | Pattern regex ("borrar todas mis arrugas", etc.) | Escalación + tono honesto de expectativas |
| **Discute contraindicaciones** | Pattern regex (embarazo + "dame igual", etc.) | Escalación INMEDIATA — NUNCA atender bot |
| **Lenguaje agresivo / amenazante** | Pattern regex (insultos, amenazas, mayúsculas excesivas) | Escalación + audit, doctora decide si atiende |

### Patterns de detección red flag

```javascript
const redFlagPatterns = {
  aggressive_negotiation: [
    /(rebaja|descuento) (mucho|grande|fuerte|considerable)/i,
    /es muy caro,.{0,30}(b[áa]jame|h[áa]zme)/i,
    /si no me bajas.{0,20}(no voy|no vengo)/i,
    /\b(rega[lr]o|gratis|invita la casa)\b/i,
    /\b(pagas tu|invita la cl[íi]nica)\b/i,
  ],

  competitor_comparison: [
    /en (munay wasi|beysa|valderma|otra cl[íi]nica) (es|sale|cobra|me ofrec)/i,
    /(.{0,50}clínica.{0,50}){2,}/i, // Multi-comparison
    /por qu[ée] tan caro/i,
    /no quiero pagar tanto/i,
  ],

  impossible_expectations: [
    /borrar (todas mis|las) arrugas/i,
    /(cambiar|cambia)me la cara/i,
    /quiero verme.{0,20}(perfecta|impecable|sin defectos)/i,
    /garantizado|garantía 100%/i,
    /no quiero ning[úu]n riesgo/i,
  ],

  contraindication_ignored: [
    /(embaraz|gestaci|cancer|c[áa]ncer|lupus|autoinmune|alergi[ac])/i,
    // Combinado con:
    /(igual quiero|no importa|h[áa]zmelo igual|aunque)/i,
  ],

  aggressive_language: [
    /\b(idiota|estúpid|imbécil|tonta|inutil)\b/i,
    /[A-ZÁÉÍÓÚÑ]{20,}/, // 20+ char string en MAYÚSCULAS
    /\b(robo|estafa|fraude|tramposo)\b/i,
  ],
};
```

### Comportamiento bot Yossie con RED FLAG

**1. NO engancharse en discusión.**
**2. NO defender precios / argumentar.**
**3. Escalar inmediato.**

**Copy estándar bot Yossie ante red flag:**
```
{{1}}, te paso con la Dra. Claudia para que coordine directamente contigo ☺️

Te responde en breve.
```

[audit_log:** `conversation.escalated_to_doctora` reason=`red_flag_{specific_pattern}` matched_text=`{snippet}` **]**

**4. Doctora decide en ERP/notif si atiende:**
- Si decide atender → marca `lead.special_handling=true` → cualquier futura interacción es manual
- Si decide rechazar → marca `lead.do_not_engage=true` → bot ignora futuros inbound (no responde) + audit

---

## Tabla de detección automática

### Inputs disponibles para scoring

| Input | Source | Valor |
|---|---|---|
| Phone del lead | WA inbound payload | string |
| Last message text | WA inbound | string |
| Conv history | `wa_messages` table | array |
| Cliente ERP | `clientes` table (lookup phone) | object o null |
| Ventas históricas | `clientes_venta` table | array |
| Lead Vtiger | `vtiger_leaddetails` (lookup phone) | object o null |
| Source attribution | `vtiger_leadscf.cf_*` fields | strings |
| Conv state | `wa_conversation_state` table | object |

### Algoritmo de scoring

```javascript
async function scoreLead(leadInbound) {
  const phone = leadInbound.phone;
  const text = leadInbound.text;
  const cliente = await lookupClienteByPhone(phone);
  const vtigerLead = await lookupVtigerLeadByPhone(phone);
  const convState = await lookupConvState(phone);

  // 1. CHECK RED FLAG primero (más prioritario)
  for (const [pattern_name, regexes] of Object.entries(redFlagPatterns)) {
    if (regexes.some(re => re.test(text))) {
      return {
        category: 'RED_FLAG',
        subtype: pattern_name,
        action: 'escalate_to_doctora_immediate',
        priority: 1, // highest
      };
    }
  }

  // 2. CHECK CONTRAINDICATION (subset de red flag pero requiere SIEMPRE escalar)
  if (/(embaraz|gestaci|cancer|c[áa]ncer|lupus|autoinmune|alergi[ac])/i.test(text)) {
    return {
      category: 'RED_FLAG',
      subtype: 'contraindication_medical',
      action: 'escalate_to_doctora_immediate',
      priority: 1,
    };
  }

  // 3. CHECK HIGH-VALUE
  if (cliente && cliente.ventas_historicas >= 3) {
    return {
      category: 'HIGH_VALUE',
      subtype: 'recurrent',
      action: 'skip_intro_premium_treatment',
      priority: 2,
      meta: { ventas: cliente.ventas_historicas, ticket_promedio: cliente.ticket_promedio },
    };
  }

  if (cliente && cliente.ticket_promedio >= 1000) {
    return {
      category: 'HIGH_VALUE',
      subtype: 'high_ticket',
      action: 'premium_tone',
      priority: 2,
    };
  }

  if (vtigerLead && countVisitasYear(cliente) >= 3) {
    return {
      category: 'HIGH_VALUE',
      subtype: 'loyalty',
      action: 'preferred_agenda',
      priority: 2,
    };
  }

  // Migrant detection
  for (const re of migrantPatterns) {
    if (re.test(text)) {
      return {
        category: 'HIGH_VALUE',
        subtype: 'migrant_from_competitor',
        action: 'expert_tone',
        priority: 2,
      };
    }
  }

  // 4. DEFAULT NORMAL
  return {
    category: 'NORMAL',
    subtype: 'new_lead',
    action: 'standard_flow',
    priority: 3,
  };
}
```

---

## Escalación — niveles de urgencia

### Nivel 1: Escalación INMEDIATA (notificación instant a doctora)

**Triggers:**
- Contraindicación médica detectada
- Lenguaje agresivo / amenazante
- Pattern "ignora contraindicaciones"
- Reporte efecto adverso post-tratamiento

**Notificación a doctora:**
- WhatsApp personal de la doctora (vía bot Yossie envía resumen + contexto)
- Email respaldo a `info@livskin.site`
- Visible en ERP con flag `urgent`

**SLA respuesta esperada:** <30 min en horario, <2h fuera horario

### Nivel 2: Escalación NORMAL (puede esperar 1-4h)

**Triggers:**
- Tratamiento fuera del catálogo activo preguntado
- Combinación compleja de tratamientos
- Descuento pedido >S/30
- Cliente recurrente high-value
- Migrant de competencia
- Pregunta médica no contraindicación

**Notificación:**
- Notificación a doctora vía WhatsApp Yossie
- Visible en ERP sin flag urgent

**SLA respuesta esperada:** <4h

### Nivel 3: Sin escalación (bot Yossie maneja)

**Triggers:**
- Painpoints estándar
- Confirmaciones de cita en horario estándar
- Cancelaciones simples
- Preguntas de dirección/pago/horario
- Reminders automáticos
- Follow-up post-venta estándar

---

## Comportamiento por categoría — copy completos

### Para HIGH_VALUE — recurrent

**Saludo:**
```
Hola {{1}} ☺️ Qué bueno saber de ti.
¿En qué te ayudo?
```

**Cuando pregunta precio:**
```
Para tu retoque habitual está en S/{precio} ☺️
¿Qué día te queda mejor?
```

**Cuando pide crédito:**
```
{{1}}, sabes que con la Dra. podemos manejar crédito ☺️
Coordínalo directo con ella en tu próxima visita.
```

### Para HIGH_VALUE — migrant_from_competitor

**Saludo:**
```
Hola ☺️ Gracias por contactarnos.

La Dra. Claudia trabaja con cada paciente individualmente, sin protocolos estándar. Su enfoque es "reposición de lo que antes tenías" — sin cambios estructurales.

¿Qué tratamiento te gustaría conversar? La consulta es gratuita.
```

**Tono:** expert + premium (asume conocimiento previo)

### Para NORMAL — new_lead

Ver `journey-map.md` Touchpoint 5 + `voice-v1.md` §5.

### Para RED_FLAG — todos los subtipos

**Saludo (sin engancharse):**
```
{{1}}, te paso con la Dra. Claudia para que coordine directamente contigo ☺️

Te responde en breve.
```

**[NO entrar en discusión, NO defender precio, NO argumentar.]**

---

## Métricas a trackear

| Métrica | Cómo medir | Target v1 |
|---|---|---|
| **% HIGH_VALUE detectados correctamente** | Audit `lead_classified` vs validación manual | ≥85% |
| **% RED_FLAG identificados correctamente** | Audit vs lista manual de problemáticos | ≥90% (alto recall, OK false positives) |
| **% leads escalados innecesariamente** | Doctora confirma "no era necesario" | ≤15% |
| **Tiempo respuesta Nivel 1 escalación** | Audit `escalation_sent` → `doctora_responded` | <30 min |
| **Conversion HIGH_VALUE → venta** | ERP `clientes_venta` filter `tag=high_value` | ≥60% |

---

## Casos edge

### Caso 1: Lead recurrente que ahora tiene RED FLAG behavior

Ejemplo: cliente ERP con 5 ventas, pero en este mensaje pide descuento agresivo

**Decisión:** RED FLAG gana sobre HIGH_VALUE. Escalación a doctora.

**Razón:** preservar relación de respeto sobre descuento puntual.

### Caso 2: Lead lookup falla (phone no en ERP pero sí en Vtiger)

**Decisión:** considerar Vtiger leads como NORMAL (no se trata como recurrente sin compra).

**Excepción:** si Vtiger lead tiene ≥5 interacciones previas → `engaged_lead` (entre NORMAL y HIGH_VALUE).

### Caso 3: Mismo phone con múltiples leads distintos (uso compartido)

**Decisión:** asumir es la persona "más reciente" del phone. Si confusión real → escalar a doctora.

### Caso 4: Lead anónimo (sin nombre)

**Decisión:** preguntar nombre en greeting:
```
Hola ☺️ Soy Yossie, asistente de la Dra. Claudia.
¿Cómo te llamas para registrarte?
```

### Caso 5: Lead extranjero (de fuera de Cusco/Perú)

**Decisión:** subtipo HIGH_VALUE_tourist + tag `viene_de_lejos` → considerations especiales (ver `precios-strategy.md` §3.4)

**Detección:** phone con país distinto de +51, o mensaje menciona "vengo desde Lima/Arequipa/extranjero".

---

## Anti-patterns scoring

❌ **NO usar IA para scoring** (doctrina #11)
❌ **NO inferir personalidad** del lead — solo patterns objetivos
❌ **NO ocultar el sistema** — si lead pregunta "¿soy cliente VIP?" → honestidad "Veo que has venido varias veces, tienes prioridad de atención ☺️"
❌ **NO discriminar** por género/edad/raza más allá de patterns objetivos
❌ **NO falsos negativos en RED_FLAG** — preferir escalar más que dejar pasar
❌ **NO scoring trade off** (recurrent con red flag = sigue red flag)

---

## Validación pendiente

🟡 Calibrar precision patterns regex post-deployment (esperar 30-60 días telemetría real)
🟡 Decisión sobre cómo manejar `do_not_engage` (lead bloqueado por doctora) — ¿cuánto dura? ¿se puede revertir?
🟡 ML para refinar patterns futuro (post-cierre bootstrap #13) — pero sigue rule-based core

---

**Fin scoring-rules.md — 2026-05-23**
