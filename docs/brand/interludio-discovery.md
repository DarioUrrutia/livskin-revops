# Interludio Estratégico — Bitácora de Discovery con la Doctora

> **Propósito**: extraer de la doctora (en sesión de 3-4h) la información cualitativa de alta calidad que necesitamos para construir el bot-broker WhatsApp + las campañas paid (FB/Google) + los flujos email + el customer journey completo del sistema RevOps Livskin.
>
> **Quién lo usa**: Dario, durante la conversación cara a cara con la doctora.
>
> **Cómo se usa**:
> 1. Dario lee este documento ANTES del encuentro (entiende qué buscamos)
> 2. Trae todo lo de la sección "Preparación previa" (data que ya tenemos en sistema)
> 3. Conduce la conversación siguiendo los 9 bloques abajo
> 4. Toma notas / graba audio (con permiso) / pide screenshots de chats
> 5. Después del encuentro: codifica las respuestas en los outputs específicos (brand voice doc, customer journey maps, copy bot, etc.)
>
> **Tiempo estimado encuentro**: 3-4h. Divisible en 2 sesiones de 2h si necesario.
> **Tiempo Dario codificar outputs post-encuentro**: 4-6h con Claude Code.

---

## 0. Filosofía del bot que estamos construyendo (contexto a tener claro antes)

Antes de la conversación con la doctora, Dario tiene que tener internalizado QUÉ tipo de bot vamos a construir. Hay 2 posturas filosóficas y elegimos la 2da:

### Postura A (mediocre, descartada) — Bot pasivo reactivo

- Cliente escribe → bot responde solo lo preguntado
- Cliente pregunta precio → bot da rango genérico o deriva a humano
- Cliente silencia → bot no hace nada
- Resultado: chat impersonal que se puede reemplazar con un FAQ web

### Postura B (top de gama, la que vamos a construir) — Bot guía activo SUTIL

- Cliente escribe → bot responde + **avanza hacia objetivo** (agendar consulta)
- Cliente pregunta precio → bot da **rango con contexto educativo** + propone consulta para precio exacto (sin escapar al precio)
- Cliente silencia → bot **re-engage con valor** después de timing inteligente (no spam)
- Tono: cálido + profesional + experto + peruano natural (no robotizado)
- **Ejemplo concreto de diálogo top de gama** (el tipo de calidad que apuntamos):

```
Lead: Hola

Bot (~30s después):
¡Hola! Bienvenida a Livskin 🌿 Soy el equipo virtual de la Dra. Claudia.
¿Qué te trajo por acá? Cuéntame qué te llama la atención (botox, ácido hialurónico,
limpieza, peeling, algo más…) o si solo querés explorar.

Lead: cuanto cuesta el botox

Bot (~30s después):
Buena pregunta. El precio del botox depende de las unidades necesarias —
eso varía por persona según la zona y profundidad de las líneas.

Para darte rangos honestos:
• Entrecejo solo: desde S/350
• Frente completa: S/500–700
• Frente + entrecejo + patas de gallo: S/700–1,100

⚠️ El precio EXACTO lo damos en consulta presencial gratuita (15 min con la doctora),
porque depende cuántas unidades de toxina necesite tu caso específico.

¿Te animás a agendar la consulta gratuita? Tengo huecos esta semana y la próxima.
```

> Esto NO es lo mismo que "te lo dice la doctora por privado". Esto da rango, educa, justifica
> por qué no podemos dar precio exacto, y propone próximo paso CON valor (consulta GRATUITA).

### Decisiones que la doctora valida en el encuentro

- ¿Acepta que el bot dé **rangos de precio con disclaimers**? (vs no dar nada)
- ¿La consulta inicial es **GRATUITA** o tiene costo? (es la palanca para que el bot ofrezca algo concreto)
- ¿Quiere que el bot tenga un **nombre/persona** o sea anónimo "equipo virtual"?
- ¿Acepta que el bot use **emojis ligeros**? (1 por mensaje máx, en saludos y cierres)

---

## 1. Preparación previa de Dario (qué traer ANTES del encuentro)

### A. Datos del sistema (descargar de Vtiger/ERP/Metabase)

| Dato | Dónde | Por qué importa |
|---|---|---|
| **134 clientes reales** segmentados por tratamiento + ticket promedio + frecuencia | ERP livskin_erp (export CSV) | Identificar QUIÉN compra REALMENTE (arquetipos basados en data, no hipótesis) |
| **Top 5 tratamientos por ingreso** (de los 88 ventas) | ERP `ventas` agrupado por `cod_item` | Priorización de portfolio que el bot debe dominar |
| **Distribución pago digital vs efectivo** (53% / 47%) | ERP `pagos` | Política de pre-pago / señas / facilidades |
| **Ticket range** (S/40 – S/1,800, promedio S/405) | ERP | Encuadre psicológico de precios |

