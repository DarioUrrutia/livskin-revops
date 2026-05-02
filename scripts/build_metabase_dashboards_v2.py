#!/usr/bin/env python3
"""Build dashboards adicionales (revenue + funnel digital cerrado) via Metabase API.

Dashboards adicionales:
3. Revenue total del negocio (88+ ventas, breakdown por mes/tipo/cliente)
4. Funnel digital cerrado (lead con UTMs → cliente → venta → revenue atribuido)

Idempotente: detecta dashboards/cards existentes por nombre.
"""
import json
import os
import urllib.request
import urllib.error

METABASE_URL = os.environ["METABASE_URL"]
ADMIN_EMAIL = os.environ["METABASE_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["METABASE_ADMIN_PASSWORD"]
DB_ID = 2  # Analytics Warehouse


def api_post(session, path, payload):
    req = urllib.request.Request(
        f"{METABASE_URL}{path}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Metabase-Session": session},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise Exception(f"POST {path} failed {e.code}: {e.read().decode()[:500]}")


def api_put(session, path, payload):
    req = urllib.request.Request(
        f"{METABASE_URL}{path}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Metabase-Session": session},
        method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode().strip()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raise Exception(f"PUT {path} failed {e.code}: {e.read().decode()[:500]}")


def api_get(session, path):
    req = urllib.request.Request(f"{METABASE_URL}{path}", headers={"X-Metabase-Session": session})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def login():
    req = urllib.request.Request(
        f"{METABASE_URL}/api/session",
        data=json.dumps({"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())["id"]


def find_or_create_card(session, name, sql, display_type="line", visualization_settings=None):
    cards = api_get(session, "/api/card")
    for c in cards:
        if c["name"] == name:
            print(f"  Card '{name}' exists (id={c['id']})")
            return c["id"]
    card = api_post(session, "/api/card", {
        "name": name,
        "dataset_query": {"type": "native", "database": DB_ID, "native": {"query": sql}},
        "display": display_type,
        "visualization_settings": visualization_settings or {}
    })
    print(f"  Card '{name}' CREATED (id={card['id']})")
    return card["id"]


def find_or_create_dashboard(session, name, description=""):
    dashboards = api_get(session, "/api/dashboard")
    for d in dashboards:
        if d["name"] == name:
            print(f"  Dashboard '{name}' exists (id={d['id']})")
            return d["id"]
    dash = api_post(session, "/api/dashboard", {"name": name, "description": description})
    print(f"  Dashboard '{name}' CREATED (id={dash['id']})")
    return dash["id"]


def set_dashboard_cards(session, dashboard_id, cards_layout):
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

    # ─── DASHBOARD 3: Revenue Total del Negocio ───
    print("\n=== Dashboard 3: Revenue Total del Negocio ===")

    sql_revenue_kpi = """
SELECT
    COUNT(*) AS ventas_total,
    COUNT(DISTINCT cod_cliente) AS clientes_unicos,
    SUM(total) AS revenue_total,
    SUM(pagado) AS revenue_pagado,
    SUM(debe) AS saldo_pendiente,
    ROUND(AVG(total), 2) AS ticket_promedio
FROM opportunities;
"""
    c_revenue_kpi = find_or_create_card(session, "Revenue KPI - Negocio Total", sql_revenue_kpi, "table")

    sql_revenue_mensual = """
SELECT
    DATE_TRUNC('month', fecha_venta)::date AS mes,
    COUNT(*) AS ventas,
    SUM(total) AS revenue
FROM opportunities
GROUP BY 1 ORDER BY 1;
"""
    c_revenue_mensual = find_or_create_card(session, "Revenue por mes", sql_revenue_mensual, "bar")

    sql_revenue_tipo = """
SELECT
    tipo,
    COUNT(*) AS ventas,
    SUM(total) AS revenue
FROM opportunities
GROUP BY 1 ORDER BY 3 DESC;
"""
    c_revenue_tipo = find_or_create_card(session, "Revenue por tipo (Tratamiento/Producto/etc)", sql_revenue_tipo, "bar")

    sql_top_clientes = """
SELECT
    cod_cliente,
    cliente_nombre,
    COUNT(*) AS compras,
    SUM(total) AS revenue_total,
    SUM(pagado) AS revenue_pagado
FROM opportunities
GROUP BY 1,2
ORDER BY 4 DESC
LIMIT 10;
"""
    c_top_clientes = find_or_create_card(session, "Top 10 clientes por revenue", sql_top_clientes, "table")

    sql_attribution_split = """
SELECT
    CASE
        WHEN cod_lead_origen IS NOT NULL THEN 'Atribuido digital'
        ELSE 'Sin atribución (legacy/walk-in)'
    END AS attribution,
    COUNT(*) AS ventas,
    SUM(total) AS revenue
FROM opportunities
GROUP BY 1
ORDER BY 3 DESC;
"""
    c_attribution = find_or_create_card(session, "Revenue por origen (atribuido vs legacy)", sql_attribution_split, "pie")

    dash3_id = find_or_create_dashboard(session, "Revenue Total del Negocio",
                                         "Vista económica: ventas históricas + nuevas, revenue por mes/tipo/cliente, split attribution")

    set_dashboard_cards(session, dash3_id, [
        {"card_id": c_revenue_kpi,    "row": 0,  "col": 0,  "size_x": 24, "size_y": 4},
        {"card_id": c_revenue_mensual,"row": 4,  "col": 0,  "size_x": 16, "size_y": 8},
        {"card_id": c_attribution,    "row": 4,  "col": 16, "size_x": 8,  "size_y": 8},
        {"card_id": c_revenue_tipo,   "row": 12, "col": 0,  "size_x": 12, "size_y": 8},
        {"card_id": c_top_clientes,   "row": 12, "col": 12, "size_x": 12, "size_y": 8},
    ])

    # ─── DASHBOARD 4: Funnel Digital Cerrado ───
    print("\n=== Dashboard 4: Funnel Digital Cerrado ===")

    sql_funnel_kpi = """
SELECT
    COUNT(DISTINCT l.id) AS leads_digitales,
    COUNT(DISTINCT o.cod_cliente) FILTER (WHERE o.cod_lead_origen IS NOT NULL) AS clientes_atribuidos,
    COALESCE(SUM(o.total) FILTER (WHERE o.cod_lead_origen IS NOT NULL), 0) AS revenue_atribuido,
    COUNT(o.id) FILTER (WHERE o.cod_lead_origen IS NOT NULL) AS ventas_atribuidas
FROM leads l
LEFT JOIN opportunities o ON o.cod_lead_origen = l.cod_lead
WHERE l.utm_source_at_capture IS NOT NULL OR l.fbclid_at_capture IS NOT NULL OR l.gclid_at_capture IS NOT NULL;
"""
    c_funnel_kpi = find_or_create_card(session, "Funnel digital KPI", sql_funnel_kpi, "table")

    sql_funnel_etapas = """
SELECT
    'Leads digitales' AS etapa,
    COUNT(*) AS count
FROM leads
WHERE utm_source_at_capture IS NOT NULL OR fbclid_at_capture IS NOT NULL OR gclid_at_capture IS NOT NULL
UNION ALL
SELECT
    'Convertidos a cliente' AS etapa,
    COUNT(DISTINCT o.cod_cliente)
FROM opportunities o
JOIN leads l ON l.cod_lead = o.cod_lead_origen
WHERE l.utm_source_at_capture IS NOT NULL OR l.fbclid_at_capture IS NOT NULL OR l.gclid_at_capture IS NOT NULL
UNION ALL
SELECT
    'Con venta cerrada' AS etapa,
    COUNT(o.id)
FROM opportunities o
JOIN leads l ON l.cod_lead = o.cod_lead_origen
WHERE l.utm_source_at_capture IS NOT NULL OR l.fbclid_at_capture IS NOT NULL OR l.gclid_at_capture IS NOT NULL;
"""
    c_funnel_etapas = find_or_create_card(session, "Funnel digital por etapa", sql_funnel_etapas, "funnel")

    sql_revenue_canal = """
SELECT
    COALESCE(NULLIF(l.utm_source_at_capture, ''), 'organico') AS canal,
    COUNT(o.id) AS ventas_atribuidas,
    SUM(o.total) AS revenue_atribuido
FROM opportunities o
JOIN leads l ON l.cod_lead = o.cod_lead_origen
GROUP BY 1
ORDER BY 3 DESC;
"""
    c_revenue_canal = find_or_create_card(session, "Revenue atribuido por canal digital", sql_revenue_canal, "bar")

    sql_journey_detalle = """
SELECT
    l.vtiger_id,
    l.nombre AS lead_nombre,
    l.utm_source_at_capture AS canal,
    l.utm_campaign_at_capture AS campaign,
    l.fecha_captura,
    o.cod_cliente,
    o.fecha_venta,
    o.tipo AS venta_tipo,
    o.total AS revenue,
    l.event_id_meta
FROM leads l
LEFT JOIN opportunities o ON o.cod_lead_origen = l.cod_lead
WHERE l.utm_source_at_capture IS NOT NULL OR l.fbclid_at_capture IS NOT NULL OR l.gclid_at_capture IS NOT NULL
ORDER BY l.fecha_captura DESC
LIMIT 50;
"""
    c_journey = find_or_create_card(session, "Journey end-to-end por lead digital", sql_journey_detalle, "table")

    dash4_id = find_or_create_dashboard(session, "Funnel Digital Cerrado",
                                         "Solo leads con attribution digital → cliente → venta. Cierra el círculo.")

    set_dashboard_cards(session, dash4_id, [
        {"card_id": c_funnel_kpi,    "row": 0,  "col": 0,  "size_x": 24, "size_y": 4},
        {"card_id": c_funnel_etapas, "row": 4,  "col": 0,  "size_x": 12, "size_y": 8},
        {"card_id": c_revenue_canal, "row": 4,  "col": 12, "size_x": 12, "size_y": 8},
        {"card_id": c_journey,       "row": 12, "col": 0,  "size_x": 24, "size_y": 10},
    ])

    print("\n=== URLs ===")
    print(f"Dashboard 3 (Revenue Total): {METABASE_URL}/dashboard/{dash3_id}")
    print(f"Dashboard 4 (Funnel Digital Cerrado): {METABASE_URL}/dashboard/{dash4_id}")


if __name__ == "__main__":
    main()
