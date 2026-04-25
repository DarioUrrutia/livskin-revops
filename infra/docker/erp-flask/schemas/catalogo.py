"""Schemas Pydantic para /api/catalogos."""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CatalogoItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lista: str
    valor: str
    orden: Optional[int]
    activo: bool


class CatalogoListResponse(BaseModel):
    lista: str
    items: list[CatalogoItem]
    count: int


class CatalogoAddRequest(BaseModel):
    lista: str = Field(..., min_length=1, max_length=100)
    valor: str = Field(..., min_length=1, max_length=200)
    orden: Optional[int] = None


class CatalogoSeedResponse(BaseModel):
    inserted: dict[str, int]
    total_inserted: int
