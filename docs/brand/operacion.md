# Operación Livskin — v1.0

**Fuentes:** workbook doctora + audio + chats reales
**Consume:** Bot Yossie (agenda + FAQ), landings FAQ, ads creative location, email signature

---

## Información práctica

### Dirección

**Urbanización La Florida O-7, Wanchaq, Cusco**

**Referencia:** Detrás del templo de los Mormones, media cuadra encima.

**Google Maps:** *(pendiente confirmar coords exactas)*

### Horario

**Política:** Todo previa coordinación, **horarios flexibles**.

**Horario observado en chats reales:**
- Mañana: desde 8:00 am
- Tarde: hasta 8:00-9:00 pm
- Excepciones: temprano (5-6 am) o tarde (10 pm) con coordinación
- **Domingos:** sí trabajan, previa coordinación
- **Feriados:** mayoría sí trabajan (confirmado: 1 mayo = *"Trabajo normal"*)

**Política comunicación bot Yossie:**
```
La Dra. atiende previa coordinación con flexibilidad — temprano, tarde, incluso domingos.

¿Qué horario te queda mejor? Coordino con ella y te confirmo.
```

### Duración tratamientos (referencia para agenda)

| Tratamiento | Duración | Recuperación |
|---|---|---|
| Botox | 30 min | Sin recuperación |
| Ácido Hialurónico | 40 min | Sin recuperación |
| Hilos Tensores | 45 min | 10 días recuperación |
| Esperma de Salmón | 1 hora | Sin recuperación |
| PRP | 1-1.5 horas | Sin sol 48h |
| Limpieza Facial | 1 hora (o 1h 20min) | Sin recuperación |
| Exosomas | 1 hora | Sin recuperación |
| **Consulta gratuita** | **30 min** | N/A |

### Capacidad agenda

**Modelo actual:** doctora atiende sola, sin asistentes.
- 1 paciente por slot
- Slots de 30 min mínimo (consulta) hasta 1.5h (PRP)
- Total slots disponibles/día: 6-8 (variable según mix tratamientos)

**Días pico:** TBD (a calcular post-deployment con data ERP appointments — pendiente migration 0009)

**Estacionalidad agenda:**
- **Mayo + Noviembre** picos (Día Madre + Navidad) → reservar slots con más anticipación
- **Junio + Febrero** valles → fácil agenda mismo día

### Cancelación

**Política:** Avisar **24 horas antes**.

**Razón:** profesional respeto al tiempo de la doctora (no es estricto, es cortesía).

**Política bot Yossie:**
```
Si necesitas reagendar, avísanos con 24h de anticipación si es posible ☺️

Si surge una emergencia, también podemos reagendar — solo escríbeme.
```

### No-show

**Política:** **NO se cobra penalidad**. Cero drama.

**Observación de chats reales:**
- Maryori: *"Me olvidé de ir el viernes mil disculpas"* → doctora reagenda sin reclamo
- Siomara: *"Me olvidé"* → reagendamiento inmediato

**Por qué importa:** marca confianza con clientela recurrente, evita pérdida de leads por miedo a multa.

**Política bot Yossie:**
```
Tranquila ☺️ No hay problema, pasan cosas.

¿Cuándo te queda mejor reagendar? La Dra. tiene flexibilidad de horarios.
```

### Pagos aceptados

| Método | Aceptado | Notas |
|---|---|---|
| Efectivo | ✅ | 44% de ventas históricas |
| Yape | ✅ | 38% de ventas (QR o número doctora) |
| Plin | ✅ | 12% de ventas |
| Transferencia bancaria | ✅ | 5% de ventas |
| Tarjeta de crédito | ❌ | NO disponible actualmente |
| Cuotas sin intereses | Solo recurrentes | Loyalty perk (ver `precios-strategy.md` §3.3) |

### Parking

**Gratis** (espacio limitado en la calle frente al consultorio).

### WiFi

**(TBD — workbook vacío)**

### Vacaciones doctora

**(TBD — workbook vacío)**

**Política bot Yossie cuando no hay info disponible:**
```
Déjame consultar con la Dra. y te confirmo en breve ☺️
```

---

## Reglas operativas Bot Yossie

### Cuando agendar cita

**Flujo deseable:**
```
1. Lead pide cita o muestra interés alto en tratamiento
2. Yossie pregunta qué horario le queda mejor
3. Lead propone (ej. "viernes a las 5pm")
4. Yossie verifica disponibilidad:
   - Si tabla `appointments` existe (post-migration 0009) → query directo
   - Si NO existe aún → escala a doctora para coordinación manual
5. Si disponible → confirma cita (template `lead_confirmed_appointment`)
6. Si no disponible → propone 2 alternativas (template `lead_proposed_alternatives`)
7. Una vez confirmada → schedule reminders T-24h y T-3h
```

