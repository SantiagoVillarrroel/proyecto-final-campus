"""Modelos de datos (capa de dominio)."""

from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Producto(Base):
    """Producto del inventario.

    El SKU es único para evitar duplicados y facilitar la búsqueda.
    """

    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    precio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Producto id={self.id} sku={self.sku!r} nombre={self.nombre!r}>"
