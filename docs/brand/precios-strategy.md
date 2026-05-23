# Estrategia de Precios — v1.0

**Fuentes:** workbook doctora + audio encuentro (audio segmentos 877-886, 957-969, 976-978)
**Decisión doctora:** Estrategia B (rango con disclaimer + consulta gratuita) + **excepciones documentadas**
**Consume:** Bot Yossie (ask_price intent), landings, ads, email marketing

---

## 1. Estrategia maestra: B híbrida (rango con disclaimer)

**Política base:**
- Comunicar **rangos públicos** en chat/landings/ads
- Cerrar precio exacto en **consulta gratuita** con la doctora
- **Consulta acredita al primer tratamiento** (no hay costo perdido)
- Sin descuentos publicitarios agresivos

**Razón:** los productos médicos tienen costos variables por:
- Marca usada
- Cantidad de producto necesaria (especialmente Ácido Hialurónico)
- Zonas a tratar (Botox)
- Combinación de tratamientos

---

## 2. Tabla pública de precios — v1

| Tratamiento | Rango público | Política comunicación |
|---|---|---|
| **Botox** | S/250 — S/800 | Por zona; precio rango directo OK |
| **Ácido Hialurónico** | Solo en consulta | NO cotizar por WhatsApp |
| **Hilos Tensores** | S/200 — S/2000 | Rango muy amplio; preferible consulta |
| **Esperma de Salmón** | S/250 — S/500 | 3 sesiones; rango directo OK |
| **PRP** | S/200 — S/250 | Diferenciado: S/200 solo, S/250 + Dermapen |
| **Limpieza Facial** | S/80 — S/100 | Rango directo OK; entry point |
| **Exosomas** | S/250 — S/600 | Rango directo OK |

### Reglas por tratamiento

#### Botox
- ✅ Comunicar S/250 por zona desde el primer mensaje
- ✅ Aclarar: hasta 4 zonas (precio total puede llegar a S/800)
- ✅ Aclarar: 1 sesión cada 6 meses (low frequency)
- ✅ Mencionar marca (Reach) solo si lead pregunta directo

#### Ácido Hialurónico — POLÍTICA ESPECIAL
- ⚠️ **NUNCA cotizar por chat** — incluso si lead insiste
- ⚠️ Razón: precio depende mucho de cantidad de producto, variable por persona
- ⚠️ Indicar rango referencial interno: *"desde S/800"* solo si lead presiona
- ✅ Empuja consulta gratuita como next-step natural

#### Hilos Tensores
- ⚠️ Rango muy amplio (10x diferencia entre min y max)
- ✅ Comunicar rango pero invitar a consulta para precisión
- ✅ Diferenciar: hay hilos lisos + espiculados (más caros)
- ✅ Mencionar recuperación 10 días (es info relevante para timing decisión)

#### PRP
- ✅ Diferenciar precios desde el primer mensaje:
  - S/200 = solo infiltrado
  - S/250 = con Dermapen (microagujas)
- ✅ Aclarar 3 sesiones mensuales

#### Limpieza Facial (entry point)
- ✅ Precio bajo S/80 — usar como hook conversión
- ✅ Sirve para conocer a la doctora antes de tratamientos mayores
- ✅ Frequency mensual genera recurrencia natural

#### Esperma de Salmón / Exosomas
- ✅ Rango directo
- ✅ Aclarar 3 sesiones (Esperma) o 1 mensual (Exosomas)
- ✅ Mencionar diferencia: Exosomas es como Esperma + extras (péptidos, células madre)

---

## 3. Excepciones documentadas

### 3.1 Excepción "cliente recurrente" — precio directo sin disclaimer

**Cuándo aplica:** Lead identificado en ERP con ≥3 ventas históricas (`clientes_venta.cod_cliente`)

**Política:**
- Comunicar precio directo y específico (ej. *"Tu retoque está en S/250"*)
- NO mencionar consulta gratuita (ya conoce el modelo)
- Skip disclaimer "depende de zonas/cantidad"
- Permitir crédito (loyalty perk, ver §3.3)

**Justificación:** observado en chats reales (Maryori, captura 06 → *"Cuánto está el retoque" / "100 soles"* — doctora responde precio fijo sin friction).

**Implementación bot Yossie:**
```javascript
const cliente = await lookupClienteByPhone(phone);
if (cliente && cliente.ventas_historicas >= 3) {
  // Skip disclaimer, dar precio directo
  return getPriceDirectForRecurrent(treatment, cliente);
} else {
  // Standard: rango + disclaimer + consulta gratuita
  return getPriceRangeWithDisclaimer(treatment);
}
```

### 3.2 Excepción "descuento por objeción precio" — máximo S/20-30

**Cuándo aplica:** Lead expresa precio alto o compara con competencia

**Política (palabras textuales doctora — audio seg 962-964):**
> *"Lo mínimo que te puedo hacer es descuento de 30, 20 soles, le bajo, pero más de eso no."*

