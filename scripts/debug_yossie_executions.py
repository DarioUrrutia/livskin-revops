"""
Lee las ejecuciones recientes de Yossie (D1) y muestra inbound/intent/action/response.
Parser robusto del formato serializado de n8n execution_data.
"""
import subprocess
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

SSH_CMD = [
    "ssh", "-F",
    "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/keys/ssh_config",
    "livskin-ops",
]

def fetch_execution_data(exec_id):
    cmd = SSH_CMD + [f"sudo sqlite3 /home/livskin/apps/n8n/data/database.sqlite 'SELECT data FROM execution_data WHERE executionId = {exec_id};'"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout.strip()

def parse_n8n_data(raw):
    """n8n serializa con referencias por índice. Resuelve hasta encontrar valores reales."""
    try:
        arr = json.loads(raw)
    except Exception:
        return None
    if not isinstance(arr, list):
        return None

    seen = set()
    def resolve(v, depth=0):
        if depth > 10:
            return None
        if isinstance(v, str):
            try:
                idx = int(v)
                if 0 <= idx < len(arr):
                    if idx in seen:
                        return None
                    seen.add(idx)
                    result = resolve(arr[idx], depth+1)
                    seen.discard(idx)
                    return result
            except ValueError:
                pass
            return v
        if isinstance(v, dict):
            return {k: resolve(val, depth+1) for k, val in v.items()}
        if isinstance(v, list):
            return [resolve(val, depth+1) for val in v]
        return v

    return resolve(arr[0])

def fetch_recent_executions(limit=50):
    cmd = SSH_CMD + [f"sudo sqlite3 /home/livskin/apps/n8n/data/database.sqlite 'SELECT id, datetime(startedAt,\"-5 hours\"), status FROM execution_entity WHERE workflowId=\"d0-wa-inbound-receiver\" ORDER BY id DESC LIMIT {limit};'"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("|")
        if len(parts) >= 3:
            out.append({"id": parts[0], "time": parts[1], "status": parts[2]})
    return out

def find_dispatcher_output(raw):
    """Busca en la data raw el output JSON del Yossie Dispatcher."""
    try:
        arr = json.loads(raw)
    except Exception:
        return None
    if not isinstance(arr, list):
        return None

    # Buscar diccionarios que tengan inbound_text + action_type + response_text
    seen = set()
    def resolve_str(v, depth=0):
        if depth > 8:
            return None
        if isinstance(v, str):
            try:
                idx = int(v)
                if 0 <= idx < len(arr) and idx not in seen:
                    seen.add(idx)
                    r = resolve_str(arr[idx], depth+1)
                    seen.discard(idx)
                    return r
            except ValueError:
                return v
        return v

    for i, item in enumerate(arr):
        if isinstance(item, dict) and 'inbound_text' in item and 'response_text' in item and 'action_type' in item:
            return {
                'from': resolve_str(item.get('from', '')),
                'inbound_text': resolve_str(item.get('inbound_text', '')),
                'intent': resolve_str(item.get('intent', '')),
                'confidence': item.get('confidence', 0),
                'referral_product': resolve_str(item.get('referral_product', '')),
                'red_flag': resolve_str(item.get('red_flag', '')),
                'painpoint': resolve_str(item.get('painpoint', '')),
                'info_type': resolve_str(item.get('info_type', '')),
                'action_type': resolve_str(item.get('action_type', '')),
                'response_text': resolve_str(item.get('response_text', '')),
                'escalate': item.get('escalate', False),
            }
    return None

def main():
    execs = fetch_recent_executions(30)
    print(f"Total ejecuciones recientes: {len(execs)}\n")

    conversations = []
    for ex in execs:
        raw = fetch_execution_data(ex['id'])
        out = find_dispatcher_output(raw)
        if out and out.get('inbound_text'):
            conversations.append({**ex, **out})

    # Ordenar por id ascendente (cronológico)
    conversations.sort(key=lambda x: int(x['id']))

    print(f"=== {len(conversations)} mensajes inbound procesados por Yossie ===\n")
    for i, c in enumerate(conversations, 1):
        print(f"--- [{i}] exec={c['id']} @ {c['time']} (Lima) ---")
        print(f"  FROM: {c['from']}")
        print(f"  INBOUND: {c['inbound_text']!r}")
        print(f"  detect: intent={c['intent']} (conf={c['confidence']}) product={c['referral_product']} painpoint={c['painpoint']} info={c['info_type']} red_flag={c['red_flag']}")
        print(f"  ACTION: {c['action_type']} (escalate={c['escalate']})")
        resp = c.get('response_text', '')
        if resp:
            resp_short = resp[:200].replace('\n', '\\n')
            print(f"  RESPONSE: {resp_short}{'...' if len(resp) > 200 else ''}")
        print()

if __name__ == '__main__':
    main()
