# pdf-extractext

Aplicación web para subir archivos PDF, extraer su texto y gestionar los documentos almacenados.

## Grupo

- Mulena, Adrián
- Ochoa Merino, Camila

## Tecnologías

- **Lenguaje:** Python
- **Framework:** FastAPI
- **Gestor de paquetes:** uv
- **Base de datos:** MongoDB
- **Testing:** pytest (metodología TDD)

## Requisitos previos

Tener instalado:
- Python 3.12 o superior
- uv
- MongoDB corriendo localmente o una URL de conexión

## Cómo ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/camilaochoamerino/pdf-extractext.git
cd pdf-extractext
```

### 2. Instalar dependencias

```bash
uv sync
```

### 3. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=pdf_extractext
```

### 4. Ejecutar la aplicación

```bash
uv run fastapi dev app/main.py
```

La API queda disponible en `http://localhost:8000`.

### 5. Correr los tests

```bash
uv run pytest tests/ -v
```

## Estructura del proyecto

```
app/
  api/              → endpoints de la API
  services/         → lógica de negocio
  models/           → modelos de datos
  db/               → conexión a MongoDB
  core/             → configuración general
tests/              → tests automatizados
```

## Principios aplicados

- **TDD:** cada funcionalidad tiene su test antes de la implementación
- **KISS, DRY, YAGNI, SOLID:** código limpio y sin complejidad innecesaria
- **12 Factor App:** configuración por variables de entorno, dependencias declaradas, código base único

## Funcionalidades

- Subir un PDF y extraer su texto en memoria (sin guardar el archivo en disco)
- Validar formato y tamaño del archivo
- Detectar y rechazar documentos duplicados por checksum
- CRUD completo de documentos almacenados