### B. Métricas de campañas previas (FB Ads — Bridge Episode + Día de la Madre)

| Dato | Dónde | Por qué importa |
|---|---|---|
| **6 leads de Bridge Episode (2026-05-03/08)** + breakdown por landing | `docs/campaigns/2026-05-first-campaign/` + Vtiger `leadsource` | Aprender qué creative + landing trajo cada lead |
| **Conversación completa de esos 6 leads** | WhatsApp histórico + Vtiger | Ver qué preguntaron, qué confundió, qué convirtió o qué los hizo abandonar |
| **Día de la Madre 2026 (campaña 2da)** stats | `docs/campaigns/2026-05-dia-madre/daily-report-2026-05-08.md` | Tracking sheet con 6 leads totales — entender pain points |
| **CPC / CPM por creative** | FB Ads Manager (descargar manual via UI hasta que tengamos API automático) | Saber qué visual + copy resuena |
| **Search Terms Report** Google (si ya corre brand defense) | Google Ads | Keywords reales que la gente busca |

### C. Información visual real (Dario pide a la doctora)

| Item | Para qué |
|---|---|
| **Screenshots de 10-15 conversaciones reales** que la doctora tuvo con clientes en su WhatsApp personal histórico | Calibrar BRAND VOICE — cómo escribe, qué palabras usa, dónde pone emojis, qué NO dice, cómo cierra |
| **Screenshots de objections comunes** (precio, miedo a aguja, contraindicaciones) y cómo la doctora las respondió | Construir copy del bot para esos casos exactos |
| **Fotos de la clínica** (entrada, sala espera, sala procedimiento) | Para usar en landings + responses del bot ("estamos en Av. La Cultura, te mostrá la entrada con jardín verde") |
| **Foto profesional de la doctora** (para el perfil WA + landings) | Branding |
| **Logo Livskin alta resolución** | Identidad visual |
| **Brand colors actuales** (si tiene paleta) | Consistencia visual |

### D. Análisis competitivo Cusco (Dario investiga 1-2h previas)

| Item | Dónde |
|---|---|
| **5-10 clínicas estéticas Cusco** — nombres, instagrams, sitios web, precios públicos si los tienen | Búsqueda Google "clínica estética cusco" + Instagram Cusco |
| **Cómo se comunican esas clínicas** | Screenshots de su mejor / peor contenido |
| **Qué tratamientos ofrecen** | Mapping de portfolio comparativo |
| **Rangos de precios públicos** | Para calibrar nuestra estrategia de precios |
| **Qué dicen sus reseñas Google** | Quejas + elogios comunes (insights de qué espera el cliente Cusco) |

---

## 2. Bloque A — Tratamientos: portfolio + ciencia + comercial (45 min)

### Objetivo
Extraer todo lo que la doctora sabe de cada tratamiento que ofrece — desde lo CLÍNICO (qué hace, contraindicaciones, recuperación) hasta lo COMERCIAL (precio típico, target ideal, objection más común).

### Preparación visual
Mostrale a la doctora un printout o pantalla con el listado de tratamientos que vendió en los últimos 12 meses (de los 88 ventas del ERP):

```
1. Botox (34% volumen — top!)
2. Ácido Hialurónico (relleno)
3. PRP (plasma rico)
4. Hilos tensores
5. Exosomas
6. Tratamientos faciales (limpieza, peeling, etc.)
7. [otros si aparecen]
```

### Por cada tratamiento, preguntar:

#### Tabla a llenar (1 fila por tratamiento, ~5-8 tratamientos clave)

