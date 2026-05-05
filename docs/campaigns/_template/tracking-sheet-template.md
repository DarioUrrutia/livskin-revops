# Tracking Sheet — {{CAMPAIGN_NAME}}

> **Para la doctora.** Imprimí este doc + el `cheat-sheet-doctora.md` y tenelos al lado del WhatsApp durante la campaña.

---

## Cómo crear el Google Sheet (1 vez al inicio)

**Opción A — Importar el CSV:**

1. Abrir Google Sheets nuevo
2. **Archivo → Importar → Subir** → seleccionar `tracking-sheet.csv`
3. Tipo de separador: **coma**
4. Reemplazar hoja activa
5. Guardar como: **"Leads {{CAMPAIGN_NAME}}"**

**Opción B — Crear manual:**

11 columnas en fila 1:
| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| Fecha | Hora | Nombre | Teléfono | Shortcode | Vino del web | Calidad | Tratamiento expresó | Status | Fecha cita | Notas |

---

## Tabla de shortcodes — qué significa cada código

(referenciar `cheat-sheet-doctora.md` con los shortcodes específicos de esta campaña)

---

## Status posibles (columna I)

- **Nuevo** — recién llegó, no contactado
- **Contactado** — la doctora respondió
- **Agendado** — cita confirmada
- **Asistio** — la persona vino a la cita
- **Cliente** — la persona compró/pagó tratamiento
- **No-show** — la cita estaba pero no vino
- **Descartado** — no califica / no le interesa / spam

---

## Tip: dropdown del status

1. Seleccionar columna **I (Status)** completa
2. **Datos → Validación de datos → + Agregar regla**
3. Criterios: **Lista desplegable**
4. Opciones:
   ```
   Nuevo
   Contactado
   Agendado
   Asistio
   Cliente
   No-show
   Descartado
   ```
5. Listo — dropdown visual para la doctora

---

## Reglas operativas

(referenciar `cheat-sheet-doctora.md` § Reglas básicas)

---

## Lo que pasa con esta data al cierre

1. Operador descarga el sheet completo
2. Cruza con costos de Facebook Ads Manager
3. Calcula CPL, conversion rate, CAC por shortcode
4. Compara calidad por temperatura
5. Aprende qué funcionó → input para próxima campaña

**Tu trabajo: anotar fielmente.** Sin atribución manual, perdemos toda la data del WhatsApp.

---

## Contact

- Cualquier duda → operador
- Urgencia → inmediato

---

**Gracias por tu paciencia con esta campaña.**
