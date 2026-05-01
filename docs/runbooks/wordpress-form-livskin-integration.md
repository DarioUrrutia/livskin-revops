---
runbook: wordpress-form-livskin-integration
severity: medium
auto_executable: false
trigger:
  - "Crear form nuevo en SureForms (test, landing, lead magnet)"
  - "Modificar form 1569 existente"
  - "Debugging si lead nuevo no aparece en Vtiger"
  - "Cambiar form de modo test → prod o viceversa"
required_secrets:
  - VTIGER_API_ACCESSKEY (en /home/livskin/apps/n8n/.env)
  - AUDIT_INTERNAL_TOKEN (en VPS 3 /srv/livskin-revops/keys/.audit-internal-token)
related_skills:
  - livskin-ops
---

# Runbook — Integración WordPress form con n8n + Vtiger + ERP

## Contexto + arquitectura

El sistema captura submissions de **cualquier form SureForms** (form-id agnostic) y los propaga a Vtiger CRM + ERP Postgres con full attribution (UTMs + click_ids + cookies + event_id). Cualquier form nuevo se integra cambiando UN valor de post_meta — sin tocar código.

**Componentes:**

```
WP form (SureForms) ──→ mu-plugin (livskin-form-to-n8n.php)
                             │
                             │  POST /webhook/acquisition/form-submit
                             ▼
                       n8n Workflow [A1]
                             │
                             │  Vtiger REST API (login + create Lead)
                             ▼
                       Vtiger CRM (12 cf_NNN custom fields)
                             │
                             │  cron 2 min
                             ▼
                       n8n Workflow [B3]
                             │
                             │  POST /api/leads/sync-from-vtiger
                             ▼
                       ERP Postgres `livskin_erp.leads`
```

---

## Cómo activar un form NUEVO en producción

### Paso 1 — Crear el form en SureForms admin

1. WP admin → **SureForms** → **Add New Form**
2. Agregar los blocks que necesites (text-field, email, phone-number, dropdown, etc.)
3. **Slugs requeridos** para que el mu-plugin extraiga correctamente:
   - Nombre completo: block `text-field` (slug `text-field`)
   - Email: block `email` (slug `email`)
   - Teléfono: block `phone-number` o `text-field` con label que contenga "telefono"/"phone"/"whatsapp"
   - Tratamiento (opcional): block `dropdown` con opciones
4. Save → anotar el **post ID del form** (lo ves en la URL `?post=XXXX&action=edit`)

### Paso 2 — Activar sync a n8n

**Opción A — via wp-cli (recomendado, scripteable):**

```bash
ssh -F keys/ssh_config livskin-wp 'sudo -u www-data wp post meta update <FORM_ID> _livskin_n8n_sync prod --path=/var/www/livskin'
```

Reemplazar `<FORM_ID>` con el post ID del form.

**Opción B — via WP admin UI:**

1. WP admin → editar el post del form
2. Screen Options (top right) → ✓ **Custom Fields**
3. Scroll abajo → **Custom Fields** panel
4. Add new:
   - Name: `_livskin_n8n_sync`
   - Value: `prod`
5. Update post

### Paso 3 — Embed el form en una página

En la página/landing donde quieras el form:
- Gutenberg: usar block **SureForms - Form** + seleccionar el form de la dropdown
- Shortcode: `[sureforms id="<FORM_ID>"]`
- Cualquier page builder: insertar el shortcode en bloque HTML/shortcode

### Paso 4 — Verificar funcionamiento

Submit el form con datos de prueba. Verificar:

```bash
# 1. mu-plugin loguea la submission
ssh livskin-wp 'sudo grep livskin /var/log/nginx/error.log | tail -3'

# Debe ver: "[livskin] form_id=<FORM_ID> webhook=...form-submit nombre_present=1 phone_present=1 ..."

# 2. Lead aparece en Vtiger (~1 segundo después)
ssh livskin-ops 'docker exec vtiger-db mysql -u livskin -plivskin livskin_db -e "SELECT leadid, firstname, lastname, email FROM vtiger_leaddetails ORDER BY leadid DESC LIMIT 3;"'

# 3. Lead aparece en ERP (~2-3 min después, esperando cron [B3])
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT id, vtiger_id, nombre, utm_source_at_capture FROM leads ORDER BY id DESC LIMIT 3;"'
```

