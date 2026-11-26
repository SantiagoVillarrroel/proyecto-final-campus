"""Operaciones de acceso a datos.

Toda la lógica SQL vive acá: los routers solo orquestan validación y
respuestas. Esto mantiene la API y las vistas desacopladas de SQLAlchemy.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def listar_productos(
    db: Session,
    busqueda: str = "",
    limite: int = 100,
    desplazamiento: int = 0,
) -> list[models.Producto]:
    """Devuelve productos ordenados por id, con búsqueda opcional por nombre o SKU."""
    sentencia = select(models.Producto).order_by(models.Producto.id)

    termino = (busqueda or "").strip()
    if termino:
        patron = f"%{termino}%"
        sentencia = sentencia.where(
            models.Producto.nombre.ilike(patron) | models.Producto.sku.ilike(patron)
        )

    sentencia = sentencia.offset(desplazamiento).limit(limite)
    return list(db.scalars(sentencia).all())


def obtener_producto(db: Session, producto_id: int) -> models.Producto | None:
    """Busca un producto por clave primaria; devuelve None si no existe."""
    return db.get(models.Producto, producto_id)


def crear_producto(db: Session, datos: schemas.ProductoCreate) -> models.Producto:
    """Inserta un producto y confirma la transacción."""
    producto = models.Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def actualizar_producto(
    db: Session,
    producto: models.Producto,
    datos: schemas.ProductoUpdate,
) -> models.Producto:
    """Sobrescribe todos los campos editables de un producto."""
    for clave, valor in datos.model_dump().items():
        setattr(producto, clave, valor)
    db.commit()
    db.refresh(producto)
    return producto


def eliminar_producto(db: Session, producto: models.Producto) -> None:
    """Elimina un producto y confirma la transacción."""
    db.delete(producto)
    db.commit()
