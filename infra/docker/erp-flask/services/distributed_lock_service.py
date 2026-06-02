"""distributed_lock_service — locks distribuidos via Redis SETNX.

Sprint 1.3 (2026-05-28): defensa contra overlap concurrente de:
- Crons n8n F1/F2/F3/B3 (mismo lock_key por cron, TTL un poco > duration típica)
- Endpoints UPSERT críticos (complementa pg_advisory_lock para casos cross-VPS)
- Webhooks burst (per phone_lead)

Patrón Redis:
    SET <key> <value> NX EX <ttl_seconds>

- Devuelve "OK" si el lock fue adquirido (key no existía)
- Devuelve null si otra instancia tiene el lock

Release: DEL <key>. Si el caller no llama release, el TTL libera automáticamente
(defensa contra crashed callers).

Conexión:
- Redis vive en VPS2 (10.114.0.2:6379)
- ERP-flask llama via VPC interno (~1-2ms latencia)
- Lazy connection: solo se conecta cuando se invoca una función
- Connection pool reusable (redis.ConnectionPool)
"""
import logging
import os
from typing import Optional

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


_pool: Optional[redis.ConnectionPool] = None


def _get_client() -> redis.Redis:
    """Lazy-init connection pool + cliente Redis.

    Lee credentials de env vars (REDIS_HOST, REDIS_PORT, REDIS_PASSWORD).
    """
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool(
            host=os.environ.get("REDIS_HOST", "10.114.0.2"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            password=os.environ.get("REDIS_PASSWORD", ""),
            db=0,
            socket_timeout=2,
            socket_connect_timeout=2,
            max_connections=10,
            decode_responses=True,
        )
    return redis.Redis(connection_pool=_pool)


def acquire(lock_key: str, ttl_seconds: int = 600, value: str = "1") -> bool:
    """Intenta adquirir el lock. Returns True si adquirió, False si ya está tomado.

    Args:
        lock_key: nombre del lock (recomendado: prefijo por dominio, ej. "cron:b3")
        ttl_seconds: tiempo máximo que el lock vive (defensa crash). Default 10 min.
        value: payload (ej. hostname o PID — debug si quieres saber quién tiene el lock)

    Raises: RedisError si Redis no es alcanzable (network/auth). El caller debe
    decidir si fail-open (proceder sin lock) o fail-closed (abortar) — para
    crons defensa por overlap, fail-OPEN es preferible (preferimos correr 2x
    que perder ejecuciones).
    """
    if not lock_key or len(lock_key) > 200:
        raise ValueError(f"lock_key inválido: {lock_key!r}")
    if ttl_seconds < 1 or ttl_seconds > 86400:
        raise ValueError(f"ttl_seconds fuera de rango (1-86400): {ttl_seconds}")

    client = _get_client()
    # SET NX EX en una sola operación atómica
    result = client.set(name=f"lock:{lock_key}", value=value, nx=True, ex=ttl_seconds)
    return result is True or result == "OK"


def release(lock_key: str) -> bool:
    """Libera el lock explícitamente. Returns True si borrado, False si ya no existía."""
    if not lock_key:
        return False
    client = _get_client()
    deleted = client.delete(f"lock:{lock_key}")
    return bool(deleted)


def is_locked(lock_key: str) -> bool:
    """Diagnóstico: ¿está el lock activo? (uso opcional, no necesario para acquire)."""
    if not lock_key:
        return False
    client = _get_client()
    return bool(client.exists(f"lock:{lock_key}"))


def ping() -> bool:
    """Health check Redis. Returns True si Redis está accesible."""
    try:
        client = _get_client()
        return client.ping() is True
    except RedisError as e:
        logger.warning(f"Redis ping failed: {e}")
        return False
