"""Tests para routes/api_internal.py — system-map JSON + audit-event ingress."""
import json

from models.audit_log import AuditLog


VALID_TOKEN = "test-internal-token-do-not-use-in-prod"


class TestSystemMapJson:
    def test_endpoint_responds(self, client):
        # Sin auth: endpoint público (es solo el mapa, no contiene secretos)
        response = client.get("/api/system-map.json")
        assert response.status_code == 200
        assert response.mimetype == "application/json"

    def test_returns_dict_with_metadata(self, client):
        response = client.get("/api/system-map.json")
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert "metadata" in data


class TestAuditEvent:
    def test_rejects_without_token(self, client):
        response = client.post(
            "/api/internal/audit-event",
            data=json.dumps({"action": "infra.deploy_completed"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_rejects_wrong_token(self, client):
        response = client.post(
            "/api/internal/audit-event",
            data=json.dumps({"action": "infra.deploy_completed"}),
            content_type="application/json",
            headers={"X-Internal-Token": "garbage"},
        )
        assert response.status_code == 403

    def test_accepts_valid_token_creates_audit_entry(self, client, db_session):
        response = client.post(
            "/api/internal/audit-event",
            data=json.dumps({
                "action": "infra.deploy_completed",
                "metadata": {"vps": "vps2", "sha": "abc123", "outcome": "success"},
            }),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 201
        body = json.loads(response.data)
        assert body["ok"] is True

    def test_rejects_missing_action(self, client):
        response = client.post(
            "/api/internal/audit-event",
            data=json.dumps({"metadata": {}}),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400

    def test_handles_failure_result(self, client, db_session):
        response = client.post(
            "/api/internal/audit-event",
            data=json.dumps({
                "action": "infra.deploy_failed",
                "metadata": {"vps": "vps3"},
                "result": "failure",
                "error_detail": "verify timeout",
            }),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 201


class TestInternalHealth:
    def test_health_responds(self, client):
        response = client.get("/api/internal/health")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["status"] == "ok"
        assert body["service"] == "erp-flask"
        assert "timestamp" in body


class TestAgentApiCallEndpoint:
    """Tests del endpoint POST /api/internal/agent-api-call (Bloque 0.10)."""

    def _seed_budget(self, db_session, agent="conv-test"):
        from decimal import Decimal as _D
        from models.agent_api_call import AgentBudget
        b = AgentBudget(
            agent_name=agent,
            daily_usd_limit=_D("3.00"),
            monthly_usd_limit=_D("60.00"),
            alert_threshold_pct=80,
            hard_block_at_limit=True,
            active=True,
        )
        db_session.add(b)
        db_session.commit()

    def test_rejects_without_token(self, client):
        response = client.post(
            "/api/internal/agent-api-call",
            data=json.dumps({"agent_name": "conv-test"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_rejects_missing_required(self, client):
        response = client.post(
            "/api/internal/agent-api-call",
            data=json.dumps({"agent_name": "conv-test"}),  # falta model, tokens
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400

    def test_records_call_returns_cost(self, client, db_session):
        self._seed_budget(db_session, agent="conv-ep-1")
        response = client.post(
            "/api/internal/agent-api-call",
            data=json.dumps({
                "agent_name": "conv-ep-1",
                "model": "claude-sonnet-4-6",
                "input_tokens": 1000,
                "output_tokens": 500,
                "task_id": "lead_42",
                "request_id": "msg_abc123",
                "latency_ms": 1245,
            }),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 201
        body = json.loads(response.data)
        assert body["ok"] is True
        assert "cost_usd" in body


class TestAgentBudgetCheckEndpoint:
    def _seed_budget(self, db_session, agent="bc-test"):
        from decimal import Decimal as _D
        from models.agent_api_call import AgentBudget
        b = AgentBudget(
            agent_name=agent,
            daily_usd_limit=_D("1.00"),
            monthly_usd_limit=_D("30.00"),
            alert_threshold_pct=80,
            hard_block_at_limit=True,
            active=True,
        )
        db_session.add(b)
        db_session.commit()

    def test_within_budget_can_proceed(self, client, db_session):
        self._seed_budget(db_session, agent="bc-1")
        response = client.get(
            "/api/internal/agent-budget-check?agent_name=bc-1&estimated_cost_usd=0.05",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["can_proceed"] is True

    def test_unknown_agent_blocks(self, client):
        response = client.get(
            "/api/internal/agent-budget-check?agent_name=ghost",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["can_proceed"] is False

    def test_rejects_without_token(self, client):
        response = client.get("/api/internal/agent-budget-check?agent_name=any")
        assert response.status_code == 403

    def test_rejects_without_agent_name(self, client):
        response = client.get(
            "/api/internal/agent-budget-check",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400
