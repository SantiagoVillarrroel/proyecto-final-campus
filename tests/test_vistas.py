"""Pruebas de las vistas HTML (flujo completo desde el navegador)."""

from __future__ import annotations


def test_index_muestra_listado(cliente, producto_ejemplo):
    cliente.post("/api/productos", json=producto_ejemplo)

    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "Gestor de Inventario GT" in respuesta.text
    assert "Lápiz" in respuesta.text


def test_alta_desde_formulario_redirige_y_guarda(cliente):
    respuesta = cliente.post(
        "/",
        data={"nombre": "Cuaderno", "sku": "cad-001", "precio": "3.50", "stock": "4"},
        follow_redirects=False,
    )

    assert respuesta.status_code == 303
    assert respuesta.headers["location"] == "/"
    assert "Cuaderno" in cliente.get("/").text


def test_formulario_invalido_muestra_error(cliente):
    respuesta = cliente.post(
        "/",
        data={"nombre": "", "sku": "X-1", "precio": "-1", "stock": "0"},
    )

    assert respuesta.status_code == 400
    assert "Revisá los datos" in respuesta.text


def test_editar_y_eliminar_desde_la_web(cliente, producto_ejemplo):
    producto_id = cliente.post("/api/productos", json=producto_ejemplo).json()["id"]

    formulario = cliente.get(f"/productos/{producto_id}/editar")
    assert formulario.status_code == 200
    assert "LAP-001" in formulario.text

    guardado = cliente.post(
        f"/productos/{producto_id}/editar",
        data={
            "nombre": "Lápiz negro",
            "sku": "LAP-002",
            "precio": "2.00",
            "stock": "3",
        },
        follow_redirects=False,
    )
    assert guardado.status_code == 303
    assert "Lápiz negro" in cliente.get("/").text

    borrado = cliente.post(
        f"/productos/{producto_id}/eliminar", follow_redirects=False
    )
    assert borrado.status_code == 303
    assert "Lápiz negro" not in cliente.get("/").text


def test_vista_inexistente_muestra_error_amigable(cliente):
    respuesta = cliente.get("/productos/999/editar")

    assert respuesta.status_code == 404
    assert "Error 404" in respuesta.text
