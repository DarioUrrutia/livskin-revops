"""Tests para routes/api_internal_lock.py — Sprint 1.3 distributed lock endpoints.

Mockean services.distributed_lock_service (Redis) — tests no requieren Redis real.
"""
from unittest.mock import patch


VALID_TOKEN = "test-internal-token-do-not-use-in-prod"


def _h() -> dict[str, str]:
    return {"X-Internal-Token": VALID_TOKEN, "Content-Type": "application/json"}


def test_acquire_lock_devuelve_true_si_redis_dice_ok(client):
    with patch("services.distributed_lock_service.acquire", return_value=True) as m:
        res = client.post("/api/internal/lock/acquire", json={"key": "cron:test", "ttl_seconds": 60}, headers=_h())
    assert res.status_code == 200
    body = res.get_json()
    assert body["acquired"] is True
    assert body["key"] == "cron:test"
    assert body["ttl_seconds"] == 60
    m.assert_called_once_with("cron:test", ttl_seconds=60, value="1")


def test_acquire_lock_devuelve_false_si_redis_dice_held(client):
    with patch("services.distributed_lock_service.acquire", return_value=False):
        res = client.post("/api/internal/lock/acquire", json={"key": "cron:test2"}, headers=_h())
    assert res.status_code == 200
    body = res.get_json()
    assert body["acquired"] is False
    assert body["reason"] == "held"


def test_acquire_lock_devuelve_503_si_redis_unreachable(client):
    with patch("services.distributed_lock_service.acquire", side_effect=RuntimeError("connection refused")):
        res = client.post("/api/internal/lock/acquire", json={"key": "cron:test3"}, headers=_h())
    assert res.status_code == 503
    body = res.get_json()
    assert body["acquired"] is False
    assert "redis_error" in body["error"]


def test_acquire_lock_400_si_key_vacia(client):
    res = client.post("/api/internal/lock/acquire", json={"key": ""}, headers=_h())
    assert res.status_code == 400


def test_acquire_lock_400_si_ttl_fuera_rango(client):
    res = client.post("/api/internal/lock/acquire", json={"key": "x", "ttl_seconds": 99999}, headers=_h())
    assert res.status_code == 400


def test_acquire_lock_403_sin_token(client):
    res = client.post("/api/internal/lock/acquire", json={"key": "x"}, headers={"Content-Type": "application/json"})
    assert res.status_code == 403


def test_release_lock_borra_y_devuelve_true(client):
    with patch("services.distributed_lock_service.release", return_value=True) as m:
        res = client.post("/api/internal/lock/release", json={"key": "cron:r1"}, headers=_h())
    assert res.status_code == 200
    body = res.get_json()
    assert body["released"] is True
    m.assert_called_once_with("cron:r1")


def test_release_lock_false_si_no_existia(client):
    with patch("services.distributed_lock_service.release", return_value=False):
        res = client.post("/api/internal/lock/release", json={"key": "cron:r2"}, headers=_h())
    assert res.status_code == 200
    body = res.get_json()
    assert body["released"] is False


def test_ping_redis_200_si_alcanzable(client):
    with patch("services.distributed_lock_service.ping", return_value=True):
        res = client.get("/api/internal/lock/ping", headers=_h())
    assert res.status_code == 200
    assert res.get_json() == {"redis": "ok"}


def test_ping_redis_503_si_unreachable(client):
    with patch("services.distributed_lock_service.ping", return_value=False):
        res = client.get("/api/internal/lock/ping", headers=_h())
    assert res.status_code == 503
    assert res.get_json() == {"redis": "unreachable"}
