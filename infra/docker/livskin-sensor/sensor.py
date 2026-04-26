"""livskin-sensor — mini Flask app que expone /api/health y /api/system-state.

Diseñado para correr en cualquier VPS de Livskin (1, 2, 3) y reportar:
- Containers Docker corriendo (si aplica)
- Disk / RAM / uptime
- Service-specific health (postgres conn count, nginx response)
- Last deploy SHA (lee /srv/livskin-revops/.git/HEAD si existe)

Modos de despliegue:
- VPS 2: container Docker en `revops_net`, puerto 9100 expuesto solo VPC
- VPS 1: systemd service (host), puerto 9100 expuesto solo VPC vía UFW

Auth: shared secret en header `X-Internal-Token`. Mismo valor que el ERP usa.
Whitelist via UFW: solo IPs `10.114.0.0/20` (DO VPC) pueden hablar a 9100.

Sin dependencias pesadas: Flask + psutil + docker (opcional) + requests.
"""
import logging
import os
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, abort, jsonify, request

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

try:
    import docker  # type: ignore
except ImportError:
    docker = None

VPS_ALIAS = os.environ.get("VPS_ALIAS", socket.gethostname())
VPS_ROLE = os.environ.get("VPS_ROLE", "unknown")
INTERNAL_TOKEN = os.environ.get("AUDIT_INTERNAL_TOKEN", "")
REPO_PATH = Path(os.environ.get("REPO_PATH", "/srv/livskin-revops"))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _check_token() -> None:
    """Aborta 403 si el token no coincide. Health endpoint no lo requiere."""
    if not INTERNAL_TOKEN:
        # Si no hay token configurado, fallar cerrado — paranoid mode
        abort(503, description="AUDIT_INTERNAL_TOKEN no configurado en sensor")
    if request.headers.get("X-Internal-Token") != INTERNAL_TOKEN:
        abort(403, description="X-Internal-Token inválido")


def _disk_info() -> dict[str, Any]:
    if psutil is None:
        return {"error": "psutil no instalado"}
    usage = psutil.disk_usage("/")
    return {
        "total_gb": round(usage.total / 1024**3, 2),
        "used_gb": round(usage.used / 1024**3, 2),
        "free_gb": round(usage.free / 1024**3, 2),
        "percent": usage.percent,
    }


def _ram_info() -> dict[str, Any]:
    if psutil is None:
        return {"error": "psutil no instalado"}
    mem = psutil.virtual_memory()
    return {
        "total_mb": round(mem.total / 1024**2),
        "used_mb": round(mem.used / 1024**2),
        "available_mb": round(mem.available / 1024**2),
        "percent": mem.percent,
    }


def _uptime_seconds() -> int:
    if psutil is None:
        try:
            with open("/proc/uptime", encoding="utf-8") as f:
                return int(float(f.read().split()[0]))
        except OSError:
            return 0
    return int(time.time() - psutil.boot_time())


def _docker_containers() -> list[dict[str, Any]]:
    if docker is None:
        return []
    try:
        client = docker.from_env()
        return [
            {
                "name": c.name,
                "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                "status": c.status,
                "started_at": c.attrs.get("State", {}).get("StartedAt", ""),
            }
            for c in client.containers.list(all=False)
        ]
    except Exception as e:
        logger.warning("docker query failed: %s", e)
        return []


def _last_deploy_sha() -> str:
    """Lee SHA del HEAD del repo en /srv/livskin-revops/.git/."""
    head_file = REPO_PATH / ".git" / "HEAD"
    if not head_file.exists():
        return "unknown"
    try:
        head = head_file.read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            ref_path = REPO_PATH / ".git" / head.split(" ", 1)[1].strip()
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8").strip()[:7]
        return head[:7]
    except OSError:
        return "unknown"


def _host_services() -> list[dict[str, Any]]:
    """Para VPS 1 (no docker): chequea estado de nginx, php-fpm, mariadb."""
    if VPS_ROLE != "vps1-wp":
        return []
    services = ["nginx", "php8.1-fpm", "mariadb"]
    result = []
    for svc in services:
        try:
            r = subprocess.run(
                ["systemctl", "is-active", svc],
                capture_output=True, text=True, timeout=5,
            )
            result.append({
                "name": svc,
                "status": r.stdout.strip(),
                "type": "systemd",
            })
        except Exception as e:
            result.append({"name": svc, "status": "unknown", "error": str(e)})
    return result


@app.get("/api/health")
def health():  # type: ignore[no-untyped-def]
    """Healthcheck básico — sin auth (solo confirma que el sensor responde)."""
    return jsonify({
        "status": "ok",
        "service": "livskin-sensor",
        "vps_alias": VPS_ALIAS,
        "vps_role": VPS_ROLE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/api/system-state")
def system_state():  # type: ignore[no-untyped-def]
    """Snapshot detallado del estado del VPS — requiere X-Internal-Token."""
    _check_token()
    return jsonify({
        "vps_alias": VPS_ALIAS,
        "vps_role": VPS_ROLE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": _uptime_seconds(),
        "disk": _disk_info(),
        "ram": _ram_info(),
        "containers": _docker_containers(),
        "host_services": _host_services(),
        "last_deploy_sha": _last_deploy_sha(),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100, debug=False)