| Pregunta | Por qué importa | Ejemplo de respuesta esperada |
|---|---|---|
| **¿Qué es el tratamiento en 2 frases para alguien que no sabe nada?** | Copy del bot cuando lead pregunta info | "El botox relaja músculos faciales que generan líneas de expresión. Resultado natural a los 5-7 días, dura 4-6 meses." |
| **¿Para qué tipo de cliente es ideal?** | Arquetipo target | "Mujeres 30-55 con líneas de expresión moderadas, primer signos de envejecimiento." |
| **¿Para quién NO es?** | Contraindicaciones para guardrails clínicos | "Embarazadas, lactancia, enfermedad neuromuscular." |
| **Duración de sesión + recuperación** | Para que bot responda "puedo trabajar después?" | "30 min sesión, recuperación 0 — vas a casa y a tu vida." |
| **Precio típico — rango HONESTO de menor a mayor caso** | Estrategia precio top de gama | "Entrecejo solo S/350; frente completa S/500-700; full face S/900-1,200." |
| **¿De qué depende el precio?** | Para que bot eduque (no parezca opaco) | "Unidades de toxina — varía por persona según fuerza muscular y zonas a tratar." |
| **Cuántas sesiones promedio** | Lifecycle del cliente | "1 sola, repetir 4-6 meses si quiere mantener." |
| **Resultado esperado realista** | Manejar expectativas | "Suaviza líneas existentes en movimiento. NO borra arrugas profundas en reposo (eso es relleno)." |
| **Top 3 objections de clientes a este tratamiento** | Copy para responses bot | "1. 'Me voy a quedar congelada' → mito, dosis low. 2. 'Es muy caro' → explicar duración. 3. 'Me da miedo la aguja' → es indolora con frío." |
| **Cross-sell típico** (con qué se combina) | Upsell automático del bot futuro | "Botox + ácido hialurónico (línea labial), HA + PRP." |
| **¿Cuándo es seguro empezar?** (edad mínima) | Filtro red flag para menores | "25 años en adelante para preventivo, 30+ para correctivo." |

### Pregunta cualitativa de cierre del bloque

> "Si vinieras un cliente nuevo hoy y te preguntara qué hacer, ¿qué le dirías para que entienda tu enfoque diferenciado vs ir a otra clínica?"

→ Esto es el **brand pitch core** que va en landings + copy bot welcome.

---

## 3. Bloque B — Tipología cliente real (arquetipos) (45 min)

### Objetivo
Dejar de hipotetizar arquetipos y construirlos sobre los 134 clientes REALES que la doctora atendió.

### Preparación visual
Mostrale a la doctora una tabla con los 134 clientes (export CSV ERP) agrupados por:
- Edad estimada
- Tratamiento de primera compra
- Frecuencia de retorno
- Ticket promedio

### Preguntas a la doctora

#### B.1 Identificar 3-5 perfiles reales

> "Si pensás en tus 134 clientes, ¿cómo los agruparías? ¿Hay 3-5 tipos diferentes que vienen por razones distintas?"

Pedirle ejemplos REALES (con nombres si querés, anonimizados después):

```
ARQUETIPO 1: ej. "Marketing Manager 35-45 años"
- Edad típica
- Ocupación
- Cómo se enteró de Livskin (referido, FB, Google, etc.)
- Qué tratamiento pidió primero
- Qué le preocupa (líneas de expresión, manchas, pérdida volumen)
- Frecuencia retorno
- Ticket promedio
- 1 cliente real ejemplo (anonimizado): "Cliente X — botox cada 5 meses + HA labial 1x año"
- Cómo le HABLA la doctora (formal? cercana? técnica?)
- Painpoint #1: "no quiere parecer obvia, busca natural"
- Lo que la convence: "ver antes/después reales + caso similar"
```

Repetir para 3-5 arquetipos.

#### B.2 Tier económico

> "¿Hay clientes que vienen con poco presupuesto vs los que vienen y compran todo?"
> "¿Cómo identificás un cliente de alto valor en los primeros 2 mensajes de WhatsApp?"

→ Esto alimenta el **scoring Vtiger** (valor económico potencial).

#### B.3 Source channel real

> "De los 134, ¿cuántos vinieron por: referido boca a boca / IG / Facebook ad / Google / pasaron por la calle / web?"

→ Esto valida hipótesis de canales (atribución real de los clientes existentes).

#### B.4 Clientes problemáticos

> "¿Hay clientes que TE GUSTARÍA NO atender? (sin nombres). Qué patrones tienen?"

→ Construir filtro tier X del scoring (a quién NO escalar).

Ejemplos comunes:
- Pregunta solo por precio sin valorar info
- Cancela última hora repetidamente
- Pide descuentos agresivos
- Argumentos médicos imposibles ("quiero botox para X que no aplica")

---

## 4. Bloque C — Brand voice: cómo habla la doctora REAL (45 min)

### Objetivo
Calibrar el tono del bot al estilo de la doctora MEJORADO. Que el cliente sienta continuidad cuando pase del bot a la doctora.

### Preparación
Dario pide ANTES del encuentro: **15 screenshots reales** de chats de la doctora con clientes (anonimizando teléfonos):

