"""Tests para routes/api_internal_wa_state.py — endpoint POST /api/internal/wa-state.

Cubre fix 2026-05-27: el UPSERT ahora persiste opcionalmente bodies de mensajes
en `wa_messages` cuando el payload incluye `inbound_message`/`outbound_message`.

Pre-fix: workflow D1v2 solo actualizaba last_inbound/outbound_text en
wa_conversation_state, dejando wa_messages vacia (0 rows) y perdiendo
trazabilidad de bodies individuales para analisis post-campania.
"""
from models.wa_conversation_state import WaConversationState
from models.wa_message import WaMessage


VALID_TOKEN = "test-internal-token-do-not-use-in-prod"
ENDPOINT = "/api/internal/wa-state"


def _headers() -> dict[str, str]:
    return {"X-Internal-Token": VALID_TOKEN, "Content-Type": "application/json"}


def test_upsert_state_sin_messages_no_crea_wa_messages(client, db_session):
    """Backward-compat: upsert sin inbound_message/outbound_message → wa_messages vacia."""
    res = client.post(
        ENDPOINT,
        json={
            "phone_lead": "+51900000001",
            "state": "qualifying",
            "last_inbound_text": "Hola, info por favor",
            "increment_inbound_count": True,
        },
        headers=_headers(),
    )
    assert res.status_code == 200
    assert db_session.query(WaMessage).count() == 0
    assert db_session.query(WaConversationState).filter_by(phone_lead="+51900000001").count() == 1


def test_upsert_con_inbound_message_persiste_wa_messages_row(client, db_session):
    """Fix bug: con inbound_message en payload → crea row en wa_messages."""
    res = client.post(
        ENDPOINT,
        json={
            "phone_lead": "+51900000002",
            "state": "qualifying",
            "last_inbound_text": "Hola",
            "increment_inbound_count": True,
            "inbound_message": {
                "meta_message_id": "wamid.test_inbound_001",
                "message_type": "text",
                "body": "Hola, quiero info de botox",
                "intent": "ask_info",
                "meta_payload_raw": {"from": "51900000002", "type": "text"},
            },
        },
        headers=_headers(),
    )
    assert res.status_code == 200

    msgs = db_session.query(WaMessage).filter_by(phone_lead="+51900000002").all()
    assert len(msgs) == 1
    assert msgs[0].direction == "inbound"
    assert msgs[0].meta_message_id == "wamid.test_inbound_001"
    assert msgs[0].body == "Hola, quiero info de botox"
    assert msgs[0].message_type == "text"
    assert msgs[0].intent == "ask_info"

    # Foreign key: conversation_id apunta a la row creada
    conv = db_session.query(WaConversationState).filter_by(phone_lead="+51900000002").first()
    assert msgs[0].conversation_id == conv.id


def test_upsert_con_outbound_message_persiste_wa_messages_row(client, db_session):
    """Fix bug: con outbound_message en payload → crea row outbound."""
    res = client.post(
        ENDPOINT,
        json={
            "phone_lead": "+51900000003",
            "state": "qualifying",
            "last_outbound_text": "Hola, soy Yossie ☺️",
            "increment_outbound_count": True,
            "outbound_message": {
                "meta_message_id": "wamid.test_outbound_001",
                "message_type": "text",
                "body": "Hola, soy Yossie ☺️",
                "meta_status": "sent",
            },
        },
        headers=_headers(),
    )
    assert res.status_code == 200

    msgs = db_session.query(WaMessage).filter_by(phone_lead="+51900000003").all()
    assert len(msgs) == 1
    assert msgs[0].direction == "outbound"
    assert msgs[0].meta_message_id == "wamid.test_outbound_001"
    assert msgs[0].body == "Hola, soy Yossie ☺️"
    assert msgs[0].meta_status == "sent"
    assert msgs[0].meta_status_updated_at is not None


