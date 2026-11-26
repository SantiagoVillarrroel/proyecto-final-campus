"""Genera un ZIP limpio del proyecto para subir como respaldo a Campus GT.

Excluye entornos virtuales, historial de Git, cachés, bases de datos locales
y archivos temporales. Se ejecuta desde cualquier directorio:

    .venv\\Scripts\\python.exe scripts\\empaquetar.py
"""

from __future__ import annotations

import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "entrega.zip"
NOMBRE_INTERNO = "proyecto-final"

CARPETAS_EXCLUIDAS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "data",
    "htmlcov",
}

ARCHIVOS_EXCLUIDOS = {
    ".env",
    "pip-freeze.tmp",
    "entrega.zip",
    "Thumbs.db",
    ".DS_Store",
}

EXTENSIONES_EXCLUIDAS = {".pyc", ".pyo", ".db", ".log", ".tmp"}

ARCHIVOS_OCULTOS_PERMITIDOS = {".gitignore", ".env.example"}


def _debe_excluirse(ruta: Path) -> bool:
    """Decide si un archivo se omites del paquete final."""
    partes = ruta.relative_to(RAIZ).parts

    if any(parte in CARPETAS_EXCLUIDAS for parte in partes[:-1]):
        return True

    nombre = ruta.name
    if nombre in ARCHIVOS_EXCLUIDOS:
        return True
    if nombre.startswith(".") and nombre not in ARCHIVOS_OCULTOS_PERMITIDOS:
        return True
    if ruta.suffix.lower() in EXTENSIONES_EXCLUIDAS:
        return True
    return False


def empaquetar() -> tuple[Path, int]:
    """Crea (o reemplaza) entrega.zip y devuelve su ruta y cantidad de archivos."""
    if SALIDA.exists():
        SALIDA.unlink()

    cantidad = 0
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
        for ruta in sorted(RAIZ.rglob("*")):
            if not ruta.is_file() or ruta == SALIDA:
                continue
            if _debe_excluirse(ruta):
                continue

            destino = Path(NOMBRE_INTERNO) / ruta.relative_to(RAIZ)
            archivo_zip.write(ruta, destino)
            cantidad += 1

    return SALIDA, cantidad


def main() -> None:
    ruta, cantidad = empaquetar()
    print(f"ZIP generado: {ruta}")
    print(f"Archivos incluidos: {cantidad}")
    print(f"Tamaño: {ruta.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
