# Plan Bridge Episode — Primera campaña paga FB Ads (2026-05-03)

> **Status:** 🚀 ARRANCANDO
> **Tipo:** Episodio puente entre Fase 3 (cerrada) y Fase 4 (reescrita post-audit 2026-05-03)
> **Doctrina rectora:** principio operativo #11 — *"Deterministic backbone first — IA es capa aditiva"*
> **Memoria efímera:** `project_first_paid_campaign_2026_05_03.md` — archivar tras post-mortem
> **Audit que precedió:** `docs/audits/agent-scope-audit-2026-05-03.md`

---

## 1. Objetivo REAL (no es generar leads — es generar data)

| Pregunta que la campaña responde | Cómo se mide | Decisión que informa |
|---|---|---|
| ¿Funciona el tracking end-to-end con tráfico real? | Leads en ERP con `utm_source=facebook` correctamente atribuidos | Si NO funciona → priorizar fix tracking sobre cualquier otra cosa de Fase 4 |
| ¿Botox vs PRP cuál convierte mejor? | Conversion rate por landing | Priorización landings futuras + ad budgets |
| ¿WA directo, landing, o site convierte mejor? | Costo / lead por destino | Decide próxima inversión: chatbot WA priority OR landing optimization |
| ¿El ICP F25-55 Cusco/Lima funciona? | Demographics de clickers en FB Ads Manager | Validación segmentación |
| ¿CAC sostenible para tratamientos $300-800? | Spend / clientes pagantes | Go/no-go de campañas a escala |
| ¿Las creatividades generadas por Dario+Claude convierten? | CTR + cost per lead por anuncio | Decide urgencia construir Brand Orchestrator IA |

**Lo que NO es objetivo:**
- ❌ Maximizar conversiones (no hay sistema optimizado todavía)
- ❌ Generar revenue inmediato (es validación, no growth)
- ❌ Probar todos los tratamientos (solo top 2 por revenue: Botox + PRP)

---

## 2. Setup

### 2.1 Budget + duración

- **Budget total:** $100 USD lifetime (no daily)
- **Duración:** 5 días corridos
- **Distribución sugerida (Ads Manager auto-optimizes):**
  - Ad set 1 — Landing Botox: ~$35
  - Ad set 2 — Landing PRP: ~$35
  - Ad set 3 — Click-to-WhatsApp: ~$30

### 2.2 Audiencia

- **Locations:** Cusco (Perú) + Lima (Perú)
- **Demographics:** Mujeres, edad 25-55
- **Detailed targeting (intereses):** Skincare, Beauty, Aesthetic Medicine, Anti-aging, Cosmetic procedures
- **Placements:** Advantage+ (FB optimiza automáticamente — Feed/Stories/Reels)
- **Optimization for delivery:** Conversions → "Lead" event

### 2.3 Pixel + CAPI

- Pixel `4410809639201712` ya healthy ✅
- CAPI server-side via n8n G3 ya activo ✅
- Pre-launch verificar en Events Manager que "Lead" event aparece como activo

### 2.4 Creative count

- **3-4 ads mínimo** (FB hace A/B test automático)
- Distribución sugerida:
  - 1 imagen + caption "Renová tu mirada con Botox profesional" → landing botox-mvp
  - 1 imagen + caption "PRP capilar y facial — resultados en 30 días" → landing prp-mvp
  - 1 carousel "Antes/Después" → WhatsApp directo
  - Opcional 1 video corto (15-30s) → si Dario tiene material

### 2.5 Constraints Meta importantes a verificar pre-launch

- ⚠️ **Categoría especial restringida**: si Meta marca tu ad account como "salud/bienestar", podría limitar targeting (no edad/género específico). Verificar al armar campaña — si aparece flag, hablar.
- ⚠️ **Compliance médico**: ads de medicina estética pasan revisión Meta más estricta. NO prometer resultados específicos, NO usar antes/después si Meta lo restringe en tu mercado, NO mencionar "rejuvenecer" o claims clínicos sin disclaimer.

---

## 3. 3 destinos del tráfico

### Destino 1 — Landing botox-mvp ✅ (existente)

**URL:** `https://campanas.livskin.site/botox-mvp/`

**Estado:** Ya construido (Mini-bloque 3.6, mayo 2026). Captura form completa con UTMs + fbclid + event_id → Vtiger Lead → ERP via B3 cron en <2 min.