- 3 saludos/welcomes
- 3 explicaciones de tratamiento
- 3 respuestas a precio
- 3 manejos de objection (miedo, duda)
- 3 cierres / agendamiento

### Análisis durante el encuentro (con doctora presente)

Mirar los screenshots juntos y para cada uno preguntar:

#### Preguntas guía

1. **¿Por qué escribiste así?** (consciente vs intuitivo)
2. **¿Qué palabras NUNCA usás?** (formal-frío, jerga médica complicada, "amorcito", etc.)
3. **¿Cuándo usás emojis y cuándo no?**
4. **¿"tu" o "usted"?** Default + cuándo cambiás
5. **¿Cómo cierras una conversación cuando agendás cita?**
6. **¿Cómo te despedís si el lead se enfría?**

### Tabla a llenar (output del bloque)

| Dimensión | Valor | Ejemplo |
|---|---|---|
| **Tratamiento** (tú/usted) | tú default, cambia a usted si lead es señora mayor | "Cuéntame qué te llama la atención" |
| **Tono base** | cálido + profesional + ligeramente peruano | "Buen día, qué amable de tu parte escribirme" |
| **Emojis** | 1 por mensaje máx, solo ciertos: 😊 🌿 ✨ ⚠️ ✅ ❌ | "Bienvenida 🌿" |
| **NO usar** | "amor", "hermosa", "linda", "guapa", jerga médica innecesaria, mayúsculas para enfatizar | — |
| **Saludo standard** | "¡Hola [nombre]! Bienvenida a Livskin" o variantes | — |
| **Despedida cita confirmada** | "¡Nos vemos el [día]! Te esperamos 🌿" | — |
| **Despedida lead frío** | "Si más adelante te interesa, escribime cuando quieras, sin compromiso" | — |
| **Estructura típica mensaje** | Reconocer + responder con valor + invitar a próximo paso | "Buena pregunta. El botox parte desde S/X... Te agendo consulta gratuita?" |

### Brand voice DON'T (lista negra)

> "Mostrame 3 mensajes de OTRAS clínicas o mensajes propios viejos que NO te representan más"

→ Lista de patterns prohibidos para el bot.

---

## 5. Bloque D — Painpoints + objections del cliente Cusco (45 min)

### Objetivo
Mapear TODOS los painpoints que un cliente de medicina estética en Cusco siente al considerar tratamiento. El bot debe poder responder cada uno con copy específico.

### Los 12 painpoints clásicos (validar con doctora + agregar Cusco-específicos)

| # | Painpoint | Manifestación típica | Cómo responde la doctora (a llenar) | Copy bot que vamos a construir |
|---|---|---|---|---|
| 1 | **Miedo al dolor** | "Duele mucho?" | (doctora explica) | "Con frío local es indolora. La mayoría dice que es menos que un pellizco." |
| 2 | **Miedo a quedar "raro"** | "Y si me quedo congelada / con cara de plástico?" | | "Trabajamos dosis bajas para naturalidad. Mirá @livskin estos antes/después" |
| 3 | **Precio percibido alto** | "Me parece caro / por qué tan caro?" | | (Explicar duración + materiales + experiencia. NO ofrecer descuento.) |
| 4 | **Desconfianza marca** | "Cómo sé que sos profesional?" | | "Soy Dra. X, certificación Y. Acá podés ver mi colegiatura: [link]" |
| 5 | **Inseguridad social** | "Mi pareja / familia va a notar?" | | "Hacemos dosis sub-clínica si querés efecto sutil. Solo vos sabés." |
| 6 | **Duda timing** | "Cuándo es buen momento? Soy muy joven/vieja?" | | (Tabla edad ideal por tratamiento + bonus de empezar preventivo) |
| 7 | **Contraindicaciones / riesgo** | "Tengo X enfermedad, puedo?" | | "Eso debe evaluarse en consulta. NO te lo defino por chat por seguridad." |
| 8 | **Falta de tiempo** | "Cuánto tiempo necesita la sesión?" | | "30-60min sesión, recuperación 0. Podés ir a trabajar después." |
| 9 | **Comparación con competencia** | "En X clínica me cobran Y" | | (Diferenciación con valor — NO entrar a guerra de precios) |
| 10 | **Distancia / ubicación** | "Estoy en Sicuani / Urubamba / extranjero" | | (Política específica: viajar es factible? cuánto antes?) |
| 11 | **Pago / facilidades** | "Acepta tarjeta? Pago en cuotas?" | | (Política exacta: Yape, transferencia, tarjeta, financiación?) |
| 12 | **Falta de info de qué necesita** | "No sé qué necesito" | | "Para eso es la consulta gratuita: te diagnosticamos sin compromiso" |

