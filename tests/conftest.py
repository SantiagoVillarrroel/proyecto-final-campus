"""Fixtures compartidas por la suite de tests."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

# database.py construye el engine al importarse, por eso la URL se define
# ANTES de importar la aplicación. Así cada corrida usa una BD aislada.
_DIRECTORIO_TEMPORAL = Path(tempfile.mkdtemp(prefix="inventario-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_DIRECTORIO_TEMPORAL / 'test.db'}"

import pytest  # noqa: E402 - import diferido a propósito, ver comentario arriba
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def base_de_datos_limpia():
    """Deja el esquema vacío antes y después de cada test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def cliente():
    """Cliente HTTP en memoria que ejecuta el ciclo de vida de la app."""
    with TestClient(app) as cliente_http:
        yield cliente_http


@pytest.fixture
def db():
    """Sesión de SQLAlchemy directa para probar la capa de datos."""
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()


@pytest.fixture
def producto_ejemplo():
    """Datos válidos reutilizables en los tests de API y vistas."""
    return {"nombre": "Lápiz", "sku": "LAP-001", "precio": 1.5, "stock": 10}
