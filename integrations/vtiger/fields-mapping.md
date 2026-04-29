# Vtiger Leads — mapeo de custom fields al schema ERP

**Fecha de creación:** 2026-04-29 (Mini-bloque 3.3 REWRITE)
**Vtiger version:** 8.2 (community)
**URL:** https://crm.livskin.site

---

## Por qué este doc

Vtiger 8.2 community edition asigna fieldnames numéricos secuenciales (`cf_853`, `cf_855`, ...) a los custom fields, en lugar de usar el label como nombre. Esta peculiaridad obliga a mantener un dictionary de traducción cuando se sincroniza Vtiger con sistemas externos (ERP, n8n, CAPI, dashboards).

**Decisión 2026-04-29 (Opción A):** aceptamos los fieldnames numéricos (no renombramos vía SQL UPDATE — riesgo > valor). En su lugar, este doc es la fuente única de traducción.

---

## Mapeo canónico — 12 custom fields del módulo Leads

| Field Vtiger (interno) | Label UI | Tipo | Maxlen | → Columna ERP `leads` | → Columna ERP `lead_touchpoints` | → Columna ERP `form_submissions` |
|---|---|---|---|---|---|---|
| `cf_853` | UTM Source | Text | 50 | `utm_source_at_capture` | `utm_source` | `utm_source` |
| `cf_855` | UTM Medium | Text | 50 | `utm_medium_at_capture` | `utm_medium` | `utm_medium` |
| `cf_857` | UTM Campaign | Text | 100 | `utm_campaign_at_capture` | `utm_campaign` | `utm_campaign` |
| `cf_859` | UTM Content | Text | 100 | `utm_content_at_capture` | `utm_content` | `utm_content` |
| `cf_861` | UTM Term | Text | 100 | `utm_term_at_capture` | `utm_term` | `utm_term` |
| `cf_863` | FBCLID | Text | 200 | `fbclid_at_capture` | `fbclid` | `fbclid` |
| `cf_865` | GCLID | Text | 200 | `gclid_at_capture` | `gclid` | `gclid` |
| `cf_867` | FBC Cookie | Text | 200 | `fbc_at_capture` | `fbc` | `fbc` |
| `cf_869` | GA Cookie | Text | 100 | `ga_at_capture` | `ga` | `ga` |
| `cf_871` | Event ID | Text | 64 | `event_id_at_capture` | `event_id` | `event_id` |
| `cf_873` | Landing URL | URL | 500 | — | `landing_url` | `landing_url_completa` |
| `cf_875` | Tratamiento de Interés | Picklist | — | `tratamiento_interes` | — | `tratamiento_interes` |

### Picklist values de `cf_875` (Tratamiento de Interés)

| sortorderid | Valor | Mapeo a ERP |
|---|---|---|
| 0 | `Botox` | `botox` (lowercase + ASCII) |
| 1 | `Esperma de Salmón / Vtech` | `vtech` |
| 2 | `PRP` | `prp` |
| 3 | `Ácido Hialurónico` | `acido_hialuronico` |
| 4 | `Hilos` | `hilos` |
| 5 | `Limpieza Facial` | `limpieza_facial` |
| 6 | `Rinomodelación` | `rinomodelacion` |
| 7 | `Bioestimuladores` | `bioestimuladores` |
| 8 | `Otro / No especificado` | `otro` |

**Nota:** la transliteración (Tildes → ASCII, lowercase, espacios → underscore) ocurre en n8n Workflow B (Vtiger → ERP espejo) o en el endpoint Flask `/api/leads/sync-from-vtiger`. El picklist en Vtiger preserva accentos y mayúsculas para legibilidad humana.

---

## Mapeo de fields nativos de Vtiger Leads

Estos NO son custom fields — vienen con Vtiger por default — pero se incluyen en el mapeo n8n:

