#!/usr/bin/env python3
"""
Patch n8n workflow [B3] B3_BATCH_FIX_v1 (2026-05-02):

Bug encontrado en smoke comprehensivo: cuando Vtiger devuelve N leads modificados,
el cron procesaba solo 1 (el primero). Causa raiz: dos Code nodes usaban
`$input.first()` en lugar de `$input.all().map(...)`, descartando N-1 items
de cada batch del split.

Fix aplicado a:
- "Prepare Retrieve" (node-prepare-retrieve)
- "Map Vtiger to ERP Schema" (node-map-to-erp) — preserva Op B (skip wa-click)

Idempotente: detecta marker "B3_BATCH_FIX_v1" y rechaza re-aplicar.

Usage:
    python scripts/patch_b3_batch_fix.py <input.json> <output.json>
"""
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: patch_b3_batch_fix.py <input.json> <output.json>", file=sys.stderr)
    sys.exit(2)

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

with open(src, encoding='utf-8') as f:
    data = json.load(f)

wf = data[0] if isinstance(data, list) else data

if 'B3_BATCH_FIX_v1' in json.dumps(wf):
    print('ERROR: workflow already has B3_BATCH_FIX_v1 marker', file=sys.stderr)
    sys.exit(1)

new_prepare_retrieve = (
    "// [B3] paso 7b: Per-item, get session + propagate id\n"
    "// B3_BATCH_FIX_v1 (2026-05-02): procesar TODOS los items del Split, no solo el primero.\n"
    "// Bug previo: $input.first() descartaba N-1 leads del cron batch.\n"
    "\n"
    "const session = $('Capture Session').first().json._vtiger_session;\n"
    "return $input.all().map(it => ({\n"
    "  json: {\n"
    "    vtiger_id: it.json.id,\n"
    "    _vtiger_session: session,\n"
    "  }\n"
    "}));"
)

new_map_to_erp = (
    "// [B3] paso 9: Map Vtiger fields cf_NNN -> ERP schema (mismo mapping que [B1])\n"
    "// B3_BATCH_FIX_v1 (2026-05-02): procesar TODOS los items que retornan de Vtiger Retrieve,\n"
    "// no solo el primero. Bug previo: $input.first() descartaba N-1 leads.\n"
    "// Op B preservada: filter wa-click leads del sync ERP (B3_SKIP_WA_CLICK_v1).\n"
    "\n"
    "const out = [];\n"
    "for (const it of $input.all()) {\n"
    "  const retrieveResponse = it.json;\n"
    "  if (!retrieveResponse.success) {\n"
    "    // Log error pero continuar con los demas items (no abort batch)\n"
    "    console.log('Vtiger retrieve failed for item, skipping:', JSON.stringify(retrieveResponse));\n"
    "    continue;\n"
    "  }\n"
    "  const v = retrieveResponse.result;\n"
    "  // Op B: skip wa-click leads (no llegan a ERP)\n"
    "  if (v.leadsource === 'WA Direct Click') {\n"
    "    continue;\n"
    "  }\n"
    "  const nombre = ((v.firstname || '') + ' ' + (v.lastname || '')).trim() || '(sin nombre)';\n"
    "  out.push({\n"
    "    json: {\n"
    "      vtiger_id: v.id,\n"
    "      nombre,\n"
    "      phone_e164: v.phone || '',\n"
    "      email: v.email || '',\n"
    "      leadstatus: v.leadstatus || '',\n"
    "      leadsource: v.leadsource || '',\n"
    "      utm_source: v.cf_853 || '',\n"
    "      utm_medium: v.cf_855 || '',\n"
    "      utm_campaign: v.cf_857 || '',\n"
    "      utm_content: v.cf_859 || '',\n"
    "      utm_term: v.cf_861 || '',\n"
    "      fbclid: v.cf_863 || '',\n"
    "      gclid: v.cf_865 || '',\n"
    "      fbc: v.cf_867 || '',\n"
    "      ga: v.cf_869 || '',\n"
    "      event_id: v.cf_871 || '',\n"
    "      landing_url: v.cf_873 || '',\n"
    "      tratamiento_interes: v.cf_875 || '',\n"
    "      consent_marketing: false,\n"
    "    }\n"
    "  });\n"
    "}\n"
    "return out;"
)

patched = 0
for node in wf['nodes']:
    if node.get('id') == 'node-prepare-retrieve':
        node['parameters']['jsCode'] = new_prepare_retrieve
        patched += 1
        print('  + patched Prepare Retrieve')
    elif node.get('id') == 'node-map-to-erp':
        node['parameters']['jsCode'] = new_map_to_erp
        patched += 1
        print('  + patched Map Vtiger to ERP Schema')

if patched != 2:
    print(f'ERROR: expected 2 patches, only applied {patched}', file=sys.stderr)
    sys.exit(1)

with open(dst, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Wrote {dst} ({patched} patches applied)')
