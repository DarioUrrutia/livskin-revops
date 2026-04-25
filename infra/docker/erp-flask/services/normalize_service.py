"""Normalización de identificadores (ADR-0013 v2 § 6.2).

Phone E.164, email lowercase + sha256 hash, nombre con espacios colapsados.
"""
import hashlib
import re

PHONE_DIGITS_RE = re.compile(r"[\s\-\(\)\.]")
WHITESPACE_RE = re.compile(r"\s+")


def normalize_phone(raw: str | None) -> str | None:
    """Normaliza phone a E.164 con asunción Perú (+51) si aplica.

    Reglas (ADR-0013 v2):
    - Strip espacios, guiones, paréntesis, puntos
    - "00..." → "+..."
    - 9 dígitos empezando 9/8/7/6 → asume Perú "+51"
    - Resultado <7 o >15 dígitos → None (inválido)
    """
    if not raw:
        return None

    cleaned = PHONE_DIGITS_RE.sub("", raw.strip())
    if not cleaned:
        return None

    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    if not cleaned.startswith("+") and cleaned.isdigit():
        if len(cleaned) == 9 and cleaned[0] in "9876":
            cleaned = "+51" + cleaned

    digits_only = cleaned.lstrip("+")
    if not digits_only.isdigit():
        return None
    if len(digits_only) < 7 or len(digits_only) > 15:
        return None

    return cleaned if cleaned.startswith("+") else "+" + cleaned


def normalize_email(raw: str | None) -> str | None:
    """Normaliza email: lowercase + trim. Retorna None si vacío o sin '@'."""
    if not raw:
        return None
    cleaned = raw.strip().lower()
    if not cleaned or "@" not in cleaned:
        return None
    return cleaned


def hash_email(normalized_email: str) -> str:
    """SHA256 hex del email normalizado (para Meta CAPI / Google Enhanced Conversions)."""
    return hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()


def normalize_nombre(raw: str | None) -> str | None:
    """Normaliza nombre: lowercase + trim + colapsar espacios. Preserva acentos."""
    if not raw:
        return None
    cleaned = WHITESPACE_RE.sub(" ", raw.strip().lower())
    return cleaned or None
