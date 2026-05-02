#!/usr/bin/env python3
"""
Patch n8n workflow [B3] B3_CONTINUE_ON_FAIL_v1 (2026-05-02):

Bug encontrado tras B3_BATCH_FIX_v1: si un POST ERP falla (e.g., cod_lead race
condition en ERP), TODO el batch de leads del cron muere. Resultado: leads
con timestamps en el window se pierden si comparten ciclo con un erroring lead.

Fix: agregar `continueOnFail: true` al nodo "POST ERP sync-from-vtiger" para que
errores individuales no aborten el batch completo. Items que fallen seran
reintentados en el proximo cron (modifiedtime sigue en window por ~3 min).

Idempotente: detecta marker via `continueOnFail: true` en el nodo y rechaza
re-aplicar.

Usage:
    python scripts/patch_b3_continue_on_fail.py <input.json> <output.json>
"""
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: patch_b3_continue_on_fail.py <input.json> <output.json>", file=sys.stderr)
    sys.exit(2)

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

with open(src, encoding='utf-8') as f:
    data = json.load(f)

wf = data[0] if isinstance(data, list) else data

patched = 0
already_set = False

for node in wf['nodes']:
    if node.get('id') == 'node-erp-post':
        if node.get('continueOnFail') is True:
            already_set = True
            print('  WARN: continueOnFail already True on POST ERP node')
        else:
            # Add continueOnFail at node-root level (n8n typeVersion 4.2 spec)
            node['continueOnFail'] = True
            # Also add retry settings for transient failures
            node['retryOnFail'] = True
            node['waitBetweenTries'] = 1000
            node['maxTries'] = 3
            patched += 1
            print('  + patched POST ERP sync-from-vtiger: continueOnFail=true, retryOnFail=true, maxTries=3')

if patched != 1 and not already_set:
    print(f'ERROR: expected 1 patch, applied {patched}', file=sys.stderr)
    sys.exit(1)

with open(dst, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Wrote {dst}')
