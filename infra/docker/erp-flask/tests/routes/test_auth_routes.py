"""Tests de routes/auth.py: GET/POST /login, /logout, /change-password."""
from models.user_session import UserSession
from services import auth_service
from middleware.auth_middleware import SESSION_COOKIE_NAME


class TestLoginGet:
    def test_login_page_renders_for_anonymous(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Iniciar sesi" in response.data
        assert b"username" in response.data

    def test_login_page_passes_next_param(self, client):
        response = client.get("/login?next=/admin/audit-log")
        assert response.status_code == 200
        assert b"/admin/audit-log" in response.data


class TestLoginPost:
    def test_valid_credentials_set_cookie_and_redirect(self, client, admin_user):
        response = client.post(
            "/login",
            data={"username": "testadmin", "password": "TestPass123"},
        )
        assert response.status_code == 302
        # Cookie de sesión seteada
        cookie_header = response.headers.get("Set-Cookie", "")
        assert SESSION_COOKIE_NAME in cookie_header

    def test_first_login_redirects_to_change_password(self, client, admin_user):
        response = client.post(
            "/login",
            data={"username": "testadmin", "password": "TestPass123"},
        )
        # last_login_at era NULL → primer login → redirige a /change-password
        assert response.headers.get("Location", "").endswith("/change-password")

    def test_wrong_password_returns_401(self, client, admin_user):
        response = client.post(
            "/login",
            data={"username": "testadmin", "password": "Wrong"},
        )
        assert response.status_code == 401

    def test_unknown_user_returns_401(self, client):
        response = client.post(
            "/login",
            data={"username": "ghost", "password": "any"},
        )
        assert response.status_code == 401

    def test_empty_credentials_returns_400(self, client):
        response = client.post("/login", data={"username": "", "password": ""})
        assert response.status_code == 400


class TestLogout:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})

    def test_logout_clears_cookie(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/logout")
        assert response.status_code == 302
        # Cookie removida
        cookie_header = response.headers.get("Set-Cookie", "")
        assert "expires=" in cookie_header.lower() or "max-age=0" in cookie_header.lower()

    def test_logout_works_without_session(self, client):
        # Logout sin estar logueado no debe romper
        response = client.get("/logout")
        assert response.status_code == 302


class TestChangePassword:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})

    def test_change_password_requires_auth(self, client):
        response = client.get("/change-password")
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")

    def test_change_password_get_renders_for_authenticated(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/change-password")
        assert response.status_code == 200
        assert b"Cambiar contrase" in response.data

    def test_change_password_post_updates(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/change-password",
            data={
                "current_password": "TestPass123",
                "new_password": "NewPass456789",
                "confirm_password": "NewPass456789",
            },
        )
        assert response.status_code == 302
        # Logout + nuevo login con la nueva password
        client.get("/logout")
        login_resp = client.post(
            "/login",
            data={"username": "testadmin", "password": "NewPass456789"},
        )
        assert login_resp.status_code == 302  # redirect = login OK

    def test_change_password_wrong_current_renders_error(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/change-password",
            data={
                "current_password": "WrongCurrent",
                "new_password": "NewPass456789",
                "confirm_password": "NewPass456789",
            },
        )
        assert response.status_code == 400
        assert b"Cambiar contrase" in response.data

    def test_change_password_too_short_rejected(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/change-password",
            data={
                "current_password": "TestPass123",
                "new_password": "short",
                "confirm_password": "short",
            },
        )
        assert response.status_code == 400


class TestAuthMiddleware:
    def test_root_requires_login(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")

    def test_ping_does_not_require_login(self, client):
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.data == b"pong"

    def test_invalid_session_token_redirects(self, client):
        client.set_cookie("erp_session", "garbage-token-xyz")
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")
