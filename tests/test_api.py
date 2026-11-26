"""Pruebas de la API REST."""

from __future__ import annotations


def test_health(cliente):
    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_alta_listado_y_busqueda(cliente, producto_ejemplo):
    respuesta = cliente.post("/api/productos", json=producto_ejemplo)

    assert respuesta.status_code == 201
    assert respuesta.json()["sku"] == "LAP-001"

    listado = cliente.get("/api/productos").json()
    assert len(listado) == 1

    filtrado = cliente.get("/api/productos", params={"busqueda": "lap"}).json()
    assert len(filtrado) == 1
    assert filtrado[0]["id"] == respuesta.json()["id"]


def test_obtener_producto_inexistente(cliente):
    assert cliente.get("/api/productos/999").status_code == 404


def test_actualizar_y_eliminar(cliente, producto_ejemplo):
    producto_id = cliente.post("/api/productos", json=producto_ejemplo).json()["id"]
    cambios = {
        **producto_ejemplo,
        "nombre": "Lápiz negro",
        "sku": "LAP-002",
        "precio": 2.0,
        "stock": 3,
    }

    respuesta = cliente.put(f"/api/productos/{producto_id}", json=cambios)
    assert respuesta.status_code == 200
    assert respuesta.json()["stock"] == 3

    assert cliente.delete(f"/api/productos/{producto_id}").status_code == 204
    assert cliente.get(f"/api/productos/{producto_id}").status_code == 404


def test_sku_duplicado_devuelve_conflicto(cliente, producto_ejemplo):
    cliente.post("/api/productos", json=producto_ejemplo)

    respuesta = cliente.post("/api/productos", json=producto_ejemplo)

    assert respuesta.status_code == 409
    assert "SKU" in respuesta.json()["detail"]


def test_datos_invalidos_devuelven_422(cliente):
    respuesta = cliente.post(
        "/api/productos",
        json={"nombre": "", "sku": "X-1", "precio": -5, "stock": 0},
    )

    assert respuesta.status_code == 422
    assert any(error["campo"] == "body.precio" for error in respuesta.json()["detail"])