### Cusco-específicos (agregar con doctora)

- Clima (Cusco altura, frío, sol fuerte → afecta piel, post-tratamiento)
- Cultura local (¿tabú? ¿estigma? ¿abierto?)
- Conexión turismo (clientes nacionales/extranjeros de paso)

---

## 6. Bloque E — Estrategia de precios "top de gama" (30 min)

### Objetivo
Decidir CON la doctora cómo el bot maneja preguntas de precio. La diferencia entre mediocre y top de gama está acá.

### Las 4 estrategias posibles (validar cuál usar)

| Estrategia | Cuándo se usa | Pros | Contras |
|---|---|---|---|
| **A. Cero precio** ("solo en consulta") | Clínicas premium tradicionales | Mantiene aura premium | Pierde leads que quieren saber rango |
| **B. Rango con disclaimer** ("desde S/X, varía") | Top de gama moderno | Da info útil + protege precio exacto | Necesita justificar bien la varianza |
| **C. Precio fijo público** | Spas commodity | Transparente | Compite por precio, no por valor |
| **D. Calculadora interactiva** (preguntas → estimado) | Tech-forward | Engagement alto | Complejo construir, requiere reglas |

**Recomendación mía**: **Estrategia B (Rango con disclaimer)** + en futuro evolucionar a D (calculadora).

### Decisiones a tomar con la doctora

Por cada tratamiento, dejar definido:
- **Precio "desde"** (caso simple) — qué número se da
- **Precio "hasta"** (caso complejo) — qué número se da
- **El "depende de"** específico para justificar el rango
- **Consulta inicial** — ¿gratuita o pagada?
- **Si pagada**: ¿cuánto? ¿deducible si se hace el tratamiento?

Ejemplo de output esperado (botox):

```
Botox
- Rango: S/350 (entrecejo solo) hasta S/1,200 (full face + cuello)
- Depende de: unidades de toxina necesarias (varía 20-100u por persona)
- Consulta inicial: GRATUITA, 15min, sin compromiso
- Otros: aceptamos Yape, Plin, transferencia, tarjeta visa/mastercard
```

### Trampa a evitar (importante)

NO ofrecer descuentos / promos como respuesta a "es caro". Eso devalúa.
En cambio: **ofrecer VALOR adicional** ("incluye consulta seguimiento gratis a la semana", "te damos un kit cuidado post-tratamiento"). El precio nunca baja.

---

## 7. Bloque F — Diferenciación competitiva (20 min)

### Objetivo
Identificar el MOAT real de Livskin vs otras clínicas Cusco. Esto va en landing + bot welcome.

### Preguntas a la doctora

1. **"¿Qué hacés vos que las otras clínicas NO hacen?"** (técnica, equipamiento, enfoque, formación)
2. **"¿Qué te diferencia como persona/profesional?"** (estudios, años, especialización, premios)
3. **"¿Por qué los 134 clientes te eligieron a vos vs ir a Lima o a otra clínica Cusco?"**
4. **"¿Qué te dicen los clientes que más valoran de vos?"** (reseñas verbales)

### Output esperado (3-5 ventajas diferenciales)

```
1. Certificación X (de la doctora — credibilidad)
2. Productos premium (Allergan, Galderma, no genéricos baratos)
3. Atención personalizada en consulta (no fast-fashion estética)
4. Diagnóstico individualizado, NO menú estándar
5. Único centro en Cusco con [equipamiento Y / técnica Z]
```

---

## 8. Bloque G — Operación: capacidad + horarios + logística (20 min)

### Objetivo
Entender restricciones físicas para que el bot proponga slots realistas.

### Preguntas

| Pregunta | Por qué importa |
|---|---|
| **Horario semanal** (días + horas atendiendo) | Bot propone slots solo en esos rangos |
| **Cuánto antes hay que agendar?** (¿slot mismo día posible? ¿1 semana mínimo?) | Lógica check_availability |
| **Duración real por tratamiento** | Bot bloquea slots correctos |
| **Capacidad diaria máxima** | Para evitar over-booking |
| **Días pico** (sábados? viernes?) | Estrategia de campaña (no saturar) |
| **Política cancelación** | Bot avisa a lead "cancela 24h antes sin costo" |
| **Política no_show** | Bot recovery flow (Día +1/+3/+7) |
| **Ubicación + cómo llegar** | Mensaje T-30min con dirección + parking |
| **Parking** disponible? | Detalle clave para mensaje T-30min |
| **WiFi sala espera** | Detalle UX |

