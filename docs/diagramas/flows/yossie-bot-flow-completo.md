# Flow completo bot Yossie v2 + F1 follow-up

> **Cómo ver**: este archivo se ve mejor en Obsidian, VS Code (con plugin Mermaid) o GitHub.
> Los bloques ```mermaid``` se renderizan automáticamente.
> Última actualización: 2026-05-26

---

## 1. Flow conversacional — primera interacción del lead

```mermaid
flowchart TD
    Start([Lead manda WA al +51 947 741 117]) --> InternalCheck{Phone interno?<br/>Dario / Doctora 1 / Doctora 2}
    InternalCheck -- Sí --> NoAction[no_action: ignora]
    InternalCheck -- No --> Delay[Bot espera 2-5s aleatorio<br/>humaniza]
    Delay --> DetectProd{¿Detecta tratamiento<br/>en referral del ad o texto?}

    DetectProd -- Sí, detecta --> SaludoQ2[Saludo + Q2 directo<br/>'¿Es tu primera vez con X?']
    DetectProd -- No --> SaludoQ1[Saludo + Q1<br/>'¿En qué tratamiento te oriento?']

    SaludoQ1 --> Q1{Q1 — 3 botones}
    Q1 -- Botox --> Q2
    Q1 -- Ácido Hialurónico --> Q2
    Q1 -- Otro tratamiento --> HandoffOther[HANDOFF: flag wants_other_treatment]

    SaludoQ2 --> Q2{Q2 — 2 botones}
    Q2 -- Primera vez --> Q3
    Q2 -- Ya me he hecho --> Q3
    Q2 -- texto libre no parseable --> HandoffUnp[HANDOFF: flag unparseable]

    Q3{Q3 — Urgencia} -- Lo antes posible --> CloseHigh[CIERRE + HANDOFF<br/>urgency: HIGH]
    Q3 -- 2-3 semanas --> CloseMed[CIERRE + HANDOFF<br/>urgency: MEDIUM]
    Q3 -- Solo averiguando --> Q4

    Q4{Q4 — Painpoints} -- Precios --> CloseInfo[CIERRE + HANDOFF<br/>flag: info_request precios]
    Q4 -- Ubicación --> CloseInfo
    Q4 -- Otra duda --> CloseInfo

    CloseHigh --> Notif
    CloseMed --> Notif
    CloseInfo --> Notif
    HandoffOther --> Notif
    HandoffUnp --> Notif
    Notif[3 notifs vía template<br/>Dario + Doctora 1 + Doctora 2]
    Notif --> Vtiger[Crear Vtiger Lead<br/>+ ERP via B3 cron]
    Vtiger --> Escalated([state: escalated])

    classDef happyPath fill:#d4f1d4,stroke:#2d8a2d
    classDef escalate fill:#fff3cd,stroke:#856404
    classDef terminal fill:#e3f2fd,stroke:#0d47a1
    class CloseHigh,CloseMed,CloseInfo happyPath
    class HandoffOther,HandoffUnp escalate
    class Escalated,NoAction terminal
```

---

## 2. Escape hatches — interrumpen el flow en cualquier momento

```mermaid
flowchart TD
    InAnyState([En cualquier state qualifying]) --> Check{¿Texto del lead matchea?}
    Check -- 'embarazada/cáncer/anticoagul' --> RedFlag[🚨 RED FLAG<br/>HANDOFF urgencia HIGH<br/>flag: red_flag_X]
    Check -- 'cuánto cuesta/precio/caro' --> Price[💰 PRICE OBJECTION<br/>respuesta empática + HANDOFF<br/>flag: price_objection]
    Check -- 'hablar con doctora' --> Human[👤 ESCAPE TO HUMAN<br/>HANDOFF directo<br/>flag: lead_requested_human]

    RedFlag --> Escalated
    Price --> Escalated
    Human --> Escalated
    Escalated([state: escalated])

    classDef urgent fill:#f8d7da,stroke:#721c24
    class RedFlag urgent
```

---

## 3. F1 — Follow-up 4h (cron cada 15 min)

