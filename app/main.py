"""Punto de entrada de la aplicación FastAPI.

Arma la app, monta archivos estáticos y plantillas, registra routers y
uniformiza el formato de errores (JSON para la API, HTML para las vistas).
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import __version__
from .config import BASE_DIR, settings
from .database import init_db
from .routers import health, productos

DIRECTORIO_PLANTILLAS = BASE_DIR / "app" / "templates"
DIRECTORIO_ESTATICO = BASE_DIR / "app" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos al levantar el servidor."""
    init_db()
    yield


app = FastAPI(
    title="Gestor de Inventario GT",
    description="CRUD de productos con API REST e interfaz web, persistido en SQLite.",
    version=__version__,
    debug=settings.debug,
    lifespan=lifespan,
)

plantillas = Jinja2Templates(directory=str(DIRECTORIO_PLANTILLAS))
app.state.templates = plantillas
app.mount("/static", StaticFiles(directory=str(DIRECTORIO_ESTATICO)), name="static")

app.include_router(health.router)
app.include_router(productos.router)
app.include_router(productos.vistas)


def _es_api(ruta: str) -> bool:
    """Decide si el error se devuelve como JSON o como página HTML."""
    return ruta.startswith("/api/")


@app.exception_handler(StarletteHTTPException)
async def manejar_error_http(request: Request, exc: StarletteHTTPException):
    """Errores 404/409/etc.: JSON para la API, plantilla para el navegador."""
    if _es_api(request.url.path):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    return plantillas.TemplateResponse(
        request=request,
        name="error.html",
        context={"codigo": exc.status_code, "mensaje": exc.detail},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, exc: RequestValidationError):
    """Convierte errores de validación en respuestas claras y consistentes."""
    errores = [
        {
            "campo": ".".join(str(parte) for parte in error["loc"]),
            "mensaje": error["msg"],
        }
        for error in exc.errors()
    ]

    if _es_api(request.url.path):
        return JSONResponse(status_code=422, content={"detail": errores})

    mensaje = errores[0]["mensaje"] if errores else "Datos inválidos"
    return plantillas.TemplateResponse(
        request=request,
        name="error.html",
        context={"codigo": 422, "mensaje": mensaje},
        status_code=422,
    )
