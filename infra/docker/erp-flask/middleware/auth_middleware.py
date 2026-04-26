"""Middleware Flask: protege todas las rutas excepto allowlist (ADR-0026)."""
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional

from flask import Flask, g, redirect, request, url_for

from db import session_scope
from services import auth_service

SESSION_COOKIE_NAME = "erp_session"


@dataclass
class CurrentUser:
    """Snapshot del usuario logueado para usar fuera del session_scope."""
    id: int
    username: str
    nombre_completo: str
    email: Optional[str]
    rol: str

# Endpoints (blueprint.endpoint_name) que NO requieren autenticación.
# Atención: usar el `endpoint_name` que Flask asigna, no la URL.
PUBLIC_ENDPOINTS = {
    "auth.login_get",
    "auth.login_post",
    "auth.logout",
    "static",
    "ping",
}


def init_auth_middleware(app: Flask) -> None:
    """Registra el before_request hook que valida la sesión en cada request."""

    @app.before_request
    def require_authentication():  # type: ignore[no-untyped-def]
        endpoint = request.endpoint

        if endpoint is None:
            return None

        if endpoint in PUBLIC_ENDPOINTS:
            return None

        token = request.cookies.get(SESSION_COOKIE_NAME)
        if not token:
            return _redirect_to_login()

        with session_scope() as db:
            result = auth_service.check_session(db, session_token=token)
            if result is None:
                response = _redirect_to_login()
                response.delete_cookie(SESSION_COOKIE_NAME)
                return response
            user, session = result
            current_user = CurrentUser(
                id=user.id,
                username=user.username,
                nombre_completo=user.nombre_completo,
                email=user.email,
                rol=user.rol,
            )
            g.current_user = current_user
            g.current_session_token = session.session_token
            g.current_user_id = current_user.id
            g.current_user_rol = current_user.rol

        return None


def _redirect_to_login():  # type: ignore[no-untyped-def]
    return redirect(url_for("auth.login_get", next=request.path))


def require_role(*allowed_roles: str) -> Callable:
    """Decorator: solo permite acceso a usuarios con uno de los roles dados."""

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):  # type: ignore[no-untyped-def]
            from flask import abort
            rol = getattr(g, "current_user_rol", None)
            if rol not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator
