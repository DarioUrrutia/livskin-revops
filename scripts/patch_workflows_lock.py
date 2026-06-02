"""Patch F1/F2/F3/B3 workflows to acquire distributed lock at start (Sprint 1.3)."""
import json
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

REPO = 'c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin'

WORKFLOWS = [
    {
        'path': f'{REPO}/infra/n8n/workflows/F-followup/f1-reengagement-4h.json',
        'target_node': 'F1 Master (fetch + template + update)',
        'lock_key': 'cron:f1-reengagement-4h',
        'ttl_seconds': 60,
    },
    {
        'path': f'{REPO}/infra/n8n/workflows/F-followup/f2-auto-close-cold-leads.json',
        'target_node': 'F2 Master (find cold + close)',
        'lock_key': 'cron:f2-auto-close-cold-leads',
        'ttl_seconds': 120,
    },
    {
        'path': f'{REPO}/infra/n8n/workflows/F-followup/f3-gdpr-data-deletion.json',
        'target_node': 'F3 Master (find + delete cross-system)',
        'lock_key': 'cron:f3-gdpr-data-deletion',
        'ttl_seconds': 120,
    },
    {
        'path': f'{REPO}/infra/n8n/workflows/B-bridge/b3-vtiger-modified-cron-pull.json',
        'target_node': 'Build Query Window',
        'lock_key': 'cron:b3-vtiger-modified-cron-pull',
        'ttl_seconds': 180,
    },
]

LOCK_GUARD_MARKER = '// === SPRINT_1_3_DISTRIBUTED_LOCK ==='


def build_lock_snippet(lock_key: str, ttl_seconds: int) -> str:
    return f"""{LOCK_GUARD_MARKER}
// Distributed lock (Sprint 1.3, 2026-05-28) — defensa contra overlap entre ejecuciones
// Si otro cron-run ya tiene el lock, este skip. TTL libera tras crash.
// Fail-OPEN: si Redis down, proceder sin lock (preferimos correr 2x que skip).
const _LOCK_ERP_URL = 'https://erp.livskin.site/api/internal/lock';
const _LOCK_AUDIT_TOKEN = $env.AUDIT_INTERNAL_TOKEN;
if (_LOCK_AUDIT_TOKEN) {{
  try {{
    const _lockRes = await this.helpers.httpRequest({{
      method: 'POST',
      url: _LOCK_ERP_URL + '/acquire',
      headers: {{ 'X-Internal-Token': _LOCK_AUDIT_TOKEN, 'Content-Type': 'application/json' }},
      body: {{ key: '{lock_key}', ttl_seconds: {ttl_seconds} }},
      json: true,
      timeout: 5000,
    }});
    if (_lockRes && _lockRes.acquired === false) {{
      return [{{ json: {{ skipped: true, reason: 'lock_held', lock_key: '{lock_key}' }} }}];
    }}
  }} catch (_e) {{
    console.warn('[lock] acquire failed, proceeding without lock:', _e.message);
  }}
}}
// === END SPRINT_1_3_DISTRIBUTED_LOCK ===

"""


def patch_workflow(wf_config: dict) -> bool:
    path = wf_config['path']
    target = wf_config['target_node']
    lock_key = wf_config['lock_key']
    ttl = wf_config['ttl_seconds']

    with open(path, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    found = False
    for node in wf['nodes']:
        if node['name'] != target:
            continue
        code = node.get('parameters', {}).get('jsCode', '')
        if LOCK_GUARD_MARKER in code:
            print(f'  SKIP {target}: already patched')
            return False
        snippet = build_lock_snippet(lock_key, ttl)
        new_code = snippet + code
        node['parameters']['jsCode'] = new_code
        found = True
        print(f'  PATCHED {target}: +{len(snippet)} chars at top')

    if not found:
        print(f'  ERR target node not found: {target}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(wf, f, ensure_ascii=False, separators=(',', ':'))
    return True


if __name__ == '__main__':
    for wf in WORKFLOWS:
        print(f"\n{os.path.basename(wf['path'])}")
        patch_workflow(wf)
    print('\nDone.')