Si los 3 retornan datos del nuevo lead → integración OK.

---

## Cómo activar un form en MODO TEST (sin tocar Vtiger/ERP)

Útil para validar flow sin contaminar producción.

```bash
ssh livskin-wp 'sudo -u www-data wp post meta update <FORM_ID> _livskin_n8n_sync test --path=/var/www/livskin'
```

En modo test, el mu-plugin **loguea el payload pero NO postea a n8n**. Verificar logs:

```bash
ssh livskin-wp 'sudo grep "TEST.*form_id=<FORM_ID>" /var/log/nginx/error.log | tail -3'
```

Cuando estés satisfecho, switch a prod (eliminar post_meta para fallback hardcoded, o setear `prod`):

```bash
ssh livskin-wp 'sudo -u www-data wp post meta delete <FORM_ID> _livskin_n8n_sync --path=/var/www/livskin'
# o
ssh livskin-wp 'sudo -u www-data wp post meta update <FORM_ID> _livskin_n8n_sync prod --path=/var/www/livskin'
```

---

## Cómo desactivar un form (sin borrarlo)

```bash
ssh livskin-wp 'sudo -u www-data wp post meta update <FORM_ID> _livskin_n8n_sync off --path=/var/www/livskin'
```

El form sigue funcionando (entries en `wp_srfm_entries`) pero NO se sincroniza a Vtiger/ERP.

---

## Configurar tratamiento default por landing

Si una landing es específica para un tratamiento (ej: `/botox` solo lead de botox), el form puede no incluir el dropdown "Tratamiento" — el mu-plugin asigna el default desde código.

**Editar `infra/wordpress/mu-plugins/livskin-form-to-n8n.php`** función `livskin_forms_default()`:

```php
function livskin_forms_default() {
    return [
        1569 => ['mode' => 'prod', 'treatment_default' => null],         // home genérica
        1570 => ['mode' => 'prod', 'treatment_default' => 'Botox'],      // landing /botox
        1571 => ['mode' => 'prod', 'treatment_default' => 'PRP'],        // landing /prp
    ];
}
```

Re-deploy a VPS 1:

```bash
scp infra/wordpress/mu-plugins/livskin-form-to-n8n.php livskin-wp:/tmp/
ssh livskin-wp 'sudo cp /tmp/livskin-form-to-n8n.php /var/www/livskin/wp-content/mu-plugins/ && sudo chown www-data:www-data /var/www/livskin/wp-content/mu-plugins/livskin-form-to-n8n.php'
```

---

## Cómo adaptarse a ediciones del form 1569 (o cualquier form existente)

| Cambio en SureForms admin | mu-plugin adaptación |
|---|---|
| Renombrar field "Nombres" → "Tu nombre" | NINGUNA — match por slug `text-field` |
| Reordenar fields | NINGUNA — no dependemos de orden |
| Agregar field nuevo (ej: edad) | NINGUNA — n8n schema lo ignora si no está mapeado |
| Cambiar label "Telefono" → "WhatsApp" | NINGUNA — fuzzy match `whatsapp` activa |
| Eliminar field email | NINGUNA — payload sale con email vacío, n8n acepta |
| Cambiar dropdown options "Botox" → "Botox Premium" | ⚠ Verificar Vtiger picklist `cf_875` acepta el nuevo valor; si no, agregar en Vtiger UI |

**Si el form usa labels exóticos NO matcheados por fuzzy** (ej: campo "Cédula" → mu-plugin no sabe qué es), editar `livskin_extract_user_fields()` en el mu-plugin agregando el patrón.

---

## Troubleshooting

### Lead no aparece en Vtiger después de submit

**Diagnóstico secuencial:**

