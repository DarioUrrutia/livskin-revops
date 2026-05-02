#!/usr/bin/env python3
"""Add 'Últimas 20 ventas' card to Dashboard 4 (Revenue Total del Negocio).

Hallazgo Dario 2026-05-02: dashboards mostraban agregados pero faltaba ver
los nombres de las personas que compraron individualmente. Esta card resuelve.
"""
import json
import os
import urllib.request

METABASE_URL = os.environ["METABASE_URL"]
ADMIN_EMAIL = os.environ["METABASE_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["METABASE_ADMIN_PASSWORD"]
DB_ID = 2
DASHBOARD_4_ID = 4


def login():
    req = urllib.request.Request(
        f"{METABASE_URL}/api/session",
        data=json.dumps({"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())["id"]


def api_call(session, method, path, payload=None):
    data = json.dumps(payload).encode() if payload else None
    headers = {"X-Metabase-Session": session}
    if payload:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{METABASE_URL}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode().strip()
        return json.loads(body) if body else {}


def main():
    session = login()
    print(f"Session: {session[:8]}***")

    # Crear card
    sql = """
SELECT
    fecha_venta,
    cliente_nombre,
    cod_cliente,
    tipo,
    categoria,
    total,
    pagado,
    debe,
    CASE
        WHEN cod_lead_origen IS NOT NULL THEN '🟢 Digital'
        ELSE '⚪ Walk-in / Legacy'
    END AS attribution
FROM opportunities
ORDER BY fecha_venta DESC, venta_id DESC
LIMIT 20;
"""
    cards = api_call(session, "GET", "/api/card")
    card_id = None
    for c in cards:
        if c["name"] == "Últimas 20 ventas":
            card_id = c["id"]
            print(f"Card existente, id={card_id}")
            break

    if not card_id:
        new_card = api_call(session, "POST", "/api/card", {
            "name": "Últimas 20 ventas",
            "dataset_query": {"type": "native", "database": DB_ID, "native": {"query": sql}},
            "display": "table",
            "visualization_settings": {}
        })
        card_id = new_card["id"]
        print(f"Card creada id={card_id}")

    # Get current dashboard layout
    dash = api_call(session, "GET", f"/api/dashboard/{DASHBOARD_4_ID}")
    existing_dashcards = dash.get("dashcards", [])
    print(f"Dashboard actual tiene {len(existing_dashcards)} cards")

    # Si la card ya está en el dashboard, no agregar
    if any(dc.get("card_id") == card_id for dc in existing_dashcards):
        print("Card ya estaba en el dashboard")
        return

    # Construir lista preservando existentes + agregar nueva al final (row=20)
    new_dashcards = []
    for i, dc in enumerate(existing_dashcards):
        new_dashcards.append({
            "id": dc["id"],
            "card_id": dc.get("card_id"),
            "row": dc.get("row", 0),
            "col": dc.get("col", 0),
            "size_x": dc.get("size_x", 12),
            "size_y": dc.get("size_y", 4),
        })
    new_dashcards.append({
        "id": -1,
        "card_id": card_id,
        "row": 20,
        "col": 0,
        "size_x": 24,
        "size_y": 10,
    })

    api_call(session, "PUT", f"/api/dashboard/{DASHBOARD_4_ID}", {"dashcards": new_dashcards})
    print(f"Dashboard 4 ahora tiene {len(new_dashcards)} cards (agregado 'Últimas 20 ventas')")


if __name__ == "__main__":
    main()
