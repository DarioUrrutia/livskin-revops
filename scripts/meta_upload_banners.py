"""
Upload 4 banners to Meta Ad Account → get image_hashes for ad creatives.

Doctrina #8: API > UI.
"""
import json
import os
import sys
import io
import urllib.request
import urllib.parse
import urllib.error
import mimetypes

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

ENV_FILE = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/keys/.env.integrations"
BANNER_DIR = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/banners-mayo-2026"
OUT_RESULT = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/meta-banners-uploaded.json"
AD_ACCOUNT = "act_2885433191763149"

BANNERS = [
    ("01-botox.jpeg", "botox"),
    ("02-acido.jpeg", "acido"),
    ("03-prp.jpeg", "prp"),
    ("04-limpieza.jpeg", "limpieza"),
]


def load_env():
    env = {}
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#') or '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def upload_image(token, filepath):
    """Upload binary image to Meta Ad Account, return image_hash."""
    url = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT}/adimages"

    # Multipart/form-data: file field name = basename of file (according to Meta docs)
    boundary = "----MetaUploadBoundary"
    filename = os.path.basename(filepath)
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = "image/jpeg"

    with open(filepath, 'rb') as f:
        file_bytes = f.read()

    body = b""
    # access_token field
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="access_token"\r\n\r\n'.encode()
    body += token.encode() + b"\r\n"
    # File field — name must match field name Meta expects (any name works for adimages endpoint)
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="{filename}"; filename="{filename}"\r\n'.encode()
    body += f'Content-Type: {mime}\r\n\r\n'.encode()
    body += file_bytes + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(url, data=body, method='POST',
                                 headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body_err = e.read().decode('utf-8', errors='replace')
        return {"_error_code": e.code, "_error_body": body_err}


def main():
    env = load_env()
    token = env["META_SYSTEM_USER_TOKEN"]
    results = []

    for filename, product in BANNERS:
        path = os.path.join(BANNER_DIR, filename)
        if not os.path.exists(path):
            print(f"[SKIP] {filename}: file not found")
            results.append({"product": product, "filename": filename, "error": "not_found"})
            continue
        size_kb = os.path.getsize(path) // 1024
        print(f"[UPLOAD] {filename} ({size_kb}KB)...")
        result = upload_image(token, path)
        if "_error_code" in result:
            print(f"     ERROR {result['_error_code']}: {result['_error_body'][:200]}")
            results.append({"product": product, "filename": filename, "result": result})
        else:
            # Meta returns {"images": {"filename.jpeg": {"hash": "...", "url": "..."}}}
            images = result.get("images", {})
            first = next(iter(images.values()), None)
            image_hash = first.get("hash") if first else None
            url = first.get("url") if first else None
            print(f"     OK: hash={image_hash}")
            results.append({
                "product": product,
                "filename": filename,
                "image_hash": image_hash,
                "url": url,
                "raw": result,
            })

    with open(OUT_RESULT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n--- Summary ---")
    for r in results:
        if "image_hash" in r:
            print(f"  {r['product']}: {r['image_hash']}")
        else:
            print(f"  {r['product']}: FAILED")

    print(f"\nResults saved to: {OUT_RESULT}")


if __name__ == '__main__':
    main()
