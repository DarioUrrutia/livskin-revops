"""Routes de auth (ADR-0026): login / logout / change-password."""
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from pydantic import ValidationError

from config import settings
from db import session_scope
from middleware.auth_middleware import SESSION_COOKIE_NAME
from models.user import User
from schemas.auth import ChangePasswordInput, LoginInput
from services import audit_service, auth_service

bp = Blueprint("auth", __name__)


def _is_safe_next_url(target: str) -> bool:
    """Acepta solo URLs internas (mismo host, path absoluto)."""
    if not target:
        return False
    parsed = urlparse(target)
    return not parsed.netloc and not parsed.scheme and target.startswith("/")


@bp.get("/login")
def login_get():  # type: ignore[no-untyped-def]
    next_url = request.args.get("next", "")
    return render_template("login.html", next_url=next_url, error=None)


@bp.post("/login")
def login_post():  # type: ignore[no-untyped-def]
    next_url = request.form.get("next", "")
    try:
        data = LoginInput(
            username=request.form.get("username", ""),
            password=request.form.get("password", ""),
        )
    except ValidationError:
        return render_template(
            "login.html",
            next_url=next_url,
            error="Usuario y contraseña son requeridos.",
        ), 400

    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip() or None
    ua = request.headers.get("User-Agent")

    try:
        with session_scope() as db:
            user, session, is_first_login = auth_service.login(
                db,
                username=data.username,
                password=data.password,
                ip=ip,
                user_agent=ua,
            )
            session_token = session.session_token
            expires_at = session.expires_at
            audit_service.log(
                db,
                action="auth.login_success",
                entity_type="user",
                entity_id=user.id,
                user_id=user.id,
                user_username=user.username,
                user_role=user.rol,
                ip=ip,
                user_agent=ua,
                metadata={"first_login": is_first_login},
            )
    except auth_service.CuentaBloqueada as e:
        current_app.logger.info("login_failed: username=%s ip=%s reason=lockout", data.username, ip)
        audit_service.log_isolated(
            action="auth.lockout_triggered",
            user_username=data.username,
            ip=ip,
            user_agent=ua,
            result="failure",
            error_detail=str(e),
        )
        return render_template("login.html", next_url=next_url, error=str(e)), 401
    except auth_service.AuthError as e:
        current_app.logger.info("login_failed: username=%s ip=%s reason=%s", data.username, ip, type(e).__name__)
        audit_service.log_isolated(
            action="auth.login_failed",
            user_username=data.username,
            ip=ip,
            user_agent=ua,
            result="failure",
            error_detail=type(e).__name__,
        )
        return render_template("login.html", next_url=next_url, error=str(e)), 401

    if is_first_login:
        target = url_for("auth.change_password_get")
    elif _is_safe_next_url(next_url):
        target = next_url
    else:
        target = url_for("views.index")

    response = make_response(redirect(target))
    secure_cookie = settings.flask_env == "production"
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        max_age=int((expires_at - datetime.now(timezone.utc)).total_seconds()),
        httponly=True,
        secure=secure_cookie,
        samesite="Lax",
        path="/",
    )
    return response


@bp.post("/logout")
@bp.get("/logout")
def logout():  # type: ignore[no-untyped-def]
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        try:
            with session_scope() as db:
                auth_service.logout(db, session_token=token, reason="logout")
                audit_service.log(db, action="auth.logout_voluntary", entity_type="user_session")
        except Exception:
            current_app.logger.exception("error during logout")
    response = make_response(redirect(url_for("auth.login_get")))
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return response


@bp.get("/change-password")
def change_password_get():  # type: ignore[no-untyped-def]
    user = getattr(g, "current_user", None)
    if user is None:
        return redirect(url_for("auth.login_get"))
    return render_template("change_password.html", error=None, success=None, forced=False)


@bp.post("/change-password")
def change_password_post():  # type: ignore[no-untyped-def]
    user = getattr(g, "current_user", None)
    if user is None:
        return redirect(url_for("auth.login_get"))

    try:
        data = ChangePasswordInput(
            current_password=request.form.get("current_password", ""),
            new_password=request.form.get("new_password", ""),
            confirm_password=request.form.get("confirm_password", ""),
        )
    except ValidationError as e:
        msg = "; ".join(err.get("msg", "") for err in e.errors()) or "Datos inválidos."
        return render_template("change_password.html", error=msg, success=None, forced=False), 400

    try:
        with session_scope() as db:
            user_db = db.get(User, user.id)
            if user_db is None:
                return redirect(url_for("auth.login_get"))
            auth_service.change_password(
                db,
                user=user_db,
                current_password=data.current_password,
                new_password=data.new_password,
                confirm_password=data.confirm_password,
            )
            audit_service.log(
                db,
                action="auth.password_changed",
                entity_type="user",
                entity_id=user_db.id,
            )
    except auth_service.AuthError as e:
        return render_template("change_password.html", error=str(e), success=None, forced=False), 400

    flash("Contraseña actualizada correctamente.")
    return redirect(url_for("views.index"))
