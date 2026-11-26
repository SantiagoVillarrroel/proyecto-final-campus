# Gestor de Inventario GT

Trabajo Práctico Final — **Entrega Final Proyecto, Stage 2 / Campus GT**.

Aplicación full-stack mínima y completa para administrar un inventario de productos: alta, listado con búsqueda, edición y baja. Expone la misma lógica mediante **API REST JSON** e **interfaz web HTML**, con persistencia en **SQLite** y tests automatizados.

---

## 1. Descripción

El sistema permite gestionar productos identificados por un **SKU único** (normalizado a mayúsculas), con nombre, precio y stock. Incluye:

- **CRUD completo** por API REST (`/api/productos`).
- **Interfaz web** responsiva con formularios y confirmación de borrado (`/`).
- **Búsqueda** por nombre o SKU y paginación básica en la API.
- **Validaciones** de datos (campos no vacíos, precio y stock mayores o iguales a cero).
- **Manejo de errores** uniforme: JSON para la API, páginas HTML para las vistas.
- **Persistencia SQLite** configurable por variable de entorno.
- **Tests** de capa de datos, API y vistas con `pytest`.

No se incluyen autenticación ni APIs externas: el alcance acordado es el mínimo obligatorio, con una arquitectura preparada para crecer.

---

## 2. Tecnologías utilizadas

| Capa | Tecnología | Versión fijada |
| --- | --- | --- |
| Lenguaje | Python | 3.15.2 (probado) |
| Framework web | FastAPI | 0.165.0 |
| Servidor ASGI | Uvicorn | 0.54.0 |
| ORM | SQLAlchemy | 2.1.9 |
| Validación | Pydantic | 2.14.4 |
| Plantillas | Jinja2 | 3.1.6 |
| Formularios | python-multipart | 0.0.34 |
| Base de datos | SQLite | integrada en Python |
| Tests | pytest + httpx2 (TestClient) | 9.2.0 / 2.16.2 |

Todas las dependencias, incluidas las transitivas, están fijadas en `requirements.txt`.

---

## 3. Estructura del proyecto

```text
proyecto-final/
├── README.md                    # Esta documentación
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Exclusiones de Git
├── requirements.txt             # Dependencias exactas
├── pytest.ini                   # Configuración de pytest
├── app/
│   ├── __init__.py              # Versión del paquete
│   ├── main.py                  # App FastAPI, plantillas, estáticos y errores
│   ├── config.py                # Configuración desde entorno
│   ├── database.py              # Engine, sesiones e init_db()
│   ├── models.py                # Modelo Producto (SQLAlchemy)
│   ├── schemas.py               # Esquemas Pydantic y validaciones
│   ├── crud.py                  # Consultas y escrituras a la base
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py            # GET /health
│   │   └── productos.py         # API REST + vistas HTML
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── producto_form.html
│   │   └── error.html
│   └── static/
│       ├── css/estilos.css
│       └── js/app.js
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # BD temporal y cliente de tests
│   ├── test_crud.py
│   ├── test_api.py
│   └── test_vistas.py
└── scripts/
    └── empaquetar.py            # Genera entrega.zip sin archivos generados
```

### Arquitectura

- **Presentación:** plantillas Jinja2 + CSS/JS propios. Las vistas usan POST-redirect-GET para evitar reenvíos al recargar.
- **Aplicación:** FastAPI, routers separados para API y vistas, esquemas Pydantic y handlers de errores.
- **Dominio/datos:** modelo `Producto` y módulo `crud.py`, único lugar con sentencias SQL.
- **Infraestructura:** configuración por entorno, creación automática de tablas y script de empaquetado.

---

## 4. Instalación paso a paso (Windows / PowerShell)

```powershell
cd C:\Users\villa\proyecto-final

# 1) Crear entorno virtual
python -m venv .venv

# 2) Actualizar pip e instalar dependencias exactas
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3) Opcional: personalizar configuración
Copy-Item .env.example .env
```

> Si `python` no funciona, probá con `py -3`. Si `git` no se reconoce en una terminal ya abierta, cerrala y abrila de nuevo (Git se instaló con `winget`).

---

## 5. Ejecución

