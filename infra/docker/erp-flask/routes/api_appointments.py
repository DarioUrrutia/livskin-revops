"""Rutas /api/appointments — modulo agenda minima ERP (ADR-0035, Fase 4A).

Endpoints (todos requieren auth bcrypt session via middleware):

    GET    /api/appointments                  Listado paginado con filtros
    GET    /api/appointments/<cod>            Detalle
    POST   /api/appointments                  Crear (status=scheduled)
    PATCH  /api/appointments/<cod>            Update fields editables (no toca status)

    POST   /api/appointments/<cod>/confirm           scheduled -> confirmed
    POST   /api/appointments/<cod>/mark-attended     trigger critico (crea cliente)
    POST   /api/appointments/<cod>/mark-no-show     scheduled/confirmed -> no_show
    POST   /api/appointments/<cod>/cancel            -> cancelled
    POST   /api/appointments/<cod>/reschedule        crea nueva + marca original

Feature flag: AGENDA_FEATURE_ENABLED (default False). Si False, todos los
endpoints retornan 404 (no aparecen como existentes).
"""
from datetime import datetime, timezone
from typing import Optional

from flask import Blueprint, abort, g, jsonify, request
from pydantic import ValidationError

from config import settings
from db import session_scope
from schemas.appointment import (
    AppointmentCreate,
    AppointmentListItem,
    AppointmentListResponse,
    AppointmentRead,
    AppointmentRescheduleRequest,
    AppointmentUpdate,
)
from services import appointment_service

bp = Blueprint("api_appointments", __name__)


def _check_feature_enabled() -> None:
    """Si feature flag desactivado, retorna 404 (endpoint no existe)."""
    if not getattr(settings, "agenda_feature_enabled", False):
        abort(404)


def _current_user_id() -> Optional[int]:
    """Obtiene user_id de g.current_user_id (seteado por auth middleware)."""
    return getattr(g, "current_user_id", None)


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parsea ISO8601 a datetime timezone-aware (UTC si naive)."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None


@bp.get("/api/appointments")
def list_appointments():  # type: ignore[no-untyped-def]
    _check_feature_enabled()

    try:
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        return jsonify({"error": "limit/offset invalidos"}), 400

    status = request.args.get("status")
    cod_cliente = request.args.get("cod_cliente")
    cod_lead = request.args.get("cod_lead")
    scheduled_from = _parse_iso_datetime(request.args.get("from"))
    scheduled_to = _parse_iso_datetime(request.args.get("to"))

    with session_scope() as db:
        items, total = appointment_service.list_with_filters(
            db,
            status=status,
            cod_cliente=cod_cliente,
            cod_lead=cod_lead,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            limit=limit,
            offset=offset,
        )
        response = AppointmentListResponse(
            items=[AppointmentListItem.model_validate(a) for a in items],
            total=total,
            limit=limit,
            offset=offset,
        ).model_dump(mode="json")

    return jsonify(response), 200


@bp.get("/api/appointments/<cod_appointment>")
def get_appointment(cod_appointment: str):  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        with session_scope() as db:
            apt = appointment_service.get_by_cod(db, cod_appointment)
            response = AppointmentRead.model_validate(apt).model_dump(mode="json")
    except appointment_service.AppointmentNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(response), 200


@bp.post("/api/appointments")
def create_appointment():  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        body = AppointmentCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    try:
        with session_scope() as db:
            apt = appointment_service.create(
                db,
                treatment=body.treatment,
                scheduled_for=body.scheduled_for,
                cod_lead=body.cod_lead,
                cod_cliente=body.cod_cliente,
                duration_min=body.duration_min,
                channel=body.channel,
                notes=body.notes,
                created_by=_current_user_id(),
            )
            response = AppointmentRead.model_validate(apt).model_dump(mode="json")
    except appointment_service.SubjectMissingError as e:
        return jsonify({"error": str(e)}), 400
    except appointment_service.LeadNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except appointment_service.ClienteNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(response), 201


@bp.patch("/api/appointments/<cod_appointment>")
def update_appointment(cod_appointment: str):  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        body = AppointmentUpdate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    try:
        with session_scope() as db:
            apt = appointment_service.update(
                db,
                cod_appointment,
                treatment=body.treatment,
                scheduled_for=body.scheduled_for,
                duration_min=body.duration_min,
                channel=body.channel,
                notes=body.notes,
                updated_by=_current_user_id(),
            )
            response = AppointmentRead.model_validate(apt).model_dump(mode="json")
    except appointment_service.AppointmentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except appointment_service.InvalidTransitionError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(response), 200


@bp.post("/api/appointments/<cod_appointment>/confirm")
def confirm_appointment(cod_appointment: str):  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        with session_scope() as db:
            apt = appointment_service.confirm(
                db, cod_appointment, updated_by=_current_user_id()
            )
            response = AppointmentRead.model_validate(apt).model_dump(mode="json")
    except appointment_service.AppointmentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except appointment_service.InvalidTransitionError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(response), 200


@bp.post("/api/appointments/<cod_appointment>/mark-attended")
def mark_attended(cod_appointment: str):  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        with session_scope() as db:
            apt = appointment_service.mark_attended(
                db, cod_appointment, updated_by=_current_user_id()
            )
            response = AppointmentRead.model_validate(apt).model_dump(mode="json")
    except appointment_service.AppointmentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except appointment_service.InvalidTransitionError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(response), 200


@bp.post("/api/appointments/<cod_appointment>/mark-no-show")
def mark_no_show(cod_appointment: str):  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        with session_scope() as db:
            apt = appointment_service.mark_no_show(
                db, cod_appointment, updated_by=_current_user_id()
            )
            response = AppointmentRead.model_validate(apt).model_dump(mode="json")
    except appointment_service.AppointmentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except appointment_service.InvalidTransitionError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(response), 200


@bp.post("/api/appointments/<cod_appointment>/cancel")
def cancel_appointment(cod_appointment: str):  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        with session_scope() as db:
            apt = appointment_service.cancel(
                db, cod_appointment, updated_by=_current_user_id()
            )
            response = AppointmentRead.model_validate(apt).model_dump(mode="json")
    except appointment_service.AppointmentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except appointment_service.InvalidTransitionError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(response), 200


@bp.post("/api/appointments/<cod_appointment>/reschedule")
def reschedule_appointment(cod_appointment: str):  # type: ignore[no-untyped-def]
    _check_feature_enabled()
    try:
        body = AppointmentRescheduleRequest.model_validate(
            request.get_json(silent=True) or {}
        )
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    try:
        with session_scope() as db:
            original, new_apt = appointment_service.reschedule(
                db,
                cod_appointment,
                new_scheduled_for=body.new_scheduled_for,
                new_duration_min=body.new_duration_min,
                notes_addendum=body.notes_addendum,
                updated_by=_current_user_id(),
            )
            response = {
                "original": AppointmentRead.model_validate(original).model_dump(mode="json"),
                "new": AppointmentRead.model_validate(new_apt).model_dump(mode="json"),
            }
    except appointment_service.AppointmentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except appointment_service.InvalidTransitionError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(response), 200
