# WhatsApp Cloud API Templates — Drafts v1 para review Dario

**Contexto:** Meta exige plantillas pre-aprobadas para mensajes **outbound iniciados por el negocio** (cuando han pasado >24h desde el último inbound del lead, o es el primer contacto outbound). Mensajes dentro de la ventana 24h activa pueden ser texto libre.

**Restricciones Meta:**
- Categoría correcta es CRÍTICA (Marketing / Utility / Authentication). Utility = cost lower + approval faster
- Variables `{{1}}`, `{{2}}`, etc. — máximo recomendado 4
- Sin URLs externos en body (excepto botones)
- Sin lenguaje promocional excesivo en Utility (clickbait → reject)
- Aprobación: 24h-72h típico, hasta 5 días

**Voice aplicado (ver `docs/brand/discovery-fill/notas-claude.md` § 2):**
- Calidez profesional, no sobre-familiar
- Emojis ✨ ☺️ 😊 permitidos, NO 💋 🔥
- Variables CON tilde respetando ortografía
- Cierre estándar: "Nos vemos" / "Te esperamos" / "Estamos en contacto"

---

## Template #1 — `new_lead_appointment_request`
**Categoría:** Utility
**Idioma:** Español (es_PE)
**Uso:** Bot Yossie envía al lead nuevo confirmando que recibió su consulta + propone consulta gratis

**Body:**
```
Hola {{1}} ☺️ Gracias por escribirnos a Livskin.

Soy Yossie, asistente de la Dra. Claudia Delgado. Vi que te interesa {{2}}.

La Dra. ofrece una consulta gratuita personalizada para evaluar tu caso y conversar sobre el tratamiento. ¿Te gustaría agendar?

*Wanchaq, Cusco — atendemos previa coordinación.*
```
**Variables:**
- `{{1}}` — nombre del lead (ej. "Maria")
- `{{2}}` — tratamiento o consulta general (ej. "Botox", "información sobre tratamientos faciales")

**Buttons (Quick Reply):**
- "Sí, agendar consulta"
- "Tengo más preguntas"
- "Por ahora no"

---

## Template #2 — `lead_confirmed_appointment`
**Categoría:** Utility
**Idioma:** es_PE
**Uso:** Confirmación de cita agendada después del flujo bot ↔ doctora

**Body:**
```
Listo, {{1}} ☺️

Tu consulta con la Dra. Claudia Delgado queda agendada para *{{2}}* a las *{{3}}*.

📍 Urbanización La Florida O-7, Wanchaq — detrás del templo de los Mormones, media cuadra encima.

Si necesitas reagendar, avísame con 24h de anticipación.

Nos vemos ✨
```
**Variables:**
- `{{1}}` — nombre lead
- `{{2}}` — fecha (ej. "viernes 30 de mayo")
- `{{3}}` — hora (ej. "6:00 pm")

**Buttons (Quick Reply):**
- "Confirmar asistencia"
- "Necesito reagendar"

---

## Template #3 — `lead_proposed_alternatives`
**Categoría:** Utility
**Idioma:** es_PE
**Uso:** La doctora no puede en el horario propuesto y ofrece alternativas via Yossie

**Body:**
```
Hola {{1}} ☺️

Vi tu propuesta para *{{2}}*, pero ese horario no está disponible. La Dra. te ofrece estas opciones:

1. {{3}}
2. {{4}}

¿Cuál te acomoda mejor?
```
**Variables:**
- `{{1}}` — nombre lead
- `{{2}}` — horario que el lead propuso
- `{{3}}` — opción 1 (ej. "Mañana viernes a las 5:30 pm")
- `{{4}}` — opción 2 (ej. "Sábado a las 6 pm")

**Buttons (Quick Reply):**
- "Opción 1"
- "Opción 2"
- "Ninguna me sirve"

---

## Template #4 — `lead_waiting_4h_followup`
**Categoría:** Utility
**Idioma:** es_PE
**Uso:** Lead silencioso 4h+ tras propuesta de horario, follow-up suave