| Field Vtiger nativo | → Columna ERP `leads` |
|---|---|
| `firstname` + ` ` + `lastname` | `nombre` (concatenado con espacio) |
| `phone` | `phone_e164` (después de normalizar a E.164) |
| `email` | `email_lower` (lowercase + trim) + `email_hash_sha256` |
| `leadstatus` | `estado_lead` (mapping: `New` → `nuevo`, `Cold` → `perdido`, etc.) |
| `leadsource` | `fuente` (mapping específico — ver § Mapping de fuente abajo) |
| `description` | (notas operativas, opcional) |

### Mapping de `leadsource` Vtiger → `fuente` ERP

Vtiger trae un picklist `leadsource` predefinido. Mapeo a los valores canónicos de ADR-0014:

| `leadsource` Vtiger | → `fuente` ERP |
|---|---|
| `Existing Customer` | `referido` |
| `Partner` | `referido` |
| `Conference` | `evento` |
| `Trade Show` | `evento` |
| `Web Site` | `form_web` |
| `Word of mouth` | `organico` |
| `Other` | `otro` |
| (otros valores Vtiger) | `otro` |

**Nota futura:** podemos extender el picklist Vtiger con valores específicos (`meta_ad`, `google_ad`, `instagram_organic`, etc.) en una sesión futura. Por ahora usamos el picklist default + mapping.

---

## Mapping inverso — para n8n Workflow A (form → Vtiger)

Cuando el form WordPress envía datos a n8n, n8n debe poblar Vtiger con los `cf_NNN` correctos:

```javascript
// n8n Function node — input desde mu-plugin POST /webhook/form-submit
const formData = $json;

const vtigerLead = {
    // Nativos
    firstname: formData.nombre.split(' ')[0],
    lastname: formData.nombre.split(' ').slice(1).join(' ') || '(sin apellido)',
    phone: normalizePhoneE164(formData.phone),
    email: formData.email?.toLowerCase().trim() || '',
    leadstatus: 'New',
    leadsource: 'Web Site',

    // Custom fields (cf_NNN — ver fields-mapping.md)
    cf_853: formData.utm_source || '',
    cf_855: formData.utm_medium || '',
    cf_857: formData.utm_campaign || '',
    cf_859: formData.utm_content || '',
    cf_861: formData.utm_term || '',
    cf_863: formData.fbclid || '',
    cf_865: formData.gclid || '',
    cf_867: formData.fbc || '',
    cf_869: formData.ga || '',
    cf_871: formData.event_id || '',
    cf_873: formData.landing_url || '',
    cf_875: formData.tratamiento_interes || 'Otro / No especificado',
};

return { json: vtigerLead };
```

---

## Cómo verificar el mapping vivo (script SQL)

```bash
ssh -F keys/ssh_config livskin-ops 'docker exec vtiger-db mysql -u livskin -plivskin livskin_db \
  -e "SELECT fieldname, fieldlabel, columnname, uitype, typeofdata FROM vtiger_field \
      WHERE tabid=(SELECT tabid FROM vtiger_tab WHERE name=\"Leads\") \
        AND fieldname LIKE \"cf_%\" ORDER BY block, sequence;"'
```

Si los IDs cambiaron (ej: alguien recreó algún campo), actualizar este doc.

---

## Cuándo actualizar este doc

- Cualquier nuevo custom field agregado en Vtiger Leads
- Cualquier cambio de naming/label (improbable, son inmutables conceptualmente)
- Cuando se agreguen custom fields a otros módulos Vtiger (Contacts, Organizations) → crear nuevo doc por módulo
- Si en el futuro se decide renombrar `cf_NNN` → nombres descriptivos (Opción B descartada hoy)

---

## Cross-references

- ADR-0011 v1.1 — modelo de datos lead/cliente/venta (origen del schema ERP)
- ADR-0014 — naming de entidades (códigos canónicos de `fuente`, `canal_adquisicion`)
- ADR-0015 — Source of Truth por dominio (Vtiger=Lead lifecycle, ERP=cliente)
- Memoria `project_capi_match_quality.md` — por qué los 12 fields son los correctos para CAPI
- Runbook `docs/runbooks/vtiger-custom-fields.md` — cómo crear o agregar más
- Migration Alembic 0006 — schema ERP destino