**Pre-launch checklist:**
- [ ] Submit form fake con UTMs falsos para verificar end-to-end
- [ ] Confirmar que llega a Vtiger con todos los campos UTM
- [ ] Confirmar sync a ERP funciona (LIVLEAD#### nuevo)
- [ ] Verificar Pixel "Lead" event dispara en navegador con FB Pixel Helper
- [ ] Verificar CAPI server-side dispara en Events Manager (server-side dedup)

**UTMs del ad → landing:**
```
?utm_source=facebook&utm_medium=paid&utm_campaign=botox-mayo-2026&utm_content=ad-botox-1
```

### Destino 2 — Landing prp-mvp ⏳ (a crear esta sesión)

**URL target:** `https://campanas.livskin.site/prp-mvp/`

**Plan:** copia exacta de `botox-mvp/` con 3 cambios mínimos:
1. Hero copy cambiado a PRP
2. Hero photo cambiada (foto PRP genérica si no hay material)
3. Tratamiento `tratamiento_interes` hidden field cambiado a "PRP"

**Construcción estimada:** 30-60 min (clonar template existente + commit + push → Cloudflare Pages auto-deploy en ~3 min).

**Pre-launch checklist:**
- [ ] DNS apunta correctamente
- [ ] Form submit funciona end-to-end (mismo verifier que botox-mvp)
- [ ] Pixel + CAPI funcionan idéntico

**UTMs del ad → landing:**
```
?utm_source=facebook&utm_medium=paid&utm_campaign=prp-mayo-2026&utm_content=ad-prp-1
```

### Destino 3 — WhatsApp directo doctora (manual tracking)

**Phone:** `+51982732978` (número actual de la doctora — fuera del sistema)

**Mecanismo:** mensajes pre-poblados con shortcodes embedded para atribución manual.

**Links:**

```
Botox FB:
https://wa.me/51982732978?text=Hola%2C%20vi%20su%20anuncio%20de%20Botox%20%5BBTX-MAY-FB%5D

PRP FB (si aplica):
https://wa.me/51982732978?text=Hola%2C%20vi%20su%20anuncio%20de%20PRP%20%5BPRP-MAY-FB%5D

Genérico (si linkeás site):
https://wa.me/51982732978?text=Hola%2C%20vi%20su%20p%C3%A1gina%20web%20%5BGEN-MAY-FB%5D
```

**Cuando alguien clickea el ad de FB:**
1. WhatsApp se abre con texto pre-poblado: *"Hola, vi su anuncio de Botox [BTX-MAY-FB]"*
2. La mayoría manda tal cual (sin editar)
3. Doctora ve el shortcode `[BTX-MAY-FB]` en el primer mensaje
4. Doctora copia número + shortcode + interés a tracking sheet manual (`tracking-sheet-template.md`)

**Atribución resultante:** 100% capturada manualmente, cruzable con cost data de Ads Manager para CAC por shortcode.

---

## 4. Cronograma operativo

| Día | Actividad | Tiempo | Responsable |
|---|---|---|---|
| 2026-05-03 noche | Tarea 1 — Verificar end-to-end botox-mvp | 30 min | Claude + Dario |
| 2026-05-03 noche | Tarea 2 — Crear landing prp-mvp clonando botox-mvp | 1h | Claude |
| 2026-05-03 noche | Tarea 3 — Generar 3 links WA con shortcodes | 15 min | Claude |
| 2026-05-03 noche | Tarea 4 — (Opcional) hotfix B3 race | 30 min | Claude |
| 2026-05-04 mañana | Tarea 5 — Setup FB Ads Manager (juntos paso a paso) | 1h | Dario + Claude guía |
| 2026-05-04 mañana | Tarea 6 — Crear creatividades (3-4 ads) | 1h | Dario + Claude |
| 2026-05-04 mañana | Tarea 7 — Cheat sheet impreso/digital para doctora | 15 min | Dario |
| 2026-05-04 mañana | Tarea 8 — Google Sheet tracking inicializado | 15 min | Dario |
| 2026-05-04 tarde | Tarea 9 — LANZAR campaña | 15 min | Dario |
| 2026-05-04 a 2026-05-09 | Campaña corre. Chequeo diario | ~10 min/día | Dario |
| 2026-05-09 o 10 | Post-mortem session — leer la data | 2h | Claude + Dario |

---

## 5. Lo que NO se hace en este Bridge Episode (resistir FOMO)

**Documentado para no escalar el episodio más de lo planeado:**

- ❌ Chatbot WhatsApp rule-based (Fase 4A, post-campaña)
- ❌ Módulo Agenda en ERP (Fase 4A)
- ❌ Notificaciones automáticas a doctora (Fase 4A)
- ❌ Brand voice formal documento (en paralelo, no bloquea esta campaña)
- ❌ Customer development entrevistas a 135 clientes (en paralelo)
- ❌ Metabase dashboard de campaña (se construye DESPUÉS con data en mano)
- ❌ Brand Orchestrator subagentes (Fase 4B post-validación)
- ❌ ADR-0035 VPS dedicado de agentes (no es momento)

**Si alguno de estos genera tentación durante los 5 días, la respuesta es:** *"Excelente idea — agendarla para post-mortem. Hoy enfocados en data real."*

---

## 6. Definition of Done — exit criteria

**El Bridge Episode se considera cerrado cuando:**

- [ ] Campaña corrió 5 días + Ads Manager muestra al menos 100 impresiones + clicks reales
- [ ] Vtiger tiene leads con `utm_source=facebook` correctamente atribuidos (mínimo 1 si la campaña funciona)
- [ ] Doctora llenó al menos 5 entradas en tracking sheet (combinación landing + WA directo)
- [ ] Post-mortem session ejecutada con data real
- [ ] Aprendizajes durables migrados a memorias permanentes (`feedback_*.md` o `project_*.md`)
- [ ] Memoria efímera `project_first_paid_campaign_2026_05_03` archivada
- [ ] Decisión de próxima fase tomada con datos en mano

---

## 7. Plan B — qué pasa si algo sale mal

| Escenario | Plan B |
|---|---|
| FB Ads rechaza la creative por compliance médico | Suavizar copy, evitar antes/después, agregar disclaimer "consulta médica requerida" |
| Pixel no dispara con tráfico real | Verificar bloqueadores ad-blocker, confirmar CAPI fallback funciona, debuggear con FB Pixel Helper |
| Cero conversiones después de día 3 | Pausar, ajustar audience o creative, no quemar todo el budget en algo que no funciona |
| Doctora se ve abrumada con WA leads | Pausar el ad set 3 (WA directo), redirigir budget a landings |
| Tracking shows desconexión Vtiger ↔ ERP | Hotfix urgente del sync, pero la data del Ads Manager sigue siendo válida |
| Account FB Ads marcado como "high-risk health" | Stop, hablar con soporte Meta antes de seguir invirtiendo |

---

## 8. Aprendizajes durables esperados (post-mortem)

Tras el post-mortem, los aprendizajes irán a:

**Si surgen reglas operativas nuevas** → memorias `feedback_*.md`:
- Ej: "Para FB Ads de medicina estética, evitar palabras X, Y, Z"
- Ej: "Doctora prefiere recibir leads via X, no Y"

**Si afectan arquitectura del proyecto** → memorias `project_*.md`:
- Ej: "Botox convierte 3x mejor que PRP — priorizar landings de Botox en Fase 4A"
- Ej: "WA directo gana sobre landing → priorizar chatbot rule-based"

**Si generan decisiones irreversibles** → ADR nuevo:
- Ej: ADR-0036 — Decisión sobre prioridad Conversation Agent vs Brand Orchestrator basada en data Bridge Episode

---

## 9. Cross-link

- **Doctrina rectora**: `feedback_deterministic_backbone_first.md` (memoria 🔥 CRÍTICA)
- **Audit que precedió**: `docs/audits/agent-scope-audit-2026-05-03.md`
- **Memoria efímera**: `project_first_paid_campaign_2026_05_03.md`
- **Session log**: `docs/sesiones/2026-05-03-strategic-pivot-and-first-campaign.md`
- **Tracking sheet template**: `docs/campaigns/2026-05-first-campaign/tracking-sheet-template.md`
- **Landing botox-mvp**: `infra/cloudflare-pages/livskin-landings/botox-mvp/`
- **Pixel Meta**: `4410809639201712` (único activo)

---

**Notas:**
- Plan vivo — refinable iterativamente durante la campaña sin re-aprobación
- Cualquier decisión que afecte budget o creative requiere OK explícito de Dario
- Post-mortem es OBLIGATORIO antes de Fase 4 — no skippear
