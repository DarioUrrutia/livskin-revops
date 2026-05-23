# Re-engagement Sequence — v1.0

**Fuentes:** workbook (drop-off D1-D6) + audio + observación chats reales
**Consume:** Workflow n8n [D5] Reengagement cron, email marketing, templates Meta

---

## Filosofía base

**Política:** ser presente sin ser molesto. Si el lead no responde, intentamos máximo 4-6 touches espaciados, después marcamos `lost_silence` y entramos a re-engagement long-term (30d+).

**Doctrina implícita doctora:** *"Estamos en contacto, cualquier cosa me avisas, previa coordinación siempre. Saludos"* — el cierre frío es ACEPTABLE. No es derrota.

---

## Secuencia drop-off D1-D6 (refinada del workbook + voice)

### D1 — Primer follow-up (48h tras silencio)

**Trigger:** lead silencio 48h tras última respuesta del bot/doctora.

**Copy (refinado del workbook):**
```
Hola {{1}} ☺️

Quería confirmar si recibiste mi mensaje. ¿Sigue tu interés en {{2}}?

La Dra. Claudia está disponible cuando quieras conversar.
```

**Variables:**
- `{{1}}` — nombre lead
- `{{2}}` — tratamiento de interés (capturado del primer mensaje)

**Canal:** WhatsApp (template `lead_waiting_4h_followup` — adaptable a este caso)

**Si responde:** vuelve a flow normal de calificación

**Si no responde:** schedule D2 en 24h

### D2 — Segundo follow-up (24h después D1)

**Trigger:** silencio post-D1.

**Copy (más contenido, no solo pregunta):**
```
Hola {{1}} ☺️

Por si te ayuda: el Botox parte desde S/250 por zona, dura 4-6 meses y son 30 minutos de tratamiento.

La Dra. tiene 10+ años de experiencia y la consulta es gratuita. Si quieres más info de algún tratamiento específico o agendar la consulta, aquí estoy.
```

**Variantes según tratamiento de interés:**
- Botox → como arriba
- Ácido Hialurónico → "El Ácido Hialurónico se cotiza en consulta, depende de la cantidad. Pero los resultados son inmediatos y duran 18-24 meses."
- PRP → "El PRP parte desde S/200, son 3 sesiones, ideal para mejorar calidad de piel."

**Si responde:** flow normal
**Si no responde:** schedule D3 en 24h

### D3 — Tercer follow-up (24h después D2)

**Trigger:** silencio post-D2.

**Copy (preguntar dudas + ofrecer agendar):**
```
Hola {{1}} ☺️

¿Tienes alguna duda o pregunta específica que pueda ayudar a aclarar?

La Dra. también puede responderte directamente si prefieres conversar con ella. O si quieres agendar la consulta gratuita, te tomo la cita ahora.
```

**Si responde:** flow normal
**Si no responde:** schedule D4 en 24h

### D4 — Cuarto follow-up (24h después D3)

**Trigger:** silencio post-D3.

**Copy (propuesta directa de cita):**
```
{{1}} ☺️

Si te interesa, te propongo agendar la consulta gratuita para esta semana — la Dra. tiene flexibilidad de horarios.

¿Qué día te queda mejor? Si prefieres esperar más, también está bien. Estamos en contacto.
```

**Si responde:** flow normal
**Si no responde:** schedule D5 en 7 días

### D5 — Quinto follow-up (7 días después D4)

**Trigger:** silencio post-D4 por 7 días.

**Copy (contenido + agendar):**
```
Hola {{1}} ☺️

Para resumir: la Dra. Claudia Delgado (CMP 091029) atiende en Wanchaq, Cusco. Ofrece tratamientos personalizados con filosofía de "reposición natural" — sin cambios estructurales.

10+ años de experiencia, Maestría en Medicina Estética en curso (UCSUR).

Si quieres agendar consulta gratuita o tienes dudas, escríbeme. Si no, no te molesto más por ahora — estamos en contacto.
```

**Si responde:** flow normal
**Si no responde:** schedule D6 en 14 días + marcar lead como `quiet_long_term`

### D6 — Re-engagement final (14+ días después D5)

**Trigger:** silencio 14d+ post-D5. ONE-SHOT (no más touches después).

**Copy (template Marketing `reengagement_inactive_30d`):**
```
Hola {{1}} ☺️

Hace un tiempo que conversamos. ¿Cómo va todo?

Si necesitas info o quieres agendar una consulta gratuita con la Dra. Claudia, aquí estoy.

"Ama tu piel siempre" ✨
```

**Si responde:** flow normal
**Si no responde:** marcar lead como `lost_silence`. Sin más touches del bot.

