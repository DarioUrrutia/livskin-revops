# Plan Operativo — Día de la Madre 2026 (Armonización Facial umbrella)

> **Refactored 2026-05-04**: de 2 tratamientos separados → 1 umbrella "Armonización Facial" por presión de tiempo.
> **Brief estratégico:** [`brief.md`](brief.md)
> **Configuración técnica:** [`campaign-config-draft.md`](campaign-config-draft.md)
> **Checklist UI manual:** [`ads-manager-checklist.md`](ads-manager-checklist.md)

---

## 1. Objetivo

**Maximizar leads (form fills + mensajes WhatsApp) durante la ventana del Día de la Madre.**

Frame umbrella "Armonización Facial" que cubre Botox + Ácido Hialurónico — la doctora decide en consulta presencial qué tratamiento aplicar.

Hipótesis secundarias (post-mortem informa):
- ¿Cost-per-lead viable en Cusco con audience chica?
- ¿Audience F30-55 Cusco radio 8km es la correcta?
- ¿Landing → form vs Click-to-WhatsApp directo: cuál convierte mejor?
- Spontaneously: ¿qué tratamiento expresan los leads en chat? (Botox vs AH vs ambos vs no especificado)

---

## 2. Estructura simplificada

```
1 Campaign: "Livskin — Día de la Madre 2026 — Armonización Facial"
   Objective: LEADS (Pixel Lead optimization)
   Budget: $100 lifetime CBO
   Schedule: 2026-05-05 → 2026-05-09
   Ad account: 2885433191763149 (Business Manager Livskin Perú)
   Pixel: 4410809639201712 (Livskin 2026)
   │
   └─🟨 1 Ad Set: "Armonización Facial - Cusco F30-55"
      Audience: Cusco radio 8km, F 30-55, intereses skincare/beauty
      Budget: $100 completo (sin split — concentrado en 1 ad set)
      Optimization: Lead conversion (Pixel)
      Placements: Advantage+ (Meta auto)
      Frequency cap: 4 / 7 días
      │
      ├─🟩 Ad 1: TOFU — banner declaración identidad
      │   Asset variants: tofu-1x1, tofu-4x5, tofu-9x16 (Dario sube a Ads Manager)
      │   Destination: landing dia-madre-armonizacion-2026
      │   utm_content=arm-tofu
      │
      ├─🟩 Ad 2: MOFU — banner consideración
      │   Asset variants: mofu-1x1, mofu-4x5, mofu-9x16
      │   Destination: landing
      │   utm_content=arm-mofu
      │
      └─🟩 Ad 3: BOFU — banner acción
          Asset variants: bofu-1x1, bofu-4x5, bofu-9x16
          Destination: landing
          utm_content=arm-bofu

📦 Total: 1 campaign / 1 ad set / 3 ads / 9 banners (3 principales × 3 aspect ratios)
   + 1 landing umbrella

🛬 Landing destination común:
   https://campanas.livskin.site/dia-madre-armonizacion-2026/
```

---

## 3. Audience

**Geografía** (Cusco-only, radio 5-8 km desde Wanchaq):

```
Ubicación principal: Wanchaq (donde está la clínica)
Radio: 8 km
   ├─ Wanchaq ✅
   ├─ Cercado de Cusco ✅
   ├─ San Sebastián ✅
   └─ Santiago ✅

Excluido:
   ❌ San Jerónimo, Saylla, provincias lejanas
```

**Demografía**:
- Mujeres
- 30-55 años
- Idioma: Spanish

⚠️ **Plan B si Meta marca "Special Ad Category — Health"**: ampliar a 18-65, ambos géneros.

**Detailed targeting**:
- Skincare, Beauty
- Cosmetic procedures
- Anti-aging
- Aesthetic medicine
- Mother's Day (si aparece)

**Behavior**: Engaged shoppers.

**Custom Audiences**:
- 36 clientes activos con phone (CSV ya generado: `_pending-uploads/livskin-clientes-CA-20260504.csv`)
- ⚠️ Solo 36 personas — Meta puede rechazar LAL o generar baja calidad (ver INS-008)
- Plan operativo: subir CA igual + intentar LAL 2-3% Peru. Si Meta rechaza LAL → seguimos con interest-based puro

**Audience size estimado** (post-filtros):
- Cusco metro radio 8km: ~280-300K personas
- Mujeres 30-55: ~45-55K
- Tras intereses: ~10-18K alcanzables

---

## 4. Métricas esperadas y targets

| Métrica | Target / Benchmark | Notas |
|---|---|---|
| **CPM** (cost per mille) | $7-15 USD | Audience chica → más caro |
| **Impresiones totales** | 7-14K con $100 lifetime | |
| **Frequency** | 2-3 promedio (cap 4) | |
| **CTR** ad | 1-2% | Benchmark medicina estética LATAM |
| **Click-to-landing rate** | ~70% del CTR (varios placements) | |
| **Cost per landing visitor** | $1-3 USD | |
| **Conversion landing → Pixel Lead** | 2-5% | Form fill o WA click |
| **Leads totales esperados** (form + WA) | 5-15 | Realista para $100/5 días Cusco |
| **Cost per Lead** | $7-20 USD | Si <$15 → bueno; >$25 → revisar |
| **Conversion Lead → cliente pagante** | 20-40% | Doctora cierra |
| **Clientes pagantes esperados (post-DM)** | 1-4 | |
| **Revenue esperado** | S/. 800-3.200 PEN | Tratamiento promedio S/. 800 |

