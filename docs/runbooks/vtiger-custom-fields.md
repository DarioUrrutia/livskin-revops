---
title: Crear custom fields en módulo Leads de Vtiger 8.2
type: runbook
applies_to: vtiger-vps2
mcp_executable: false
---

# Vtiger 8.2 — Crear custom fields en módulo Leads

**Cuándo usar este runbook:**
- Setup inicial del módulo Leads (Mini-bloque 3.3 REWRITE — primera ejecución)
- Cualquier adición futura de campos custom a Leads (o adaptable a otros módulos: Contacts, Organizations, etc.)

**Requisitos:**
- Acceso admin a https://crm.livskin.site
- Lista de campos a crear con tipo + maxlength + bloque destino

---

## 1. Acceso a Module Layout Editor

1. Login en `https://crm.livskin.site` con usuario admin
2. En la barra superior, click en **gear icon (⚙)** → **Settings**
3. En el menú izquierdo, click **Module Manager** (sección "Studio Designer")
4. En la lista de módulos, encontrar **Leads** → click **Layout Editor** (icono de lápiz a la derecha del módulo)

Estás ahora en el editor visual del Lead. Vas a ver los bloques (secciones colapsables) y los campos dentro de cada uno.

---

## 2. Crear los 2 bloques nuevos (Atribución Digital + Tracking Avanzado)

Antes de agregar campos, creamos los bloques que los van a contener.

### Bloque 1: "Atribución Digital"

1. En el Layout Editor, scroll al final de la lista de bloques existentes
2. Click **Add Block** (botón abajo o "+")
3. **Block Label:** `Atribución Digital`
4. **Block Position:** después de "Lead Information" (default es OK si ya está al final)
5. **Save**

### Bloque 2: "Tracking Avanzado"

Repetir lo mismo con:
- **Block Label:** `Tracking Avanzado`
- **Block Position:** después de "Atribución Digital"

---

## 3. Crear los 12 custom fields

Para cada campo, en el Layout Editor:

1. Localizar el bloque destino (de la tabla abajo)
2. Click **+ Add Custom Field** dentro de ese bloque
3. Completar el formulario según la tabla
4. Click **Save**

### Lista de campos a crear

| # | Bloque destino | Field Type | Label Name | Field Name (auto) | Max Length | Default | Notas |
|---|---|---|---|---|---|---|---|
| 1 | Atribución Digital | Text | UTM Source | `cf_utm_source` | 50 | (vacío) | — |
| 2 | Atribución Digital | Text | UTM Medium | `cf_utm_medium` | 50 | (vacío) | — |
| 3 | Atribución Digital | Text | UTM Campaign | `cf_utm_campaign` | 100 | (vacío) | — |
| 4 | Atribución Digital | Text | UTM Content | `cf_utm_content` | 100 | (vacío) | — |
| 5 | Atribución Digital | Text | UTM Term | `cf_utm_term` | 100 | (vacío) | — |
| 6 | Atribución Digital | Text | FBCLID | `cf_fbclid` | 200 | (vacío) | Meta click ID |
| 7 | Atribución Digital | Text | GCLID | `cf_gclid` | 200 | (vacío) | Google click ID |
| 8 | Tracking Avanzado | Text | FBC Cookie | `cf_fbc` | 200 | (vacío) | Cookie `_fbc` |
| 9 | Tracking Avanzado | Text | GA Cookie | `cf_ga` | 100 | (vacío) | Cookie `_ga` |
| 10 | Tracking Avanzado | Text | Event ID | `cf_event_id` | 64 | (vacío) | UUID GTM |
| 11 | Tracking Avanzado | URL | Landing URL | `cf_landing_url` | 500 | (vacío) | URL completa |
| 12 | Tracking Avanzado | **Picklist** | Tratamiento de Interés | `cf_tratamiento_interes` | — | (vacío) | Ver opciones abajo |

### Para campo #12 — opciones del picklist

Después de seleccionar **Field Type = Picklist**, el formulario te pedirá las opciones. Agregar **una por una** (o copiar/pegar separadas por línea):

```
Botox
Esperma de Salmón / Vtech
PRP
Ácido Hialurónico
Hilos
Limpieza Facial
Rinomodelación
Bioestimuladores
Otro / No especificado
```