### Ejemplo output esperado

```
Horario atención: Lunes-Sábado 9am-7pm. Domingos previa coordinación.
Anticipación mínima agendar: 24h (slots last-minute disponibles a discreción).
Duración promedio sesión: Botox 30min, HA 45min, PRP 60min.
Capacidad: 6 sesiones/día máximo.
Días pico: viernes tarde + sábados (subir CPC en ads esos días? o redirigir a otros días).
Cancelación: avisar 24h antes vía WhatsApp, sin costo. <24h cobramos 30% del tratamiento.
No-show: 50% del tratamiento.
Dirección: Av La Cultura 1234, Wanchaq. Edificio rojo con jardín verde, 2do piso.
Parking: gratuito en el edificio.
WiFi: red "Livskin", password en la sala.
```

---

## 9. Bloque H — Casos de éxito + testimonios (15 min)

### Objetivo
Construir biblioteca de casos REALES anonimizados que el bot pueda mencionar.

### Preguntas

1. **3 casos reales del último año** (anonimizados) — qué tratamiento, qué resultado, qué emoción
2. **¿Hay foto antes/después** que la cliente autorizó usar? (con consentimiento escrito)
3. **¿Reseñas Google positivas** que podamos citar?

### Output esperado

```
Caso 1 (anonimizado): "M.A., 38 años, profesional. Vino preocupada por entrecejo profundo
que la hacía verse 'enojada'. Botox 30u, resultado natural a los 7 días. Volvió a los 5
meses para retoque y agregó ácido hialurónico labial."

Bot puede citar: "Hace poco tratamos una cliente con caso similar. En 7 días vio el
cambio que buscaba, sin perder expresión natural. Si te gustaría ver fotos del antes/
después o conversar tu caso, te agendo consulta."
```

---

## 10. Bloque I — Drop-off + re-engagement strategy (20 min)

### Objetivo
Definir CON la doctora qué hacer cuando lead se enfría en cada stage.

### Los 6 escenarios drop-off

| Drop | Escenario | ¿Qué pasa hoy sin sistema? | Qué queremos que pase con bot |
|---|---|---|---|
| **D1** | Lead NUNCA respondió primer mensaje bot | Se pierde silencio | Template 48h "te respondí, sigue interesada?" |
| **D2** | Respondió saludo pero abandonó en qualifying | Se pierde silencio | Flujo educativo (3-touch contenido de valor sobre tratamiento de interés) |
| **D3** | Completó qualifying pero no agendó | Se pierde silencio | Identificar objection (precio/tiempo/duda) → secuencia específica |
| **D4** | Agendó pero canceló o no asistió | A veces doctora llama, a veces no | Recovery sequence Día +1 (warm), +3 (educativo), +7 (oferta) |
| **D5** | Asistió consulta pero no compró tratamiento | Se pierde | Email + WA con contenido validación del tratamiento + caso similar |
| **D6** | Compró 1 vez no volvió 90d | Se pierde | Reactivación temporal ("tu botox ya cumplió 4 meses, momento de renovar") |

### Por cada drop-off, definir con doctora

1. **Cuánto esperar** antes de re-engage (24h? 48h? 7d?)
2. **Qué contenido / oferta** mandar (ojo: NO descuentos siempre)
3. **Canal** (solo WA? email? ambos coordinados?)
4. **Cuántos touches máximo** antes de stop (3? 5? regla anti-spam)
5. **Cuándo escalar a doctora** para llamada humana

---

## 11. Bloque J — Sistema global de captación (30 min)

### Objetivo
Mapear TODOS los canales por donde puede entrar un lead + cómo se trackean.

### Diagrama actual

