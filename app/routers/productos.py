"""Rutas de productos: API REST (JSON) y vistas HTML para el usuario."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

# API: expuesta en /api/productos y documentada en /docs.
router = APIRouter(prefix="/api/productos", tags=["productos"])

# Vistas: páginas HTML, excluidas de OpenAPI.
vistas = APIRouter(include_in_schema=False)


def _obtener_o_404(db: Session, producto_id: int):
    """Centraliza la regla 'no encontrado' para API y vistas."""
    producto = crud.obtener_producto(db, producto_id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return producto


def _plantillas(request: Request):
    """Accede al motor de plantillas guardado en el estado de la app."""
    return request.app.state.templates


def _conflicto_por_sku(db: Session) -> HTTPException:
    """Deshace la transacción y prepara un error 409 por SKU duplicado."""
    db.rollback()
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ya existe un producto con ese SKU",
    )


def _render_listado(
    request: Request,
    db: Session,
    busqueda: str = "",
    error: str | None = None,
    formulario: dict[str, str] | None = None,
    codigo: int = status.HTTP_200_OK,
):
    """Renderiza el listado conservando los valores cargados tras un error."""
    return _plantillas(request).TemplateResponse(
        request=request,
        name="index.html",
        context={
            "productos": crud.listar_productos(db, busqueda),
            "busqueda": busqueda,
            "error": error,
            "formulario": formulario or {},
        },
        status_code=codigo,
    )


# ---------------------------------------------------------------------------
# API REST
# ---------------------------------------------------------------------------


@router.get("", response_model=list[schemas.ProductoOut])
def listar_api(
    busqueda: str = Query("", max_length=120, description="Filtro por nombre o SKU"),
    limite: int = Query(100, ge=1, le=200),
    desplazamiento: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Lista productos; admite búsqueda y paginación básica."""
    return crud.listar_productos(db, busqueda, limite, desplazamiento)


@router.get("/{producto_id}", response_model=schemas.ProductoOut)
def obtener_api(producto_id: int, db: Session = Depends(get_db)):
    """Devuelve un producto por id."""
    return _obtener_o_404(db, producto_id)


@router.post(
    "",
    response_model=schemas.ProductoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_api(datos: schemas.ProductoCreate, db: Session = Depends(get_db)):
    """Da de alta un producto."""
    try:
        return crud.crear_producto(db, datos)
    except IntegrityError:
        raise _conflicto_por_sku(db) from None


@router.put("/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_api(
    producto_id: int,
    datos: schemas.ProductoUpdate,
    db: Session = Depends(get_db),
):
    """Reemplaza todos los campos de un producto existente."""
    producto = _obtener_o_404(db, producto_id)
    try:
        return crud.actualizar_producto(db, producto, datos)
    except IntegrityError:
        raise _conflicto_por_sku(db) from None


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_api(producto_id: int, db: Session = Depends(get_db)):
    """Elimina un producto; responde 204 sin cuerpo."""
    producto = _obtener_o_404(db, producto_id)
    crud.eliminar_producto(db, producto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Vistas HTML
# ---------------------------------------------------------------------------


@vistas.get("/", response_class=HTMLResponse)
def inicio(
    request: Request,
    busqueda: str = "",
    db: Session = Depends(get_db),
):
    """Página principal: listado, búsqueda y formulario de alta."""
    return _render_listado(request, db, busqueda=busqueda)


@vistas.post("/", response_class=HTMLResponse)
async def crear_desde_formulario(request: Request, db: Session = Depends(get_db)):
    """Procesa el alta desde el formulario HTML."""
    formulario = await request.form()
    valores = {
        campo: str(formulario.get(campo, "")).strip()
        for campo in ("nombre", "sku", "precio", "stock")
    }

    try:
        datos = schemas.ProductoCreate(
            nombre=valores["nombre"],
            sku=valores["sku"],
            precio=float(valores["precio"]),
            stock=int(valores["stock"] or "0"),
        )
    except (ValidationError, ValueError) as exc:
        return _render_listado(
            request,
            db,
            error=f"Revisá los datos del formulario: {exc}",
            formulario=valores,
            codigo=status.HTTP_400_BAD_REQUEST,
        )

    try:
        crud.crear_producto(db, datos)
    except IntegrityError:
        return _render_listado(
            request,
            db,
            error="Ya existe un producto con ese SKU.",
            formulario=valores,
            codigo=status.HTTP_409_CONFLICT,
        )

    # Post/Redirect/Get: evita reenviar el formulario al recargar.
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@vistas.get("/productos/{producto_id}/editar", response_class=HTMLResponse)
def formulario_edicion(
    producto_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Muestra el formulario de edición cargado con los datos actuales."""
    producto = _obtener_o_404(db, producto_id)
    return _plantillas(request).TemplateResponse(
        request=request,
        name="producto_form.html",
        context={"producto": producto, "error": None},
    )


@vistas.post("/productos/{producto_id}/editar", response_class=HTMLResponse)
async def actualizar_desde_formulario(
    producto_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Guarda los cambios del formulario de edición."""
    producto = _obtener_o_404(db, producto_id)
    formulario = await request.form()
    valores = {
        campo: str(formulario.get(campo, "")).strip()
        for campo in ("nombre", "sku", "precio", "stock")
    }

    try:
        datos = schemas.ProductoUpdate(
            nombre=valores["nombre"],
            sku=valores["sku"],
            precio=float(valores["precio"]),
            stock=int(valores["stock"] or "0"),
        )
    except (ValidationError, ValueError) as exc:
        return _plantillas(request).TemplateResponse(
            request=request,
            name="producto_form.html",
            context={
                "producto": producto,
                "error": f"Revisá los datos del formulario: {exc}",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        crud.actualizar_producto(db, producto, datos)
    except IntegrityError:
        db.rollback()
        return _plantillas(request).TemplateResponse(
            request=request,
            name="producto_form.html",
            context={
                "producto": producto,
                "error": "Ya existe un producto con ese SKU.",
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@vistas.post("/productos/{producto_id}/eliminar")
def eliminar_desde_formulario(
    producto_id: int,
    db: Session = Depends(get_db),
):
    """Elimina desde la web. HTML no tiene DELETE, por eso se usa POST."""
    producto = _obtener_o_404(db, producto_id)
    crud.eliminar_producto(db, producto)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
