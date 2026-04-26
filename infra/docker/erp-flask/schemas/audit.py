"""Schemas Pydantic para audit log dashboard (ADR-0027)."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class AuditLogQuery(BaseModel):
    """Filtros del dashboard /admin/audit-log."""

    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    action: Optional[str] = None
    category: Optional[str] = None
    user_username: Optional[str] = None
    result: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=500)
