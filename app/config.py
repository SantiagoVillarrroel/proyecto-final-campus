"""Configuración de la aplicación.

Los valores se leen de variables de entorno para que el mismo código sirva
en desarrollo, en tests y en un eventual despliegue. No se usa
pydantic-settings para mantener el proyecto con el mínimo de dependencias.
"""

from __future__ import annotations

import os
from pathlib import Path

# Raíz del repositorio (carpeta que contiene a "app").
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Valores de configuración resueltos al importar el módulo."""

    def __init__(self) -> None:
        # Modo depuración: solo afecta mensajes y comportamiento de FastAPI.
        self.debug = os.getenv("DEBUG", "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        # Si no se define DATABASE_URL, se usa SQLite dentro de data/.
        url = os.getenv("DATABASE_URL", "").strip()
        if not url:
            directorio_datos = BASE_DIR / "data"
            directorio_datos.mkdir(parents=True, exist_ok=True)
            url = f"sqlite:///{directorio_datos / 'inventario.db'}"
        self.database_url = url

        self.host = os.getenv("HOST", "127.0.0.1")
        try:
            self.port = int(os.getenv("PORT", "8000"))
        except ValueError:
            # Ante un valor inválido, se usa el puerto estándar del proyecto.
            self.port = 8000


settings = Settings()