---

## Resumen secuencia

| Touch | Cuándo | Categoría Meta | Copy foco |
|---|---|---|---|
| D1 | 48h tras silencio | Utility | Check-in suave |
| D2 | +24h | Utility | Info adicional tratamiento |
| D3 | +24h | Utility | Preguntar dudas + agendar |
| D4 | +24h | Utility | Propuesta horario directa |
| D5 | +7d | Utility | Resumen + agendar/no más |
| D6 | +14d | Marketing | Re-engagement final |

**Total ventana:** ~25 días desde primer silencio hasta D6.

**Touches máximos:** 6 (después → `lost_silence`, no más bot)

---

## Lógica n8n workflow [D5] Reengagement (cron 1h)

```javascript
// Pseudocódigo
cron('0 */1 * * *', async () => {
  // Detectar leads silenciosos
  const candidates = await db.query(`
    SELECT wcs.*, cli.primer_nombre, leads.tratamiento_interes
    FROM wa_conversation_state wcs
    LEFT JOIN clientes cli ON ... (lookup by phone)
    LEFT JOIN leads ON ... (lookup last interaction)
    WHERE
      wcs.state IN ('waiting_lead', 'open')
      AND wcs.last_outbound_at < NOW() - INTERVAL '48 hours'
      AND (
        wcs.last_inbound_at IS NULL
        OR wcs.last_inbound_at < wcs.last_outbound_at
      )
      AND wcs.reengagement_attempts < 6
      AND wcs.last_reengagement_at < NOW() - INTERVAL '24 hours'
  `);

  for (const lead of candidates) {
    const touchNumber = lead.reengagement_attempts + 1;
    const template = getReengagementTemplate(touchNumber);
    const params = { name: lead.primer_nombre, treatment: lead.tratamiento_interes };

    await sendTemplate(lead.phone, template, params);

    await db.update(`
      UPDATE wa_conversation_state SET
        reengagement_attempts = reengagement_attempts + 1,
        last_reengagement_at = NOW(),
        last_outbound_at = NOW()
      WHERE phone_lead = $1
    `, [lead.phone]);

    await emitAuditEvent('conversation.reengagement_sent', {
      phone: lead.phone,
      touch_number: touchNumber,
      template: template.name,
    });

    // Si es D6 y aún silencio → mark lost
    if (touchNumber === 6 && lead.last_inbound_at < NOW() - INTERVAL '14 days') {
      await markLeadAsLost(lead.phone);
      await emitAuditEvent('conversation.marked_lost', {
        phone: lead.phone,
        reason: 'silence_after_d6',
      });
    }
  }
});
```

---

## Re-engagement long-term (clientes recurrentes inactivos)

### Trigger: cliente ERP con última venta hace 5+ meses (Botox) o más

**Lógica:**
```sql
SELECT cli.primer_nombre, cli.telefono,
       MAX(v.fecha_venta) as ultima_venta,
       LISTAGG(t.nombre_tratamiento) as tratamientos_pasados
FROM clientes cli
LEFT JOIN clientes_venta v ON cli.cod_cliente = v.cod_cliente
WHERE
  v.fecha_venta < NOW() - INTERVAL '5 months'
  AND cli.activo = true
  AND NOT EXISTS (
    SELECT 1 FROM reengagement_log
    WHERE phone = cli.telefono
    AND sent_at > NOW() - INTERVAL '60 days'
  )
GROUP BY cli.cod_cliente
```

### Copy según tratamiento previo

**Botox (5+ meses):**
```
Hola {{1}} ☺️

Ya van 5 meses desde tu último Botox. ¿Quieres coordinar tu retoque?

La Dra. tiene tu historial — solo coordinamos el día y listo.
```

**Ácido Hialurónico (18+ meses):**
```
Hola {{1}} ☺️

Hace tiempo que no nos vemos. El Ácido Hialurónico dura 18-24 meses, así que probablemente ya estás cerca de un refresco.

¿Quieres que la Dra. te evalúe? La consulta es la de siempre.
```

**Tratamientos sin estacionalidad (PRP/Esperma Salmón/Exosomas/Limpieza):**
```
Hola {{1}} ☺️ Qué bueno saber de ti.

¿Cómo va todo? Si quieres retomar tu rutina de cuidado (PRP, Esperma de Salmón, Limpieza), aquí estamos.
```

### Frequency cap re-engagement long-term

- **Máximo 1 mensaje cada 60 días** por cliente recurrente
- NO si ya recibió D1-D6 en últimos 30 días
- NO si cliente marcó "no recordatorios"

---

## Email re-engagement (canal secundario)