- Bot Yossie NUNCA aplica descuento por su cuenta
- Bot puede mencionar que la doctora "puede ajustar S/20-30 según el caso"
- Bot menciona como contexto, no como oferta cerrada
- Decisión final del descuento → en consulta con doctora

**Razón explícita doctora (audio seg 967):**
> *"Si es demasiado bajo, el producto es bastante cálido [caro]."*

→ Defensa de precio = "es por el costo del producto", NO por el margen de la clínica.

**Copy bot Yossie:**
```
Lo mínimo que la Dra. suele ajustar son S/20-30 según el caso (lo decide ella en consulta).

Más de eso no es posible — los productos médicos tienen un costo fijo de origen.
```

### 3.3 Excepción "crédito a recurrentes"

**Cuándo aplica:** Lead identificado en ERP como cliente recurrente (mismo criterio §3.1)

**Política (palabras textuales doctora — workbook + audio seg 976):**
> *"El crédito lo manejo solamente con clientes muy recurrentes."*

- NO se anuncia públicamente (no es promesa)
- Se ofrece de manera implícita en consulta con doctora
- Bot Yossie puede mencionar a recurrentes identificados

**Copy bot Yossie (recurrente identificada):**
```
{{1}}, sabes que con la Dra. podemos manejar crédito ☺️

¿Necesitas dividir el pago para este tratamiento? Coordínalo directo con ella en la consulta.
```

**Copy bot Yossie (lead nuevo que pregunta cuotas):**
```
Por ahora el pago es al momento del tratamiento ☺️

Aceptamos Yape, Plin, transferencia y efectivo.

Si te vuelves cliente recurrente y la Dra. te conoce bien, en el futuro puede manejar crédito caso por caso. Pero para primera visita es pago directo.
```

### 3.4 Excepción "viene de lejos"

**Cuándo aplica:** Lead menciona venir de fuera de Cusco (Lima, Arequipa, otra región/país)

**Política (palabras textuales doctora — audio seg 974):**
> *"Tengo consideraciones porque viene de lejos."*

**Tipos de "consideración" posibles** (a confirmar con doctora, draft):
- Horarios flexibles fuera del estándar
- Concentrar varios tratamientos en 1 visita (descuento de bundle implícito)
- Coordinación post-tratamiento remoto (followup vía WhatsApp)
- Eventual descuento por bundle (a discreción doctora)

**Copy bot Yossie:**
```
Genial que estés interesada ☺️

Para pacientes que viajan, la Dra. tiene consideraciones especiales — puede:
- Concentrar varios tratamientos en 1 visita
- Coordinar horarios flexibles
- Seguimiento por WhatsApp después

¿Qué tratamientos te interesan? Coordino con ella las mejores fechas.
```

---

## 4. Pagos aceptados

| Método | ¿Cómo? |
|---|---|
| **Yape** | QR o número doctora (compartir en consulta) |
| **Plin** | QR o número doctora |
| **Transferencia bancaria** | Datos en consulta |
| **Efectivo** | En consultorio |
| **Tarjeta de crédito** | ❌ NO disponible actualmente |
| **Cuotas (sin intereses)** | Solo a recurrentes (ver §3.3) |

**Distribución observada en ERP (88 ventas Sep-Nov 2025):**
- Efectivo: 44%
- Yape: 38%
- Plin: 12%
- Giro/transferencia: 5%
- *(distribución no cambia significativamente para outputs de captación)*

---

## 5. Consulta — política

**Costo:** Gratuita
**Duración:** ~30 minutos
**Acredita:** ✅ SÍ — el valor (implícito) se descuenta del primer tratamiento si la paciente decide hacerlo
**Mínimo:** No requiere mínimo de compra
**Cancelación:** Avisar 24h antes (cortesía, no penalidad)
**No-show:** No se cobra penalidad

**Posicionamiento copy:**
> "Consulta gratuita personalizada de 30 minutos. La Dra. evalúa tu caso y te explica las opciones. Sin compromiso de hacer ningún tratamiento ese día."

---

## 6. NO hacer (anti-patterns)

### 6.1 No usar descuentos como reclamo principal
❌ ~~"50% OFF en Botox SOLO esta semana 🔥"~~
❌ ~~"Compra 1 lleva 2 - Promoción única"~~
❌ ~~"Precio especial bloggers"~~

**Razón:** desvaloriza la marca médica + atrae clientela problemática (negociadores agresivos)

### 6.2 No cotizar Ácido Hialurónico por WhatsApp
❌ ~~"AH cuesta S/1500"~~ (puede ser S/800 o S/3000 según cantidad)
✅ *"Solo en consulta — depende mucho de la cantidad de producto"*

### 6.3 No bajar precio por defecto al primer "es caro"
❌ ~~"OK, te lo dejo en S/200 entonces"~~
✅ Mantener precio + explicar valor + ofrecer alternativa más económica (otra marca)

