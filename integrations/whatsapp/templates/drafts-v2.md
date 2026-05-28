# WhatsApp Cloud API Templates — Drafts v2 (batch para Sprint 1)

**Contexto:** ampliar pool de 9 → 18 templates pre-aprobados. Submit batch para que Sprint 3 (3ra campaña) no se bloquee por aprobación Meta (48-72h).

**Voice aplicado** (alineado `docs/brand/copy-principles.md` v0.1 + post-mortem 2da campaña — mensajes 2-3 líneas, cálido NO efusivo):
- Calidez profesional, no sobre-familiar
- Emojis permitidos: ☺️ ✨ 📍 (NO 💋 🔥 ❤️)
- Cierre estándar: "Nos vemos" / "Te esperamos" / "Estamos en contacto"
- Variables CON tilde

**Restricciones Meta:**
- Variables `{{1}}`, `{{2}}`... — máx 4 recomendado
- NO variables en bordes del mensaje (causa reject)
- Lenguaje promocional excesivo en Utility → reject. Promo va a MARKETING category.

---

## 🧰 UTILITY (3 nuevos)

### Template #10 — `appointment_cancelled_v1`
**Categoría:** UTILITY
**Idioma:** es_PE
**Uso:** Lead/cliente cancela cita, bot confirma cancelación + ofrece reagendar

**Body:**
```
Listo, {{1}} ☺️ tu cita del {{2}} queda cancelada.

Si quieres reagendar, escríbeme cuando estés lista y la coordinamos sin problema.

Estamos en contacto ✨
```
**Variables:**
- `{{1}}` — nombre lead
- `{{2}}` — fecha original (ej. "viernes 30 de mayo")

---

### Template #11 — `appointment_reschedule_confirmed_v1`
**Categoría:** UTILITY
**Idioma:** es_PE
**Uso:** Confirmación de re-schedule tras coordinar con doctora (vs `lead_confirmed_appointment_v1` que es 1ra confirmación)

**Body:**
```
Listo {{1}} ☺️ tu cita queda reagendada para *{{2}}* a las *{{3}}*.

📍 Urbanización La Florida O-7, Wanchaq.

Nos vemos ✨
```
**Variables:**
- `{{1}}` — nombre
- `{{2}}` — nueva fecha
- `{{3}}` — nueva hora

---

### Template #12 — `appointment_reminder_1h_v1`
**Categoría:** UTILITY
**Idioma:** es_PE
**Uso:** Recordatorio 1h antes de la cita (complementa 24h y 3h existentes)

**Body:**
```
Hola {{1}} ☺️ te recordamos que en 1 hora tienes tu cita con la Dra. Claudia.

📍 Urbanización La Florida O-7, Wanchaq — detrás del templo de los Mormones.

Te esperamos ✨
```
**Variables:**
- `{{1}}` — nombre

---

## 📣 MARKETING TOFU (5 nuevos — uno por tratamiento principal)

### Template #13 — `promo_botox_v1`
**Categoría:** MARKETING
**Idioma:** es_PE
**Uso:** Outreach a leads/clientes con interés previo Botox que llevan >30d sin contacto. Para campañas reactivación o anuncio nueva oferta Botox.

**Body:**
```
Hola {{1}} ☺️ soy Yossie, de Livskin Cusco.

La Dra. Claudia está atendiendo consultas de Botox esta semana. Si te interesa evaluar tu caso con una consulta gratuita, escríbenos aquí ✨

Nos vemos.
```
**Variables:**
- `{{1}}` — nombre

---

### Template #14 — `promo_acido_hialuronico_v1`
**Categoría:** MARKETING
**Idioma:** es_PE
**Uso:** Outreach Ácido Hialurónico (mismo patrón que Botox)

**Body:**
```
Hola {{1}} ☺️ soy Yossie, de Livskin Cusco.

La Dra. Claudia está atendiendo consultas de Ácido Hialurónico esta semana. Si quieres evaluar tu caso con una consulta gratuita, escríbenos aquí ✨

Te esperamos.
```
**Variables:**
- `{{1}}` — nombre

---

### Template #15 — `promo_prp_v1`
**Categoría:** MARKETING
**Idioma:** es_PE
**Uso:** Outreach PRP

