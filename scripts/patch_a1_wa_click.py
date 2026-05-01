#!/usr/bin/env python3
"""
Patch n8n workflow [A1] to accept _source: 'wa-click' WA click events
that arrive without phone (visitor never entered one).

3 modifications:
  - Validate Phone:    skip phone validation if _source == 'wa-click'
  - Decide Create:     force _lead_exists=false if _source == 'wa-click' (no phone dedup)
  - Build CREATE:      set leadsource='WA Direct Click' + phone='' for wa-click

Idempotent: detects "WA_CLICK_PATCH_v1_1" marker and refuses to double-apply.

Usage:
    python scripts/patch_a1_wa_click.py <input.json> <output.json>
"""
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: patch_a1_wa_click.py <input.json> <output.json>", file=sys.stderr)
    sys.exit(2)

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

with open(src, encoding='utf-8') as f:
    data = json.load(f)

wf = data[0] if isinstance(data, list) else data

if 'WA_CLICK_PATCH_v1_1' in json.dumps(wf):
    print('ERROR: workflow already has WA_CLICK_PATCH_v1_1 marker - refusing double-apply', file=sys.stderr)
    sys.exit(1)

new_validate_phone = (
    "// [A1] paso 2: Validate & Normalize Phone to E.164 (default Peru +51)\n"
    "// WA_CLICK_PATCH_v1_1 (2026-05-01): accept _source='wa-click' with empty phone.\n"
    "// In that case, phone_e164='' and downstream skips dedup + sets distinctive leadsource.\n"
    "\n"
    "const body = $input.first().json.body || $input.first().json;\n"
    "const phoneRaw = (body.phone || '').toString().trim();\n"
    "const isWaClick = body._source === 'wa-click';\n"
    "\n"
    "if (!phoneRaw) {\n"
    "  if (isWaClick) {\n"
    "    return [{ json: { ...body, phone_e164: '', _phone_invalid: false, _is_wa_click: true } }];\n"
    "  }\n"
    "  return [{ json: { ...body, _phone_invalid: true, _phone_error: 'empty' } }];\n"
    "}\n"
    "\n"
    "let cleaned = phoneRaw.replace(/[^\\d+]/g, '');\n"
    "\n"
    "let phone_e164 = null;\n"
    "\n"
    "if (cleaned.startsWith('+')) {\n"
    "  const digits = cleaned.slice(1);\n"
    "  if (digits.length < 8 || digits.length > 15) {\n"
    "    return [{ json: { ...body, _phone_invalid: true, _phone_error: 'length_out_of_range' } }];\n"
    "  }\n"
    "  phone_e164 = '+' + digits;\n"
    "} else if (cleaned.startsWith('51') && cleaned.length >= 11 && cleaned.length <= 12) {\n"
    "  phone_e164 = '+' + cleaned;\n"
    "} else if (cleaned.length === 9 && cleaned.startsWith('9')) {\n"
    "  phone_e164 = '+51' + cleaned;\n"
    "} else if (cleaned.length === 11 && cleaned.startsWith('519')) {\n"
    "  phone_e164 = '+' + cleaned;\n"
    "} else {\n"
    "  return [{ json: { ...body, _phone_invalid: true, _phone_error: 'unknown_format' } }];\n"
    "}\n"
    "\n"
    "return [{ json: { ...body, phone_e164, _phone_invalid: false, _is_wa_click: isWaClick } }];"
)

