# Captación Global — Sistema Multi-canal v1.0

**Fuentes:** workbook (canales) + audio (estacionalidad) + ERP analytics histórico
**Consume:** Acquisition synth script (futuro), planificación trimestral, ads budget allocation, decisiones canal

---

## Resumen ejecutivo

**Canales activos:**
1. **Boca a boca** — #1 fuente histórica, orgánica, 100% gratis
2. **Google Business** — segundo más importante para captación local Cusco
3. **Google Ads** — paid intencional (búsqueda)
4. **Facebook Ads** — paid display + retargeting
5. **Instagram orgánico** — subutilizado actualmente
6. **WhatsApp directo** — entrada de inbound (no captación per se)

**Canales NO usados pero candidatos:**
- TikTok (decisión doctora: candidato a explorar)
- Email marketing (Fase 4A.5 — pendiente con MailerLite Free)
- Programa referidos (decisión doctora: NO implementar por ahora)

**Estacionalidad clave:**
- 🔴 **Mayo + Noviembre** = picos altos (Día Madre + Navidad)
- 🟢 Resto del año = demanda más distribuida

---

## Canal por canal

### Canal #1 — Boca a boca (orgánico)

**Estatus:** activo, sin intervención sistemática
**Volumen estimado:** ~60-70% de los leads actuales según workbook
**Costo:** S/0 (100% gratis)
**Conversion estimada:** alta (>50% lead-to-cliente)
**Tipo de cliente que trae:** todos los arquetipos, especialmente #1 ("mantienen") y #2 ("primeras arrugas")

**Por qué funciona:**
- 10+ años de experiencia + filosofía "reposición natural" = clientes contentas
- Clientes recurrentes referencia activamente a amigas/familia
- Cusco es ciudad mediana → red social compacta, alta amplificación

**Estrategias para amplificar:**
1. **Programa referidos** (DECISIÓN DOCTORA: NO implementar aún) — puede explorarse Fase 5+
2. **Post-venta UX excelente** → genera deseo de recomendar orgánico
3. **Pedir reseña Google** post-3 visitas (no la primera, para no incomodar)
4. **Pacientes recurrentes** como caso de éxito (con consentimiento) → social proof orgánico
5. **Eventos privados** (workshops o "open days" con clientes existentes invitando amigas)

**KPI a trackear:**
- "¿Cómo nos encontraste?" en consulta primera vez → meta: 60%+ digan "amiga/familiar"
- Referidos identificados en `clientes.canal_origen = 'boca_a_boca'`

### Canal #2 — Google Business / Maps

**Estatus:** activo, requiere optimización
**Volumen estimado:** ~15-20% de leads
**Costo:** S/0 (gratis)
**Conversion estimada:** media-alta
**Tipo de cliente:** búsqueda intencional ("clínica botox cusco", "doctora estética wanchaq")

**Estado actual:**
- ⚠️ Pendiente audit completo Google Business
- ⚠️ Pendiente confirmar reseñas existentes (count + score)
- ⚠️ Pendiente sincronizar info (horario, fotos, servicios)

**Optimizaciones inmediatas:**
1. **Foto profesional consultorio + doctora** (no genérica) → CTR ↑
2. **Servicios listados** (Botox, AH, Hilos, etc.) con keywords correctas
3. **Horario actualizado** ("Por cita previa" en Google Business)
4. **Posts semanales** (Google posts: tipo "Esta semana atendemos sábado 8am-8pm")
5. **Responder TODAS las reseñas** (positivas y negativas) — Google premia engagement
6. **Categorización correcta**: "Clínica de medicina estética" + "Especialista en medicina estética" + "Médico"

**Backlog:**
- [ ] Audit Google Business completo (cuándo?)
- [ ] Configurar acceso Dario al GMB
- [ ] Subir 8-12 fotos profesionales
- [ ] Setup respuesta automática a reseñas (post-deployment)

**KPI a trackear:**
- Impresiones GMB / mes
- Clicks to WhatsApp desde GMB
- Reseñas count + score
- Direcciones consultadas (interés geográfico)

### Canal #3 — Google Ads (paid search)

