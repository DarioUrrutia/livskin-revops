"""Auth service — bcrypt + sesiones + lockout (ADR-0026)."""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from models.user import User
from models.user_session import UserSession


class AuthError(Exception):
    """Error genérico de auth (mensaje seguro para el usuario)."""


class CredencialesInvalidas(AuthError):
    """Username o password incorrecto."""


class CuentaBloqueada(AuthError):
    """Cuenta bloqueada por demasiados intentos fallidos."""


class CuentaInactiva(AuthError):
    """Cuenta marcada como inactiva."""


class SesionInvalida(AuthError):
    """Sesión no existe, expiró, fue revocada o inactiva."""


class PasswordIncorrecto(AuthError):
    """Password actual no coincide al cambiar."""


class PasswordsNoCoinciden(AuthError):
    """new_password != confirm_password."""


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def generate_session_token() -> str:
    return secrets.token_urlsafe(48)


def login(
    db: Session,
    *,
    username: str,
    password: str,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> tuple[User, UserSession, bool]:
    """Verifica credenciales y crea sesión nueva.

    Returns: (user, session, is_first_login).
    `is_first_login` es True si el usuario nunca había logueado antes de esta sesión
    (last_login_at era NULL al momento de validar las credenciales).

    Raises: CredencialesInvalidas, CuentaBloqueada, CuentaInactiva.
    """
    now = datetime.now(timezone.utc)
    user = db.execute(
        select(User).where(User.username == username.strip().lower())
    ).scalar_one_or_none()

    if user is None:
        raise CredencialesInvalidas("Usuario o contraseña incorrectos.")

    if not user.activo:
        raise CuentaInactiva("Esta cuenta está inactiva. Contacta al administrador.")

    if user.locked_until is not None and user.locked_until > now:
        raise CuentaBloqueada(
            f"Cuenta bloqueada por intentos fallidos. Intenta de nuevo después de "
            f"{user.locked_until.strftime('%H:%M')}."
        )

    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.login_max_attempts:
            user.locked_until = now + timedelta(minutes=settings.login_lockout_minutes)
            user.failed_login_count = 0
            db.flush()
            raise CuentaBloqueada(
                f"Demasiados intentos fallidos. Cuenta bloqueada por "
                f"{settings.login_lockout_minutes} minutos."
            )
        db.flush()
        raise CredencialesInvalidas("Usuario o contraseña incorrectos.")

    is_first_login = user.last_login_at is None

    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now
    user.last_activity_at = now

    session = UserSession(
        session_token=generate_session_token(),
        user_id=user.id,
        expires_at=now + timedelta(hours=settings.session_duration_hours),
        last_activity_at=now,
        ip=ip,
        user_agent=user_agent,
    )
    db.add(session)
    db.flush()
    return user, session, is_first_login


def logout(db: Session, *, session_token: str, reason: str = "logout") -> None:
    session = db.execute(
        select(UserSession).where(UserSession.session_token == session_token)
    ).scalar_one_or_none()
    if session is None or session.revoked:
        return
    session.revoked = True
    session.revoked_at = datetime.now(timezone.utc)
    session.revoked_reason = reason
    db.flush()


def check_session(db: Session, *, session_token: str) -> Optional[tuple[User, UserSession]]:
    """Devuelve (user, session) si la sesión es válida; None si no.

    Valida: existe, no revocada, no expirada, sin inactividad >2h.
    Actualiza last_activity_at en cada llamada (sliding window).
    """
    if not session_token:
        return None

    now = datetime.now(timezone.utc)
    session = db.execute(
        select(UserSession).where(UserSession.session_token == session_token)
    ).scalar_one_or_none()

    if session is None or session.revoked:
        return None

    if session.expires_at <= now:
        session.revoked = True
        session.revoked_at = now
        session.revoked_reason = "expired"
        db.flush()
        return None

    inactivity_limit = timedelta(hours=settings.session_inactivity_hours)
    if now - session.last_activity_at > inactivity_limit:
        session.revoked = True
        session.revoked_at = now
        session.revoked_reason = "inactivity"
        db.flush()
        return None

    user = db.get(User, session.user_id)
    if user is None or not user.activo:
        return None

    session.last_activity_at = now
    user.last_activity_at = now
    db.flush()
    return user, session


def change_password(
    db: Session,
    *,
    user: User,
    current_password: str,
    new_password: str,
    confirm_password: str,
) -> None:
    if new_password != confirm_password:
        raise PasswordsNoCoinciden("La nueva contraseña y la confirmación no coinciden.")
    if not verify_password(current_password, user.password_hash):
        raise PasswordIncorrecto("La contraseña actual es incorrecta.")
    user.password_hash = hash_password(new_password)
    db.flush()