```mermaid
flowchart TD
    Cron([Cron F1 cada 15 min]) --> Query[GET pending-followup<br/>state=qualifying<br/>+ last_inbound &lt; NOW-4h<br/>+ followup_sent != true<br/>+ snoozed_until &lt; NOW]
    Query --> Leads{¿Hay leads pendientes?}
    Leads -- No --> Skip([skip])
    Leads -- Sí, X leads --> Loop[Para cada lead]
    Loop --> SendTpl[Send template Meta:<br/>lead_waiting_4h_followup_v1<br/>vars: nombre + tratamiento]
    SendTpl --> Sanitize{¿Nombre válido?}
    Sanitize -- Sí --> UseFirstName[Solo primer nombre<br/>'Gladys Portugal Dueñas' → 'Gladys']
    Sanitize -- No --> NoName["Saludo sin nombre<br/>'Hola ☺️'"]
    UseFirstName --> SetFlag
    NoName --> SetFlag
    SetFlag[Update wa_state:<br/>followup_sent=true<br/>followup_sent_at=NOW] --> Wait([Lead recibe template])

    Wait --> LeadResp{¿Lead responde?}
    LeadResp -- 'Sí, sigo interesada' --> FU_Yes[Bot: 'Genial. Le paso a la Dra'<br/>HANDOFF inmediato<br/>state: escalated]
    LeadResp -- 'Más tarde respondo' --> FU_Later[Bot: 'Te escribimos mañana'<br/>snoozed_until = NOW+24h<br/>reset followup_sent=false<br/>state: qualifying]
    LeadResp -- 'Ya no, gracias' --> Q5_Optin[Bot pregunta opt-in<br/>'¿promociones o eliminar datos?']
    LeadResp -- silencio total --> ColdLead[lead frío<br/>queda en state qualifying<br/>F1 NO reenvía<br/>⚠️ GAP]

    Q5_Optin --> Q5Resp{¿Respuesta?}
    Q5Resp -- 'Sí, mantenme' --> OptInYes[state: closed<br/>opt_in_marketing=true<br/>queda en lista promos]
    Q5Resp -- 'No, eliminar' --> OptInNo[state: closed<br/>opt_in_marketing=false<br/>request_data_deletion=true<br/>⚠️ GAP: nadie procesa el delete]

    FU_Later --> WaitSnooze[24h pasan...]
    WaitSnooze --> Query

    classDef good fill:#d4f1d4
    classDef gap fill:#f8d7da,stroke:#721c24
    class FU_Yes,OptInYes good
    class ColdLead,OptInNo gap
```

---

## 4. Estados completos en `wa_conversation_state`

```mermaid
stateDiagram-v2
    [*] --> new: Lead inbound 1ra vez
    new --> qualifying: Bot envía Q1 o Q2

    state qualifying {
        [*] --> q1
        q1 --> q2: respuesta válida
        q2 --> q3: respuesta válida
        q3 --> q4: 'averiguando'
        q3 --> [*]: 'asap' o '2-3 sem' → escalated
        q4 --> [*]: cualquier opción → escalated

        q1 --> snoozed: 'Más tarde respondo' (F1)
        q2 --> snoozed: 'Más tarde respondo' (F1)
        q3 --> snoozed: 'Más tarde respondo' (F1)
        snoozed --> q1: 24h pasaron, F1 reenvía

        q1 --> q5_optin: 'Ya no, gracias' (F1)
        q2 --> q5_optin
        q3 --> q5_optin
    }

    qualifying --> escalated: handoff (Q3 close, Q4, red_flag, price_obj, escape, FU_yes)
    qualifying --> closed: Q5_optin respondido (sí o no)

    escalated --> [*]: humano (Dario/doctora) toma over
    closed --> [*]: terminal

    note right of escalated
        Doctora atiende manualmente.
        Bot ya no responde
        (excepto en internal phones)
    end note

    note right of closed
        Lead descartado por decisión.
        Si opt_in=true: queda para promos.
        Si opt_in=false: data debe borrarse.
    end note
```

---

## 5. ⚠️ GAPS IDENTIFICADOS (sin resolver — control que necesitas)

### A. Lead que NO responde NUNCA (ni al primer mensaje ni al follow-up)
**Estado actual**: queda en `qualifying` con `followup_sent=true`. F1 NO reenvía. Nadie hace nada. Lead "muere" en silencio.

**Propuesta de fix**:
- Tras 48h-72h sin respuesta post-followup → marcar `state=closed_cold` automáticamente
- Workflow F2: cron diario que detecta `qualifying` + `followup_sent=true` + silencio > 72h → cierra como `closed_cold`
- Opcional: 2do follow-up suave a las 72h (template MARKETING aprobado: `reengagement_inactive_30d_v1` modificado)

### B. Lead pide "No, eliminar mis datos" — NADIE elimina realmente
**Estado actual**: bot pone `request_data_deletion=true` en context_json. Pero NO existe workflow que procese esa bandera y haga DELETE cross-system.

**Propuesta de fix**:
- Workflow F3 (cron diario): GET leads con `request_data_deletion=true AND state=closed`
- Para cada uno:
  - Delete `wa_messages WHERE phone_lead=X`
  - Delete `wa_conversation_state WHERE phone_lead=X`
  - Delete lead Vtiger asociado (cascade)
  - Delete `leads` ERP asociado
  - Audit log: `system.gdpr_data_deletion` (preservar el registro de que se borró, sin PII)

### C. Lead manda emoji / sticker / imagen / audio en lugar de texto
**Estado actual**: bot detecta `type` (text, button, interactive, image, audio, document, location) pero solo PROCESA `text` y `button`. Si manda imagen/audio/sticker, bot lo trata como texto vacío → cae en `handoff_unparseable`.

**Propuesta de fix**:
- Si type=image → bot responde "Recibí tu imagen. Le paso a la Dra. para que la revise ☺️" + handoff con flag `lead_sent_image`
- Si type=audio → ídem con flag `lead_sent_audio`
- Si type=sticker → ignorar (no responder, common WA quirk)