def test_upsert_con_inbound_y_outbound_crea_dos_rows(client, db_session):
    """Single call con ambos → 2 rows wa_messages (inbound + outbound)."""
    res = client.post(
        ENDPOINT,
        json={
            "phone_lead": "+51900000004",
            "state": "qualifying",
            "last_inbound_text": "Botox",
            "last_outbound_text": "Genial, dime ¿es tu primera vez?",
            "increment_inbound_count": True,
            "increment_outbound_count": True,
            "inbound_message": {
                "meta_message_id": "wamid.in_004",
                "message_type": "text",
                "body": "Botox",
                "intent": "botox",
            },
            "outbound_message": {
                "meta_message_id": "wamid.out_004",
                "message_type": "interactive",
                "body": "Genial, dime ¿es tu primera vez?",
                "meta_status": "sent",
            },
        },
        headers=_headers(),
    )
    assert res.status_code == 200
    msgs = db_session.query(WaMessage).filter_by(phone_lead="+51900000004").order_by(WaMessage.direction).all()
    assert len(msgs) == 2
    inbound = next(m for m in msgs if m.direction == "inbound")
    outbound = next(m for m in msgs if m.direction == "outbound")
    assert inbound.body == "Botox"
    assert outbound.body == "Genial, dime ¿es tu primera vez?"
    assert outbound.message_type == "interactive"


def test_upsert_meta_message_id_duplicado_no_crea_segunda_row(client, db_session):
    """Idempotency: insertar el mismo meta_message_id 2x → solo 1 row (no error)."""
    payload = {
        "phone_lead": "+51900000005",
        "state": "qualifying",
        "last_inbound_text": "Hola",
        "increment_inbound_count": True,
        "inbound_message": {
            "meta_message_id": "wamid.duplicate_test",
            "message_type": "text",
            "body": "Hola duplicate",
        },
    }
    res1 = client.post(ENDPOINT, json=payload, headers=_headers())
    res2 = client.post(ENDPOINT, json=payload, headers=_headers())
    assert res1.status_code == 200
    assert res2.status_code == 200
    msgs = db_session.query(WaMessage).filter_by(meta_message_id="wamid.duplicate_test").all()
    assert len(msgs) == 1


def test_upsert_sin_meta_message_id_inserta_sin_dedupe(client, db_session):
    """Messages sin meta_message_id (raro pero posible) → insert sin idempotency check."""
    payload = {
        "phone_lead": "+51900000006",
        "state": "qualifying",
        "last_outbound_text": "Sin wamid",
        "increment_outbound_count": True,
        "outbound_message": {
            "message_type": "text",
            "body": "Mensaje sin meta_message_id",
            "meta_status": "sent",
        },
    }
    res1 = client.post(ENDPOINT, json=payload, headers=_headers())
    res2 = client.post(ENDPOINT, json=payload, headers=_headers())
    assert res1.status_code == 200
    assert res2.status_code == 200
    msgs = db_session.query(WaMessage).filter_by(phone_lead="+51900000006").all()
    assert len(msgs) == 2  # Sin meta_message_id no hay dedupe


def test_upsert_outbound_message_failed_persiste_status_error(client, db_session):
    """outbound_message con meta_status='failed' + meta_error_message → persiste error."""
    res = client.post(
        ENDPOINT,
        json={
            "phone_lead": "+51900000007",
            "state": "qualifying",
            "last_outbound_text": "Failed send",
            "increment_outbound_count": True,
            "outbound_message": {
                "meta_message_id": "wamid.failed_001",
                "message_type": "text",
                "body": "Failed send",
                "meta_status": "failed",
                "meta_error_message": "(#131047) Re-engagement message required template",
            },
        },
        headers=_headers(),
    )
    assert res.status_code == 200
    msg = db_session.query(WaMessage).filter_by(meta_message_id="wamid.failed_001").first()
    assert msg.meta_status == "failed"
    assert "131047" in (msg.meta_error_message or "")
