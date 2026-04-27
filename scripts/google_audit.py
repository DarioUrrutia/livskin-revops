"""Audit programmatico Google stack — GA4 + GTM.

Lee credenciales OAuth de keys/google-oauth-token.json + client de
keys/google-oauth-client.json y usa Google APIs para extraer:

GA4:
- Lista de accounts + properties accesibles
- Streams de la property Livskin con measurement IDs
- Eventos disparados ultimas 48h (top 20)

GTM:
- Lista de accounts + containers accesibles
- Tags + triggers + variables del container livskin.site
- Versiones publicadas vs workspace actual
- Codigo exacto del tag "Pixel Meta - Config" (clave para resolver doble disparo)
"""
import json
from datetime import date, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = "keys/google-oauth-token.json"


def load_creds() -> Credentials:
    data = json.loads(Path(TOKEN_FILE).read_text(encoding="utf-8"))
    return Credentials(
        token=data["token"],
        refresh_token=data["refresh_token"],
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=data["scopes"],
    )


def section(title: str) -> None:
    print(f"\n{'=' * 70}\n  {title}\n{'=' * 70}")


def audit_ga4_admin(creds: Credentials) -> None:
    section("GA4 — Admin: Accounts + Properties + Streams")
    admin = build("analyticsadmin", "v1beta", credentials=creds)

    accounts = admin.accountSummaries().list().execute().get("accountSummaries", [])
    for acct in accounts:
        print(f"\nAccount: {acct.get('displayName')} (id: {acct.get('account', '').split('/')[-1]})")
        for prop in acct.get("propertySummaries", []):
            prop_name = prop["property"]
            print(f"  Property: {prop.get('displayName')} ({prop_name})")
            try:
                streams = (
                    admin.properties()
                    .dataStreams()
                    .list(parent=prop_name)
                    .execute()
                    .get("dataStreams", [])
                )
                for s in streams:
                    web = s.get("webStreamData", {})
                    print(
                        f"    Stream: {s.get('displayName')} | "
                        f"measurement_id={web.get('measurementId', 'n/a')} | "
                        f"firebase_app_id={web.get('firebaseAppId', 'n/a')} | "
                        f"url={web.get('defaultUri', 'n/a')}"
                    )
            except Exception as e:
                print(f"    (no streams readable: {e})")


def audit_ga4_events(creds: Credentials, property_id: str) -> None:
    section(f"GA4 — Top 20 events ultimas 48h (property {property_id})")
    data = build("analyticsdata", "v1beta", credentials=creds)
    today = date.today()
    yesterday = today - timedelta(days=2)
    try:
        resp = (
            data.properties()
            .runReport(
                property=f"properties/{property_id}",
                body={
                    "dateRanges": [
                        {"startDate": yesterday.isoformat(), "endDate": today.isoformat()}
                    ],
                    "dimensions": [{"name": "eventName"}],
                    "metrics": [{"name": "eventCount"}, {"name": "totalUsers"}],
                    "orderBys": [{"metric": {"metricName": "eventCount"}, "desc": True}],
                    "limit": 20,
                },
            )
            .execute()
        )
        rows = resp.get("rows", [])
        if not rows:
            print("  (sin eventos en ese rango)")
            return
        print(f"  {'event_name':<32} {'count':>10} {'users':>10}")
        for r in rows:
            name = r["dimensionValues"][0]["value"]
            cnt = r["metricValues"][0]["value"]
            usr = r["metricValues"][1]["value"]
            print(f"  {name:<32} {cnt:>10} {usr:>10}")
    except Exception as e:
        print(f"  ERROR: {e}")


def audit_gtm(creds: Credentials) -> None:
    section("GTM — Accounts + Containers + Tags")
    tm = build("tagmanager", "v2", credentials=creds)

    accounts = tm.accounts().list().execute().get("account", [])
    for acct in accounts:
        acct_path = acct["path"]
        print(f"\nAccount: {acct.get('name')} ({acct_path})")
        containers = (
            tm.accounts().containers().list(parent=acct_path).execute().get("container", [])
        )
        for c in containers:
            c_path = c["path"]
            print(f"  Container: {c.get('name')} ({c.get('publicId')}) — {c_path}")

            workspaces = (
                tm.accounts()
                .containers()
                .workspaces()
                .list(parent=c_path)
                .execute()
                .get("workspace", [])
            )
            print(f"    Workspaces: {len(workspaces)}")

            try:
                versions = (
                    tm.accounts()
                    .containers()
                    .versions()
                    .live(parent=c_path)
                    .execute()
                )
                live_id = versions.get("containerVersionId", "?")
                live_name = versions.get("name", "(sin nombre)")
                print(f"    Live version: {live_id} '{live_name}'")
                live_tags = versions.get("tag", []) or []
                live_triggers = versions.get("trigger", []) or []
                live_vars = versions.get("variable", []) or []
                print(
                    f"    Live: {len(live_tags)} tags, "
                    f"{len(live_triggers)} triggers, {len(live_vars)} variables"
                )
                for t in live_tags:
                    print(
                        f"      LIVE TAG: name='{t.get('name')}' type={t.get('type')} "
                        f"firingTriggerId={t.get('firingTriggerId')}"
                    )
            except Exception as e:
                print(f"    (no live version: {e})")

            for ws in workspaces:
                ws_path = ws["path"]
                print(f"    Workspace: {ws.get('name')}")
                tags = (
                    tm.accounts()
                    .containers()
                    .workspaces()
                    .tags()
                    .list(parent=ws_path)
                    .execute()
                    .get("tag", [])
                )
                print(f"      Tags ({len(tags)}):")
                for t in tags:
                    print(f"        - {t.get('name')} | type={t.get('type')}")
                    if "Pixel" in (t.get("name") or "") or t.get("type") == "html":
                        print(
                            f"          firingTriggerId={t.get('firingTriggerId')} "
                            f"paused={t.get('paused', False)}"
                        )
                        for p in t.get("parameter", []) or []:
                            key = p.get("key")
                            val = p.get("value", "")
                            if isinstance(val, str) and len(val) > 200:
                                val = val[:200] + "...(truncated)"
                            print(f"          param[{key}] = {val}")


def main() -> None:
    creds = load_creds()
    audit_ga4_admin(creds)
    audit_gtm(creds)

    # Fetch eventos del property Livskin (id 528880125 segun screenshot)
    audit_ga4_events(creds, "528880125")


if __name__ == "__main__":
    main()