### Reglas duras agenda

1. **Mínimo 2h de anticipación** para agendar (no last-minute < 2h sin escalación)
2. **Máximo 30 días en el futuro** (eventos lejanos requieren reconfirmación)
3. **NUNCA double-booking** (verificar slot disponible antes de confirmar)
4. **Slots respetan duración de tratamiento** (no offer Botox de 30min en slot de 15min)
5. **Domingos requieren escalación a doctora primero** (no confirmar autoauto)
6. **Horarios atípicos (antes 8am o después 8pm) requieren escalación** (no autoaprobar)

### Comunicación de la dirección

**Bot Yossie SIEMPRE incluye:**
- 📍 Urbanización La Florida O-7, Wanchaq, Cusco
- Referencia: "detrás del templo de los Mormones, media cuadra encima"

**En reminders + confirmación:**
```
📍 Urbanización La Florida O-7, Wanchaq
Detrás del templo de los Mormones, media cuadra encima.
```

---

## Flujo del día — checklist operativo doctora

### Antes del día (T-24h)

- [ ] Bot Yossie envía template `appointment_reminder_24h` a pacientes con cita mañana
- [ ] Pacientes confirman vía botones quick reply
- [ ] Doctora ve agenda del día siguiente en ERP

### Día mismo (T-3h)

- [ ] Bot Yossie envía template `appointment_reminder_3h`
- [ ] Pacientes confirman asistencia o reagendan

### Durante el día

- [ ] Doctora atiende pacientes
- [ ] Doctora marca asistencia en ERP (workflow A2 sync a Vtiger automático)
- [ ] Si paciente hace tratamiento → registra venta + pago en ERP

### Después del día

- [ ] Bot Yossie envía follow-up 24h post-tratamiento (próximo día)
- [ ] Si paciente tiene plan de sesiones → schedule próxima

---

## Templates útiles para Yossie (operación)

### Confirmación cita
Ver `integrations/whatsapp/templates/drafts-v1.md` § Template #2 `lead_confirmed_appointment`

### Reagendamiento solicitado por lead
```
Claro {{1}} ☺️

¿Qué día te queda mejor? La Dra. tiene flexibilidad — temprano, tarde, domingos también si es necesario.
```

### Cancelación por lead
```
Oki {{1}}, entendido.

Si más adelante quieres volver a agendar, aquí estoy. Estamos en contacto ☺️
```

### Pregunta por dirección
```
📍 Estamos en Urbanización La Florida O-7, Wanchaq, Cusco.

Detrás del templo de los Mormones, media cuadra encima.

Hay parking gratis frente al consultorio ☺️
```

### Pregunta por pagos
```
Aceptamos Yape, Plin, transferencia y efectivo ☺️

El pago es al momento del tratamiento.
```

### Pregunta por horario disponible
```
La Dra. atiende previa coordinación con bastante flexibilidad — desde temprano hasta tarde, incluso domingos.

¿Qué día y horario te queda mejor? Coordino con ella.
```

---

## Reglas de escalación operativa

### Escalación inmediata a doctora

- Lead solicita atención < 2h (last-minute)
- Lead solicita horario atípico (antes 8am o después 9pm)
- Lead solicita domingo
- Lead reagenda 2+ veces en mismo plan
- Lead reporta efecto adverso post-tratamiento

### Escalación normal (puede esperar 4-24h)

- Lead pide tratamiento fuera del catálogo activo
- Lead pregunta sobre tratamiento combinado complejo
- Lead pregunta por descuento >S/30
- Lead trae caso médico que requiere evaluación

### Sin escalación (Yossie maneja)

- Agendar dentro de horario estándar (8am-8pm, lunes-sábado)
- Responder painpoints estándar (ver `painpoints-responses.md`)
- Confirmar dirección + horario + pagos
- Cancelaciones simples
- Reminders automáticos
- Follow-up post-venta

---

## KPIs operativos

| Métrica | Target v1 |
|---|---|
| **Tiempo respuesta primer mensaje** | <60s (bot) |
| **Tiempo confirmación cita** | <5 min (con doctora) |
| **% asistencia con reminder T-3h** | ≥85% |
| **% no-show no recuperable** | <10% |
| **% reagendamientos** | <30% |
| **Capacidad agenda utilizada** | ≥70% (post-pico mayo/noviembre) |

---

## Validación pendiente

🟡 WiFi disponible para pacientes — confirmar con doctora
🟡 Política vacaciones doctora (semanas off al año, anticipación aviso)
🟡 Coords exactas Google Maps
🟡 Días picos exactos (post-deployment con data appointments)
🔴 Plan de cobertura si doctora se enferma / emergencia (no hay backup actualmente)

---

**Fin operacion.md — 2026-05-23**
