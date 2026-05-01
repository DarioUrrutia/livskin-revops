"""capi_emitter_service — emite Meta CAPI events vía n8n webhook (ADR-0019).

Función interna del ERP que se llama desde service hooks (lead_sync, pago,
appointment futuro). NON-BLOCKING: si n8n cae, audit log + return ok=False,
NO raise (la business logic principal NO debe fallar por tracking issue).

Hashing PII: lo hace n8n (Workflow [G3]), no este service. ERP envía raw values.

Eventos canónicos: Lead, Schedule, Purchase. event_id debe coincidir con
Pixel client-side fired (ver ADR-0019 § 6 deduplicación).

Audit log:
- Success → action="tracking.capi_event_emitted"
- Failure → action="tracking.capi_event_failed" (network error, 4xx, 5xx)
- Disabled → no audit (return early)
"""
import time
from decimal import Decimal
from typing import Any, Optional

import requests
from sqlalchemy.orm import Session

from config import settings
from services import audit_service


VALID_EVENT_NAMES = {"Lead", "Schedule", "Purchase"}


def emit_event(
    db: Session,
    event_name: str,
    event_id: str,
    *,
    event_time: Optional[int] = None,
    event_source_url: Optional[str] = None,
    # user_data (raw — n8n hashea)
    email: Optional[str] = None,
    phone_e164: Optional[str] = None,
    fbc: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None,
    client_ip_address: Optional[str] = None,
    client_user_agent: Optional[str] = None,
    # custom_data
    currency: str = "PEN",
    value: Optional[Decimal] = None,
    content_name: Optional[str] = None,
    content_category: Optional[str] = None,
    # audit context
    trigger_entity_type: Optional[str] = None,
    trigger_entity_id: Optional[str] = None,
) -> dict[str, Any]:
    """Emite CAPI event vía n8n. Returns dict con ok/error/details.

    Raises ValueError si event_name o event_id inválidos.
    Cualquier otro error (network, n8n 5xx, etc.) se loguea en audit + return ok=False.
    """
    # ─── Validación schema ───────────────────────────────────────────
    if event_name not in VALID_EVENT_NAMES:
        raise ValueError(
            f"event_name inválido: {event_name!r}. Válidos: {sorted(VALID_EVENT_NAMES)}"
        )
    if not event_id or not event_id.strip():
        raise ValueError("event_id requerido (UUID coherente con Pixel client-side)")

    # ─── Feature flag ────────────────────────────────────────────────
    if not settings.capi_emit_enabled:
        return {
            "ok": False,
            "error": "capi_emit_disabled",
            "event_name": event_name,
            "event_id": event_id,
        }

    # ─── Build payload ───────────────────────────────────────────────
    if event_time is None:
        event_time = int(time.time())

    user_data: dict[str, Any] = {}
    for key, val in [
        ("email", email),
        ("phone_e164", phone_e164),
        ("fbc", fbc),
        ("fbp", fbp),
        ("external_id", external_id),
        ("client_ip_address", client_ip_address),
        ("client_user_agent", client_user_agent),
    ]:
        if val:
            user_data[key] = val

    custom_data: dict[str, Any] = {"currency": currency}
    if value is not None:
        custom_data["value"] = value
    if content_name:
        custom_data["content_name"] = content_name
    if content_category:
        custom_data["content_category"] = content_category

    payload: dict[str, Any] = {
        "event_name": event_name,
        "event_id": event_id,
        "event_time": event_time,
        "action_source": "website",
        "user_data": user_data,
        "custom_data": custom_data,
    }
    if event_source_url:
        payload["event_source_url"] = event_source_url

    # ─── POST a n8n ──────────────────────────────────────────────────
    audit_metadata = {
        "event_name": event_name,
        "event_id": event_id,
        "trigger_entity_type": trigger_entity_type,
        "trigger_entity_id": trigger_entity_id,
    }

    try:
        # default=str para serializar Decimal sin error
        response = requests.post(
            settings.n8n_capi_webhook_url,
            json=_serialize_payload(payload),
            timeout=settings.n8n_capi_timeout_seconds,
        )

        if response.status_code >= 400:
            audit_metadata["http_status"] = response.status_code
            audit_metadata["response_body"] = response.text[:500]
            audit_service.log(
                db,
                action="tracking.capi_event_failed",
                entity_type=trigger_entity_type,
                entity_id=trigger_entity_id,
                metadata=audit_metadata,
                result="failure",
                error_detail=f"n8n HTTP {response.status_code}",
                user_username="capi-emitter",
                user_role="system",
            )
            return {
                "ok": False,
                "error": f"n8n_http_{response.status_code}",
                "event_name": event_name,
                "event_id": event_id,
            }

        # Success
        audit_service.log(
            db,
            action="tracking.capi_event_emitted",
            entity_type=trigger_entity_type,
            entity_id=trigger_entity_id,
            metadata=audit_metadata,
            user_username="capi-emitter",
            user_role="system",
        )
        return {
            "ok": True,
            "event_name": event_name,
            "event_id": event_id,
        }

    except requests.RequestException as e:
        audit_metadata["exception"] = str(e)
        audit_service.log(
            db,
            action="tracking.capi_event_failed",
            entity_type=trigger_entity_type,
            entity_id=trigger_entity_id,
            metadata=audit_metadata,
            result="failure",
            error_detail=f"n8n network error: {e}",
            user_username="capi-emitter",
            user_role="system",
        )
        return {
            "ok": False,
            "error": f"n8n_connection_error: {e}",
            "event_name": event_name,
            "event_id": event_id,
        }


def _serialize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Convierte Decimal → str para JSON serialization. Recursivo."""
    if isinstance(payload, dict):
        return {k: _serialize_payload(v) for k, v in payload.items()}
    if isinstance(payload, list):
        return [_serialize_payload(v) for v in payload]
    if isinstance(payload, Decimal):
        return str(payload)
    return payload