**Estatus:** activo, según workbook (sin info de performance actual)
**Volumen estimado:** desconocido (a auditar)
**Costo:** variable según presupuesto

**Plan optimización:**

#### Keywords priority

**Top tier (alta intención + alto valor):**
- "botox cusco"
- "doctora medicina estética cusco"
- "rellenos faciales cusco"
- "clínica estética wanchaq"
- "ácido hialurónico cusco"

**Mid tier (intención exploratoria):**
- "primeras arrugas qué hacer"
- "rejuvenecimiento facial cusco"
- "tratamientos estéticos no quirúrgicos"
- "hilos tensores cusco"

**Low tier (descubrimiento):**
- "cómo verse joven naturalmente"
- "envejecer bien"
- "cuidado piel mujeres 40"

#### Estructura de campañas

```
Campaign #1 — Botox (Top intención)
  Ad Group A: Búsqueda directa
    - "botox cusco"
    - "botox wanchaq"
    - Negativos: "que es el botox" (informativo, baja intención)
  Ad Group B: Por arquetipo
    - "primeras arrugas tratamiento"
    - "preventivo arrugas"

Campaign #2 — Ácido Hialurónico
  Similar estructura

Campaign #3 — Brand
  Ad Group: marca + variaciones
    - "livskin"
    - "claudia delgado doctora"
    - "livskin cusco"
    - (CTR alto, CPC bajo — defensivo)
```

#### Copy ads

**Ad #1 — Botox Top:**
```
Headline 1: Botox Cusco - Médico Cirujano CMP
Headline 2: Resultados Naturales, Sin Cambios
Headline 3: Consulta Gratuita - Dra. Claudia
Description: 10+ años de experiencia. Filosofía "reposición no transformación". Wanchaq, Cusco.
URL: livskin.site/botox
```

**Ad #2 — Ácido Hialurónico:**
```
Headline 1: Rellenos Faciales en Cusco
Headline 2: Resultados Inmediatos, 18-24 Meses
Headline 3: Dra. Claudia Delgado - CMP 091029
Description: Personalización extrema, sin protocolos estándar. Marca certificada Yvoire.
URL: livskin.site/acido-hialuronico
```

#### Budget allocation (sugerido v1)

**Total mensual:** TBD (Dario decide)

**Sugerencia:**
- 60% → Top intención (Botox + AH search)
- 25% → Mid intención (descubrimiento)
- 10% → Brand defensivo
- 5% → Retargeting (visitantes landing sin conversión)

**Aumento estacional:**
- Mes pre-Mayo: 2x budget habitual
- Mes pre-Noviembre: 1.5x budget habitual

### Canal #4 — Facebook Ads (paid display)

**Estatus:** activo según workbook
**Volumen estimado:** desconocido

#### Targeting

**Audiences:**
1. **Audience custom: Lookalike de clientes ERP** (excluir clientes actuales)
2. **Audience custom: Engaged 30d con IG/FB** + interés "medicina estética", "Botox"
3. **Audience custom: Web visitors retargeting** (Pixel `4410809639201712`)
4. **Geo:** Cusco metropolitano (Wanchaq, San Sebastian, San Jerónimo)
5. **Geo extendido (low budget):** Lima, Arequipa, Madre de Dios (pacientes que viajan)
6. **Demographic:** Mujeres 30-55 años primarias, 25-30 secundario

#### Creatives

**Creative A: Hero "Reposición natural"**
- Imagen: foto natural mujer 40s (no retoque excesivo, real)
- Copy primary:
  > *"Reposición no transformación. La filosofía de la Dra. Claudia Delgado para tratamientos naturales que respetan tus facciones. Médico Cirujano CMP 091029."*
- CTA: "Consulta gratuita"

**Creative B: Quote testimonial**
- Imagen: quote en background suave
- Copy:
  > *"Vengo donde la Dra. hace años. Es como hablar con una amiga que sabe lo que hace. Nada exagerado, todo natural."*
- CTA: "Conoce la Dra."

**Creative C: Educacional**
- Imagen: infografía simple "Botox preventivo vs correctivo"
- Copy:
  > *"¿Cuándo empezar Botox preventivo? La Dra. Claudia explica."*
