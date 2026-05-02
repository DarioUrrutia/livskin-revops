# Tracking sheet template — Bridge Episode WhatsApp directo

> **Para la doctora.** Imprimí este cheat sheet o tenelo abierto en pantalla mientras atendés WhatsApp durante la campaña (5 días, 2026-05-04 a 2026-05-09 estimado).

---

## Cómo funciona

Cuando lance la campaña, los anuncios de Facebook van a llevar tráfico a tres destinos:
1. Landing Botox (formulario web — atribución automática, no necesitás hacer nada)
2. Landing PRP (idem)
3. **Tu WhatsApp directo** ← acá tenés que ayudar a anotar

Cuando alguien clickea el ad de Facebook que va al WhatsApp, **WhatsApp se abre con un mensaje pre-llenado** con un código en corchetes. La mayoría manda el mensaje sin editar.

Vos vas a ver mensajes nuevos como:
> *"Hola, vi su anuncio de Botox **[BTX-MAY-FB]**"*

El código entre corchetes es el que necesitamos para saber de qué campaña vino esa persona.

---

## Tabla de códigos

| Código que ves en el mensaje | Significado |
|---|---|
| `[BTX-MAY-FB]` | Anuncio de Botox en Facebook |
| `[PRP-MAY-FB]` | Anuncio de PRP en Facebook |
| `[GEN-MAY-FB]` | Anuncio genérico (sitio web) en Facebook |
| Sin código | Lead orgánico (no de campaña) — anotar igual con código `[ORGANIC]` |

---

## Qué anotar

**Para CADA mensaje nuevo de WhatsApp durante los 5 días de campaña**, copiar a un Google Sheet con estas columnas:

| Fecha | Hora | Phone | Código visto | Tratamiento de interés | Status | Notas |
|---|---|---|---|---|---|---|
| 2026-05-05 | 14:23 | +51999111222 | BTX-MAY-FB | Botox + Hilos | Contactado | Quiere venir el sábado |
| 2026-05-05 | 18:45 | +51988333444 | PRP-MAY-FB | PRP capilar | Agendado | Cita 2026-05-08 16:00 |
| 2026-05-06 | 10:00 | +51977555666 | (sin código) | Limpieza facial | ORGANIC | Lead orgánico, no atribuir |
| ... | | | | | | |

**Status posibles:**
- `Nuevo` — recién llegó, no contactado todavía
- `Contactado` — la doctora respondió
- `Agendado` — cita confirmada
- `Asistio` — la persona vino a la cita
- `Cliente` — la persona compró/pagó tratamiento
- `No-show` — la cita estaba pero no vino
- `Descartado` — no califica / no le interesa / spam

**El status se actualiza con el tiempo.** Lo importante es la primera entrada al recibir el mensaje.

---

## Google Sheet recomendado

Crear un Sheet nuevo con esta estructura:

```
Hoja 1 — "Leads WA Campaña Mayo 2026"
   Columnas A-G: Fecha | Hora | Phone | Código | Tratamiento_interés | Status | Notas
```

Compartir el sheet con Dario en modo edit.

---

## Lo que pasa con esta data

Al final de los 5 días (~2026-05-09), Dario y Claude:

1. Cargan los datos del sheet a una tabla en el ERP
2. Cruzan con costos de Facebook Ads Manager
3. Calculan:
   - Cost per lead (CPL) por código
   - Conversion rate de lead → cliente por código
   - Cost per cliente (CAC) por código
4. Comparan con landings (Botox + PRP) que se atribuyeron automáticamente
5. Aprenden qué destino convierte mejor → decide próxima fase

**Tu trabajo: anotar fielmente.** Sin atribución manual, perdemos toda la data del WhatsApp directo.

---

## Reglas operativas durante la campaña

1. **Responder a TODOS los mensajes nuevos** — la velocidad de respuesta es la métrica #1 de campañas WA en medicina estética
2. **NO cotizar precios definitivos por WhatsApp** — siempre "necesito verte para cotizarte exacto"
3. **Si la persona quiere agendar**, agendar manual (esta campaña es PRE-módulo Agenda en ERP)
4. **Si llega lead muy raro o spam**, anotar igual con status "Descartado"
5. **Si te abruma el volumen**, avisar a Dario inmediatamente — pausamos el ad

---

## Si algo sale mal

| Situación | Qué hacer |
|---|---|
| Llegan demasiados mensajes (>20/día) | Avisar a Dario, pausamos ad set 3 |
| Mensaje sin código pero con UTM en el text | Anotar como `[OTRO]` y avisar a Dario para investigar |
| Persona molesta o agresiva | Bloquear sin explicar, marcar `Descartado` con nota |
| Sheet se rompe | Anotar en papel y cargar después |

---

## Contact

- Cualquier duda → Dario
- Cualquier urgencia con la campaña (ej. ad rechazado por Facebook) → Dario inmediato

---

**Gracias por tu paciencia con esta primera campaña — es manual a propósito porque queremos aprender del proceso real antes de automatizar.** 🚀
