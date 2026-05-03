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

## 2. Estructura final (decidida 2026-05-04)

```
📦 Campaign: "Livskin — Día de la Madre 2026 — Armonización Facial"
   Objective: TRÁFICO (Traffic / Maximize Link Clicks)
   Budget: $100 lifetime CBO
   Schedule: 2026-05-05 06:00 → 2026-05-09 23:59 (Lima)
   Ad account: 2885433191763149 (BM Livskin Perú)
   Pixel: 4410809639201712 (tracking, no optimización)
   │
   ├─🟦 Ad Set 1: "Landing - Cusco F30-55"
   │   Spend limit: $50-70 (CBO da más a quien convierte mejor)
   │   Conversion location: Sitio web
   │   Optimization: Link clicks
   │   ├─🟩 Ad TOFU → Landing (?src=tofu)
   │   │   Banner: tofu.png (9:16, Meta crop auto)
   │   │   utm_content=tofu
   │   │
   │   └─🟩 Ad MOFU → Landing (?src=mofu)
   │       Banner: mofu.png
   │       utm_content=mofu
   │
   └─🟩 Ad Set 2: "WhatsApp directo - Cusco F30-55"
       Spend limit: $30-50
       Conversion location: Messaging Apps (WhatsApp)
       Optimization: Conversaciones
       └─🟥 Ad BOFU → WhatsApp directo
           Banner: bofu.png
           Pre-text: "Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB-BOFU]"

Total: 1 campaign · 2 ad sets · 3 ads · 3 banners 9:16
```

**Hipótesis a validar**: ¿landing convierte mejor que WA directo? CBO redistribuye el budget según performance → respuesta natural en 2-3 días.

**Tracking de origen al WA (3 calidades de lead)**:
| Shortcode | Vino de | Calidad |
|---|---|---|
| `[ARM-MAY-FB-BOFU]` | Ad BOFU directo (no vio landing) | Frío educado |
| `[ARM-MAY-FB-MOFU-WEB]` | Ad MOFU → landing → click WA | Tibio |
| `[ARM-MAY-FB-TOFU-WEB]` | Ad TOFU → landing → click WA | Caliente (más info procesada) |

🛬 **Landing destino**: https://campanas.livskin.site/dia-madre-armonizacion-2026/

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

**Custom Audiences (decidido 2026-05-04 tras revisar audiences existentes)**:

✅ **Usar las 4 audiences históricas** (todas en ad account `2885433191763149`):
1. `TODO COMPLETO FB` — engagement general
2. `personas que hicieron clic en llamada de accion` — warm (mostraron intención)
3. `Interaccion con la pagina 365 dias` — cobertura amplia anual
4. `PERSONA QUE INTERACTUARON 28 DIAS` — hot reciente

❌ **Saltar el upload del CSV de 36 clientes** — muy chico para LAL útil + agrega fricción
❌ **Sin LAL en esta corrida** — generar seed nueva con la data que recolectemos. La próxima campaña sí tendrá LAL.

**Bonus**: usar las 6 audiences "Por caducar 0 días" en una campaña activa **las salva automáticamente** de la eliminación.

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

❌ 2 ad sets por tratamiento (refactored a 1 umbrella Armonización Facial)
❌ Marketing API token (UI manual con checklist)
❌ Banners para 3+ aspect ratios (solo 9:16 — Meta hace crop auto a 1:1 / 4:5)
❌ Targeting fuera de Cusco
❌ Promociones / descuentos / "antes del 11"
❌ Landings dedicadas separadas Botox + AH
❌ Upload del CSV de 36 clientes (muy chico para LAL útil)
❌ LAL en esta corrida (generar seed nueva con la data de esta campaña)
❌ Optimización por Pixel Lead (objective Tráfico, no Conversiones — $100/5d sin volumen para optimizar bien)

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
