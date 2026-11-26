"""Pruebas de la capa de acceso a datos."""

from __future__ import annotations

from app import crud, schemas


def test_crear_y_listar(db):
    creado = crud.crear_producto(
        db,
        schemas.ProductoCreate(nombre="Lápiz", sku="lap-001", precio=1.5, stock=10),
    )

    assert creado.id is not None
    assert creado.sku == "LAP-001"  # el esquema normaliza el SKU
    productos = crud.listar_productos(db)
    assert len(productos) == 1
    assert productos[0].nombre == "Lápiz"


def test_busqueda_por_nombre_y_sku(db):
    crud.crear_producto(
        db, schemas.ProductoCreate(nombre="Cuaderno A4", sku="CAD-001", precio=3, stock=5)
    )
    crud.crear_producto(
        db, schemas.ProductoCreate(nombre="Lápiz", sku="LAP-001", precio=1.5, stock=10)
    )

    assert len(crud.listar_productos(db, "cuaderno")) == 1
    assert len(crud.listar_productos(db, "lap-001")) == 1
    assert len(crud.listar_productos(db, "inexistente")) == 0


def test_actualizar_producto(db):
    producto = crud.crear_producto(
        db, schemas.ProductoCreate(nombre="Lápiz", sku="LAP-001", precio=1.5, stock=10)
    )

    actualizado = crud.actualizar_producto(
        db,
        producto,
        schemas.ProductoUpdate(
            nombre="Lápiz negro", sku="LAP-002", precio=2.0, stock=4
        ),
    )

    assert actualizado.nombre == "Lápiz negro"
    assert crud.obtener_producto(db, producto.id).sku == "LAP-002"


def test_eliminar_producto(db):
    producto = crud.crear_producto(
        db, schemas.ProductoCreate(nombre="Lápiz", sku="LAP-001", precio=1.5, stock=10)
    )

    crud.eliminar_producto(db, producto)

    assert crud.obtener_producto(db, producto.id) is None