**No marcar "Mandatory"** (lo dejamos opcional para que el form WP pueda mandar lead sin tratamiento_interes definido).

### Para los campos Text — flags importantes

Para CADA campo Text (1-11), confirmar:
- **Mandatory:** ❌ DESMARCAR (campos opcionales)
- **Active:** ✅ MARCAR (siempre activo)
- **Quick Create:** ❌ DESMARCAR (no aparecen en el modal de creación rápida)
- **Mass Edit:** ❌ DESMARCAR (no editables masivamente — son al-capture, inmutables conceptualmente)

Para el campo URL (#11):
- Igual que Text + Vtiger valida formato URL automáticamente

---

## 4. Verificación post-creación

### 4.1 Verificar via UI

1. Ir a **CRM** (icono casa arriba) → **Leads**
2. Click **+ Add Lead**
3. Confirmar que aparecen los 2 bloques nuevos al final del form
4. Confirmar que los 12 campos están visibles
5. Llenar uno de prueba (firstname=Test, lastname=Lead, phone=+51999999999) sin tocar los custom fields → Save → debe guardarse OK

### 4.2 Verificar via DB (SSH)

```bash
ssh -F keys/ssh_config livskin-ops 'docker exec vtiger-db mysql -u livskin -plivskin livskin_db \
  -e "SELECT fieldname, fieldlabel, uitype, columnname FROM vtiger_field \
      WHERE tabid=(SELECT tabid FROM vtiger_tab WHERE name=\"Leads\") \
        AND fieldname LIKE \"cf_%\" ORDER BY block;"'
```

Debe listar los 12 fields. Si aparecen menos: revisar cuál falta y crearlo en UI.

### 4.3 Verificar via REST API

```bash
# Login: getchallenge
curl -s "https://crm.livskin.site/webservice.php?operation=getchallenge&username=admin"

# Login: paso 2 — pedir session
# (token devuelto + md5(token + accesskey))

# Describe Leads → debe incluir los 12 cf_*
curl -s "https://crm.livskin.site/webservice.php" \
  -d "operation=describe&sessionName=<session>&elementType=Leads"
```

Detalles completos del REST API en script `scripts/vtiger_describe_leads.py` (a crear en Sub-paso 3.5).

### 4.4 Borrar el Lead de prueba

Después de verificar que se guardó OK:
- Ir a Leads list
- Buscar "Test Lead"
- Click en el lead → 3-dot menu → Delete
- Confirmar

---

## 5. Troubleshooting

### "El campo se creó pero no aparece en el form"

- Refrescar el browser con **Ctrl+Shift+R** (force-reload sin cache)
- Si persiste: SSH al container y limpiar cache de Vtiger:
  ```bash
  ssh livskin-ops 'docker exec vtiger rm -rf /var/www/html/cache/vtlib/*'
  ```

### "Error al guardar el campo: duplicate fieldname"

Vtiger no acepta dos campos con el mismo `fieldname`. Si ya existe `cf_utm_source` (de un intento anterior fallido), borrarlo desde Layout Editor antes de re-crear.

### "Picklist values no aparecen al crear lead"

- En Module Manager → Picklist Editor → seleccionar módulo Leads
- Buscar el picklist `cf_tratamiento_interes`
- Confirmar que las 9 opciones están en "Available" (no en "Disabled")
- **Save** si hubo cambios

---

## 6. Cuándo extender este runbook

- **Nuevos campos custom a Leads** (Fase 5+): agregar a la tabla del paso 3
- **Nuevos módulos**: copiar este runbook como `vtiger-custom-fields-<modulo>.md`
- **Reset de Vtiger** (DR drill): ejecutar este runbook completo después de restaurar DB

---

## Cross-references

- ADR-0011 v1.1 — modelo de datos lead/cliente/venta
- ADR-0015 — SoT por dominio
- Memoria `project_capi_match_quality.md` — por qué los 12 campos son los correctos
- Backlog Mini-bloque 3.3 REWRITE — pre-requisito de este runbook
- Sub-paso 3.5 — `scripts/vtiger_describe_leads.py` consumirá los campos creados
