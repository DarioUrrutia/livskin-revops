"""Schemas Pydantic para auth (ADR-0026)."""
from pydantic import BaseModel, Field, field_validator


class LoginInput(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        return v.strip().lower()


class ChangePasswordInput(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=12, max_length=200)
    confirm_password: str = Field(min_length=12, max_length=200)

    @field_validator("new_password")
    @classmethod
    def validate_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v