```
                          ┌──────────────────────────────────────┐
                          │     LIVSKIN — SISTEMA RevOps         │
                          └──────────────────────────────────────┘
                                            │
              ┌─────────────────────────────┼───────────────────────────────┐
              ▼                             ▼                               ▼
        FB Ads (paid)              Google Ads (paid)                  Orgánico
              │                             │                               │
   ┌──────────┼──────────┐                 │              ┌────────────────┼───────────────┐
   ▼          ▼          ▼                 ▼              ▼                ▼               ▼
 Botox      HA      Retargeting       Brand Defense  SEO web       IG orgánico      Boca a boca
 landing  landing      audience         Search                       (no ad)
   │          │          │                 │              │                │               │
   └──────────┼──────────┘                 │              │                │               │
              ▼                             ▼              ▼                ▼               ▼
   ┌─────────────────────────────────────────────────────────────────────────────────┐
   │   Touchpoint 1: Click → Landing Page (campanas.livskin.site) o WP livskin.site  │
   │   • UTMs capturadas + persistidas en cookies                                     │
   │   • event_id único generado                                                     │
   │   • Pixel + GA4 events: PageView, ViewContent                                   │
   │   • CTA: botón "Pregunta por WhatsApp" → +51 947 741 117 con mensaje pre-llenado│
   └─────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
   ┌─────────────────────────────────────────────────────────────────────────────────┐
   │   Touchpoint 2: WhatsApp Cloud API → Bot rule-based (Sprint 2-3)                │
   │   • Workflow [D1] dispara: signature check + dedup + load state + parser        │
   │   • Vtiger lead creado/updated (cf_treatment_interest, cf_source_campaign...)   │
   │   • Stage greeting → qualifying → booking                                       │
   │   • CAPI event: Lead                                                            │
   └─────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
   ┌─────────────────────────────────────────────────────────────────────────────────┐
   │   Touchpoint 3: Booking (slot agendado en ERP appointments)                     │
   │   • CAPI event: Schedule                                                        │
   │   • Recordatorios T-24h → T-3h → T-2h alerta Dario → T-30min                    │
   └─────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
   ┌─────────────────────────────────────────────────────────────────────────────────┐
   │   Touchpoint 4: Asistencia consulta presencial                                  │
   │   • Doctora marca attended/no_show en ERP                                       │
   │   • Si attended y compra: lead → cliente, venta registrada                      │
   │   • CAPI event: Purchase (con value)                                            │
   └─────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
   ┌─────────────────────────────────────────────────────────────────────────────────┐
   │   Touchpoint 5: Post-tratamiento lifecycle                                      │
   │   • Email + WA safety check T+24h                                               │
   │   • Validación T+14d                                                            │
   │   • Reseña Google T+21d                                                         │
   │   • Upsell contextual T+45d                                                     │
   │   • Reactivación temporal T+90d / +4m / +9m (según tratamiento)                 │
   └─────────────────────────────────────────────────────────────────────────────────┘
```

### Preguntas a la doctora sobre canales

1. **¿Cuál canal cree que da los mejores clientes** (mejor calidad, mayor lifetime value)?
2. **¿Cuál canal da los más problemáticos** (negociadores, cancelones)?
3. **¿Hay canales que NO usamos pero deberíamos** (Tiktok? Influencer marketing? Partnerships con peluquerías?)
4. **¿Programa de referidos** ya existe? ¿Funciona? ¿Cómo lo escalamos?

---

## 12. Bloque K — Output del encuentro (checklist a llenar JUNTOS)

Al terminar el encuentro, Dario debe salir con TODO ESTO documentado:

### Checklist de outputs

- [ ] **Brand voice doc** (`docs/brand/voice-v1.md`) con tono, vocabulario, NO usar, ejemplos saludo/cierre/objection
- [ ] **Arquetipos cliente** (`docs/brand/personas.md`) — 3-5 personas reales con detalle
- [ ] **Customer Journey Map** (`docs/brand/journey-map.md`) por arquetipo × canal × tratamiento
- [ ] **Catálogo tratamientos** (`docs/brand/catalogo-tratamientos.md`) — 5-8 tratamientos con info clínica + comercial + objections + cross-sell
- [ ] **Política de precios** (`docs/brand/precios-strategy.md`) — rangos exactos por tratamiento + disclaimer + consulta gratuita policy
- [ ] **Painpoints + responses** (`docs/brand/painpoints-responses.md`) — 12 painpoints + cómo responde el bot a cada uno (copy real)
- [ ] **Diferenciación competitiva** (`docs/brand/diferenciacion.md`) — 3-5 ventajas core
- [ ] **Operación** (`docs/brand/operacion.md`) — horarios, capacidad, ubicación, política cancelación
- [ ] **Casos de éxito** (`docs/brand/casos-exito.md`) — 3 casos anonimizados + fotos antes/después con consentimiento
- [ ] **Drop-off strategies** (`docs/brand/reengagement.md`) — 6 escenarios + secuencias copy
- [ ] **Reglas scoring Vtiger** (`docs/brand/scoring-rules.md`) — señales con puntos por arquetipo
- [ ] **Sistema global captación** (`docs/brand/captacion-global.md`) — diagrama actualizado con canales activos + planeados

