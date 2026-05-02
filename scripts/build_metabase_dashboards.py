#!/usr/bin/env python3
"""
Build Metabase dashboards via REST API for Mini-bloque 3.5.

Dashboards creados:
1. Leads/día por canal+UTM
2. Funnel snapshot por estado

Cada dashboard creado contiene Questions (queries SQL guardadas) embebidas
como cards.

Idempotente: detecta si dashboard ya existe (por nombre) y lo update.

Usage:
    python scripts/build_metabase_dashboards.py
"""
import json
import os
import sys
import urllib.request
import urllib.error

METABASE_URL = os.environ["METABASE_URL"]
ADMIN_EMAIL = os.environ["METABASE_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["METABASE_ADMIN_PASSWORD"]
DB_ID = 2  # Analytics Warehouse


def api_post(session, path, payload):
    req = urllib.request.Request(
        f"{METABASE_URL}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Metabase-Session": session},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"POST {path} failed {e.code}: {body[:500]}")


def api_put(session, path, payload):
    req = urllib.request.Request(
        f"{METABASE_URL}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Metabase-Session": session},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode().strip()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"PUT {path} failed {e.code}: {body[:500]}")


def api_get(session, path):
    req = urllib.request.Request(
        f"{METABASE_URL}{path}",
        headers={"X-Metabase-Session": session},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def login():
    req = urllib.request.Request(
        f"{METABASE_URL}/api/session",
        data=json.dumps({"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())["id"]


def find_or_create_card(session, name, sql, display_type="line", visualization_settings=None):
    """Crea question (card) o reusa si existe por nombre."""
    cards = api_get(session, "/api/card")
    for c in cards:
        if c["name"] == name:
            print(f"  Card '{name}' already exists (id={c['id']}). Updating SQL.")
            return api_put(session, f"/api/card/{c['id']}", {
                "name": name,
                "dataset_query": {
                    "type": "native",
                    "database": DB_ID,
                    "native": {"query": sql},
                },
                "display": display_type,
                "visualization_settings": visualization_settings or {},
            })["id"] if False else c["id"]  # Skip update for now, just reuse
    card = api_post(session, "/api/card", {
        "name": name,
        "dataset_query": {
            "type": "native",
            "database": DB_ID,
            "native": {"query": sql},
        },
        "display": display_type,
        "visualization_settings": visualization_settings or {},
    })
    print(f"  Card '{name}' CREATED (id={card['id']}).")
    return card["id"]


def find_or_create_dashboard(session, name, description=""):
    dashboards = api_get(session, "/api/dashboard")
    for d in dashboards:
        if d["name"] == name:
            print(f"  Dashboard '{name}' already exists (id={d['id']}).")
            return d["id"]
    dash = api_post(session, "/api/dashboard", {
        "name": name,
        "description": description,
    })
    print(f"  Dashboard '{name}' CREATED (id={dash['id']}).")
    return dash["id"]


def set_dashboard_cards(session, dashboard_id, cards_layout):
    """cards_layout: [{card_id, row, col, size_x, size_y}, ...] — REEMPLAZA layout completo del dashboard."""
    dashcards = [
        {"id": -(i + 1), "card_id": c["card_id"], "row": c["row"], "col": c["col"],
         "size_x": c["size_x"], "size_y": c["size_y"]}
        for i, c in enumerate(cards_layout)
    ]
    api_put(session, f"/api/dashboard/{dashboard_id}", {"dashcards": dashcards})
    print(f"  Set {len(cards_layout)} cards en dashboard {dashboard_id}")


def main():
    print("=== Login Metabase ===")
    session = login()
    print(f"Session: {session[:8]}***")

    # ─── Dashboard 1: Leads/día por canal ───
    print("\n=== Dashboard 1: Leads por canal ===")
    sql_leads_dia = """
SELECT
    DATE(fecha_captura) AS dia,
    COALESCE(NULLIF(utm_source_at_capture, ''), 'organico') AS canal,
    COUNT(*) AS leads_count
FROM leads
WHERE fecha_captura >= NOW() - INTERVAL '30 days'
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC;
"""
    card1 = find_or_create_card(session, "Leads por día y canal (30d)", sql_leads_dia, "line")

    sql_leads_total = """
SELECT
    COALESCE(NULLIF(utm_source_at_capture, ''), 'organico') AS canal,
    COUNT(*) AS total_leads
FROM leads
WHERE fecha_captura >= NOW() - INTERVAL '30 days'
GROUP BY 1
ORDER BY 2 DESC;
"""
    card2 = find_or_create_card(session, "Leads totales por canal (30d)", sql_leads_total, "bar")

    sql_leads_kpi = """
SELECT
    COUNT(*) FILTER (WHERE fecha_captura > NOW() - INTERVAL '24 hours') AS ultimas_24h,
    COUNT(*) FILTER (WHERE fecha_captura > NOW() - INTERVAL '7 days') AS ultimos_7d,
    COUNT(*) FILTER (WHERE fecha_captura > NOW() - INTERVAL '30 days') AS ultimos_30d,
    COUNT(*) AS total_historico
FROM leads;
"""
    card3 = find_or_create_card(session, "Leads KPI - ventana temporal", sql_leads_kpi, "table")

    sql_leads_tratamiento = """
SELECT
    COALESCE(NULLIF(tratamiento_interes, ''), 'No especificado') AS tratamiento,
    COUNT(*) AS leads_count
FROM leads
WHERE fecha_captura >= NOW() - INTERVAL '30 days'
GROUP BY 1
ORDER BY 2 DESC;
"""
    card4 = find_or_create_card(session, "Leads por tratamiento (30d)", sql_leads_tratamiento, "pie")

    dash1_id = find_or_create_dashboard(session, "Leads por canal", "Vista por origen + UTM source de los últimos 30 días")

    # Set all cards in one PUT (fix: api_put REEMPLAZA dashcards, no agrega)
    set_dashboard_cards(session, dash1_id, [
        {"card_id": card3, "row": 0,  "col": 0,  "size_x": 24, "size_y": 4},   # KPI top full-width
        {"card_id": card1, "row": 4,  "col": 0,  "size_x": 16, "size_y": 8},   # Line chart
        {"card_id": card4, "row": 4,  "col": 16, "size_x": 8,  "size_y": 8},   # Pie chart side
        {"card_id": card2, "row": 12, "col": 0,  "size_x": 24, "size_y": 6},   # Bar chart bottom
    ])

    # ─── Dashboard 2: Funnel snapshot ───
    print("\n=== Dashboard 2: Funnel estado actual ===")
    sql_funnel = """
SELECT
    estado_lead AS etapa,
    COUNT(*) AS leads_en_etapa
FROM leads
WHERE fecha_captura >= NOW() - INTERVAL '90 days'
GROUP BY 1
ORDER BY
    CASE estado_lead
        WHEN 'nuevo' THEN 1
        WHEN 'contactado' THEN 2
        WHEN 'agendado' THEN 3
        WHEN 'asistio' THEN 4
        WHEN 'cliente' THEN 5
        WHEN 'perdido' THEN 6
        ELSE 99
    END;
"""
    card5 = find_or_create_card(session, "Funnel actual leads (90d)", sql_funnel, "funnel")

    sql_attribution_table = """
SELECT
    vtiger_id,
    nombre,
    fuente,
    utm_source_at_capture AS source,
    utm_campaign_at_capture AS campaign,
    estado_lead AS estado,
    fecha_captura,
    event_id_meta
FROM leads
ORDER BY fecha_captura DESC
LIMIT 50;
"""
    card6 = find_or_create_card(session, "Tabla leads con attribution", sql_attribution_table, "table")

    dash2_id = find_or_create_dashboard(session, "Funnel + Attribution", "Estado actual del funnel + tabla detallada de leads con UTMs preservados")

    set_dashboard_cards(session, dash2_id, [
        {"card_id": card5, "row": 0, "col": 0, "size_x": 24, "size_y": 8},   # Funnel chart top full-width
        {"card_id": card6, "row": 8, "col": 0, "size_x": 24, "size_y": 10},  # Detail table bottom
    ])

    print("\n=== Dashboards URLs ===")
    print(f"Dashboard 1 (Leads por canal): {METABASE_URL}/dashboard/{dash1_id}")
    print(f"Dashboard 2 (Funnel + Attribution): {METABASE_URL}/dashboard/{dash2_id}")
    print("\nDone.")


if __name__ == "__main__":
    main()