**ROI mínimo aceptable**: $100 ≈ S/. 380. 1 cliente que pague S/. 600+ = break-even directo.

---

## 5. Cronograma operativo

| Día | Fecha | Acciones |
|-----|-------|----------|
| **Día -1 (prep)** | 2026-05-04 (hoy) | • Brief aprobado<br>• Custom Audience subida<br>• Banners 3 principales producidos por Dario<br>• Landing casi-final entregada por Dario<br>• Adaptación landing + push CF Pages<br>• Smoke E2E pre-launch |
| **Día 0 (configuración)** | 2026-05-04 noche / 2026-05-05 mañana | • Configurar campaña en Ads Manager (siguiendo `ads-manager-checklist.md`)<br>• Submit a Meta review (4-24h aprobación) |
| **Día 1 (launch)** | 2026-05-05 (lunes) | • Meta aprueba ads<br>• Monitor primeras 6h<br>• Lanzamiento target: 18:00-21:00 hora Cusco |
| **Día 2-4** | 2026-05-06 a 2026-05-08 | • Daily check Ads Manager<br>• Doctora llena tracking sheet<br>• Pause/swap ads bajos performance |
| **Día 5 (cierre)** | 2026-05-09 (viernes) | • Last-day spend<br>• Pre-DM final push |
| **Día 6 (Día de la Madre)** | 2026-05-11 (domingo) | • Doctora atiende citas<br>• Anota en sheet quiénes vinieron de la campaña |
| **Día 7-8** | 2026-05-12 a 2026-05-13 | • Post-mortem session<br>• Cierre del modo bootstrap (principio #13)<br>• Doctrina v0.X → v1.0 |

---

## 6. Tracking + monitoring (sin Marketing API)

100% manual:

### Daily checklist Dario (5 min cada mañana)

1. Abrir Ads Manager → ad account `2885433191763149`
2. Filtrar campaña "Livskin — Día de la Madre 2026 — Armonización Facial"
3. Screenshot/copia de métricas clave
4. Pasar a Claude vía chat
5. Claude genera análisis + recomendaciones en `daily-reports/YYYY-MM-DD.md`

### Tracking manual WhatsApp doctora

- Cheat sheet impreso con shortcode `[ARM-MAY-FB]`
- Doctora anota cada mensaje en Google Sheet
- Status flow: Nuevo → Contactado → Agendado → Asistió → Cliente

### Tracking automático (lo que sí funciona)

- ✅ Pixel + CAPI: cada PageView + form submit + click WA dispara events
- ✅ Form de la landing → A1 webhook → Vtiger Lead → ERP via B3 cron (validado smoke E2E 2026-05-03)
- ✅ Audit log ERP: registra cada lead

---

## 7. Risk + mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Meta marca "Special Ad Category — Health" | Media | Audience más amplia (no F30-55) | Plan B: ajustar a 18-65 ambos géneros |
| Compliance ad rejection por copy | Baja-Media | Retraso 24-48h | Pre-validar copy contra políticas Meta |
| Audience Cusco demasiado chica | Baja | CPM alto | Ampliar radio a 10 km en plan B |
| Doctora no llena tracking sheet | Media | Pérdida atribución manual | Cheat sheet impreso + WA recordatorio |
| Banners no aprobados a tiempo | Media | Lanzamiento tardío | Submit ads viernes noche para aprobación lunes |
| Budget se gasta antes de día 5 | Baja | Termina antes DM | Lifetime budget evita esto |
| Pixel no firea | Baja | Pérdida optimization | Smoke E2E pre-launch (validado) |
| LAL rechazada por Meta (36 source < 100) | Alta | Sin LAL targeting | OK, dependemos de interest-based |
| Landing tarda más de lo esperado | Media | Lanzamiento se mueve | Empezamos sin landing (Click-to-WhatsApp directo) si aprieta — fallback Op A |

---

## 8. Lo que NO se hace en esta campaña

❌ 2 ad sets por tratamiento (refactored a 1 umbrella)
❌ Marketing API token (UI manual con checklist)
❌ Banners para 3+ tratamientos (solo umbrella armonización)
❌ Targeting fuera de Cusco
❌ Promociones / descuentos / "antes del 11"
❌ Landings dedicadas separadas Botox + AH

---

## 9. Definition of Done

- [ ] Campaña corrió 5 días + Ads Manager muestra impresiones + clicks reales
- [ ] Mínimo 5 leads recibidos (form + WA combined)
- [ ] Doctora llenó tracking sheet con al menos 5 entradas
- [ ] Daily reports de Claude
- [ ] Post-mortem ejecutado con data real
- [ ] Modo bootstrap cerrado (doctrina v0.X → v1.0)
- [ ] Aprendizajes durables migrados a memorias permanentes
- [ ] Carpeta `2026-05-dia-madre/` movida a `_archive/` post-cierre

---

## 10. Cross-link

- Brief: [`brief.md`](brief.md) — gate de aprobación
- Tracking consolidado: [`tracking.md`](tracking.md)
- Config técnico exhaustivo: [`campaign-config-draft.md`](campaign-config-draft.md)
- Checklist UI: [`ads-manager-checklist.md`](ads-manager-checklist.md)
- Tratamiento umbrella: [`armonizacion-facial/`](armonizacion-facial/)
- Doctrine feedback: [`_doctrine-feedback.md`](_doctrine-feedback.md)
- Post-mortem template: [`post-mortem.md`](post-mortem.md)

---

**Plan vivo.** Refinable hasta lanzamiento. Una vez en producción, NO se modifica estructura/budget/audience sin OK explícito de Dario.
