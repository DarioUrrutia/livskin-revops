# ADR-0033 — Match automático lead↔cliente al crear cliente en ERP

**Estado:** ✅ Aprobada
**Fecha:** 2026-05-02
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 3 (Bloque puente operacional pre-Fase 4)
**Workstream:** Datos · Adquisición · Atribución

---

## 1. Contexto

**Hallazgo en smoke E2E observable 2026-05-02 PM:** la doctora opera el ERP creando clientes desde la pestaña CLIENTE cuando una persona viene físicamente a la clínica. Si esa persona vino originalmente de una campaña digital (lead con UTMs+fbclid+event_id en Vtiger+ERP), **HOY no hay forma automática de vincular al cliente con su lead origen**. Resultado: la attribution se pierde — Metabase no puede atribuir esa venta al canal Meta/Google que la generó.

**Modelo operacional REAL** (clarificado por Dario 2026-05-02):
- Vtiger gestiona el lead lifecycle de marketing (Dario opera Vtiger)
- ERP gestiona cliente operacional + ventas (la doctora opera ERP)
- El lead llega a Vtiger via form/WhatsApp; la doctora contacta por su WhatsApp/llamada (no usa ERP UI)
- Eventualmente el cliente viene físicamente → la doctora abre ERP → crea cliente → cobra venta
- **EN EL MOMENTO DE CREAR CLIENTE** debería poderse cruzar phone/email con leads existentes para vincular automáticamente

Sin esto, el círculo de atribución solo cierra cuando el chatbot Fase 4 esté operativo (donde el bot enriquecerá vinculando phone). HOY, la doctora opera manualmente y la attribution se pierde.

**Referencias:**
- Memoria `project_acquisition_flow.md` — modelo flujo end-to-end
- Memoria `project_vtiger_erp_sot.md` — Vtiger=lead, ERP=cliente
- Memoria `project_attribution_chain_event_id.md` — event_id como hilo conductor
- ADR-0011 v1.1 — modelo datos (cliente.cod_lead_origen ya existe)
- ADR-0023 — ERP refactor (preserva form actual, agrega solo)

---

## 2. Opciones consideradas

### Opción A — Match automático silencioso

Cuando se crea cliente sin `cod_lead_origen` explícito, sistema busca automáticamente match en `leads` por phone/email/nombre. Si encuentra, vincula sin avisar a la doctora.

### Opción B — Match interactivo con tip UI (elegida)

Misma búsqueda automática, pero mostrar **tip visual** a la doctora cuando hay candidato lead matching:

> 💡 *"Este parece ser un lead reciente: **Sofia Test** capturada de **facebook** el 2026-05-01. ¿Es la misma persona?"*
> [✓ Sí, vincular] [✗ No, cliente nuevo]

Doctora confirma o descarta. Solo vincula con OK explícito.

### Opción C — Búsqueda manual via campo dropdown

Doctora tiene un dropdown de leads sin convertir y puede seleccionar manualmente al crear cliente.

---

## 3. Tradeoffs

| Dimensión | A (silencioso) | B (interactivo) ✅ | C (manual) |
|---|---|---|---|
| UX doctora | 0 fricción pero sin transparencia | Mínima fricción + control | Alta fricción (1 paso extra siempre) |
| Riesgo falsos positivos | Alto (vincula equivocados) | Bajo (doctora valida) | Bajo |
| Visibilidad atribución | Implícita (no se entera) | Explícita | Explícita |
| Implementación | Simple | Media | Media |
| Reversibilidad | Difícil (silencioso) | Fácil (logs UI) | N/A |
| Alineación principio "doctora al mando" | Bajo | Alto | Alto |

---

## 4. Recomendación

**Opción B (interactivo con tip)** porque:
1. Doctora mantiene control (memoria `feedback_explain_to_beginner` — la usuaria principal del ERP toma decisiones, no el sistema)
2. Falsos positivos en Cusco (nombres similares, phones rotados) son riesgo real
3. Tip visual da contexto (canal + fecha capture) → doctora decide con info
4. Audit log distingue `cliente.created_with_lead_match` vs `cliente.created_walk_in` → trazable

---

## 5. Decisión

**Elección:** Opción B — Match interactivo con tip UI.

**Fecha aprobación:** 2026-05-02 por Dario

---

## 6. Implementación

### 6.1 Service layer — `cliente_service`

**Nueva función:**
```python
def search_lead_match(
    db: Session,
    phone_e164: Optional[str] = None,
    email_lower: Optional[str] = None,
    nombre: Optional[str] = None,
) -> Optional[Lead]:
    """Busca lead candidate matching por phone (priority 1), email (priority 2), nombre fuzzy (priority 3).

    Retorna Lead más reciente que NO esté ya convertido a cliente
    (i.e., su cod_lead NO aparece en clientes.cod_lead_origen).

    Priorización:
    - phone exacto match → 1 result → return ese
    - sin phone match, email exacto match → 1 result → return ese
    - sin email, nombre similarity ≥ 0.8 → 1 result → return ese
    - múltiples matches → return None (no auto-vincular ambiguo)
    """
```

