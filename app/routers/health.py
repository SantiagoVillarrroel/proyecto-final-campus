"""Endpoint de salud para verificar que la app y la base responden."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from ..database import engine

router = APIRouter(tags=["salud"])


@router.get("/health")
def verificar_salud() -> dict[str, str]:
    """Comprueba una consulta mínima contra la base de datos."""
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - se informa el fallo sin detener la app
        return {"estado": "degradado", "detalle": str(exc)}
    return {"estado": "ok"}
