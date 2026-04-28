"""Publica el workspace actual como nueva version (v18) del container GTM.

Esto hace LIVE todos los cambios del workspace 18:
- 17 variables (cookies + dataLayer)
- 3 triggers (form_submit_lvk, whatsapp_click, scroll_75)
- 6 tags (Tracking Engine + 3 GA4 Events + 2 Pixel Events)

Si quieres rollback, GTM permite volver a una version anterior desde la UI o API.
"""
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = "keys/google-oauth-token.json"
WS_PATH = "accounts/6344785058/containers/246604629/workspaces/18"


def main() -> None:
    data = json.loads(Path(TOKEN_FILE).read_text(encoding="utf-8"))
    creds = Credentials(
        token=data["token"], refresh_token=data["refresh_token"],
        token_uri=data["token_uri"], client_id=data["client_id"],
        client_secret=data["client_secret"], scopes=data["scopes"],
    )
    tm = build("tagmanager", "v2", credentials=creds)

    # Step 1: create version from workspace
    print("Creando version desde workspace...")
    create_resp = (
        tm.accounts()
        .containers()
        .workspaces()
        .create_version(
            path=WS_PATH,
            body={
                "name": "v18 - Tracking Engine + UTM persistence + events",
                "notes": "Mini-bloque 3.2 Fase 3 — UTM persistence cookies + form_submit/whatsapp_click/scroll events + Pixel CAPI dedup via event_id. Reverted bad workspace change to Pixel Meta Config trigger.",
            },
        )
        .execute()
    )

    if create_resp.get("compilerError"):
        print(f"ERROR compiler: {create_resp['compilerError']}")
        return

    version = create_resp.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    version_path = version.get("path")
    print(f"Version creada: {version_id}")
    print(f"  Tags: {len(version.get('tag', []))}")
    print(f"  Triggers: {len(version.get('trigger', []))}")
    print(f"  Variables: {len(version.get('variable', []))}")

    # Step 2: publish version
    print(f"\nPublicando version {version_id}...")
    pub_resp = tm.accounts().containers().versions().publish(path=version_path).execute()
    print(f"  Published: {pub_resp.get('containerVersion', {}).get('containerVersionId')}")
    print(f"  Compiled: {len(str(pub_resp))} chars")

    # Step 3: verify live version is now the new one
    live = tm.accounts().containers().versions().live(parent="accounts/6344785058/containers/246604629").execute()
    print(f"\n=== VERIFICACION LIVE ===")
    print(f"Live version: {live.get('containerVersionId')} '{live.get('name')}'")
    print(f"Tags live: {len(live.get('tag', []))}")
    print(f"Triggers live: {len(live.get('trigger', []))}")
    print(f"Variables live: {len(live.get('variable', []))}")


if __name__ == "__main__":
    main()
