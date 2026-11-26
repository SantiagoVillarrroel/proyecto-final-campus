"""Capa de persistencia: engine, sesiones e inicialización de tablas."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

# En SQLite se desactiva la comprobación de hilo para poder usar TestClient.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos."""


def init_db() -> None:
    """Crea las tablas que todavía no existan."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    """Dependencia de FastAPI: entrega una sesión y siempre la cierra."""
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
