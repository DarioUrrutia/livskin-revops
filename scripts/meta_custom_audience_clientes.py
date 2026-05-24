"""
Hashea PII clientes ERP (SHA-256) y crea Custom Audience en Meta + 3 Lookalikes 1% Cusco.

Doctrina #8: usa scripts API > UI tanteos.
Doctrina #11: deterministic, no IA fallbacks.

Input: docs/brand/raw/clientes-pii-raw.txt (PSQL output, gitignored)
Output:
- Custom Audience "WC_LIVSKIN_CLIENTES_34"
- Lookalike Audiences derivadas (1% Cusco)

Meta SHA-256 PII normalization rules:
- Phone: only digits, country code first, no '+'
- Email: lowercase, trimmed
- Name: lowercase, no special chars

Refs:
- https://developers.facebook.com/docs/marketing-api/reference/custom-audience/
- https://developers.facebook.com/docs/marketing-api/audiences/guides/custom-audiences#hash
"""
import hashlib
import json
import os
import sys
import io
import urllib.request
import urllib.parse
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

ENV_FILE = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/keys/.env.integrations"
PII_FILE = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/clientes-pii-raw.txt"
OUT_RESULT = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/meta-audiences-created.json"


def load_env():
    env = {}
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def sha256_hex(s: str) -> str:
    if not s:
        return ""
    normalized = s.strip().lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def parse_pii_file(path: str):
    """Parse `psql -t` output (4 columns pipe-separated)."""
    records = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for raw in f:
            line = raw.strip()
            if not line or 'rows' in line.lower():
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 4:
                continue
            phone, fn, ln, email = parts[0], parts[1], parts[2], parts[3]
            if not phone or not phone.isdigit():
                continue
            records.append({
                "phone": phone,
                "first_name": fn,
                "last_name": ln if ln else "",
                "email": email if email else "",
                "country": "pe",
            })
    return records


def build_audience_schema_data(records):
    """Build Meta multi-key user data: [PHONE,EMAIL,FN,LN,COUNTRY]."""
    schema = ["PHONE", "EMAIL", "FN", "LN", "COUNTRY"]
    data = []
    for r in records:
        row = [
            sha256_hex(r["phone"]),
            sha256_hex(r["email"]) if r["email"] else "",
            sha256_hex(r["first_name"]) if r["first_name"] else "",
            sha256_hex(r["last_name"]) if r["last_name"] else "",
            sha256_hex(r["country"]),
        ]
        data.append(row)
    return schema, data


def graph_post(url, params, payload=None):
    if payload is None:
        data_bytes = urllib.parse.urlencode(params).encode('utf-8')
    else:
        # Mix: query params + json body not supported by Meta; use form-encoded for everything
        params_str = urllib.parse.urlencode(params)
        url = f"{url}?{params_str}"
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8'))

    req = urllib.request.Request(url, data=data_bytes, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"\n[ERROR {e.code}] body: {body}\n")
        raise


def graph_get(url, params):
    full = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full, method='GET')
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def create_custom_audience(env, name, description):
    """Step 1: create empty audience."""
    url = f"https://graph.facebook.com/v21.0/act_{env['META_AD_ACCOUNT_ID_NUM']}/customaudiences"
    params = {
        "access_token": env["META_SYSTEM_USER_TOKEN"],
        "name": name,
        "description": description,
        "subtype": "CUSTOM",
        "customer_file_source": "USER_PROVIDED_ONLY",
    }
    return graph_post(url, params)


def add_users_to_audience(env, audience_id, schema, data):
    """Step 2: upload hashed users."""
    url = f"https://graph.facebook.com/v21.0/{audience_id}/users"
    payload = {
        "schema": schema,
        "data": data,
    }
    # Meta wants payload as form param "payload" with JSON string
    params = {
        "access_token": env["META_SYSTEM_USER_TOKEN"],
        "payload": json.dumps(payload),
    }
    return graph_post(url, params)


def create_lookalike(env, name, description, origin_audience_id, country, ratio_start, ratio_end):
    """Create lookalike from custom audience."""
    url = f"https://graph.facebook.com/v21.0/act_{env['META_AD_ACCOUNT_ID_NUM']}/customaudiences"
    lookalike_spec = {
        "type": "custom_ratio",
        "ratio": ratio_end,
        "starting_ratio": ratio_start,
        "country": country,
        "origin_audience_id": origin_audience_id,
    }
    params = {
        "access_token": env["META_SYSTEM_USER_TOKEN"],
        "name": name,
        "description": description,
        "subtype": "LOOKALIKE",
        "origin_audience_id": origin_audience_id,
        "lookalike_spec": json.dumps(lookalike_spec),
    }
    return graph_post(url, params)


def main():
    env = load_env()
    env["META_AD_ACCOUNT_ID_NUM"] = "2885433191763149"

    print("[1/5] Parsing clientes PII raw file...")
    records = parse_pii_file(PII_FILE)
    print(f"     loaded {len(records)} records")

    if not records:
        print("ERROR: no valid records found")
        return

    print("[2/5] Hashing PII with SHA-256...")
    schema, data = build_audience_schema_data(records)
    print(f"     schema: {schema}")
    print(f"     {len(data)} rows hashed (sample row[0] first 4 chars: {data[0][0][:8]}...)")

    print("[3/5] Creating Custom Audience 'WC_LIVSKIN_CLIENTES_34'...")
    audience = create_custom_audience(
        env,
        name="WC_LIVSKIN_CLIENTES_34",
        description=f"Clientes activos ERP con phone validado +51 - {len(data)} records - Created {time.strftime('%Y-%m-%d')}",
    )
    print(f"     created: {json.dumps(audience, indent=2)}")
    audience_id = audience["id"]

    print("[4/5] Uploading hashed users to audience...")
    upload_result = add_users_to_audience(env, audience_id, schema, data)
    print(f"     upload result: {json.dumps(upload_result, indent=2)}")

    print("[5/5] Creating 3 Lookalike audiences (Cusco-PE)...")
    lookalikes = []
    for ratio_start, ratio_end, label in [(0.01, 0.01, "1%"), (0.01, 0.03, "1-3%"), (0.01, 0.05, "1-5%")]:
        name = f"LAL_LIVSKIN_CLIENTES_{label}_PE"
        try:
            lal = create_lookalike(
                env,
                name=name,
                description=f"Lookalike Cusco-PE de WC_LIVSKIN_CLIENTES_34 - {label}",
                origin_audience_id=audience_id,
                country="PE",
                ratio_start=ratio_start,
                ratio_end=ratio_end,
            )
            lookalikes.append({"name": name, "result": lal})
            print(f"     {label}: {lal.get('id', 'ERROR')}")
        except Exception as e:
            print(f"     {label}: FAILED - {e}")
            lookalikes.append({"name": name, "error": str(e)})

    print(f"\nSaving result to {OUT_RESULT}")
    with open(OUT_RESULT, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "audience": audience,
            "upload_result": upload_result,
            "lookalikes": lookalikes,
            "n_records": len(records),
            "schema": schema,
        }, f, ensure_ascii=False, indent=2)

    print("\nDone.")


if __name__ == '__main__':
    main()
