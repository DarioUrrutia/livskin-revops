# ADR-0012 — Pipeline stages en Vtiger

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-21
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos

---

## 1. Contexto

Vtiger CRM es el Source of Truth de identidad de Lead/Cliente (ADR-0015). Para que el Conversation Agent (Fase 4) y el equipo comercial trabajen coherentemente, necesitamos definir los **stages del pipeline comercial** de forma canónica — dónde está cada lead/cliente en su journey hacia conversión y retención.

Hoy Vtiger trae stages default genéricos (Prospecting, Qualification, Proposal, Negotiation, Closed Won/Lost) diseñados para B2B enterprise sales. Livskin es una clínica estética: el journey es diferente (consultas breves, agendamiento, tratamiento, reagendamiento).

Referencias:
- Plan maestro § 6.2 (Vtiger como CRM master)
- ADR-0011 (modelo de datos — define campos `estado_lead` en tabla leads)
- Blueprint § Modelo de adquisición
- Memory `project_erp_migration` (base actual word-of-mouth)

---

## 2. Opciones consideradas

### Opción A — 5 stages simples (MVP)
`Nuevo → Contactado → Agendado → Cliente → Perdido`

Un lead entra como "Nuevo" (captado por ad/form/WhatsApp), pasa a "Contactado" tras primer mensaje del Conversation Agent, "Agendado" cuando tiene cita confirmada, "Cliente" cuando hace primera venta (se convierte a Cliente en el modelo). "Perdido" para no-responde o explícitamente rechaza.

### Opción B — 7 stages detallados
`Nuevo → Contactado → Calificado → Agendado → Asistió → Cliente → Perdido`

Añade "Calificado" (Conversation Agent verificó interés real + presupuesto) y "Asistió" (confirma que fue a la cita, no solo que la agendó). Permite medir no-show rate.

### Opción C — Dual-funnel (adquisición + retención separados)
Pipeline 1 (adquisición): `Nuevo → Contactado → Agendado → Cliente`
Pipeline 2 (retención): `Activo → En riesgo → Inactivo → Reactivado`

Dos pipelines complementarios. Permite Growth Agent (Fase 6) trabajar sobre retención sin mezclar con captación.

---

## 3. Análisis de tradeoffs

| Dimensión | A (5 simple) | B (7 detallado) | C (dual-funnel) |
|---|---|---|---|
| Complejidad comercial | Muy baja | Media | Alta |
| Complejidad implementación Vtiger | Baja | Media | Media-alta |
| Insight analítico | Básico | Medio-alto (no-show rate) | Alto (retención visible) |
| Alineación con scale de Livskin | **Alta** (clínica pequeña) | Media | Baja inicialmente |
| Reversibilidad | Alta | Alta | Media |
| Dependencia con Fase 4 (Conversation Agent) | Mínima | Mínima | Requiere más reglas |

---

## 4. Recomendación

**Opción A (5 stages) para MVP, con extensibilidad a B/C después.**

Razones:
1. Livskin tiene ~135 clientes en 6 meses — el volumen no justifica granularidad
2. Stages simples = reglas del Conversation Agent claras y debuggeables
3. Si no-show rate emerge como problema medible, se puede agregar "Asistió" como sub-stage sin romper historia
4. El pipeline de retención (Opción C) puede vivir como **vista calculada** en Metabase sobre el modelo de ADR-0011 (`ventas.fecha` vs `now()`), sin crear stages explícitos en Vtiger

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-21 por Dario.

**Razonamiento:**
> "Algo que no sea altamente complicado pero tampoco demasiado básico, y que escale. 5 stages cubren el journey real sin sobre-ingeniería, con path claro para agregar granularidad cuando la evidencia lo justifique."

---

## 6. Stages canónicos MVP

