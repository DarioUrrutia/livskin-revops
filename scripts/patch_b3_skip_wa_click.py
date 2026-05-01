#!/usr/bin/env python3
"""
Patch n8n workflow [B3] to skip ERP sync for wa-click leads (Opcion B
del hallazgo smoke 2026-05-01: leads sin phone no son operacionalmente
accionables; viven solo en Vtiger para attribution marketing).

Modifica el nodo "Map Vtiger to ERP Schema" para que si leadsource ===
'WA Direct Click', devuelva un array vacio (los items no continuan al
POST ERP).

Idempotente: detecta marker "B3_SKIP_WA_CLICK_v1" y rechaza re-aplicar.

Usage:
    python scripts/patch_b3_skip_wa_click.py <input.json> <output.json>
"""
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: patch_b3_skip_wa_click.py <input.json> <output.json>", file=sys.stderr)
    sys.exit(2)

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

with open(src, encoding='utf-8') as f:
    data = json.load(f)

wf = data[0] if isinstance(data, list) else data

if 'B3_SKIP_WA_CLICK_v1' in json.dumps(wf):
    print('ERROR: workflow already has B3_SKIP_WA_CLICK_v1 marker', file=sys.stderr)
    sys.exit(1)

new_map_code = (
    "// [B3] paso 9: Map Vtiger fields cf_NNN -> ERP schema (mismo mapping que [B1])\n"
    "// B3_SKIP_WA_CLICK_v1 (2026-05-01): wa-click leads NO se sincronizan a ERP.\n"
    "// Razon arquitectonica: WA-click leads no tienen phone (visitor solo clickeo),\n"
    "// por lo que no son accionables operativamente en ERP. Viven en Vtiger para\n"
    "// marketing attribution (Pixel + CAPI client-side ya cubren la attribution Meta).\n"
    "// Cuando la doctora atiende WA y crea cliente real en ERP, se vincula manualmente\n"
    "// por phone real del visitante.\n"
    "\n"
    "const retrieveResponse = $input.first().json;\n"
    "if (!retrieveResponse.success) {\n"
    "  throw new Error('Vtiger retrieve failed: ' + JSON.stringify(retrieveResponse));\n"
    "}\n"
    "\n"
    "const v = retrieveResponse.result;\n"
    "\n"
    "// Skip wa-click leads: no llegan al ERP (Opcion B documentada)\n"
    "if (v.leadsource === 'WA Direct Click') {\n"
    "  return [];\n"
    "}\n"
    "\n"
    "const nombre = ((v.firstname || '') + ' ' + (v.lastname || '')).trim() || '(sin nombre)';\n"
    "\n"
    "const erpPayload = {\n"
    "  vtiger_id: v.id,\n"
    "  nombre,\n"
    "  phone_e164: v.phone || '',\n"
    "  email: v.email || '',\n"
    "  leadstatus: v.leadstatus || '',\n"
    "  leadsource: v.leadsource || '',\n"
    "  utm_source: v.cf_853 || '',\n"
    "  utm_medium: v.cf_855 || '',\n"
    "  utm_campaign: v.cf_857 || '',\n"
    "  utm_content: v.cf_859 || '',\n"
    "  utm_term: v.cf_861 || '',\n"
    "  fbclid: v.cf_863 || '',\n"
    "  gclid: v.cf_865 || '',\n"
    "  fbc: v.cf_867 || '',\n"
    "  ga: v.cf_869 || '',\n"
    "  event_id: v.cf_871 || '',\n"
    "  landing_url: v.cf_873 || '',\n"
    "  tratamiento_interes: v.cf_875 || '',\n"
    "  consent_marketing: false,\n"
    "};\n"
    "\n"
    "return [{ json: erpPayload }];"
)

patched = 0
for node in wf['nodes']:
    if node.get('id') == 'node-map-to-erp':
        node['parameters']['jsCode'] = new_map_code
        patched += 1
        print('  + patched Map Vtiger to ERP Schema')

if patched != 1:
    print(f'ERROR: expected 1 patch, only applied {patched}', file=sys.stderr)
    sys.exit(1)

with open(dst, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Wrote {dst} ({patched} patch applied)')
