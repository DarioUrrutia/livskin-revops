"""Setup one-time del refresh token OAuth para acceso read-only Google.

Corre este script UNA VEZ desde la maquina local. Abre un navegador, Dario
autoriza con daizurma@gmail.com, se guarda refresh token en keys/.

Scopes solicitados (read-only):
- analytics.readonly: leer properties + eventos GA4
- tagmanager.readonly: leer containers + tags GTM

NO se pide Google Ads scope todavia — se agrega cuando haya campañas activas.
"""
import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS = "keys/google-oauth-client.json"
TOKEN_OUT = "keys/google-oauth-token.json"

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/tagmanager.readonly",
    # Write scopes para setup de Fase 3 mini-bloque 3.2 (variables/triggers/tags)
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
]


def main() -> None:
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
        open_browser=True,
        success_message=(
            "Autorizacion OK. Token guardado. Podes cerrar esta pestaña y volver al chat."
        ),
    )

    payload = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
    }
    Path(TOKEN_OUT).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"OK token guardado en {TOKEN_OUT}")
    print(f"refresh_token presente: {bool(creds.refresh_token)}")
    print(f"scopes: {creds.scopes}")


if __name__ == "__main__":
    main()
