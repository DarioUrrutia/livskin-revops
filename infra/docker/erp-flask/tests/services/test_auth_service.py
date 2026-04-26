"""Tests de auth_service (ADR-0026)."""
from datetime import datetime, timedelta, timezone

import pytest

from models.user import User
from models.user_session import UserSession
from services import auth_service


class TestHashAndVerify:
    def test_hash_and_verify_correct_password(self):
        h = auth_service.hash_password("MiPass123")
        assert auth_service.verify_password("MiPass123", h) is True

    def test_verify_wrong_password(self):
        h = auth_service.hash_password("MiPass123")
        assert auth_service.verify_password("OtraPass456", h) is False

    def test_hash_returns_different_hashes_each_time(self):
        h1 = auth_service.hash_password("MiPass123")
        h2 = auth_service.hash_password("MiPass123")
        assert h1 != h2  # bcrypt salt distinto cada vez
        assert auth_service.verify_password("MiPass123", h1) is True
        assert auth_service.verify_password("MiPass123", h2) is True

    def test_verify_handles_invalid_hash_gracefully(self):
        assert auth_service.verify_password("any", "not-a-valid-hash") is False
        assert auth_service.verify_password("any", "") is False


class TestGenerateSessionToken:
    def test_token_is_long_and_random(self):
        t1 = auth_service.generate_session_token()
        t2 = auth_service.generate_session_token()
        assert len(t1) >= 40
        assert t1 != t2