**Tool:** MailerLite Free (a configurar — Fase 4A.5)

### Lista #1: "Recurrentes inactivos 6+ meses"

**Asunto:**
> "{{1}}, te extrañamos en Livskin ☺️"

**Contenido:**
```
Hola {{1}},

Ya pasaron unos meses desde tu última visita a Livskin. ¿Cómo has estado?

Te dejamos un recordatorio amistoso: tu retoque de [tratamiento] probablemente ya está cerca.

La Dra. Claudia tiene tu historial y puede coordinar contigo cuando quieras.

📍 Urbanización La Florida O-7, Wanchaq, Cusco
📱 WhatsApp: +51 947 741 117

"Ama tu piel siempre" ✨

Saludos,
Yossie + Dra. Claudia Delgado
```

### Lista #2: "Leads que vieron landing pero no agendaron"

**Asunto:**
> "Antes de que decidas — algunas preguntas frecuentes"

**Contenido:**
```
Hola,

Visitaste nuestra landing de Botox pero notamos que aún no agendaste consulta. Sin presión — solo queremos ayudarte con info útil:

1. ¿Duele? → Todo duele un poquito, pero los resultados valen.
2. ¿Me va a cambiar la cara? → No. La filosofía de la Dra. es "reposición natural" — trabajo sobre tus facciones.
3. ¿Cuánto cuesta? → Desde S/250 por zona.
4. ¿Quién aplica? → La Dra. Claudia Delgado, Médico Cirujano CMP 091029.

Si tienes otra duda específica, respondé este email o escríbeme a WhatsApp.

Yossie + Dra. Claudia Delgado
"Ama tu piel siempre" ✨
```

### Lista #3: "Newsletter educativa mensual"

**Frecuencia:** 1 vez al mes
**Audiencia:** todos los clientes/leads que opt-in

**Asuntos rotativos:**
- "5 mitos sobre Botox que escuchamos seguido"
- "Cuándo empezar tratamientos preventivos (no es lo que piensas)"
- "Diferencia real entre Ácido Hialurónico y Botox"
- "Cuidados pre y post tratamiento"

**Foco:** educacional, NO promocional. Construir autoridad de la doctora.

---

## Reglas hard de re-engagement

### NO hacer

❌ **Ofrecer descuentos en re-engagement** — desvaloriza marca
❌ **Mensajes urgentes / FOMO** ("HOY ÚLTIMO DÍA")
❌ **Más de 6 touches** sin respuesta
❌ **Asumir consentimiento** — si lead pidió "no más mensajes", respetar always
❌ **Reactivar `lost_silence` automático** — solo si lead responde proactivamente

### SÍ hacer

✅ **Tono cálido + sin presión** ("estamos en contacto", "sin compromiso")
✅ **Quote filosofía marca** en D5 (refuerza positioning)
✅ **Mencionar credenciales** para credibilidad (CMP, Maestría)
✅ **Variar copy por touch** (no spam idéntico)
✅ **Honrar segmentación arquetipo** (formal vs informal)

---

## Métricas de re-engagement

| Métrica | Target v1 |
|---|---|
| **D1 response rate** | ≥40% |
| **D2 response rate (acum)** | ≥55% |
| **D3 response rate (acum)** | ≥65% |
| **D4 response rate (acum)** | ≥72% |
| **D5 response rate (acum)** | ≥78% |
| **D6 → conversión** | ≥10% |
| **% lost_silence final (D6 sin respuesta)** | <25% |
| **Recurrente re-activado vía cron 5m+** | ≥30% |

---

## Política consentimiento (compliance)

**Default:** todo lead que escribe inbound → consentimiento implícito para comunicación bidireccional 24h.

**Para outbound fuera ventana 24h:** template Meta-approved.

**Opt-out:**
- Lead puede escribir "no más mensajes" / "stop" / "no escribir" → marcar `opt_out=true`
- Bot Yossie respeta opt-out (skip todo touch)
- Re-opt-in solo si lead escribe proactivo de nuevo

**Privacy:**
- Datos lead almacenados en ERP livskin_erp + Vtiger livskin_db
- Procesamiento bajo Ley 29733 Perú (Protección Datos Personales)
- Política privacidad en landings (link footer)

---

## Validación pendiente

🟡 **Templates Meta a aprobar:** D2-D5 copies necesitan submit como `lead_waiting_extended_followup` (Utility) o variantes
🟡 **Email tool a configurar** (MailerLite o alternativa) — Fase 4A.5
🟡 **A/B testing post-deployment** — variar copy y ver qué touch funciona mejor

---

**Fin reengagement.md — 2026-05-23**
