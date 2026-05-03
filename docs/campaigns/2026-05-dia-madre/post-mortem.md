---
campaign: 2026-05-dia-madre
status: TEMPLATE — llenar al cerrar campaña (estimado 2026-05-12/13)
trigger_for_close: principio operativo #13 — cierre del modo BOOTSTRAP
---

# Post-Mortem — Campaña Día de la Madre 2026

> **Llenar al cerrar la campaña.** Esta sesión es la más importante de todo el bridge episode — informa la doctrina v0.X → v1.0 y las decisiones de Fase 4.

---

## 1. Resumen ejecutivo

**Llenar:**
- ¿La campaña fue éxito, fracaso, o mixto? (1 oración)
- Top 3 aprendizajes más importantes
- Decisión clave para próxima campaña

---

## 2. Métricas finales

### Performance Meta Ads

| Métrica | Esperada | Real | Variación |
|---|---|---|---|
| Impresiones totales | 7-14K | | |
| Alcance único | 5-10K | | |
| Frequency promedio | 2-3 | | |
| Spend total | $100 | | |
| CPM promedio | $7-15 USD | | |
| CTR promedio | 1-2% | | |
| Mensajes WhatsApp recibidos | 6-15 | | |
| Cost per message | $5-15 USD | | |

### Performance por Ad Set

| Ad Set | Spend | Mensajes | Cost per message | CTR |
|---|---|---|---|---|
| Botox ($60 budget) | | | | |
| Ácido Hialurónico ($40 budget) | | | | |

### Performance por creative (top 3 + bottom 3)

| Banner | Funnel | Aspect ratio | CTR | Mensajes generados |
|---|---|---|---|---|
| | | | | |

### Funnel completo (cross-check con tracking sheet doctora)

| Stage | Cantidad | % conversion |
|---|---|---|
| Mensajes recibidos (WhatsApp) | | 100% (baseline) |
| Conversación iniciada por doctora | | / total mensajes |
| Cita agendada | | / contactados |
| Asistió a cita | | / agendados |
| Cliente pagante | | / asistieron |
| Revenue total generado | S/. | |
| **CAC real** (spend / clientes pagantes) | | |
| **ROI directo** (revenue / spend) | | |

---

## 3. Hipótesis del brief — validación

| Hipótesis original | Resultado real | ¿Se confirmó? | Implicación |
|---|---|---|---|
| Click-to-WhatsApp directo convierte mejor que landing→form para Cusco | | | |
| Botox vs AH: cuál convierte mejor en Cusco | | | |
| Audience F30-55 Cusco radio 5-8km es viable | | | |
| LAL 2-3% mejora performance vs interest-based puro | | | |
| Identidad "decisión personal" del Día de la Madre resuena | | | |
| Ads sin mencionar tratamiento específico convierten | | | |

---

## 4. Qué funcionó (proteger para próximas campañas)

**Llenar con detalle:**

- [insight 1]
- [insight 2]
- [insight 3]

---

## 5. Qué NO funcionó (evitar para próximas campañas)

- [insight 1]
- [insight 2]
- [insight 3]

---

## 6. Sorpresas (cosas que no esperábamos)

- [sorpresa 1]
- [sorpresa 2]

---

## 7. Refinamientos a doctrina v0.1 → v1.0

> Aquí se compila el `_doctrine-feedback.md` acumulado durante la campaña + nuevos insights del post-mortem. **Esta sección dispara el ascenso v0.X → v1.0**.

### Cambios propuestos a `docs/brand/brand-system.md`

- [refinamiento 1 con razón]

### Cambios propuestos a `docs/brand/copy-principles.md`

- [refinamiento 1 con razón]

### Cambios propuestos a `docs/brand/design-principles.md`

- [refinamiento 1 con razón]

### Cambios propuestos a `docs/brand/image-guidelines.md`

- [refinamiento 1 con razón]

### Cambios propuestos a `docs/brand/campaign-brief-template.md`

- [refinamiento 1 con razón]

---

## 8. Cierre del modo BOOTSTRAP (principio operativo #13)

**Acciones formales al cerrar el bootstrap:**

- [ ] Doctrina v0.X → v1.0 (eliminar header BORRADOR, bumpear frontmatter)
- [ ] Crear memoria 🔥 CRÍTICA `project_brand_methodology_v1.md` apuntando a `docs/brand/`
- [ ] Crear memoria `feedback_brand_voice_consolidated.md` (si aplica con voice tonal)
- [ ] Update CLAUDE.md: principio #13 marcar como **CERRADO**, mover descripción a histórico
- [ ] Update master plan changelog v1.6 con cierre del bootstrap
- [ ] Commit `docs(brand): cierre bootstrap — doctrina v1.0 post-mortem campaña dia-madre-2026-05`
- [ ] A partir del cierre: modos PROYECTO/CAMPAÑA son separados estrictos sin excepciones

---

## 9. Decisiones para próxima campaña

**Basado en la data real de esta campaña:**

| Área | Decisión |
|---|---|
| Próxima campaña: ¿cuál + cuándo? | |
| Budget allocation Botox/AH/otros | |
| ¿Producir landings dedicadas o seguir 100% Click-to-WhatsApp? | |
| Audience: refinamientos | |
| Creative direction: qué replicar / evitar | |
| ¿Marketing API token (App Review)? | |
| ¿Custom Audience refresh (post-conversiones nuevas)? | |

---

## 10. Aprendizajes para Brand Orchestrator futuro (Fase 4B)

> Cuando llegue la construcción del Brand Orchestrator IA, estos insights ya están entrenados como precedente.

- [insight táctico 1]
- [insight estructural 1]
- [insight de proceso 1]

---

## 11. Acciones derivadas — backlog

| Acción | Prioridad | Asignar |
|---|---|---|
| Cleanup BM "Livskin Perú Comercial" vacío | 🟢 | post-Bridge |
| Cleanup ad account personal `2130672884136872` | 🟢 | post-Bridge |
| App Review formal Meta Marketing API | 🟡 | side-project |
| Customer development entrevistas (10-20 clientes) | 🟡 | paralelo |
| ... | | |

---

## 12. Archivado de la campaña

**Al completar el post-mortem:**

```bash
git mv docs/campaigns/2026-05-dia-madre docs/campaigns/_archive/2026-05-dia-madre
```

Razón: cerrar el ciclo — la campaña ya no es activa, su valor histórico se preserva en `_archive/`.

Memoria efímera `project_first_paid_campaign_2026_05_03.md` (renombrada mentalmente a `dia-madre`):
- [ ] Borrar de `~/.claude/projects/.../memory/` post-cierre
- [ ] Aprendizajes durables ya migrados a memorias permanentes (paso 8)

---

## Notas finales

- [llenar al cerrar]