```powershell
cd C:\Users\villa\proyecto-final
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

URLs:

| URL | Qué muestra |
| --- | --- |
| <http://127.0.0.1:8000/> | Interfaz web del inventario |
| <http://127.0.0.1:8000/docs> | Documentación interactiva (Swagger) |
| <http://127.0.0.1:8000/redoc> | Documentación alternativa (ReDoc) |
| <http://127.0.0.1:8000/health> | Estado de la app y la base (`{"estado":"ok"}`) |

Para detener el servidor: `Ctrl + C`.

La base se crea automáticamente en `data/inventario.db` la primera vez que levanta la app.

---

## 6. Ejemplos de uso

### Desde el navegador

1. Abrir <http://127.0.0.1:8000/>.
2. Completar nombre, SKU, precio y stock → **Guardar**.
3. Buscar por nombre o SKU con el formulario de búsqueda.
4. **Editar** o **Eliminar** desde la tabla.

### Desde la API (PowerShell)

```powershell
# Alta
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/productos" `
  -ContentType "application/json" `
  -Body '{"nombre":"Cuaderno A4","sku":"CAD-001","precio":3.5,"stock":12}'

# Listado con búsqueda
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/productos?busqueda=CAD"

# Edición (PUT reemplaza todos los campos)
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:8000/api/productos/1" `
  -ContentType "application/json" `
  -Body '{"nombre":"Cuaderno A4 x50","sku":"CAD-002","precio":4.2,"stock":8}'

# Baja (204 sin contenido)
Invoke-WebRequest -Method Delete -Uri "http://127.0.0.1:8000/api/productos/1"
```

### Con curl

```bash
curl -X POST http://127.0.0.1:8000/api/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Lápiz","sku":"LAP-001","precio":1.5,"stock":10}'
```

Códigos de respuesta relevantes: `201` alta correcta, `200` consulta/edición, `204` baja, `404` inexistente, `409` SKU duplicado, `422` validación fallida.

---

## 7. Variables de entorno

Copiar `.env.example` a `.env` si se quiere cambiar alguno de estos valores:

| Variable | Por defecto | Descripción |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///data/inventario.db` | URL SQLAlchemy. Ej.: `sqlite:///C:/ruta/mi.db` o `postgresql+psycopg://...` |
| `DEBUG` | `true` | Modo depuración de FastAPI |
| `HOST` | `127.0.0.1` | Host usado en la documentación |
| `PORT` | `8000` | Puerto usado en la documentación |

> El archivo `.env` está ignorado por Git. La app lee las variables del entorno del proceso; si querés cargar `.env` automáticamente, exportalas antes de ejecutar o usá un cargador externo.

---

## 8. Tests y verificación

```powershell
.\.venv\Scripts\python.exe -m pytest
```

La suite usa una base SQLite temporal aislada por corrida y verifica:

- `tests/test_crud.py`: alta, búsqueda, actualización y baja en la capa de datos.
- `tests/test_api.py`: health, CRUD por HTTP, 404, 409 por SKU duplicado y 422 por validación.
- `tests/test_vistas.py`: carga de la home, alta desde formulario, errores, edición, borrado y 404 amigable.

Resultado esperado: **15 tests aprobados**.

---

## 9. Preparación de Git y entrega

Estado actual: Git instalado con `winget install --id Git.Git -e --source winget`, rama `main` publicada y remoto `origin` configurado hacia <https://github.com/SantiagoVillarrroel/proyecto-final-campus>.

El repositorio ya está sincronizado. Para replicar la conexión en otra máquina:

```powershell
cd C:\Users\villa\proyecto-final

git remote add origin https://github.com/SantiagoVillarrroel/proyecto-final-campus.git
git branch -M main
git push -u origin main
```

Si el repo remoto ya tiene archivos (README, por ejemplo), usar antes:

```powershell
git pull origin main --allow-unrelated-histories
```

### ZIP de respaldo

```powershell
.\.venv\Scripts\python.exe scripts\empaquetar.py
```

Genera `entrega.zip` con la carpeta `proyecto-final/` adentro, excluyendo `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `data/*.db`, `.env` y archivos temporales.

---

## 10. Comentario listo para Campus GT

> Proyecto final Stage 2: Gestor de Inventario GT. Implementé un CRUD de productos con FastAPI + SQLAlchemy + SQLite, con API REST documentada en `/docs`, interfaz web responsiva, búsqueda, validaciones y manejo de errores. Incluye 15 tests automatizados que pasan correctamente con `pytest`, README con instrucciones de instalación y uso, `.env.example`, `requirements.txt` con dependencias exactas y ZIP de respaldo. Repositorio: https://github.com/SantiagoVillarrroel/proyecto-final-campus

---

## 11. Solución de problemas

| Situación | Solución |
| --- | --- |
| `git` no se reconoce | Cerrar y abrir la terminal, o usar `C:\Program Files\Git\cmd\git.exe`. |
| El puerto 8000 está ocupado | `--port 8001` y actualizar la URL. |
| `python` no se reconoce | Usar `py -3`. |
| Error al importar `app` | Verificar que se ejecuta desde la raíz del proyecto y que el `.venv` tenga las dependencias instaladas. |
| Datos "raros" al probar | Borrar `data/inventario.db`; se regenera vacío al iniciar. |

---

**Uso:** trabajo académico individual para Campus GT.