### D. Lead responde con texto libre POST-cierre (state=escalated)
**Estado actual**: bot retorna `no_action` (correcto — humano takes over). Pero ¿la doctora se entera del mensaje?

**Propuesta de fix**:
- Verificar: ¿la doctora recibe automáticamente el mensaje del lead post-escalado vía Meta? Sí, porque su WA está conectado al número Livskin (24h window abierta).
- Si NO → agregar fallback que reenvíe a doctora un mensaje "el lead te escribió X"

### E. Bot envió template follow-up pero Meta lo rechazó (failed)
**Estado actual**: F1 marca `followup_sent=true` aunque Meta NO entregue (ej. número inválido, bloqueo de usuario).

**Propuesta de fix**:
- F1 verifica el status callback de Meta antes de marcar followup_sent
- Si Meta devuelve `failed` → log error + NO marcar followup_sent → permitir retry en próximo ciclo

### F. Conversación queda atorada en `qualifying:q5_optin` sin respuesta
**Estado actual**: si lead recibe pregunta opt-in pero no responde, queda en limbo. No hay follow-up para Q5.

**Propuesta de fix**:
- Default tras 7 días sin respuesta a Q5: asumir `opt_in_marketing=false` + cerrar (privacy-default-deny)

### G. Race condition: lead manda 2 mensajes seguidos
**Estado actual**: si lead manda "Hola" y 5 segundos después "vi su anuncio botox" — Meta dispara 2 webhooks. Bot procesa ambos pero el segundo lee state que el primero acaba de actualizar. Posible inconsistencia.

**Propuesta de fix**:
- Lock optimista en wa_conversation_state (campo `version` o `updated_at` con WHERE en UPDATE)
- O cola serializada en n8n (pero complica arquitectura)
- O acceptar que es un edge case raro (<1% probable) y dejar

### H. Doctora responde al lead DESDE su WhatsApp personal (no desde el número Livskin)
**Estado actual**: la doctora ve la notif del bot Yossie + tiene número Livskin asociado vía 24h window. Pero si responde al lead DESDE su número personal (+51 910 848 995), el lead recibe mensaje desde un número desconocido — confusión.

**Propuesta de fix**:
- La doctora DEBE responder desde el número Livskin (+51 947 741 117) — no desde su personal
- Esto NO es un gap técnico sino operacional. Requiere capacitación + clarificación con doctora.

### I. Campaña Meta sigue corriendo después que se agote el lifetime budget S/350
**Estado actual**: Meta auto-pausa la campaña cuando se agota el cap. ✅ No es gap.

### J. Template Meta `doctor_lead_notification_v1` no incluye el flag (red_flag, price_objection)
**Estado actual**: la doctora recibe nombre+tel+tratamiento+experiencia+urgencia+mensaje. Pero NO le llega el `flag` (ej. "el lead tiene una contraindicación médica" o "objetó precio").

**Propuesta de fix**:
- Modificar template para incluir 7ma variable `{{7}}` con `flag` legible
- Re-submit a Meta (~24-48h aprobación)
- O usar templates distintos según flag (varios templates pre-aprobados)

---

## 6. Prioridad de fixes (matriz)

| Gap | Severidad | Impacto operacional | Esfuerzo fix |
|---|---|---|---|
| A — Lead frío sin cerrar | 🟡 Media | Métricas inflan "qualifying" | 1h workflow F2 |
| B — Data deletion no ejecuta | 🔴 ALTA (compliance) | Bot dice "te elimino" pero NO se elimina | 2h workflow F3 |
| C — Lead manda imagen/audio | 🟡 Media | ~5-10% de leads van por esta vía | 1h handlers |
| D — Mensaje post-escalado | 🟢 Baja | Resuelto automáticamente | 0h (verificación) |
| E — F1 marca sent aunque Meta failed | 🟡 Media | Pierde retries | 30min check status callback |
| F — Q5_optin sin respuesta | 🟢 Baja | Edge case raro | 30min default deny |
| G — Race condition msgs simultáneos | 🟢 Baja | <1% probable | 1-2h locks (no urgente) |
| H — Doctora responde desde personal | 🟡 Media | UX confuso lead | 0h tecnológico (capacitación) |
| J — Template doctora sin flag | 🟡 Media | Doctora pierde contexto crítico | 1h + 48h approval Meta |

**Total fixes urgentes** (B + A + C + E): ~5h trabajo.

---

## 7. Próximos pasos sugeridos

1. **Hoy**: revisar este árbol contigo en Obsidian — validar comprensión
2. **Hoy/mañana**: priorizar qué gaps arreglamos (recomiendo B, A, C, E)
3. **Semana**: implementar fixes prioritarios + smoke tests
4. **Continuo**: aplicar protocolo de detección de gaps (memoria `feedback_sistematizar_deteccion_gaps`) en cada flow nuevo
