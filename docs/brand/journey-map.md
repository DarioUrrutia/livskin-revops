# Customer Journey Map — v1.0

**Fuentes:** workbook doctora + audio + chats reales + ERP analytics
**Consume:** Bot Yossie (workflow D1/D2/D3), ads creative (touchpoint copy), email sequence

---

## Mapa completo del journey

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         AWARENESS / DESCUBRIMIENTO                       │
└──────────────────────────────────────────────────────────────────────────┘

  Boca a boca    │  Google Business  │  Google Ads  │  Facebook Ads  │ Instagram
  (#1, orgánico) │  (búsquedas)      │  (intencional)│ (display)      │ (orgánico)

                                       │
                                       ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                              INTERÉS                                     │
└──────────────────────────────────────────────────────────────────────────┘

  Visita Google Business    Click ad → Landing       Visita perfil IG
  → ve fotos + reseñas      → form + WA              → ve casos antes/después

                                       │
                                       ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                          PRIMER CONTACTO                                 │
└──────────────────────────────────────────────────────────────────────────┘

  WhatsApp inbound a Cloud API Livskin (+51 947 741 117)
  → [D1] Webhook n8n → Parser intent + lookup ERP
  → Tool Dispatcher decide acción

                                       │
                          ┌────────────┼──────────────┐
                          ▼            ▼              ▼
                    LEAD NUEVO   RECURRENTE      RED FLAG
                          │            │              │
                          ▼            ▼              ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                        CONSIDERACIÓN (Yossie)                            │
└──────────────────────────────────────────────────────────────────────────┘

Lead nuevo:                Recurrente:               Red flag:
- Yossie identifica        - Skip intro              - Escala doctora
- Pregunta intent          - Acceso precio directo   - Audit red_flag
- Responde con copy        - Propuesta horarios      - Doctora decide
  según painpoint          - Bot relaya a doctora    - sin friction
- Ofrece consulta gratis     si necesita
                                       │
                                       ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                       INTENT / CALIFICACIÓN                              │
└──────────────────────────────────────────────────────────────────────────┘

  ¿Lead listo agendar?
       │
       ├── SÍ → propuesta de horario → [D2] WA Send confirma → ERP cita
       │
       ├── DUDA → painpoint handling → más info → vuelve a evaluar
       │
       └── NO → cierre frío "estamos en contacto" → trigger D5 reengagement

                                       │
                                       ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                        CONSULTA (presencial)                             │
└──────────────────────────────────────────────────────────────────────────┘

  Día de la cita:
  - [D6] Reminder T-24h (template Meta)
  - [D6] Reminder T-3h (template Meta)
  - Doctora atiende (30 min consulta gratuita)
  - Evaluación + propuesta tratamiento + precio exacto
  - Decisión: ¿se hace tratamiento HOY o agenda?

                                       │
                          ┌────────────┴──────────────┐
                          ▼                          ▼
                    HACE TRATAMIENTO            VUELVE OTRO DÍA
                          │                          │
                          ▼                          ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                     CONVERSIÓN (cliente nuevo)                           │
└──────────────────────────────────────────────────────────────────────────┘

  ERP registra:
  - Cliente (clientes table)
  - Venta (clientes_venta table)
  - Pago (clientes_pago table)

  Workflow [G3] emite CAPI Purchase a Meta
  con event_id que ata anuncio→form→Vtiger→ERP

                                       │
                                       ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                         POST-VENTA / RETENCIÓN                           │
└──────────────────────────────────────────────────────────────────────────┘

  Yossie automated:
  - Follow-up 24h: "¿Cómo te sentiste? Si tienes dudas, escríbeme"
  - Follow-up 7d: "Los resultados se empiezan a ver, cualquier consulta aquí estoy"

  Yossie segmenta:
  - Tratamientos con sesiones múltiples → reminder próxima sesión
  - Tratamientos one-shot → calendar de retoque (Botox 6m, AH 18-24m)

                                       │
                                       ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                          RECURRENCIA                                     │
└──────────────────────────────────────────────────────────────────────────┘

  Recurrente identificada en ERP:
  - Yossie reconoce y skip intro
  - Acceso a crédito (loyalty)
  - Cross-sell suave en cada visita
  - Trigger "es hora de retoque" en cron D5

                                       │
                                       ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                          ADVOCACY (boca a boca)                          │
└──────────────────────────────────────────────────────────────────────────┘

  Cliente satisfecho → recomienda a amigas/familia
  → Nueva lead boca a boca → vuelve a comienzo del funnel
  → Tracking: pedir "¿cómo nos encontraste?" en consulta primera vez
```

---

## Touchpoints detallados con copy real

### Touchpoint 1: Google Business / Búsqueda orgánica

**Acción del lead:** busca *"clínica botox cusco"* o *"medicina estética wanchaq"*

**Lo que ve en Google Business:**
- Foto consultorio + tratamientos
- Reseñas (objetivo ≥4.5⭐)
- Dirección + teléfono + WhatsApp
- Horario "previa coordinación"
- Categoría "Clínica de medicina estética"

**Decisión esperada:** click en WhatsApp → primer contacto

**Optimización:**
- ✅ Pedir reseña a clientes satisfechos post-venta
- ✅ Subir 1-2 fotos antes/después con consentimiento
- ✅ Mantener horario actualizado en GMB

### Touchpoint 2: Click en ad Meta (Facebook/Instagram)

**Ad creative draft (Botox):**

> Imagen: foto de mujer 40+ con piel natural (NO retoque excesivo)
>
> Copy:
> **"Líneas de expresión sin cambiar tu rostro"**
> Botox profesional con la Dra. Claudia Delgado.
> Médico Cirujano CMP 091029 — Maestría UCSUR en curso.
> Filosofía: reposición natural, no cambios estructurales.
>
> CTA: "Consulta gratuita" → click → Landing botox-mvp

**Tracking:**
- Pixel ID: `4410809639201712`
- Event ID único (cookie `lvk_event_id`)
- UTM tracking persistente 90 días

### Touchpoint 3: Landing page (botox-mvp / prp-mvp / future)

**Hero section:**
```
Tratamientos personalizados
con la Dra. Claudia Delgado

10+ años de experiencia en Cusco
Médico Cirujano CMP 091029
Maestría en Medicina Estética UCSUR (en curso)

[Botón WhatsApp pre-filled: "Hola, vi tu anuncio de Botox y me interesa más info"]
```

**Sección "Cómo trabajamos":**
> *"Reposición de lo que antes tenías, no cambios estructurales."*
>
> Trabajo individualizado con cada paciente — sin protocolos estándar. Escucho tus necesidades y te ofrezco las opciones que mejor se ajusten a lo que buscas.

**Sección FAQ (extracto):**
- ¿Cuánto cuesta el Botox? → "Desde S/250 por zona. Precio final en consulta gratuita."
- ¿Duele? → "Todo duele un poquito, pero los resultados valen. La Dra. usa anestesia tópica."
- ¿Y si me cambia la cara? → Quote: *"Mírame, tú me conoces y yo no he cambiado ni siquiera nada. La idea es mejorar lo que ya tenías."*

**CTA bottom:**
> "Agenda tu consulta gratuita ahora"
> [Botón WhatsApp]

### Touchpoint 4: Form submit (legacy LatePoint / SureForms)

**Status actual:** form WP existe pero NO se usará como canal principal post-Sprint 2.3.

**Fallback:** si form llega, n8n workflow [A1] crea Lead Vtiger + Yossie envía template `new_lead_appointment_request` al phone capturado.

### Touchpoint 5: WhatsApp Cloud API — primer mensaje

**Inbound:**
> Lead: *"Hola, vi el anuncio de Botox"*

**Yossie response (lead nuevo):**
```
Hola ☺️ Gracias por escribirnos a Livskin.

Soy Yossie, asistente de la Dra. Claudia Delgado.
Vi que te interesa Botox.

El Botox parte desde S/250 por zona — el precio depende de las áreas a tratar. La Dra. lo evalúa en la consulta gratuita.

¿Quieres agendar? Dura unos 30 min, sin compromiso.
```

**Tono según arquetipo detectado** (ver `personas.md` §11)

### Touchpoint 6: Negociación de horario

**Flujo:**
```
Lead: "El viernes a las 5pm puedo"
  ↓
Yossie verifica disponibilidad (consulta ERP appointments — pendiente migration 0009)
  ↓
Si disponible → confirma:
  "Listo, te confirmo viernes 30/5 a las 5pm con la Dra. ☺️"
  ↓
Si NO disponible → propone alternativas:
  "Ese horario no está disponible. La Dra. te ofrece:
   1. Viernes 30/5 a las 6pm
   2. Sábado 31/5 a las 5pm
   ¿Cuál te queda mejor?"
```

**Si lead recurrente identificado:** skip verificación automática → relaya propuesta a doctora vía notificación (caso Opción A híbrida del plan n8n).

### Touchpoint 7: Recordatorios (T-24h + T-3h)

**Template Meta `appointment_reminder_24h`:**
```
Hola {{1}} ☺️ Te recordamos tu cita con la Dra. Claudia Delgado:

📅 Viernes 30 de mayo a las 5:00 pm
📍 Urbanización La Florida O-7, Wanchaq

Si necesitas reagendar, avísanos lo antes posible.
Te esperamos ✨
```

**Template Meta `appointment_reminder_3h`:**
```
{{1}} ☺️ Te esperamos en 3h para tu cita.

📍 Urbanización La Florida O-7, Wanchaq — detrás del templo de los Mormones.

Nos vemos ✨
```

### Touchpoint 8: Día de la consulta presencial

**Antes:** lead llegó al consultorio (Yossie ya hizo su trabajo). Doctora retoma.

**Durante:**
- Saludo cálido en persona (*"Buen día"* + nombre)
- Evaluación visual + escucha activa
- Propuesta de tratamientos personalizada (basada en filosofía "reposición")
- Cotización si aplica (cierre AH solo aquí)
- Decisión: hacer hoy o agendar

**Después:**
- Si hizo tratamiento → cobro (Yape/Plin/transferencia/efectivo)
- ERP registra venta + pago
- Workflow [G3] CAPI Purchase emit a Meta con event_id

### Touchpoint 9: Post-venta follow-up

**Yossie automated 24h después del tratamiento:**
```
Hola {{1}} ☺️ ¿Cómo te sentiste con el tratamiento?

Si tienes alguna duda o molestia, escríbeme y te ayudo. La Dra. también puede responderte si es algo médico.
```

**Yossie automated 7d después (solo tratamientos con resultados gradual — Botox, Esperma Salmón):**
```
Hola {{1}} ☺️

Ya empiezan a verse los primeros resultados del Botox. ¿Notas la diferencia?

Recuerda evitar masajes en la zona + sol directo por unos días.

Cualquier consulta aquí estoy.
```

### Touchpoint 10: Recordatorio retoque (long-term)

**Yossie automated según tratamiento:**
- Botox: a los 5 meses (1 mes antes de cuando expira efecto)
- Ácido Hialurónico: a los 18 meses
- Hilos: a los 22 meses
- PRP/Esperma Salmón/Exosomas: a los 25-28 días después de última sesión (si pendiente next sesión del paquete 3)

**Template Meta `reengagement_inactive_30d` (adaptable):**
```
Hola {{1}} ☺️

Ya van 5 meses desde tu Botox. ¿Quieres coordinar tu retoque?

Te tomo la cita y la Dra. te recibe con flexibilidad de horarios.

"Ama tu piel siempre" ✨
```

---

## Variantes del journey según canal de origen

### Variante A: Boca a boca (sin tracking digital)

```
Amiga recomienda → Lead googlea "claudia delgado livskin" o "doctora estética cusco"
  → encuentra Google Business → WA inbound
  → entra al journey en Touchpoint 5
  → tracking: pedir "¿cómo nos encontraste?" en consulta
```

**Sin event_id digital end-to-end** — pero se captura en ERP `cliente.canal_origen = "boca_a_boca"`.

### Variante B: Google Ads → Landing → Form/WA

```
Search "botox cusco" → Click ad → Landing botox-mvp
  → Form submit (legacy) o WA pre-filled (preferido)
  → entra al journey en Touchpoint 5
  → event_id digital persisted end-to-end
  → CAPI emit cuando se cierra venta
```

### Variante C: Meta Ads → IG/FB → Landing → WA

```
Scroll IG/FB → Ad creative → Click → Landing botox-mvp (target_url_meta=...)
  → click WA pre-filled
  → entra journey en Touchpoint 5
  → event_id end-to-end
```

### Variante D: Recurrente vuelve

```
Yossie cron D5 detecta "ya pasaron 5 meses desde último Botox"
  → envía reminder retoque (template)
  → recurrente confirma → propuesta horario
  → cita programada → atención
```

---

## Métricas por touchpoint (post-deployment)

| Touchpoint | Métrica | Target v1 |
|---|---|---|
| 1. Google Business | Click-to-WA rate | ≥15% |
| 2. Meta Ad | CTR | ≥1.5% |
| 3. Landing | WA click rate | ≥20% |
| 4. Form submit | Form completion rate | ≥40% |
| 5. WA primer mensaje | Bot response time | <60s |
| 6. Negociación horario | % agenda en ≤3 mensajes | ≥60% |
| 7. Recordatorios | % asistencia confirmada T-3h | ≥85% |
| 8. Consulta presencial | Conversion to first sale | ≥50% |
| 9. Post-venta follow-up | Engagement rate | ≥40% |
| 10. Recordatorio retoque | Re-booking rate | ≥35% |

---

## Decisiones de escalación en cada touchpoint

| Touchpoint | Trigger escalación humana | Acción |
|---|---|---|
| 5. Primer mensaje | Contraindicación / red flag | Audit + notif doctora |
| 5. Primer mensaje | Confidence parser <0.5 | Audit + notif doctora |
| 6. Negociación horario | Lead pide horario específico no disponible repetidamente | Notif doctora para coordinación directa |
| 6. Negociación horario | Lead pregunta por tratamiento fuera de catálogo activo | Notif doctora |
| 8. Consulta presencial | (siempre humana — doctora) | N/A |
| 9. Post-venta | Lead reporta dolor/inflamación anormal | Notif doctora IMMEDIATE |
| 10. Recordatorio retoque | Lead pide cambio drástico de plan | Notif doctora |

---

## Anti-patterns en el journey

❌ **NO hacer follow-up agresivo** — si lead dice "más adelante", respetar (cron D5 vuelve en 7-14 días)

❌ **NO ofrecer descuento por defecto** para reactivar — solo si la doctora autoriza caso específico

❌ **NO mezclar canales sin tracking** — todo touchpoint digital debe persistir event_id

❌ **NO sobre-saturar con mensajes** — máximo 1 mensaje cada 12h de Yossie sin respuesta

❌ **NO dar diagnóstico médico desde el bot** — siempre escalar a doctora

❌ **NO romper la ilusión de Yossie como entidad consistente** — si lead pregunta "¿hablo con la doctora?", honestidad pero sin abandono ("Soy Yossie, asistente virtual de la Dra. Claudia ☺️ Si quieres hablar con ella directamente, te conecto")

---

## Versionado

**v1.0 (este doc):** 2026-05-23
**v1.1 (futuro):** post-Sprint 2.3 + 30 días bot deployment con métricas reales
**v2.0 (futuro):** post-cierre bootstrap (#13) con journey optimizado

---

**Fin journey-map.md — 2026-05-23**
