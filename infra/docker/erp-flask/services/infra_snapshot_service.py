"""InfraSnapshotService — recolecta y persiste snapshots cross-VPS (Bloque 0.4).

Pollea los endpoints `/api/system-state` de los 3 VPS y guarda en
`postgres-data.infra_snapshots`. Diseñado para invocarse desde un cron en VPS
3 cada 5 minutos.

Uso:
    docker exec erp-flask python -m services.infra_snapshot_service collect
    docker exec erp-flask python -m services.infra_snapshot_service cleanup
"""
import logging
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from db import session_scope
from models.infra_snapshot import InfraSnapshot

logger = logging.getLogger(__name__)


# Targets a pollear: (alias, url base)
# VPS 3 se autoreporta vía endpoint local (sin cross-VPS HTTP)
SENSOR_TARGETS = [
    {"alias": "livskin-wp", "role": "vps1-wp", "url": "http://10.114.0.3:9100/api/system-state"},
    {"alias": "livskin-ops", "role": "vps2-ops", "url": "http://10.114.0.2:9100/api/system-state"},
    {"alias": "livskin-erp", "role": "vps3-erp", "url": "http://localhost:8000/api/internal/system-state"},
]

REQUEST_TIMEOUT_S = 10
RETENTION_DAYS = 30


def _fetch_one(target: dict[str, str]) -> tuple[dict[str, Any], Optional[str]]:
    """Pollea un sensor. Returns (payload, error_msg). En error, payload={}."""
    try:
        r = requests.get(
            target["url"],
            headers={"X-Internal-Token": settings.audit_internal_token},
            timeout=REQUEST_TIMEOUT_S,
        )
        if r.status_code == 200:
            return r.json(), None
        return {}, f"HTTP {r.status_code}: {r.text[:200]}"
    except requests.RequestException as e:
        return {}, f"connection failed: {e}"
    except Exception as e:
        return {}, f"unexpected: {e}"


def _persist(db: Session, target: dict[str, str], payload: dict[str, Any], error: Optional[str]) -> None:
    disk = payload.get("disk") or {}
    ram = payload.get("ram") or {}
    containers = payload.get("containers") or []

    snapshot = InfraSnapshot(
        vps_alias=target["alias"],
        vps_role=target["role"],
        uptime_seconds=payload.get("uptime_seconds"),
        disk_pct=Decimal(str(disk.get("percent"))) if disk.get("percent") is not None else None,
        disk_used_gb=Decimal(str(disk.get("used_gb"))) if disk.get("used_gb") is not None else None,
        disk_total_gb=Decimal(str(disk.get("total_gb"))) if disk.get("total_gb") is not None else None,
        ram_pct=Decimal(str(ram.get("percent"))) if ram.get("percent") is not None else None,
        ram_used_mb=ram.get("used_mb"),
        ram_total_mb=ram.get("total_mb"),
        containers_count=len(containers) if isinstance(containers, list) else None,
        last_deploy_sha=payload.get("last_deploy_sha"),
        raw_payload=payload if payload else None,
        error=error,
    )
    db.add(snapshot)
    db.flush()


def collect() -> dict[str, Any]:
    """Pollea los 3 VPS y persiste un snapshot por cada uno.

    Returns: {alias: status} para cada target. status = 'ok' o error string.
    """
    results: dict[str, str] = {}
    with session_scope() as db:
        for target in SENSOR_TARGETS:
            payload, error = _fetch_one(target)
            _persist(db, target, payload, error)
            results[target["alias"]] = "ok" if error is None else error
    return results


def cleanup_old(retention_days: int = RETENTION_DAYS) -> int:
    """Borra snapshots más viejos que retention_days. Returns count borrados."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    with session_scope() as db:
        from sqlalchemy import delete
        result = db.execute(delete(InfraSnapshot).where(InfraSnapshot.captured_at < cutoff))
        return result.rowcount or 0


def latest_per_vps(db: Session) -> dict[str, Optional[InfraSnapshot]]:
    """Devuelve el snapshot más reciente por VPS. Para dashboards."""
    result: dict[str, Optional[InfraSnapshot]] = {}
    for target in SENSOR_TARGETS:
        latest = db.execute(
            select(InfraSnapshot)
            .where(InfraSnapshot.vps_alias == target["alias"])
            .order_by(InfraSnapshot.captured_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        result[target["alias"]] = latest
    return result


# CLI
def _main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO)
    cmd = argv[1] if len(argv) > 1 else "collect"
    if cmd == "collect":
        results = collect()
        print("Collected snapshots:")
        for alias, status in results.items():
            print(f"  {alias}: {status}")
        return 0 if all(s == "ok" for s in results.values()) else 1
    elif cmd == "cleanup":
        n = cleanup_old()
        print(f"Cleaned up {n} snapshots older than {RETENTION_DAYS} days")
        return 0
    else:
        print(f"Unknown command: {cmd}. Use 'collect' or 'cleanup'.")
        return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
