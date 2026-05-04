# Tracking Sheet — Campaña Día de la Madre 2026 (Armonización Facial)

> **Para la doctora.** Imprimí este doc + el `cheat-sheet-doctora.md` y tenelos al lado del WhatsApp durante los 6 días de campaña (4 al 9 mayo 2026).

---

## Cómo crear el Google Sheet (1 vez al inicio)

**Opción A — Importar el CSV que armé:**

1. Abrir Google Sheets nuevo
2. **Archivo → Importar → Subir** → seleccionar `tracking-sheet.csv` (en `docs/campaigns/2026-05-dia-madre/`)
3. Tipo de separador: **coma**
4. Reemplazar hoja activa
5. Guardar el Sheet con nombre: **"Leads Día de la Madre 2026"**

**Opción B — Crear manual:**

Crear hoja con estas 11 columnas en fila 1:

| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| Fecha | Hora | Nombre | Teléfono | Shortcode | Vino del web | Calidad | Tratamiento expresó | Status | Fecha cita | Notas |

---

## Tabla de shortcodes — qué significa cada código

| Shortcode | Vino de | Calidad |
|---|---|---|
| `[ARM-MAY-FB-BOFU-COLDWA]` | Ad BOFU directo a WA, no vio web | 🟥 Frío educado |
| `[ARM-MAY-FB-MOFU-COLDWA]` | Ad MOFU directo a WA, no vio web | 🟧 Tibio sin contexto |
| `[ARM-MAY-FB-MOFU-WARM]` | Ad MOFU a WA — audiencia que YA conoce Livskin | 🟧 Reactivación tibia |
| `[ARM-MAY-FB-BOFU-WARM]` | Ad BOFU a WA — audiencia que YA conoce Livskin | 🟥 Reactivación cierre |
| `[ARM-MAY-FB-TOFU-WEB]` | Ad TOFU → web → click WA | 🟩 Caliente (leyó info) |
| `[ARM-MAY-FB-MOFU-WEB]` | Ad MOFU → web → click WA | 🟧 Tibio (leyó info) |
| `[ARM-MAY-FB]` (sin sufijo) | Tráfico orgánico desde la web | ⚪ Mixto |
| Sin código | Lead orgánico (no de campaña) | ⚪ Normal |

---

## Cómo trato cada calidad de lead

| Calidad | Cómo lo trato |
|---|---|
| 🟥 **Frío educado** (BOFU sin web) | Empezar con info básica de Armonización Facial. La persona aún no leyó la propuesta. Reasegurar criterio profesional. |
| 🟧 **Tibio sin contexto** (MOFU sin web) | Saludar e invitar a explicar qué busca. Educar suave. |
| 🟧 **Reactivación tibia** (MOFU Warm) | Ya conoce Livskin. Saludar como cliente que vuelve. Sin presión, ofrecer evaluar. |
| 🟥 **Reactivación cierre** (BOFU Warm) | Ya conoce Livskin. Ir directo a fechas y disponibilidad. |
| 🟧 **Tibio leyó web** (MOFU-WEB) | Pasó por landing. Saltar info básica, pasar a fechas. |
| 🟩 **Caliente leyó web** (TOFU-WEB) | Leyó la página completa. Está procesando. Cerrar agenda rápido. |
| ⚪ **Sin código** | Lead orgánico (no de campaña). Trato normal. |

---

## Status posibles (columna I)

- **Nuevo** — recién llegó, no contactado todavía
- **Contactado** — la doctora respondió
- **Agendado** — cita confirmada
- **Asistio** — la persona vino a la cita
- **Cliente** — la persona compró/pagó tratamiento
- **No-show** — la cita estaba pero no vino
- **Descartado** — no califica / no le interesa / spam

El status se actualiza con el tiempo. Lo importante es la primera entrada al recibir el mensaje.

---

## Reglas operativas durante la campaña

1. **Responder a TODOS los mensajes nuevos** — velocidad de respuesta = métrica #1 en medicina estética. Idealmente <1h en horario laboral.
2. **NO cotizar precios definitivos por WhatsApp** — siempre "necesito verte para cotizarte exacto"
3. **NO ofrecer descuentos espontáneos** — la marca es "decide tú", no "compra ya"
4. **Si la persona quiere agendar**, agendar manual (módulo Agenda ERP llega Fase 4A post-campaña)
5. **Si llega lead muy raro o spam**, anotar igual con status `Descartado`
6. **Si te abruma el volumen** (>15/día), avisar a Dario — pausamos el ad set que más viene

---

## Lo que va a pasar con esta data al cierre (post-mortem 2026-05-12/13)

1. Dario y Claude descargan el sheet completo
2. Cruzan con costos de Facebook Ads Manager
3. Calculan por shortcode:
   - Click → mensaje real (cuántos de los X clicks WA acabaron en mensaje)
   - Cost per lead por origen (CPL)
   - Conversion rate lead → cliente
   - Cost per cliente (CAC)
4. Comparan calidad por temperatura (¿el TOFU-WEB convierte mejor que el BOFU-COLDWA?)
5. Aprenden qué destino + temperatura combinan mejor → input directo para próxima campaña

**Tu trabajo: anotar fielmente.** Sin atribución manual, perdemos toda la data del WhatsApp.

---

## Si algo sale mal

| Situación | Qué hacer |
|---|---|
| Llegan demasiados mensajes (>15/día) | Avisar a Dario, pausamos ad set que más viene |
| Mensaje sin shortcode pero parece de campaña | Anotar como `[NO-CODE]` y avisar a Dario |
| Persona molesta o agresiva | Bloquear sin explicar, marcar `Descartado` con nota |
| Sheet se rompe | Anotar en papel y cargar después |
| Doctora pide ayuda con respuesta | Reenviar mensaje a Dario para que coordine con Claude |

---

## Primer lead ya cargado en el sheet

Como referencia, ya hay 1 lead pre-cargado en el CSV:

```
Fecha:        2026-05-04
Hora:         09:41
Teléfono:     +51 968 322 731
Shortcode:    ARM-MAY-FB-BOFU-COLDWA
Calidad:      🟥 Frío educado
Status:       Contactado (doctora respondió 09:48)
Notas:        Primer lead de la campaña. Pendiente respuesta a "qué te gustaría mejorar"
```

A partir de ahí, sumá cada lead nuevo en una fila.

---

## Contact

- Cualquier duda → Dario
- Urgencia con la campaña (ad rechazado, volumen anómalo, etc.) → Dario inmediato

---

**Gracias por tu paciencia con esta primera campaña paga — es manual a propósito porque queremos aprender del proceso real antes de automatizar próximas con API.**
