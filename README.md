# crud-django-meico — API REST de Catálogo

API REST para la gestión de productos y categorías, desarrollada con **Django 5.2** y **Django REST Framework 3.17**. Incluye documentación Swagger automática, pruebas unitarias y controles de calidad de código PEP 8.

---

## Tabla de contenidos

1. [Requisitos](#1-requisitos)
2. [Instalación de Make en Windows](#2-instalación-de-make-en-windows)
3. [Configuración del entorno](#3-configuración-del-entorno)
4. [Ejecutar el servidor](#4-ejecutar-el-servidor)
5. [Documentación Swagger](#5-documentación-swagger)
6. [Endpoints disponibles](#6-endpoints-disponibles)
7. [Pruebas unitarias](#7-pruebas-unitarias)
8. [Calidad de código](#8-calidad-de-código)
9. [Estructura del proyecto](#9-estructura-del-proyecto)

---

## 1. Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| Python      | 3.10+          |
| pip         | 23+            |
| make        | Cualquiera     |

---

## 2. Instalación de Make en Windows

Los comandos `make lint`, `make test`, etc. requieren GNU Make. Elige una de estas opciones:

### Opción A — Chocolatey (recomendado)
```powershell
# 1. Instalar Chocolatey si no lo tienes (PowerShell como administrador):
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Instalar Make:
choco install make
```

### Opción B — winget
```powershell
winget install GnuWin32.Make
# Agregar al PATH: C:\Program Files (x86)\GnuWin32\bin
```

### Opción C — WSL (Windows Subsystem for Linux)
```bash
# Make ya está disponible en WSL:
sudo apt install make   # Ubuntu/Debian
```
> El proyecto ya está configurado para WSL: el `Makefile` usa el ejecutable de Python en `../venv-crud-django-meico/Scripts/python.exe` ac
cesible desde WSL via interop de Windows.

### Opción D — Git Bash
Git for Windows incluye Make. Abre los comandos en Git Bash en lugar de cmd/PowerShell.

---

## 3. Configuración del entorno

```bash
# Desde la carpeta raíz meico/
python -m venv venv-crud-django-meico

# Activar el entorno virtual
# Windows (PowerShell):
.\venv-crud-django-meico\Scripts\Activate.ps1
# Windows (cmd):
venv-crud-django-meico\Scripts\activate.bat
# WSL / macOS / Linux:
source venv-crud-django-meico/bin/activate

# Entrar al proyecto
cd crud-django-meico

# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar dependencias de desarrollo (linters, formateadores, type checkers)
pip install -r requirements-dev.txt

# Aplicar migraciones (crea la base de datos SQLite)
python manage.py migrate
```

### Variable de entorno requerida

Crea el archivo `.env` en `crud-django-meico/` con:

```env
SECRET_KEY=django-insecure-cambia-esto-en-produccion
```

---

## 4. Ejecutar el servidor

```bash
python manage.py runserver
```

El servidor queda disponible en `http://localhost:8000`.

---

## 5. Documentación Swagger

Con el servidor en marcha, accede a cualquiera de estas URLs:

| Interfaz        | URL                                    |
|-----------------|----------------------------------------|
| Swagger UI      | http://localhost:8000/api/schema/swagger-ui/ |
| ReDoc           | http://localhost:8000/api/schema/redoc/ |
| Schema OpenAPI  | http://localhost:8000/api/schema/       |

---

## 6. Endpoints disponibles

### Productos — `/api/products/`

| Método   | URL                                | Descripción                          |
|----------|------------------------------------|--------------------------------------|
| `GET`    | `/api/products/`                   | Listar productos activos             |
| `GET`    | `/api/products/?search=laptop`     | Buscar por nombre                    |
| `GET`    | `/api/products/?category_id=1`     | Filtrar por categoría                |
| `POST`   | `/api/products/`                   | Crear producto                       |
| `GET`    | `/api/products/{id}/`              | Detalle de un producto               |
| `PUT`    | `/api/products/{id}/`              | Actualización completa               |
| `PATCH`  | `/api/products/{id}/`              | Actualización parcial                |
| `DELETE` | `/api/products/{id}/`              | Soft delete (pone `is_active=False`) |
| `POST`   | `/api/products/{id}/adjust_stock/` | Ajuste atómico de stock              |

**Body de `adjust_stock`:**
```json
{ "quantity": 10 }
```
`quantity` puede ser negativo para restar stock. La operación falla si el stock resultante sería negativo.

### Categorías — `/api/categories/`

| Método   | URL                      | Descripción              |
|----------|--------------------------|--------------------------|
| `GET`    | `/api/categories/`       | Listar categorías        |
| `POST`   | `/api/categories/`       | Crear categoría          |
| `GET`    | `/api/categories/{id}/`  | Detalle de una categoría |
| `PUT`    | `/api/categories/{id}/`  | Actualización completa   |
| `PATCH`  | `/api/categories/{id}/`  | Actualización parcial    |
| `DELETE` | `/api/categories/{id}/`  | Eliminar categoría       |

---

## 7. Pruebas unitarias

```bash
# Ejecutar todas las pruebas
python manage.py test apps.catalog

# O con Make (usa el venv de la carpeta padre)
make test
```

La suite incluye **53 pruebas** distribuidas en 4 módulos:

| Archivo                      | Qué prueba                                          |
|------------------------------|-----------------------------------------------------|
| `test_models.py`             | Validaciones y comportamientos de los modelos       |
| `test_serializers.py`        | Validación de precio, category_id, campos de solo lectura |
| `test_views.py`              | Todos los endpoints: CRUD, filtros, adjust_stock    |
| `test_signals.py`            | Señal `post_save` y formato del mensaje en consola  |

---

## 8. Calidad de código

Todos los controles apuntan a los configs en `.code_quality/` con límite de línea de **79 caracteres** (PEP 8 estándar).

### Formatear código (aplica cambios automáticamente)
```bash
make format
```

### Verificar formato sin aplicar cambios

```bash
make lint-black    # Verifica estilo Black
make lint-isort    # Verifica orden de imports
make lint-flake8   # Verifica PEP 8 y errores
```

### Análisis estático de tipos y seguridad

```bash
make lint-mypy     # Type checking con mypy
make lint-bandit   # Análisis de seguridad con Bandit
make lint-pylint   # Análisis profundo con Pylint
```

### Ejecutar todos los linters de una vez

```bash
make lint
# Equivale a: lint-black + lint-isort + lint-flake8 + lint-mypy + lint-bandit
```

### Resumen de herramientas

| Herramienta | Config                          | Propósito                       |
|-------------|---------------------------------|---------------------------------|
| Black       | `.code_quality/pyproject.toml`  | Formateo automático             |
| isort       | `.code_quality/pyproject.toml`  | Orden de imports                |
| Flake8      | `.code_quality/.flake8`         | PEP 8 y errores                 |
| mypy        | `.code_quality/mypy.ini`        | Type checking estático          |
| Bandit      | `.code_quality/bandit.yaml`     | Vulnerabilidades de seguridad   |
| Pylint      | `.code_quality/.pylintrc`       | Análisis profundo de código     |

---

## 9. Estructura del proyecto

```
crud-django-meico/
├── .code_quality/          # Configuración de linters (Black, isort, Flake8, mypy, Bandit, Pylint)
├── apps/
│   └── catalog/
│       ├── api/
│       │   ├── serializers.py   # CategorySerializer, ProductSerializer
│       │   └── viewsets.py      # CategoryViewSet, ProductViewSet
│       ├── migrations/
│       ├── tests/
│       │   ├── test_models.py
│       │   ├── test_serializers.py
│       │   ├── test_signals.py
│       │   └── test_views.py
│       ├── apps.py          # AppConfig — registra señales en ready()
│       ├── models.py        # Category, Product (soft delete, SET_NULL)
│       ├── signals.py       # post_save → print en consola
│       └── urls.py          # DefaultRouter
├── config/
│   ├── settings.py          # CORS, DRF, drf-spectacular, python-dotenv
│   └── urls.py              # /api/ + /api/schema/
├── .env                     # SECRET_KEY (no versionar)
├── Makefile                 # format, lint, test
├── requirements.txt         # Dependencias de producción
├── requirements-dev.txt     # Herramientas de desarrollo
└── manage.py
```
