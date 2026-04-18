# Conversation Agent

**Rol:** primera línea de atención al paciente potencial a través de WhatsApp. El agente que más impacta la conversión porque la velocidad y calidad de respuesta inicial definen si el lead se convierte o se enfría.

**Fase de construcción:** Fase 4 (Semana 6)

## Objetivo

- Responder en **<60 segundos** a todo mensaje entrante
- Conocer tratamientos, precios, horarios, brand voice
- Mantener conversación autónoma en preguntas frecuentes
- Acceder a calendario real de Vtiger para proponer horarios
- Registrar toda conversación en segundo cerebro + Vtiger
- Escalar a la doctora cuando corresponda

## Tools (a implementar)

- `vtiger_get_lead(phone)` → recupera contexto del paciente
- `vtiger_update_lead(id, fields)` → tags, notas (no teléfono/email)
- `whatsapp_send(phone, message)` → envía respuesta
- `calendar_check_availability(date_range)` → consulta agenda doctora
- `calendar_create_event(patient_id, datetime, treatment)` → agenda cita
- `brain_get_patient_history(patient_id)` → L4 del cerebro, historial exacto
- `brain_search_similar_conversations(msg_embedding, limit=5)` → L4 precedentes
- `brain_get_clinic_knowledge(topic)` → L1 catálogo autoritativo

## Escalación a doctora

Triggers (ADR-0033):

- Pregunta médica específica (contraindicaciones, medicación, condiciones salud)
- Solicitud de precio complejo / negociación
- Señales claras de intención de compra inmediata
- Caso VIP / referido alto valor

**Protocolo:** WhatsApp a número personal doctora con:
- Link al Lead en Vtiger
- Resumen de la conversación (últimos 5 mensajes)
- Razón de escalación
- Doctora responde directo al paciente
- Sistema detecta "handoff done" y lo registra

## Lead scoring integrado

Cada lead se puntúa al inicio (ADR-0035):
- Mujer 35-60 → +15
- Fuente paid → +20
- Ya fue cliente → +30
- Responde rápido → +15
- Pregunta por tratamiento específico → +10

Score 0-100 se usa para priorizar escalaciones.

## Referencias

- ADR-0029 — Conversation Agent (completo, Fase 4)
- ADR-0033 — Escalación a doctora
- ADR-0035 — Lead scoring v1
- ADR-0038 — WhatsApp test number

## Estado actual

⏳ Pendiente — construcción en Fase 4 (Semana 6 del roadmap).