- CTA: "Leer más" (link a landing educacional)

**Creative D: Antes/Después** (post fotos disponibles)
- Carousel con 3-4 casos antes/después
- Anonimizado o con consentimiento explícito
- CTA: "Ver más casos"

#### Budget allocation

- 40% creative A (top funnel)
- 30% retargeting visitantes
- 20% lookalike audiences
- 10% creative D antes/después (post-disponibilidad)

### Canal #5 — Instagram orgánico

**Estatus:** subutilizado (workbook menciona "Instagram" sin elaboración)
**Volumen estimado:** bajo

**Plan optimización:**

**Frecuencia posts:** 3 por semana mínimo (sustainable)

**Tipos de contenido:**
1. **Educacional** (40%) — tips, mitos vs realidad, info tratamientos
2. **Behind the scenes** (25%) — doctora trabajando, momentos del consultorio, equipo
3. **Casos antes/después** (20%) — con consentimiento
4. **Lifestyle** (15%) — paisajes Cusco, café cultural local, conexión con cliente

**Hashtags estratégicos:**
- #MedicinaEsteticaCusco
- #BotoxCusco
- #DraClaudiaDelgado
- #LivskinPeru
- #MedicinaEstetica
- #CuidadoFacialCusco
- #BellezaNatural

**Stories diarias:** 1-3 stories/día (sostenido)
- Momentos del consultorio
- Quick tips
- Casos del día

**Reels:** 1-2 por semana (formato corto, alto engagement)
- "Antes/después con consentimiento"
- "Mitos del Botox"
- "Por qué la consulta es gratuita"

### Canal #6 — TikTok (NO usado, candidato)

**Status:** workbook menciona como "canal NO usado pero deberíamos"
**Decisión:** explorar Fase 5+ (post-cierre bootstrap)

**Por qué tiene potencial:**
- Audiencia joven (25-35) — arquetipo entry #6E
- Bajo costo de producción
- Algoritmo favorece engagement orgánico

**Por qué no urgente:**
- Requiere consistency alta (3-7 posts/semana)
- Tono diferente a otros canales (más casual, joven)
- Mejor explorar post-Sprint 2.3 cuando bot Yossie esté operativo

### Canal #7 — Email marketing (Fase 4A.5 pendiente)

**Status:** pendiente
**Tool propuesto:** MailerLite Free
**Plan:** ver `reengagement.md` § "Email re-engagement"

---

## Sistema de tracking unificado

### Event_id flow (ver `project_attribution_chain_event_id.md`)

```
Anuncio Meta/Google → Click → Landing (event_id generated)
  → Form submit o WA click (event_id persisted)
  → Vtiger Lead created (cf_X = event_id)
  → ERP cliente (cuando se convierte)
  → CAPI Purchase (mismo event_id) → Meta dedup
```

### UTMs estandarizados

| UTM | Valores |
|---|---|
| `utm_source` | google / facebook / instagram / tiktok / email / boca_a_boca |
| `utm_medium` | cpc / cpm / organic / email / referral / wa_direct |
| `utm_campaign` | botox-mayo-2026 / dia-madre / general |
| `utm_content` | hero-a / hero-b / quote-c / antes-despues-d |
| `utm_term` | (keyword si Google Ads) |

### Cookies first-party (90 días)

- `lvk_utm_source`, `lvk_utm_medium`, `lvk_utm_campaign`, etc.
- `lvk_event_id` (UUID único por visitante)
- `lvk_first_touch_timestamp`

### Capture en form submit

Todos los hidden inputs `lvk_*` se copian al Lead Vtiger via mu-plugin WordPress.

### Capture en WA click

Click en botón WA pre-fill incluye:
- Phone destino: `+51 947 741 117`
- Texto pre-filled con UTMs encoded
- Event_id en URL params

---

## Distribución de canales — meta v1

| Canal | % share leads actual | % share meta v1 (post-Sprint 2.3) |
|---|---|---|
| Boca a boca | ~65% | 60% (mantener) |
| Google Business | ~15% | 18% (+optimización) |
| Google Ads | ~10% | 12% (+budget) |
| Facebook Ads | ~5% | 5% (mantener) |
| Instagram orgánico | ~3% | 3% (mantener) |
| Otros | ~2% | 2% |