new_decide = (
    "// [A1] paso 7: Decidir create vs existing lead match\n"
    "// WA_CLICK_PATCH_v1_1.1: si _is_wa_click -> short-circuit BEFORE checking query response\n"
    "// (la query con phone='' devuelve INTERNAL_SERVER_ERROR de Vtiger; ignorar para wa-click).\n"
    "\n"
    "const formBody = $('Validate Phone').first().json;\n"
    "const session = $('Capture Session').first().json._vtiger_session;\n"
    "\n"
    "// WA click: phone vacio, no se hizo dedup util; SIEMPRE CREATE\n"
    "if (formBody._is_wa_click) {\n"
    "  return [{ json: { ...formBody, _vtiger_session: session, _lead_exists: false } }];\n"
    "}\n"
    "\n"
    "// Resto del flow: form normal, validar queryResponse\n"
    "const queryResponse = $input.first().json;\n"
    "if (!queryResponse.success) {\n"
    "  throw new Error('Vtiger query failed: ' + JSON.stringify(queryResponse));\n"
    "}\n"
    "\n"
    "const results = queryResponse.result || [];\n"
    "\n"
    "if (results.length > 0) {\n"
    "  return [{ json: {\n"
    "    ...formBody,\n"
    "    _vtiger_session: session,\n"
    "    _lead_exists: true,\n"
    "    _existing_lead_id: results[0].id,\n"
    "  } }];\n"
    "} else {\n"
    "  return [{ json: {\n"
    "    ...formBody,\n"
    "    _vtiger_session: session,\n"
    "    _lead_exists: false,\n"
    "  } }];\n"
    "}"
)

new_build_create = (
    "// [A1] paso 8b: Build CREATE payload con los 12 cf_NNN + nativos\n"
    "// WA_CLICK_PATCH_v1_1: si _is_wa_click -> leadsource='WA Direct Click', phone=''.\n"
    "\n"
    "const body = $input.first().json;\n"
    "\n"
    "const nombreParts = (body.nombre || '').trim().split(/\\s+/);\n"
    "const firstname = nombreParts[0] || '(sin nombre)';\n"
    "const lastname = nombreParts.slice(1).join(' ') || '(sin apellido)';\n"
    "\n"
    "const isWaClick = body._is_wa_click === true;\n"
    "\n"
    "const element = {\n"
    "  firstname,\n"
    "  lastname,\n"
    "  phone: isWaClick ? '' : body.phone_e164,\n"
    "  email: (body.email || '').toLowerCase().trim(),\n"
    "  leadstatus: 'New',\n"
    "  leadsource: isWaClick ? 'WA Direct Click' : 'Web Site',\n"
    "  description: isWaClick ? 'Lead vino de click directo en WhatsApp desde landing - sin captura de form. Atribucion conservada en custom fields.' : '',\n"
    "\n"
    "  cf_853: body.utm_source || '',\n"
    "  cf_855: body.utm_medium || '',\n"
    "  cf_857: body.utm_campaign || '',\n"
    "  cf_859: body.utm_content || '',\n"
    "  cf_861: body.utm_term || '',\n"
    "  cf_863: body.fbclid || '',\n"
    "  cf_865: body.gclid || '',\n"
    "  cf_867: body.fbc || '',\n"
    "  cf_869: body.ga || '',\n"
    "  cf_871: body.event_id || '',\n"
    "  cf_873: body.landing_url || '',\n"
    "  cf_875: body.tratamiento_interes || 'Otro / No especificado',\n"
    "};\n"
    "\n"
    "element.assigned_user_id = '19x1';\n"
    "\n"
    "return [{ json: {\n"
    "  _vtiger_session: body._vtiger_session,\n"
    "  _element_json: JSON.stringify(element),\n"
    "} }];"
)

patched = 0
for node in wf['nodes']:
    if node.get('id') == 'node-normalize-phone':
        node['parameters']['jsCode'] = new_validate_phone
        patched += 1
        print('  + patched Validate Phone')
    elif node.get('id') == 'node-decide-create-or-skip':
        node['parameters']['jsCode'] = new_decide
        patched += 1
        print('  + patched Decide Create or Existing')
    elif node.get('id') == 'node-build-create-payload':
        node['parameters']['jsCode'] = new_build_create
        patched += 1
        print('  + patched Build CREATE payload')

if patched != 3:
    print(f'ERROR: expected 3 patches, only applied {patched}', file=sys.stderr)
    sys.exit(1)

with open(dst, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Wrote {dst} ({patched} patches applied)')
