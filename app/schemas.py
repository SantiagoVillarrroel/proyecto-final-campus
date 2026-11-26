"""Esquemas Pydantic: validación de entradas y serialización de salidas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductoBase(BaseModel):
    """Campos compartidos por alta, edición y salida."""

    nombre: str = Field(..., min_length=1, max_length=120, description="Nombre visible")
    sku: str = Field(..., min_length=1, max_length=40, description="Código único")
    precio: float = Field(..., ge=0, description="Precio mayor o igual a cero")
    stock: int = Field(0, ge=0, description="Cantidad disponible")

    @field_validator("nombre", "sku")
    @classmethod
    def recortar_espacios(cls, valor: str) -> str:
        """Quita espacios marginales y rechaza cadenas vacías."""
        limpio = valor.strip()
        if not limpio:
            raise ValueError("El campo no puede estar vacío")
        return limpio

    @field_validator("sku")
    @classmethod
    def normalizar_sku(cls, valor: str) -> str:
        """Guarda el SKU siempre en mayúsculas."""
        return valor.upper()


class ProductoCreate(ProductoBase):
    """Datos necesarios para dar de alta un producto."""


class ProductoUpdate(ProductoBase):
    """Datos completos para reemplazar un producto existente (PUT)."""


class ProductoOut(ProductoBase):
    """Representación devuelta por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
