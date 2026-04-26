"""SystemMapService — parsea docs/sistema-mapa.md y expone como JSON.

Lee el archivo Markdown autoritativo, extrae los bloques YAML de cada
sección, y devuelve un dict estructurado. Cache en memoria por 60s para
evitar re-parsing en cada request.

El system-map vive en `/srv/livskin-revops/docs/sistema-mapa.md` (montado
read-only al container vía volume).
"""
import logging
import re
import time
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

# Path al system-map dentro del container (montado read-only)
SYSTEM_MAP_PATH = Path("/repo/docs/sistema-mapa.md")

# Cache TTL en segundos
CACHE_TTL_S = 60

_cache: dict[str, Any] = {}
_cache_ts: float = 0.0


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extrae frontmatter YAML del head del archivo. Returns (meta, body)."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, match.group(2)


def _extract_yaml_blocks(body: str) -> list[dict[str, Any]]:
    """Extrae todos los bloques ```yaml ... ``` del body y los parsea."""
    blocks = re.findall(r"```yaml\n(.*?)```", body, re.DOTALL)
    parsed = []
    for block in blocks:
        try:
            data = yaml.safe_load(block)
            if isinstance(data, dict):
                parsed.append(data)
        except yaml.YAMLError as e:
            logger.warning("system-map: error parseando bloque YAML: %s", e)
    return parsed


def _merge_blocks(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """Combina los bloques en un único dict (top-level keys de cada bloque)."""
    result: dict[str, Any] = {}
    for block in blocks:
        for key, value in block.items():
            if key in result and isinstance(result[key], list) and isinstance(value, list):
                result[key].extend(value)
            else:
                result[key] = value
    return result


def get_system_map() -> dict[str, Any]:
    """Devuelve el system-map parseado como dict. Cacheado 60s.

    Estructura del dict:
        {
          "metadata": {...frontmatter...},
          "vps": [...],
          "containers": [...],
          "cross_vps_connections": [...],
          "dependency_matrix": [...],
          "spofs": [...],
          "public_urls": [...],
          "backups": [...],
          "secrets_inventory": [...],
          "capacity": [...],
          "ai_agent_consumption": {...},
        }
    """
    global _cache, _cache_ts
    now = time.time()
    if _cache and (now - _cache_ts) < CACHE_TTL_S:
        return _cache

    if not SYSTEM_MAP_PATH.exists():
        logger.error("system-map: %s no existe", SYSTEM_MAP_PATH)
        return {"metadata": {}, "error": f"system-map no encontrado en {SYSTEM_MAP_PATH}"}

    try:
        content = SYSTEM_MAP_PATH.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(content)
        blocks = _extract_yaml_blocks(body)
        merged = _merge_blocks(blocks)
        result = {"metadata": metadata, **merged}
        _cache = result
        _cache_ts = now
        return result
    except Exception:
        logger.exception("system-map: error parseando")
        return {"metadata": {}, "error": "parse failure — ver logs"}


def invalidate_cache() -> None:
    """Fuerza re-parse en el próximo get_system_map(). Útil para tests."""
    global _cache, _cache_ts
    _cache = {}
    _cache_ts = 0.0
