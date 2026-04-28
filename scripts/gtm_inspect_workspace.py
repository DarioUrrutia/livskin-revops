"""Inspeccion completa del workspace GTM (Default Workspace) vs live version.

Muestra tags + triggers + variables + folders del workspace y de la live version
17 para identificar exactamente que es el "1 cambio sin publicar".
"""
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = "keys/google-oauth-token.json"
ACCOUNT_PATH = "accounts/6344785058"
CONTAINER_PATH = "accounts/6344785058/containers/246604629"


def load_creds() -> Credentials:
    data = json.loads(Path(TOKEN_FILE).read_text(encoding="utf-8"))
    return Credentials(
        token=data["token"], refresh_token=data["refresh_token"],
        token_uri=data["token_uri"], client_id=data["client_id"],
        client_secret=data["client_secret"], scopes=data["scopes"],
    )


def section(t: str) -> None:
    print(f"\n{'='*60}\n{t}\n{'='*60}")


def show_tag(t: dict, prefix: str = "") -> None:
    print(f"{prefix}TAG: {t.get('name')!r} type={t.get('type')} "
          f"firingTriggerId={t.get('firingTriggerId')} "
          f"paused={t.get('paused', False)}")
    for p in t.get("parameter", []) or []:
        v = str(p.get("value", ""))[:80]
        print(f"{prefix}  param[{p.get('key')}] = {v}")


def show_trigger(tr: dict, prefix: str = "") -> None:
    print(f"{prefix}TRIGGER: {tr.get('name')!r} type={tr.get('type')} "
          f"id={tr.get('triggerId')}")


def show_variable(v: dict, prefix: str = "") -> None:
    print(f"{prefix}VAR: {v.get('name')!r} type={v.get('type')} "
          f"id={v.get('variableId')}")


def main() -> None:
    creds = load_creds()
    tm = build("tagmanager", "v2", credentials=creds)

    section("LIVE VERSION (publicada actualmente)")
    live = tm.accounts().containers().versions().live(parent=CONTAINER_PATH).execute()
    print(f"Live version: {live.get('containerVersionId')} '{live.get('name')}'")
    for t in live.get("tag", []) or []:
        show_tag(t)
    print(f"\n  Live triggers ({len(live.get('trigger', []) or [])}):")
    for tr in live.get("trigger", []) or []:
        show_trigger(tr, "  ")
    print(f"\n  Live variables ({len(live.get('variable', []) or [])}):")
    for v in live.get("variable", []) or []:
        show_variable(v, "  ")

    section("WORKSPACE: Default Workspace (draft)")
    ws_list = (
        tm.accounts().containers().workspaces().list(parent=CONTAINER_PATH).execute()
        .get("workspace", [])
    )
    ws = ws_list[0]
    ws_path = ws["path"]
    print(f"Workspace: {ws.get('name')} (id={ws.get('workspaceId')})")

    tags = tm.accounts().containers().workspaces().tags().list(parent=ws_path).execute().get("tag", [])
    print(f"\nTags en workspace ({len(tags)}):")
    for t in tags:
        show_tag(t, "  ")

    triggers = tm.accounts().containers().workspaces().triggers().list(parent=ws_path).execute().get("trigger", [])
    print(f"\nTriggers en workspace ({len(triggers)}):")
    for tr in triggers:
        show_trigger(tr, "  ")

    variables = tm.accounts().containers().workspaces().variables().list(parent=ws_path).execute().get("variable", [])
    print(f"\nVariables en workspace ({len(variables)}):")
    for v in variables:
        show_variable(v, "  ")

    section("STATUS — cambios pendientes en workspace")
    try:
        status = (
            tm.accounts().containers().workspaces()
            .getStatus(path=ws_path).execute()
        )
        changes = status.get("workspaceChange", [])
        print(f"Total cambios: {len(changes)}")
        for c in changes:
            kind = c.get("changeStatus")
            ent = c.get("tag") or c.get("trigger") or c.get("variable") or {}
            name = ent.get("name", "(sin nombre)")
            print(f"  {kind}: {name}")
    except Exception as e:
        print(f"  status error: {e}")


if __name__ == "__main__":
    main()