**Body:**
```
Hola {{1}} ☺️

Quería confirmar si recibiste mi mensaje. ¿Sigue en pie tu interés en {{2}}?

La Dra. Claudia está disponible para responder tus dudas cuando puedas.

Estamos en contacto ✨
```
**Variables:**
- `{{1}}` — nombre lead
- `{{2}}` — tratamiento de interés

**Buttons (Quick Reply):**
- "Sí, sigo interesado"
- "Más tarde respondo"
- "Ya no, gracias"

---

## Template #5 — `appointment_reminder_24h`
**Categoría:** Utility
**Idioma:** es_PE
**Uso:** Recordatorio 24h antes de la cita

**Body:**
```
Hola {{1}} ☺️ Te recordamos tu cita con la Dra. Claudia Delgado:

📅 *{{2}}* a las *{{3}}*
📍 Urbanización La Florida O-7, Wanchaq

Si necesitas reagendar, avísanos lo antes posible.

Te esperamos ✨
```
**Variables:**
- `{{1}}` — nombre
- `{{2}}` — fecha cita
- `{{3}}` — hora cita

**Buttons (Quick Reply):**
- "Confirmar asistencia"
- "Reagendar"

---

## Template #6 — `appointment_reminder_3h`
**Categoría:** Utility
**Idioma:** es_PE
**Uso:** Recordatorio 3h antes de la cita (last-call)

**Body:**
```
{{1}} ☺️ Te esperamos en *{{2}}h* para tu cita.

📍 Urbanización La Florida O-7, Wanchaq — detrás del templo de los Mormones.

Nos vemos ✨
```
**Variables:**
- `{{1}}` — nombre
- `{{2}}` — horas restantes (ej. "3", "2")

---

## Template #7 — `reengagement_inactive_30d` (opcional, propone si hace sentido)
**Categoría:** Marketing
**Idioma:** es_PE
**Uso:** Lead inactivo >30 días, reactivación suave (no campaña agresiva)

**Body:**
```
Hola {{1}} ☺️

Hace un tiempo que conversamos. ¿Cómo va todo?

Si necesitas información o quieres agendar una consulta gratuita con la Dra. Claudia, aquí estoy.

*"Ama tu piel siempre"* ✨
```
**Variables:**
- `{{1}}` — nombre

**Buttons (Quick Reply):**
- "Quiero info"
- "Agendar consulta"

---

## Categorización Meta (resumen para submission)

| Template | Categoría | Razón |
|---|---|---|
| 1. new_lead_appointment_request | Utility | Respuesta a inquiry, no promocional |
| 2. lead_confirmed_appointment | Utility | Confirmación booking |
| 3. lead_proposed_alternatives | Utility | Coordinación logística |
| 4. lead_waiting_4h_followup | Utility | Follow-up de inquiry abierta |
| 5. appointment_reminder_24h | Utility | Recordatorio cita confirmada |
| 6. appointment_reminder_3h | Utility | Recordatorio cita confirmada |
| 7. reengagement_inactive_30d | Marketing | Re-engagement post-30d (categoría Marketing es honesta) |

**Costo estimado por mensaje (Perú, marzo 2026 rates Meta):**
- Utility conversation: ~$0.005 USD c/u
- Marketing conversation: ~$0.030 USD c/u
- Service conversation (inbound primero): $0.00 (gratis)

→ Optimización: mantener conversaciones dentro de ventana 24h activa siempre que sea posible → solo usamos templates para outbound o re-engagement.

---

## ¿Qué necesito de Dario antes de submit?

1. **Aprobar los 7 templates** (o pedir ajustes)
2. **Confirmar idioma `es_PE`** (Español Perú) vs `es` genérico → recomiendo `es_PE` por consistencia regional
3. **Decidir si template #7 (reengagement) lo submitimos ya o esperamos** → es Marketing, mayor scrutiny Meta
4. **Confirmar que "Yossie" es OK** como nombre del asistente (alternativas: bot anónimo, "asistente Livskin")
5. **Validar copy de dirección** — *"Urbanización La Florida O-7, Wanchaq — detrás del templo de los Mormones, media cuadra encima"* es lo que está en workbook

Una vez aprobados, los submito vía Meta Graph API `POST /{waba}/message_templates` con app token. Approval window 24h-72h típico.
