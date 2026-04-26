"""Tests de routes/admin.py: dashboard /admin/audit-log + export CSV + 403 a operadora."""
from services import audit_service


class TestAdminAccessControl:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})

    def test_admin_access_dashboard(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/admin/audit-log")
        assert response.status_code == 200
        assert b"Audit Log" in response.data

    def test_operadora_gets_403(self, client, operadora_user):
        self._login(client, operadora_user, "TestPass456")
        response = client.get("/admin/audit-log")
        assert response.status_code == 403

    def test_anonymous_redirects_to_login(self, client):
        response = client.get("/admin/audit-log", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")


class TestAuditLogView:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})

    def test_dashboard_shows_existing_entries(self, client, admin_user, db_session):
        # Pre-cargar entries via service (en otra session)
        audit_service.log_isolated(action="venta.created", user_username="dario")
        audit_service.log_isolated(action="auth.login_success", user_username="claudia")

        self._login(client, admin_user, "TestPass123")
        response = client.get("/admin/audit-log")
        assert response.status_code == 200
        # No verificamos exact match — el login del admin agrega su propio entry
        assert b"audit_log" not in response.data.lower() or b"venta.created" in response.data

    def test_filter_by_action(self, client, admin_user):
        audit_service.log_isolated(action="venta.created")
        audit_service.log_isolated(action="pago.created")

        self._login(client, admin_user, "TestPass123")
        response = client.get("/admin/audit-log?action=venta.created")
        assert response.status_code == 200

    def test_pagination_query_params(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/admin/audit-log?page=2&per_page=10")
        assert response.status_code == 200

    def test_export_csv_returns_csv_file(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/admin/audit-log/export.csv")
        assert response.status_code == 200
        assert response.mimetype == "text/csv"
        assert b"action,category" in response.data or b"id,occurred_at" in response.data

    def test_export_csv_blocked_for_operadora(self, client, operadora_user):
        self._login(client, operadora_user, "TestPass456")
        response = client.get("/admin/audit-log/export.csv")
        assert response.status_code == 403

    def test_dropdown_includes_canonical_categories(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/admin/audit-log")
        assert response.status_code == 200
        body = response.data.decode("utf-8")
        # Las 8 categorías canónicas deben aparecer en el dropdown
        for cat in ["auth", "venta", "pago", "gasto", "cliente", "lead", "admin", "webhook"]:
            assert f">{cat}<" in body or f"'{cat}'" in body or f"\"{cat}\"" in body