| # | Stage | Definición | Trigger entrada | Trigger salida |
|---|---|---|---|---|
| 1 | **nuevo** | Lead recién capturado (form WP, WhatsApp, walk-in, referido) — aún no contactado | Form submit, primer mensaje WhatsApp, alta manual por comercial | Conversation Agent (o comercial) envía primer mensaje respuesta |
| 2 | **contactado** | Conversación iniciada por nuestro lado, esperando/intercambiando respuestas | Primer mensaje respuesta enviado | Cita confirmada O respuesta negativa explícita O silencio >14 días |
| 3 | **agendado** | Cita en calendario confirmada por el lead | Confirmación de cita (palabra clave, botón, o comercial) | Fecha de cita pasa (→ cliente si hizo venta; o agendado_nuevo) |
| 4 | **cliente** | Primera venta registrada — pasa a ser Cliente en modelo ADR-0011 | Primera venta en `ventas` con este cod_lead | Es estado terminal desde perspectiva de adquisición; retención se mide vía métricas sobre `ventas.fecha` |
| 5 | **perdido** | Descartado: respuesta negativa explícita, silencio >14 días tras contacto, o bounce de contacto | Rechazo explícito O 14 días sin respuesta tras `contactado` | Puede reactivarse manualmente a `nuevo` si vuelve por otro canal |

**Reglas de transición:**
- Solo el Conversation Agent (Fase 4) y comerciales pueden mover stages manualmente
- Transiciones automáticas (agendado→cliente cuando hay venta) se implementan en Fase 4 con webhooks Vtiger↔ERP
- No se "retrocede" de `cliente` a otro stage — el lead convertido queda inmutable en pipeline de adquisición; para retención se usa layer analítico separado

**Métricas de pipeline que habilita:**
- Conversion rate por stage (nuevo→contactado, contactado→agendado, agendado→cliente)
- Tiempo promedio en cada stage
- Distribución de "perdido" por razón (silencio vs rechazo explícito)
- Revenue atribuible por `fuente` del lead original

**Retención (vive en Metabase, NO en Vtiger):**
- Activo: cliente con venta en últimos 90 días
- En riesgo: 90-180 días sin venta
- Inactivo: >180 días sin venta
- Reactivado: cliente inactivo que volvió a comprar

Esto se calcula sobre `clientes JOIN ventas` — no requiere modificar stages de Vtiger.

### Campos custom en Vtiger para leads

Agregar a la entidad Lead de Vtiger (vía UI de Vtiger, no vía código):
- `fuente` (picklist: meta_ad, instagram_organic, form_web, whatsapp_directo, referido, walk_in, otro)
- `canal_adquisicion` (picklist: paid, organic, referral, walk_in)
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` (text)
- `fbclid`, `gclid` (text)
- `tratamiento_interes` (picklist poblada desde `catalogos.cat_Tratamiento`)
- `consent_marketing` (checkbox)
- `cod_cliente_vinculado` (text, se llena cuando convierte a cliente — vincula con ERP)

Esos mismos campos viven en la tabla `leads` del ERP (ADR-0011) para joins analíticos.

### Qué se difiere explícitamente

- **Lead scoring** (0-100 basado en señales) — Fase 4 (Conversation Agent) con reglas simples v1
- **Sub-stages dentro de `contactado`** (ej: "preguntó precio", "pidió foto") — agregar si Conversation Agent identifica patrones
- **Pipeline separado por tipo de tratamiento** — diferido
- **Stages de retención explícitos en Vtiger** — se resuelve en Metabase

---

## 7. Consecuencias

### Desbloqueado
- Configuración inicial de Vtiger en Fase 2 tiene lista de stages canónica
- ADR-0029 (Conversation Agent) puede diseñar reglas sobre stages estables
- Métricas de conversion funnel se diseñan sobre esta taxonomía
- Tabla `leads` de ADR-0011 tiene valores válidos para columna `estado_lead`

### Bloqueado / descartado
- No se crean stages adicionales sin justificación medible
- Opción B y C quedan como "pathsnext" si evidencia lo pide

### Implementación derivada
- [ ] Configurar Vtiger: reemplazar stages default por estos 5 (Fase 2)
- [ ] Crear picklists custom con los valores enumerados (Fase 2)
- [ ] Documentar en `integrations/vtiger/README.md` el mapeo stages ↔ entidad Lead ERP
- [ ] Dashboard Metabase "Conversion funnel" usa estos 5 stages (Fase 3)
- [ ] Growth Agent (Fase 6) implementa lógica de retención sobre vista SQL, no sobre stages Vtiger

### Cuándo reabrir
- Volumen >50 leads nuevos/semana: evaluar granularidad adicional
- No-show rate >20%: agregar stage "asistió" (Opción B)
- Nuevo canal importante (ej: e-commerce productos): puede requerir pipeline paralelo
- Revisión trimestral obligatoria: 2026-07-21

---

## 8. Changelog

- 2026-04-21 — v1.0 — Creada y aprobada (MVP Fase 2)