class TestLogin:
    def test_login_success_creates_session(self, db_session):
        u = User(
            cod_usuario="USR-T1",
            username="test1",
            nombre_completo="T1",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()

        user, session, is_first = auth_service.login(
            db_session,
            username="test1",
            password="Pass1234",
            ip="1.2.3.4",
        )
        assert user.id == u.id
        assert is_first is True  # primer login (last_login_at era NULL)
        assert session.session_token is not None
        assert session.user_id == u.id
        assert session.expires_at > datetime.now(timezone.utc)
        assert user.last_login_at is not None
        assert user.failed_login_count == 0

    def test_login_second_time_marks_is_first_false(self, db_session):
        u = User(
            cod_usuario="USR-T2",
            username="test2",
            nombre_completo="T2",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
            last_login_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(u)
        db_session.flush()

        _, _, is_first = auth_service.login(db_session, username="test2", password="Pass1234")
        assert is_first is False

    def test_login_wrong_password_increments_count(self, db_session):
        u = User(
            cod_usuario="USR-T3",
            username="test3",
            nombre_completo="T3",
            password_hash=auth_service.hash_password("Real1234"),
            rol="admin",
            activo=True,
            failed_login_count=2,
        )
        db_session.add(u)
        db_session.flush()

        with pytest.raises(auth_service.CredencialesInvalidas):
            auth_service.login(db_session, username="test3", password="Wrong")
        db_session.refresh(u)
        assert u.failed_login_count == 3
        assert u.locked_until is None

    def test_login_unknown_user(self, db_session):
        with pytest.raises(auth_service.CredencialesInvalidas):
            auth_service.login(db_session, username="ghost", password="any")

    def test_login_inactive_user(self, db_session):
        u = User(
            cod_usuario="USR-T4",
            username="test4",
            nombre_completo="T4",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="operadora",
            activo=False,
        )
        db_session.add(u)
        db_session.flush()

        with pytest.raises(auth_service.CuentaInactiva):
            auth_service.login(db_session, username="test4", password="Pass1234")

    def test_login_locks_after_max_attempts(self, db_session, monkeypatch):
        from config import settings
        monkeypatch.setattr(settings, "login_max_attempts", 3)
        monkeypatch.setattr(settings, "login_lockout_minutes", 15)

        u = User(
            cod_usuario="USR-T5",
            username="test5",
            nombre_completo="T5",
            password_hash=auth_service.hash_password("Real1234"),
            rol="admin",
            activo=True,
            failed_login_count=2,  # un intento más activa lockout
        )
        db_session.add(u)
        db_session.flush()

        with pytest.raises(auth_service.CuentaBloqueada):
            auth_service.login(db_session, username="test5", password="Wrong")
        db_session.refresh(u)
        assert u.locked_until is not None
        assert u.locked_until > datetime.now(timezone.utc)
        assert u.failed_login_count == 0  # se resetea al activar lockout

    def test_login_blocked_account_rejects_even_with_correct_password(self, db_session):
        u = User(
            cod_usuario="USR-T6",
            username="test6",
            nombre_completo="T6",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
            locked_until=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        db_session.add(u)
        db_session.flush()

        with pytest.raises(auth_service.CuentaBloqueada):
            auth_service.login(db_session, username="test6", password="Pass1234")

    def test_login_unlocks_after_lock_expired(self, db_session):
        u = User(
            cod_usuario="USR-T7",
            username="test7",
            nombre_completo="T7",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
            locked_until=datetime.now(timezone.utc) - timedelta(minutes=1),  # ya expiró
            failed_login_count=0,
        )
        db_session.add(u)
        db_session.flush()

        user, _, _ = auth_service.login(db_session, username="test7", password="Pass1234")
        db_session.refresh(user)
        assert user.locked_until is None


class TestCheckSession:
    def test_valid_session_returns_user(self, db_session):
        u = User(
            cod_usuario="USR-S1",
            username="sess1",
            nombre_completo="S1",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()

        _, session, _ = auth_service.login(db_session, username="sess1", password="Pass1234")
        result = auth_service.check_session(db_session, session_token=session.session_token)
        assert result is not None
        user, sess = result
        assert user.id == u.id
        assert sess.id == session.id

    def test_invalid_token_returns_none(self, db_session):
        assert auth_service.check_session(db_session, session_token="ghost-token") is None

    def test_empty_token_returns_none(self, db_session):
        assert auth_service.check_session(db_session, session_token="") is None

    def test_revoked_session_returns_none(self, db_session):
        u = User(
            cod_usuario="USR-S2",
            username="sess2",
            nombre_completo="S2",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()
        _, session, _ = auth_service.login(db_session, username="sess2", password="Pass1234")
        auth_service.logout(db_session, session_token=session.session_token)

        assert auth_service.check_session(db_session, session_token=session.session_token) is None

    def test_expired_session_marked_revoked(self, db_session):
        u = User(
            cod_usuario="USR-S3",
            username="sess3",
            nombre_completo="S3",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()
        s = UserSession(
            session_token="expired-token-xyz",
            user_id=u.id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            last_activity_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(s)
        db_session.flush()

        result = auth_service.check_session(db_session, session_token="expired-token-xyz")
        assert result is None
        db_session.refresh(s)
        assert s.revoked is True
        assert s.revoked_reason == "expired"

    def test_inactive_session_marked_revoked(self, db_session, monkeypatch):
        from config import settings
        monkeypatch.setattr(settings, "session_inactivity_hours", 2)

        u = User(
            cod_usuario="USR-S4",
            username="sess4",
            nombre_completo="S4",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()
        s = UserSession(
            session_token="inactive-token-xyz",
            user_id=u.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=10),
            last_activity_at=datetime.now(timezone.utc) - timedelta(hours=3),  # 3h sin actividad
        )
        db_session.add(s)
        db_session.flush()

        result = auth_service.check_session(db_session, session_token="inactive-token-xyz")
        assert result is None
        db_session.refresh(s)
        assert s.revoked is True
        assert s.revoked_reason == "inactivity"

    def test_check_session_updates_last_activity(self, db_session):
        u = User(
            cod_usuario="USR-S5",
            username="sess5",
            nombre_completo="S5",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()
        _, session, _ = auth_service.login(db_session, username="sess5", password="Pass1234")
        original_activity = session.last_activity_at

        # Simular paso de 30 min: forzar last_activity en el pasado
        session.last_activity_at = datetime.now(timezone.utc) - timedelta(minutes=30)
        db_session.flush()

        auth_service.check_session(db_session, session_token=session.session_token)
        db_session.refresh(session)
        assert session.last_activity_at > original_activity - timedelta(minutes=30)


class TestChangePassword:
    def test_change_password_success(self, db_session):
        u = User(
            cod_usuario="USR-CP1",
            username="cp1",
            nombre_completo="CP1",
            password_hash=auth_service.hash_password("Old1234567"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()

        auth_service.change_password(
            db_session,
            user=u,
            current_password="Old1234567",
            new_password="New9876543",
            confirm_password="New9876543",
        )
        assert auth_service.verify_password("New9876543", u.password_hash) is True
        assert auth_service.verify_password("Old1234567", u.password_hash) is False

    def test_change_password_wrong_current(self, db_session):
        u = User(
            cod_usuario="USR-CP2",
            username="cp2",
            nombre_completo="CP2",
            password_hash=auth_service.hash_password("Old1234567"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()

        with pytest.raises(auth_service.PasswordIncorrecto):
            auth_service.change_password(
                db_session,
                user=u,
                current_password="WrongPass",
                new_password="New9876543",
                confirm_password="New9876543",
            )
        assert auth_service.verify_password("Old1234567", u.password_hash) is True

    def test_change_password_no_match(self, db_session):
        u = User(
            cod_usuario="USR-CP3",
            username="cp3",
            nombre_completo="CP3",
            password_hash=auth_service.hash_password("Old1234567"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()

        with pytest.raises(auth_service.PasswordsNoCoinciden):
            auth_service.change_password(
                db_session,
                user=u,
                current_password="Old1234567",
                new_password="New9876543",
                confirm_password="DistintoSyntax",
            )


class TestLogout:
    def test_logout_marks_session_revoked(self, db_session):
        u = User(
            cod_usuario="USR-L1",
            username="lo1",
            nombre_completo="L1",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()
        _, session, _ = auth_service.login(db_session, username="lo1", password="Pass1234")

        auth_service.logout(db_session, session_token=session.session_token)
        db_session.refresh(session)
        assert session.revoked is True
        assert session.revoked_reason == "logout"
        assert session.revoked_at is not None

    def test_logout_unknown_token_silently_passes(self, db_session):
        # No raise — logout es idempotente
        auth_service.logout(db_session, session_token="ghost-token")

    def test_logout_already_revoked_no_op(self, db_session):
        u = User(
            cod_usuario="USR-L2",
            username="lo2",
            nombre_completo="L2",
            password_hash=auth_service.hash_password("Pass1234"),
            rol="admin",
            activo=True,
        )
        db_session.add(u)
        db_session.flush()
        _, session, _ = auth_service.login(db_session, username="lo2", password="Pass1234")
        auth_service.logout(db_session, session_token=session.session_token)
        original_revoked_at = session.revoked_at

        auth_service.logout(db_session, session_token=session.session_token)
        db_session.refresh(session)
        assert session.revoked_at == original_revoked_at  # no se sobreescribió