**Body:**
```
Hola {{1}} ☺️ soy Yossie, de Livskin Cusco.

La Dra. Claudia está atendiendo consultas de PRP (plasma rico en plaquetas) esta semana. Si te interesa una consulta gratuita para evaluar tu caso, escríbenos aquí ✨

Estamos en contacto.
```
**Variables:**
- `{{1}}` — nombre

---

### Template #16 — `promo_limpieza_facial_v1`
**Categoría:** MARKETING
**Idioma:** es_PE
**Uso:** Outreach Limpieza Facial Profunda

**Body:**
```
Hola {{1}} ☺️ soy Yossie, de Livskin Cusco.

La Dra. Claudia tiene espacios disponibles para Limpieza Facial Profunda esta semana. Si quieres reservar el tuyo, escríbenos aquí ✨

Te esperamos.
```
**Variables:**
- `{{1}}` — nombre

---

### Template #17 — `promo_hilos_tensores_v1`
**Categoría:** MARKETING
**Idioma:** es_PE
**Uso:** Outreach Hilos Tensores

**Body:**
```
Hola {{1}} ☺️ soy Yossie, de Livskin Cusco.

La Dra. Claudia está atendiendo consultas de Hilos Tensores esta semana. Si quieres evaluar tu caso con una consulta gratuita, escríbenos aquí ✨

Nos vemos.
```
**Variables:**
- `{{1}}` — nombre

---

## 🔁 FOLLOW-UPS (2 nuevos — completan 24h, 4h ya existe; 30d ya existe)

### Template #18 — `post_consulta_24h_v1`
**Categoría:** UTILITY
**Idioma:** es_PE
**Uso:** 24h después de consulta gratuita, follow-up "¿lista para agendar tratamiento?". UTILITY porque es transactional/follow-up, no promocional puro.

**Body:**
```
Hola {{1}} ☺️ pasó por aquí Yossie de Livskin.

¿Cómo te quedaste tras la consulta de ayer con la Dra. Claudia? Si tienes dudas o quieres agendar tu tratamiento, estoy aquí ✨

Nos vemos.
```
**Variables:**
- `{{1}}` — nombre

---

### Template #19 — `reengagement_cliente_60d_v1`
**Categoría:** MARKETING
**Idioma:** es_PE
**Uso:** Cliente que asistió hace 60+ días sin volver. Diferente a `reengagement_inactive_30d_v1` (que es LEAD 30d sin convertir). Aquí es CLIENTE que ya vino.

**Body:**
```
Hola {{1}} ☺️ pasó por aquí Yossie de Livskin Cusco.

Hace tiempo que no nos vemos. Si quieres una consulta de seguimiento con la Dra. Claudia o tienes alguna duda nueva, escríbenos aquí ✨

Te esperamos.
```
**Variables:**
- `{{1}}` — nombre

---

## 📊 Pool resultante (18 templates total)

### Por categoría:
- **UTILITY (10):** appointment_reminder_24h, appointment_reminder_3h, appointment_reminder_1h, lead_confirmed_appointment, lead_proposed_alternatives, appointment_reschedule_confirmed, appointment_cancelled, post_consulta_24h, doctor_lead_notification (interno)
- **MARKETING (9):** new_lead_appointment_request, lead_waiting_4h_followup, reengagement_inactive_30d, doctor_lead_returning, promo_botox, promo_acido_hialuronico, promo_prp, promo_limpieza_facial, promo_hilos_tensores, reengagement_cliente_60d

Wait — eso suma 19. Quitamos 1: `appointment_reminder_1h_v1` se puede eliminar si Sprint 3 lo considera no esencial (la doctora ya manda mensaje suelto si quiere recordar).

### Por status proyectado tras submit:
- **8 ya APPROVED** (no tocar)
- **1 PENDING** (`doctor_lead_returning_v1`)
- **10 NEW a submit** (este batch)

**Total efectivo después del batch:** 19 templates en pool, ~18 utiles (1 redundante puede sacarse).

---

## Próximo paso

Tras aprobación del usuario de los 10 NEW templates → submit batch via Graph API:

```bash
POST https://graph.facebook.com/v21.0/{WABA_ID}/message_templates
Authorization: Bearer {SYSTEM_USER_TOKEN}
Content-Type: application/json

{
  "name": "promo_botox_v1",
  "language": "es_PE",
  "category": "MARKETING",
  "components": [...]
}
```

Tras submit: monitorear status via `GET /{WABA_ID}/message_templates?fields=name,status`. Espera típica 48-72h.

---

**Status:** drafts ready — esperando aprobación Dario