### 6.4 No prometer cuotas a leads nuevos
❌ ~~"Sí, podemos hacer crédito sin problema"~~
✅ *"Por ahora el pago es al momento. Si te vuelves recurrente, en el futuro la Dra. puede manejar crédito."*

### 6.5 No hablar mal de la competencia
❌ ~~"Munay Wasi usa productos peores"~~
❌ ~~"Beysa cobra menos porque su láser no es médico"~~
✅ *"Cada clínica tiene sus productos y precios. Lo que cambia es marca, experiencia de quien aplica, y seguimiento."*

---

## 7. Casos especiales — primer contacto del lead

### 7.1 Lead pregunta solo precio (sin context tratamiento)
> Lead: *"Cuánto cuesta?"*
>
> Yossie: *"Hola ☺️ ¿Qué tratamiento te interesa? Tenemos varios — Botox parte desde S/250, Limpieza Facial desde S/80, Ácido Hialurónico se cotiza en consulta. Cuéntame qué buscas mejorar."*

### 7.2 Lead pregunta por tratamiento sin precio
> Lead: *"Hola, info de botox por favor"*
>
> Yossie: *"Hola ☺️ El Botox parte desde S/250 por zona. Funciona como preventivo o correctivo para líneas de expresión, dura 4-6 meses. La consulta con la Dra. es gratuita y dura 30 minutos. ¿Quieres agendar?"*

### 7.3 Lead pregunta por paquete / múltiples tratamientos
> Lead: *"Quiero hacerme botox y ácido hialurónico, en cuánto sale?"*
>
> Yossie: *"Para combinaciones lo evalúa la Dra. en consulta — porque el precio depende mucho de qué zonas trabajar con cada uno ☺️ Botox parte desde S/250 por zona, Ácido Hialurónico se cotiza individualmente. ¿Te agendamos la consulta gratuita?"*

### 7.4 Lead identifica tratamiento + zona específica
> Lead: *"Quiero botox en la frente, cuánto?"*
>
> Yossie: *"Para 1 zona (frente) está en S/250 ☺️ Dura 4-6 meses, sin recuperación, 30 minutos de tratamiento. ¿Agendamos?"*

### 7.5 Lead recurrente identificada en ERP
> Lead: *"Hola Clau, ya toca mi retoque, cuánto?"*
>
> Yossie: *"Hola {{1}} ☺️ Te confirmo S/250 por zona como siempre. ¿Qué día te queda mejor?"*
> [lookup_erp.match=true → skip disclaimer]

---

## 8. Estacionalidad de precios (NO cambiar, pero ajustar marketing)

### Picos de demanda
- **Mayo** (Día de la Madre — picos 2-3x demanda)
- **Noviembre** (Navidad — picos 2x demanda)

**Política durante picos:**
- NO subir precios
- NO bajar precios artificialmente
- SI saturar agenda (pueden requerir más anticipación de coordinación)
- SI concentrar ads paid pre-pico (2-3 semanas antes)

### Valles
- Febrero-Marzo (post temporada alta)
- Junio-Octubre (excepto Día Padre junio)
- Diciembre tardío (post-Navidad)

**Política durante valles:**
- Foco en re-engagement de inactivas
- Promoción de tratamientos sin estacionalidad (PRP, Limpieza, Esperma Salmón)
- NO descuentos públicos — pero SÍ ofertar bundles a recurrentes vía WhatsApp directo

---

## 9. Métricas a trackear

| Métrica | Cómo medir | Target v1 |
|---|---|---|
| **Conversion ask_price → consulta agendada** | Vtiger leads / WA conversations | ≥35% |
| **Cancelación post-precio recibido** | Audit `wa_message_sent` → silencio >48h | ≤25% |
| **Negociación de descuento (red flag)** | Audit `red_flag_aggressive_negotiation` | ≤10% leads |
| **Ticket promedio primer tratamiento** | ERP `clientes_venta` filter por `primera_venta=true` | ≥S/400 |
| **% recurrencia 6 meses** | ERP clientes con ≥2 ventas | ≥40% |

**Distribución actual histórica (ERP 88 ventas Sep-Nov 2025):**
- Ticket promedio: S/409
- Tratamiento más común: Botox (50.1% revenue share)
- Recurrencia: a calcular post-deployment Yossie

---

## 10. Versionado

**v1.0 (este doc):** 2026-05-23 — basado en workbook + audio encuentro
**v1.1 (futuro):** post-Sprint 2.3 + 100+ conversaciones → ajustes según conversion rates
**v2.0 (futuro):** post-2da campaña paga → estrategia consolidada

**Cuándo revisar:**
- Si conversion ask_price → consulta agendada cae <25%
- Si ticket promedio cae >15% trimestre vs trimestre
- Si doctora ajusta política de marcas/cuotas/descuentos
- Si entra aparatología nueva al consultorio (cambia oferta)

---

**Fin precios-strategy.md — 2026-05-23**