**Meta cualitativa:** mantener mix DIVERSIFICADO. NO depender >75% de boca a boca (riesgo concentración).

---

## Estacionalidad — calendario marketing

### Mayo (Día de la Madre) 🔴 PICO

**Preparación:**
- T-6 semanas: ads creative específico "regalo para mamá"
- T-4 semanas: aumento budget Google Ads + Facebook Ads (2x)
- T-3 semanas: campaña email "Regala bienestar"
- T-2 semanas: posts diarios Instagram + Stories countdown
- Día Madre: ad campaign con CTA fuerte ("aún a tiempo")

**Productos foco:**
- Botox (entry punto regalo)
- Limpieza Facial (entry accesible)
- Esperma de Salmón / Exosomas (premium gift)

**Bundles potenciales:**
- "Pack Mamá": Limpieza + Botox 1 zona → S/300 (descuento bundle pequeño)
- Tarjeta regalo: monto variable, válida 90 días

### Junio-Julio-Agosto (Valle)

**Estrategia:**
- Foco en re-engagement de inactivos
- Tratamientos sin estacionalidad: PRP, Exosomas, Esperma Salmón
- Content educacional Instagram (alta producción)
- Audit + optimización Google Business

### Septiembre-Octubre (Pre-Noviembre)

**Preparación pre-pico:**
- Creatives nuevos para Noviembre
- Audit landings + bot
- Re-cordatorios a recurrentes ("estás cerca de retoque")

### Noviembre (Navidad) 🔴 PICO

**Estrategia similar a Mayo** con angle "regalo de Navidad" / "verte bien para fin de año".

**Productos foco:**
- AH (resultados inmediatos, ideal para "estar bien en Navidad")
- Botox (sin recuperación)
- Limpieza Facial (multi-sesiones desde ahora)

### Diciembre tardío-Febrero (Valle profundo)

**Estrategia:**
- "Empezar el año con buena piel"
- Foco en planes de cuidado anual (PRP 3 sesiones, Esperma Salmón 3 sesiones)
- Newsletter educacional

---

## Plan referidos (decisión actual: NO IMPLEMENTAR)

> **Doctora workbook:** *"Programa referidos: No existe aun no lo implementaremos."*

**Razón:** boca a boca orgánico funciona bien sin incentivos artificiales. Programa formal puede sentir "transaccional" y desvirtuar.

**Re-evaluar:** Fase 5+ cuando bot Yossie y otros canales estén consolidados.

**Si se implementa en futuro:**
- Sugerencia: "Trae una amiga, ambas reciben S/50 de descuento en próximo tratamiento"
- Tracking: campo `referido_por_cod_cliente` en `clientes`
- Cap: máximo S/200 acumulables por cliente referidor

---

## Métricas globales captación

| Métrica | Cómo medir | Target v1 |
|---|---|---|
| **Leads totales / mes** | Vtiger + WA inbound count | TBD baseline + +20% v1 |
| **CAC (Customer Acquisition Cost)** | Total ads spend / new clientes | TBD baseline |
| **LTV (Lifetime Value)** | ERP suma ventas / cliente | TBD baseline |
| **LTV:CAC ratio** | LTV / CAC | ≥3:1 |
| **Conversion lead → cliente** | Cliente ERP / lead Vtiger | ≥35% |
| **% leads boca a boca** | "¿cómo nos encontraste?" en consulta | mantener ≥50% |
| **% leads via Google Ads** | Vtiger `cf_origen_lead = google_ads` | meta 15% |
| **CTR ads Meta** | Meta Ads Manager | ≥1.5% |
| **CPC ads Google** | Google Ads | ≤S/2 (botox) |

---

## Validación pendiente

🟡 **Cifras reales de baseline** — Dario debe consultar Google Ads + Meta Ads Manager para histórico
🟡 **Audit Google Business completo**
🟡 **Cusco context para targeting** (clima altura, fototipo andino, turistas) — gap del workbook
🟡 **Decisión final budgets ads** — Dario decide presupuesto mensual

---

**Fin captacion-global.md — 2026-05-23**