---

## 13. Lo que Dario hace POST-encuentro (4-6h con Claude Code)

Una vez que tenés todos los outputs del bloque K, Dario sesión con Claude Code para:

1. **Codificar el brand voice en wa_parser.js** — agregar dictionary de palabras prohibidas + frases standard + emojis permitidos
2. **Construir el copy del bot** por stage × intent (mensajes en español natural del bot)
3. **Vtiger custom fields** — agregar cf_score_*, cf_tier, cf_agent_stage según reglas definidas
4. **Workflow D1 con contenido real** — los responses no son placeholders, son los textos definidos por la doctora
5. **Templates Meta** — submitir a aprobación los 4-6 templates definidos
6. **Brain pgvector** — poblar `clinic_knowledge` con info clínica + precios + painpoints + casos éxito
7. **Customer journey maps** publicados en docs/brand/ (markdown + diagramas)
8. **Campaign briefs** (`docs/brand/campaign-brief-template.md` existente) para próximas campañas FB + Google

---

## 14. Por qué este encuentro vale 3-4h

Sin esta sesión, todo lo que codeemos del bot va a ser **scaffolding sin contenido** — funcional pero impersonal. Con esta sesión, vamos a tener:

- Bot que responde como hablaría la doctora MEJORADA (con info + estructura sistemática)
- Sistema de captación que sabe POR QUÉ cada lead viene y QUÉ valora
- Estrategia de precios que da info sin perder valor
- Re-engagement coordinado en vez de spam
- Scoring que predice quién va a convertir

Es la diferencia entre construir un robot misero replicable barato vs un **sistema de adquisición premium** que escale el negocio.

---

## Anexo A — Preguntas rápidas que la doctora debe responder por anticipado (mandarlas por WA antes del encuentro)

Para que llegue preparada al encuentro, Dario le manda este cuestionario corto un día antes:

```
Para nuestro encuentro del [día], me ayudaría que pienses estas preguntas:

1. ¿Cuáles son los 5-6 tratamientos que más vendés hoy?

2. Pensá en 3 clientes específicos (anónimos) muy distintos entre sí: ¿quiénes son y qué hacen?

3. ¿Cuál es el rango de precios típico por tu tratamiento más vendido?

4. ¿Te animarías a darme screenshots de 10-15 conversaciones tuyas con clientes
   (anonimizando teléfonos)? Para entender cómo escribís y construir un bot que
   suene como vos.

5. ¿Cuál es la pregunta MÁS frecuente que te hacen por WhatsApp?

6. ¿Hay algún tratamiento que querrías VENDER MÁS y por qué no estás vendiendo más
   hoy?

7. ¿La consulta inicial la cobrás o es gratuita? ¿Querrías que sea gratuita?

¡Gracias! Esto nos ahorra MUCHO tiempo en el encuentro.
```

---

## Anexo B — Materiales físicos a traer al encuentro

Dario lleva en laptop o impreso:

1. Lista de 134 clientes (anonimizada) con columnas: edad estimada, tratamiento principal, frecuencia, ticket promedio
2. Top 5 tratamientos por revenue (de las 88 ventas)
3. Stats de Bridge Episode + Día de la Madre (6 leads cada uno, qué dijeron, qué pasó)
4. Análisis competitivo (3-5 clínicas Cusco con screenshots de su comunicación)
5. Esta bitácora (impresa o en pantalla)
6. Plantilla para tomar notas (puede ser MS Word, GDoc, papel A4)
7. Grabadora de audio (con permiso de la doctora)

---

## Anexo C — Tono de la conversación con la doctora

Importante: este NO es interrogatorio. Es **conversación entre socios** donde Dario llega con propuesta + datos y la doctora valida/refina/agrega con su expertise clínico + experiencia.

- Empezar agradeciendo + explicar contexto (estamos construyendo un sistema que la va a ayudar a más leads de calidad + menos tiempo perdido)
- Mostrar data del sistema actual primero (los 134 clientes, los 88 ventas) — eso genera confianza ("este chico sabe de qué habla")
- Hacer preguntas abiertas + escuchar
- Mostrar ejemplos concretos del bot que estamos construyendo
- Cerrar con próximos pasos claros (cuándo recibe el output del encuentro codificado)

---

**Última nota**: si después del encuentro hay 2-3 temas que quedaron sin resolver, no forzar. Es OK programar un 2do encuentro de 1h específico para resolver eso.