```bash
# 1. mu-plugin loguea? (si no → mu-plugin no se ejecutó)
ssh livskin-wp 'sudo grep "form_id=<FORM_ID>" /var/log/nginx/error.log | tail -5'

# 2. Form mode = prod?
ssh livskin-wp 'sudo -u www-data wp post meta get <FORM_ID> _livskin_n8n_sync --path=/var/www/livskin'
# Debe ser 'prod' o vacío (con form_id en LIVSKIN_FORMS_DEFAULT como prod)

# 3. n8n recibió el webhook?
ssh livskin-ops 'docker logs n8n --since 5m 2>&1 | grep "/webhook/acquisition/form-submit" | tail -5'

# 4. n8n [A1] workflow active?
ssh livskin-ops 'sqlite3 /home/livskin/apps/n8n/data/database.sqlite "SELECT id, name, active FROM workflow_entity WHERE id=\"a1-form-submit-vtiger-lead\";"'

# 5. Vtiger reachable from n8n?
ssh livskin-ops 'docker exec n8n node -e "const https = require(\"https\"); https.get(\"https://crm.livskin.site/webservice.php?operation=getchallenge&username=admin\", (r) => { let d = \"\"; r.on(\"data\", c => d += c); r.on(\"end\", () => console.log(d.substring(0, 100))); });"'
```

### Lead aparece en Vtiger pero NO en ERP

**Diagnóstico:**

```bash
# 1. Workflow [B3] active?
ssh livskin-ops 'sqlite3 /home/livskin/apps/n8n/data/database.sqlite "SELECT name, active FROM workflow_entity WHERE id=\"b3-vtiger-modified-cron-pull\";"'
# active=1?

# 2. [B3] executions recientes?
ssh livskin-ops 'sqlite3 /home/livskin/apps/n8n/data/database.sqlite "SELECT id, status, startedAt FROM execution_entity WHERE workflowId=\"b3-vtiger-modified-cron-pull\" ORDER BY id DESC LIMIT 5;"'
# Debe haber executions cada 2 min con status=success

# 3. [B3] llega a postear al ERP endpoint?
# Inspeccionar execution data en n8n UI: https://flow.livskin.site → Workflows → [B3] → Executions

# 4. Endpoint ERP responde?
TOKEN=$(ssh livskin-erp 'sudo cat /srv/livskin-revops/keys/.audit-internal-token')
curl -sk https://erp.livskin.site/api/leads/sync-from-vtiger -X POST -H "Content-Type: application/json" -H "X-Internal-Token: $TOKEN" -d '{"vtiger_id":"10xTEST","nombre":"Manual Test","phone_e164":"+51999000000"}'
# Esperar 200 OK
```

### Custom field nuevo en form no se ve en Vtiger

Si Dario agrega un nuevo field a form 1569 que debe propagarse:

1. Agregar el custom field correspondiente en Vtiger (runbook `vtiger-custom-fields.md`)
2. Update `integrations/vtiger/fields-mapping.md` con la nueva fila cf_NNN ↔ ERP
3. Update mapping en `livskin_extract_user_fields()` del mu-plugin si requiere fuzzy match nuevo
4. Update mapping en n8n workflow [A1] (Build Create Payload node) + [B1]/[B3] (Map Vtiger to ERP Schema node)
5. Update Migration Alembic si requiere nueva columna en ERP `leads`

---

## Roadmap futuro

| Cuándo | Cambio |
|---|---|
| Bloque puente Agenda (entre F3 y F4) | Tabla `appointments` + campo "fecha cita" en form (opcional) |
| Mini-bloque 3.4 (CAPI) | Lead emite Lead event a Meta CAPI server-side |
| Fase 4 (Conversation Agent) | Forms en landings de WhatsApp (deeplink + form genérico) |
| Fase 5 (Brand Orchestrator) | Auto-creación de forms via API al deployar nueva landing |
| Fase 6 (Custom PHP Hook Vtiger) | Realtime webhook on-change reemplaza cron de [B3] |

---

## Cross-references

- `infra/wordpress/mu-plugins/livskin-form-to-n8n.php` — código del mu-plugin
- `infra/n8n/workflows/A-acquisition/a1-form-submit-to-vtiger-lead.md` — workflow A1
- `infra/n8n/workflows/B-bridge/b3-vtiger-modified-cron-pull.md` — workflow B3
- `integrations/vtiger/fields-mapping.md` — mapeo cf_NNN ↔ ERP
- `docs/runbooks/vtiger-custom-fields.md` — agregar custom fields Vtiger
- ADR-0011 v1.1 — modelo datos lead/cliente/venta
- ADR-0015 — Source of Truth por dominio
- Memoria `project_capi_match_quality` — por qué los 12 fields son los correctos