**Mejora a `cliente_service.create()`:**

Agregar parámetro `cod_lead_origen: Optional[str] = None` (explícito de la UI cuando doctora confirma tip).

Si `cod_lead_origen` se pasa explícit:
- Buscar lead, validar que existe, copiar attribution UTMs al cliente nuevo
- Audit event: `cliente.created_with_lead_match`

Si no se pasa:
- Audit event: `cliente.created_walk_in`

Sin auto-match silencioso (la decisión del match queda en UI).

### 6.2 Endpoints

**Nuevo:** `GET /api/leads/search-match?phone=X&email=Y&nombre=Z`

Llama a `cliente_service.search_lead_match()`. Retorna:
```json
{
  "match": {
    "cod_lead": "LIVLEAD0008",
    "vtiger_lead_id": "10x66",
    "nombre": "Sofia Test",
    "fuente": "facebook",
    "fecha_captura": "2026-05-01T14:30:00Z",
    "tratamiento_interes": "Botox"
  }
}
```

O `{"match": null}` si no hay candidate único.

**Mejora:** `POST /api/clientes` acepta `cod_lead_origen` opcional en payload. Pasa al service.

### 6.3 UI — TAB VENTA (formulario de venta)

**Aclaración:** la doctora NO crea clientes desde la pestaña CLIENTE (esa pestaña es solo búsqueda/historial read-only). El cliente se crea **implícitamente** al cobrar una venta en la **pestaña VENTA** (form `/venta`, campos `input-cliente-venta` + `input-telefono-venta` + `input-email-venta`). Ahí debe aparecer el tip.

JavaScript debounced en input nombre/phone/email:
- Después de 600ms sin tipear → fetch `/api/leads/search-match?phone=X&email=Y&nombre=Z`
- Si hay match → render tip visual (verde, dismissible) sobre los campos del cliente
- Botones del tip: ✓ Vincular / ✗ Descartar
- Si vincular → set `<input type="hidden" name="cod_lead_origen">` con el cod_lead
- Si descartar → tip desaparece, cliente se crea como walk-in (sin cod_lead_origen)
- Si el nombre ya matchea cliente existente (CLIENTES_DATA[nombre]) → NO mostrar tip (no se crearía cliente nuevo)

### 6.4 Feature flag

`settings.auto_match_lead_enabled = True` (default).

Si False:
- Endpoint `/api/leads/search-match` retorna 404
- UI tip nunca aparece (frontend chequea flag desde `/api/config`)
- Sistema queda como antes (rollback instantáneo)

### 6.5 Audit log eventos canónicos nuevos

- `cliente.created_with_lead_match` — metadata: `{cod_cliente, cod_lead_origen, vtiger_lead_id_origen, match_field}` (match_field = "phone" / "email" / "nombre")
- `cliente.created_walk_in` — metadata: `{cod_cliente}`

Agregar a memoria `audit-events-schema.md` (49 eventos → 51).

### 6.6 Tests (TDD)

`tests/test_cliente_service_match.py`:
- match exacto por phone (1 lead → return)
- match por email cuando sin phone
- match nombre fuzzy ≥ 0.8
- múltiples matches phone → return None
- lead ya convertido a cliente → excluido del search
- search sin parámetros → return None

`tests/test_api_clientes_match.py`:
- GET /api/leads/search-match con phone → 200 + lead body
- GET con email → 200
- POST /api/clientes con cod_lead_origen → cliente creado con vinculación
- POST sin cod_lead_origen → cliente walk-in normal
- Feature flag off → 404 search-match

Coverage target: ≥75% en cambios.

---

## 7. Consecuencias

### Desbloqueado por esta decisión

- **Atribución end-to-end automática** cuando doctora opera ERP cotidianamente
- Dashboards Metabase D4 (Funnel Digital Cerrado) se llena con conversiones reales sin depender del chatbot Fase 4
- Foundation para Fase 4 — el bot también podrá usar `search_lead_match` como tool

### Bloqueado / descartado

- Opción A (match silencioso) — descartada por riesgo de falsos positivos
- Opción C (dropdown manual) — descartada por fricción UX

### Cuándo reabrir

- Si chatbot Fase 4 está operativo y el flow de creación cliente cambia drásticamente (cuando todos los clientes vendrían pre-attributed por el bot)
- Si volume de clientes/leads crece y el search-match se vuelve lento (>500ms) → migrar a indexed search

---

## 8. Changelog

- 2026-05-02 — v1.0 — Creada y aprobada por Dario

---

**Notas:** ADR alive — los detalles de UI tip se pueden refinar iterativamente sin re-superseder esta decisión.
