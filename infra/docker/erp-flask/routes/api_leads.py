"""Routes para captura de leads desde forms web (mini-bloque 3.3 Fase 3).

Endpoint principal: POST /api/leads/intake
- Recibe form data desde SureForms 1569 (livskin.site)
- Acepta JSON o application/x-www-form-urlencoded (SureForms suele usar form-encoded)
- Valida via Cloudflare Turnstile token (configurable)
- Llama lead_intake_service para upsert + touchpoint + audit log

NO requiere login bcrypt (es endpoint publico anti-spam protected by Turnstile).
"""
from typing import Any

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from db import session_scope
from middleware.auth_middleware import PUBLIC_ENDPOINTS
from schemas.lead import LeadIntakeRequest
from services import lead_intake_service

bp = Blueprint("api_leads", __name__, url_prefix="/api/leads")


def _extract_payload() -> dict[str, Any]:
    """Soporta JSON y form-encoded. SureForms suele usar form-encoded."""
    if request.is_json:
        return request.get_json(silent=True) or {}
    # form-encoded o multipart
    return {k: v for k, v in request.form.items()}


def _client_ip() -> str | None:
    """Extrae IP cliente (Cloudflare X-Forwarded-For multi-IP safe)."""
    raw_xff = request.headers.get("X-Forwarded-For", "") or ""
    if raw_xff:
        return raw_xff.split(",")[0].strip()
    return request.remote_addr


@bp.post("/intake")
def lead_intake():  # type: ignore[no-untyped-def]
    """Captura un lead desde form web (SureForms 1569).

    Auth: Turnstile token (Cloudflare) si lead_intake_require_turnstile=True.
    En modo dev (require=False) acepta cualquier request — para testing inicial.

    Body (JSON o form-encoded):
    {
      "nombre": "Maria Rodriguez",
      "telefono": "987654321",
      "tratamiento": "Botox",
      "email": "maria@gmail.com",
      "utm_source": "instagram",
      "utm_medium": "social",
      "utm_campaign": "abril2026",
      "fbclid": "...",
      "landing_url": "https://www.livskin.site/?utm_source=instagram",
      "first_referrer": "https://instagram.com/",
      "event_id": "lead_1745847123456_x7k2j8h",
      "consent_marketing": true,
      "cf-turnstile-response": "<turnstile_token>"
    }

    Returns 201 + LeadIntakeResponse en exito; 400/403/422 en error.
    """
    try:
        raw_payload = _extract_payload()
        # Pydantic v2 con alias=cf-turnstile-response — pasar usando alias mode
        payload = LeadIntakeRequest.model_validate(raw_payload)
    except ValidationError as e:
        return jsonify({
            "ok": False,
            "error": "validation_error",
            "detail": e.errors(),
        }), 422
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": "bad_request",
            "detail": str(e),
        }), 400

    client_ip = _client_ip()
    user_agent = request.headers.get("User-Agent", "")[:1000] or None

    # Turnstile verification (sirve de spam-shield)
    if not lead_intake_service.verify_turnstile(payload.cf_turnstile_response, client_ip):
        return jsonify({
            "ok": False,
            "error": "turnstile_verification_failed",
            "detail": "Cloudflare Turnstile token invalido o ausente",
        }), 403

    try:
        with session_scope() as db:
            lead, touchpoint, is_new_lead = lead_intake_service.intake_lead(
                db,
                payload,
                client_ip=client_ip,
                user_agent=user_agent,
                session_id=request.cookies.get("PHPSESSID"),
            )
            return jsonify({
                "ok": True,
                "cod_lead": lead.cod_lead,
                "is_new_lead": is_new_lead,
                "touchpoint_id": touchpoint.id,
            }), 201
    except lead_intake_service.IntakeValidationError as e:
        return jsonify({
            "ok": False,
            "error": "intake_validation_error",
            "detail": str(e),
        }), 422
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": "internal_error",
            "detail": str(e),
        }), 500


def register_public_endpoints() -> None:
    """Marca el endpoint como publico (sin sesion bcrypt requerida)."""
    PUBLIC_ENDPOINTS.add("api_leads.lead_intake")
