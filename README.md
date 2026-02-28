# Bot Seguridad Social Argentina 🇦🇷

Promotor de Seguridad Social basado en RAG (Retrieval Augmented Generation) para responder consultas sobre la seguridad social Argentina. Utiliza Google Gemini API, ChromaDB para almacenamiento vectorial, e IBM Docling para procesamiento de documentos.

## 📋 Tabla de Contenidos

- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [🐳 Quick Start con Docker (Recomendado)](#-quick-start-con-docker-recomendado)
  - [Instalación Básica](#instalación-básica)
  - [Ingesta de Documentos](#ingesta-de-documentos)
  - [Sistema de Versionado](#sistema-de-versionado)
  - [Comandos Útiles](#comandos-útiles-docker)
- [💻 Instalación Manual (Desarrollo Local)](#-instalación-manual-desarrollo-local)
  - [Requisitos Previos](#requisitos-previos)
  - [Instalación y Configuración](#instalación-y-configuración)
  - [Ejecución de la Aplicación](#ejecución-de-la-aplicación)
- [Estructura de Carpetas](#-estructura-de-carpetas)

---

## 🚀 Tecnologías Utilizadas

### Backend
- **Python 3.13+** con `uv` o `pip` para gestión de dependencias
- **FastAPI** para la API REST
- **Google Gemini API** para embeddings y generación de respuestas
- **ChromaDB** como base de datos vectorial
- **IBM Docling** para procesamiento de documentos

### Frontend
- **React 19** con TypeScript
- **Vite** como bundler
- **Google GenAI SDK** para integración con Gemini

### Arquitectura
El proyecto sigue **Arquitectura Hexagonal (Ports & Adapters)** para máxima flexibilidad y testeabilidad.

---

## 🏗️ Arquitectura del Proyecto

```
Bot_seguridad_social/
├── rag_app/              # Backend (Python/FastAPI)
│   ├── config/           # Configuración y settings
│   ├── domain/           # Modelos de dominio
│   ├── ports/            # Interfaces/Abstracciones
│   ├── adapters/         # Implementaciones concretas
│   ├── services/         # Lógica de negocio
│   └── api_main.py       # FastAPI application
│
└── front/                # Frontend (React/TypeScript)
    ├── components/       # Componentes React
    ├── services/         # API clients
    └── App.tsx           # Aplicación principal
```

---

## 🐳 Quick Start con Docker (Recomendado)

La forma más fácil de ejecutar la aplicación es usando Docker. No necesitás instalar Python, Node.js ni dependencias manualmente.

### Requisitos

- **Docker** y **Docker Compose** instalados ([Instalar Docker](https://docs.docker.com/get-docker/))
- **API Key de Google Gemini** ([Obtener aquí](https://aistudio.google.com/app/apikey))

### Instalación Básica

#### 1. Configurar variables de entorno

Copiá el template de configuración y editalo con tu API key:

```bash
cp .env.example .env
```

Editá el archivo `.env` y agregá tu `GEMINI_API_KEY`:

```bash
# .env
GEMINI_API_KEY=tu_api_key_de_gemini_aqui

# Configuración opcional (valores por defecto)
CORPUS_VERSION=v1
HOST=0.0.0.0
PORT=8000
```

#### 2. Levantar los servicios

```bash
# Construir y levantar backend + frontend
docker compose up --build -d

# Ver logs en tiempo real
docker compose logs -f
```

Esto iniciará:
- **Backend (FastAPI + RAG):** http://localhost:8000
- **Frontend (React):** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

#### 3. Verificar que los servicios están corriendo

```bash
docker compose ps
```

Deberías ver ambos contenedores como `Up` y el backend como `healthy`:

```
NAME                     STATUS
bot-seguridad-backend    Up (healthy)
bot-seguridad-frontend   Up
```

---

### Ingesta de Documentos

El sistema necesita documentos legales indexados para funcionar. Hay dos formas de ingestar documentos:

> **💡 `docker compose run` vs `docker exec`:**
>
> - `docker compose run --rm ingest` → **Crea un contenedor temporal nuevo.** Usar para la ingesta inicial o cuando el backend no está corriendo.
> - `docker exec bot-seguridad-backend` → **Ejecuta dentro del contenedor que ya está corriendo.** Más rápido, usar para operaciones de mantenimiento (reset, re-ingesta).
>
> Es importante usar `uv run python` en lugar de solo `python` para que las dependencias estén disponibles.

#### Opción A: Ingestar todas las leyes configuradas

Procesa todas las leyes definidas en `rag_app/config/leyes_config.json`:

```bash
# Si el backend NO está corriendo (crea contenedor temporal)
docker compose run --rm ingest

# Si el backend YA está corriendo (más rápido)
docker exec bot-seguridad-backend uv run python /app/rag_app/scripts/setup_db.py
```

#### Opción B: Ingestar una sola ley específica

Para testing o desarrollo, podés procesar una ley individual:

```bash
# Ver lista de leyes disponibles
docker compose run --rm ingest uv run python /app/rag_app/scripts/ingest_single_law.py --list

# Ingestar una ley específica por su número
docker compose run --rm ingest uv run python /app/rag_app/scripts/ingest_single_law.py 24714
```

---

### Sistema de Versionado

El sistema implementa **versionado de corpus** con aislamiento físico. Esto permite mantener múltiples versiones de la base de datos simultáneamente.

#### Estructura de Datos Versionados

```
data/
├── chroma_db/
│   ├── v1/              # Versión 1 del corpus
│   │   └── chroma.sqlite3
│   ├── v2/              # Versión 2 del corpus (si existe)
│   │   └── chroma.sqlite3
│   └── ...
├── processed/
│   ├── v1/              # Documentos procesados v1
│   │   ├── ley_24714.md
│   │   └── ...
│   └── v2/              # Documentos procesados v2
├── corpus_raw/          # Documentos fuente (compartidos)
└── logs/                # Logs de la aplicación
```

#### Crear una Nueva Versión

Para crear una nueva versión del corpus (ej: con leyes actualizadas o diferentes parámetros):

```bash
# Crear versión v2 con todas las leyes
CORPUS_VERSION=v2 docker compose run --rm ingest

# O crear v2 con solo una ley para testing
CORPUS_VERSION=v2 docker compose run --rm ingest uv run python /app/rag_app/scripts/ingest_single_law.py 24714

# Usar versión v2 en el backend
CORPUS_VERSION=v2 docker compose up -d backend
```

**Ejemplo práctico:**
```bash
# 1. Crear v2 solo con Ley 24714 (Asignaciones Familiares)
CORPUS_VERSION=v2 docker compose run --rm ingest uv run python /app/rag_app/scripts/ingest_single_law.py 24714
```

#### Listar Versiones Disponibles

```bash
ls -lh data/chroma_db/
# Output:
# v1/
# v2/
# v3/
```

#### Cambiar Entre Versiones

Para cambiar la versión activa del corpus en el backend:

**Paso 1:** Editá el archivo `.env` y cambiá la variable `CORPUS_VERSION`:

```bash
# .env
CORPUS_VERSION=v2  # Cambiar de v1 a v2 (o la versión que quieras)
```

**Paso 2:** Recreá el contenedor backend para aplicar los cambios:

```bash
# ✅ CORRECTO: Recrea el contenedor con nuevas variables de entorno
docker compose up -d backend

# ❌ INCORRECTO: restart NO recarga variables de entorno
# docker compose restart backend
```

**Paso 3:** Verificá que el cambio se aplicó correctamente:

```bash
# Ver logs del backend
docker compose logs backend --tail=20

# Deberías ver algo como:
# "Initialized ChromaDB at /app/data/chroma_db/v2"
# "Collection: legal_documents_v2 (version: v2)"
# "📊 Indexed documents: 1"  (o el número de docs en v2)

# Verificar documents endpoint
curl http://localhost:8000/api/v1/documents | jq '.documents | length'
```

**Paso 4:** Refrescá el frontend (F5 en el navegador) para ver los cambios

> **⚠️ IMPORTANTE:**
> 
> - `docker compose restart` **NO recarga** las variables de entorno del archivo `.env`
> - **Siempre usá** `docker compose up -d` para aplicar cambios en `.env`
> - El frontend necesita un refresh (F5) para actualizar el contador de documentos

#### Ventajas del Versionado

- ✅ **Aislamiento completo:** Cada versión tiene su propia base de datos
- ✅ **Rollback fácil:** Volvé a una versión anterior cambiando `CORPUS_VERSION`
- ✅ **Testing:** Probá nuevos parámetros sin afectar producción
- ✅ **Trazabilidad:** Cada versión mantiene su historial de procesamiento

---

### Comandos Útiles Docker

#### Gestión de Servicios

```bash
# Levantar servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f backend
docker compose logs -f frontend

# Detener servicios
docker compose stop

# Detener y eliminar contenedores
docker compose down

# Detener y eliminar contenedores + volúmenes
docker compose down -v  # ⚠️ Esto borrará los datos!
```

#### Verificar Estado de la Base de Datos

```bash
# Cantidad de documentos indexados
docker exec bot-seguridad-backend uv run python -c "from rag_app.adapters.stores.chroma_adapter import ChromaAdapter; print(f'Documentos: {ChromaAdapter().count_documents()}')"

# IDs de todos los documentos
docker exec bot-seguridad-backend uv run python -c "from rag_app.adapters.stores.chroma_adapter import ChromaAdapter; print(ChromaAdapter().get_all_document_ids())"
```

#### Resetear Base de Datos

```bash
# Modo interactivo (pide confirmación)
docker exec bot-seguridad-backend uv run python /app/rag_app/scripts/reset_db.py

# Modo force (sin confirmación)
docker exec bot-seguridad-backend uv run python /app/rag_app/scripts/reset_db.py --force

# Después de resetear, re-ingestar
docker exec bot-seguridad-backend uv run python /app/rag_app/scripts/setup_db.py
```

#### Reconstruir Imágenes

Si cambiaste dependencias o Dockerfiles:

```bash
# Reconstruir todas las imágenes
docker compose build --no-cache

# Reconstruir solo el backend
docker compose build --no-cache backend

# Reconstruir solo el frontend
docker compose build --no-cache frontend
```

#### Debugging

```bash
# Acceder a un shell dentro del contenedor backend
docker compose exec backend bash

# Acceder a un shell dentro del contenedor frontend
docker compose exec frontend sh

# Ver logs detallados del build
docker compose build --progress=plain backend
```

#### Limpieza de Docker

```bash
# Eliminar contenedores detenidos
docker compose down

# Eliminar imágenes no utilizadas
docker image prune

# Eliminar todos los recursos no utilizados
docker system prune -a
```



## 💻 Instalación Manual (Desarrollo Local)

Si preferís ejecutar la aplicación sin Docker (ej: para debugging más profundo), seguí estas instrucciones.

### Requisitos Previos

Antes de comenzar, asegurate de tener instalado:

- **Python 3.13+**
- **Node.js 18+** (para el frontend)
- **uv** (gestor de paquetes Python, recomendado) o **pip**
- **API Key de Google Gemini** ([Obtener aquí](https://aistudio.google.com/app/apikey))

### Instalar `uv` (recomendado)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

O con pip:

```bash
pip install uv
```

---

## ⚙️ Instalación y Configuración

> **💡 Nota:** Si estás usando Docker (recomendado), podés saltar esta sección. Ir a [Quick Start con Docker](#-quick-start-con-docker-recomendado).

Esta sección es para desarrollo local sin Docker.

### 1. Backend (RAG App)

#### Paso 1.1: Clonar el repositorio (si aún no lo hiciste)

```bash
cd /home/emiliano/Documentos/Exdata/Bot_seguridad_social
```

#### Paso 1.2: Configurar variables de entorno

Crear el archivo `.env` en el directorio `rag_app/`:

```bash
cd rag_app
```

Crear el archivo `.env` con el siguiente contenido:

```bash
# .env
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
```

**Importante:** Reemplazá `tu_api_key_de_gemini_aqui` con tu API key real de Google Gemini.

#### Paso 1.3: Instalar dependencias

**Opción A: Usando `uv` (recomendado)**

```bash
# Desde el directorio rag_app/
uv sync
```

**Opción B: Usando `pip` tradicional**

```bash
pip install -r requirements.txt
```

#### Paso 1.4: Configurar la base de datos vectorial

El sistema necesita documentos legales indexados para funcionar. Ejecutá el script de setup:

```bash
# Desde el directorio raíz del proyecto
cd ..
python -m rag_app.scripts.setup_from_md
```

Este script:
- ✅ Lee el documento `Anses1.md` disponible
- ✅ Genera embeddings usando Gemini
- ✅ Indexa el contenido en ChromaDB
- ✅ Crea la base vectorial en `rag_app/chroma_db/`

---

### 2. Frontend (React + TypeScript)

#### Paso 2.1: Navegar al directorio del frontend

```bash
cd front
```

#### Paso 2.2: Instalar dependencias de Node.js

```bash
npm install
```

#### Paso 2.3: Configurar variables de entorno

Crear el archivo `.env.local` en el directorio `front/`:

```bash
# .env.local
VITE_GEMINI_API_KEY=tu_api_key_de_gemini_aqui
```

**Nota:** Si ya conectaste el frontend con el backend FastAPI, este paso podría ser opcional dependiendo de tu configuración.

---

## ▶️ Ejecución de la Aplicación

Necesitás **dos terminales separadas** para correr el backend y el frontend:

### Terminal 1: Backend (FastAPI)

```bash
cd rag_app
python api_main.py
```

O usando uvicorn directamente:

```bash
uvicorn rag_app.api_main:app --host 0.0.0.0 --port 8000 --reload
```

El backend estará disponible en:
- **API:** http://localhost:8000
- **Documentación interactiva:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Terminal 2: Frontend (React)

```bash
cd front
npm run dev
```

El frontend estará disponible en:
- **Aplicación Web:** http://localhost:5173 (o el puerto que Vite asigne)

---

### Solo Backend API (para desarrollo/testing)

Si solo querés levantar la API sin frontend para probar los endpoints:

```bash
cd rag_app
python api_main.py
```

Accedé a la documentación interactiva en http://localhost:8000/docs para probar los endpoints.

---

## 🗄️ Gestión de la Base de Datos

Comandos útiles para gestionar la base de datos vectorial ChromaDB:

### Verificar estado de la base de datos

```bash
# Ver cantidad de documentos
uv run python -c "from rag_app.adapters.stores.chroma_adapter import ChromaAdapter; print(f'Documentos: {ChromaAdapter().count_documents()}')"

# Ver IDs de todos los documentos
uv run python -c "from rag_app.adapters.stores.chroma_adapter import ChromaAdapter; print(ChromaAdapter().get_all_document_ids())"
```

### Resetear la base de datos

```bash
# Modo interactivo (pide confirmación)
uv run python -m rag_app.scripts.reset_db

# Modo force (sin confirmación - útil para scripts)
uv run python -m rag_app.scripts.reset_db --force

# Modo verbose (muestra lista de documentos)
uv run python -m rag_app.scripts.reset_db --verbose

# Ver ayuda
uv run python -m rag_app.scripts.reset_db --help
```

### Re-ingestar documentos

Después de resetear, podés volver a cargar los documentos:

```bash
# Cargar desde Anses1.md
uv run python -m rag_app.scripts.setup_from_md

# Cargar desde URLs en leyes_config.json
uv run python -m rag_app.scripts.setup_db
```

---

## 📚 Estructura de Carpetas (Detallada)

```
rag_app/
  config/
    leyes_config.json      # Metadata de leyes a ingestar
    settings.py            # Configuración central (API keys, rutas, etc.)
  
  domain/
    models.py              # Modelos: Law, Chunk, QueryResult, etc.
  
  ports/
    chunker.py             # Interface para dividir documentos
    embedder.py            # Interface para generar embeddings
    vector_store.py        # Interface para bases vectoriales
    contextualizer.py      # Interface para construir contexto LLM
  
  adapters/
    chunkers/              # Implementaciones de chunking
    embedders/             # Implementaciones de embeddings (Gemini)
    stores/                # Implementaciones de almacenamiento (ChromaDB)
    contextualizers/       # Lógica de construcción de prompts
    http/                  # Adaptadores HTTP (FastAPI routers)
  
  services/
    ingestion_service.py   # Servicio de ingestión de documentos
    retrieval_service.py   # Servicio de búsqueda y recuperación
  
  pipelines/               # Orquestación de alto nivel
  
  scripts/
    setup_from_md.py       # Script de configuración inicial
    setup_db.py            # Script de ingestión desde URLs
  
  utils/
    logger.py              # Configuración de logging
    hashing.py             # Generación de content_hash
  
  tests/                   # Tests unitarios e integración
  
  api_main.py              # Punto de entrada FastAPI
  
front/
  components/              # Componentes React reutilizables
  services/                # Clients para API calls
  App.tsx                  # Aplicación principal
  types.ts                 # Definiciones de tipos TypeScript
```

### Descripción de Módulos Clave

#### `config/`
| Archivo             | Función                                                                                                                                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `settings.py`       | Configuración central. Carga variables desde `.env` (API keys, rutas, configuración de embeddings, base vectorial, etc.). |
| `leyes_config.json` | Metadata declarativa de las leyes a ingestar: fuente, URL, versión, tipo de documento, jurisdicción, etc.                              |

#### `domain/`
| Archivo     | Función                                                                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `models.py` | Define clases como `Law` (documento legal completo), `Chunk` (fragmento indexable), `QueryResult`, etc. Sin lógica específica; solo estructura. |

#### `ports/` (Interfaces / Abstracciones)
| Archivo             | Función                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `chunker.py`        | Interface para dividir documentos (`Law → list[Chunk]`).                                                           |
| `embedder.py`       | Interface para generar embeddings a partir de texto.                                                               |
| `vector_store.py`   | Interface para almacenar/buscar chunks en bases vectoriales.                                                       |
| `contextualizer.py` | Interface para armar el "contexto final" que verá el LLM (prompt builder, re-ranker, formateo de citas). |

#### `adapters/`
| Carpeta            | Contenido                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `chunkers/`        | Implementaciones: `HybridMarkdownChunker`, `ArticleChunker`, etc.                        |
| `embedders/`       | Implementaciones: `GeminiEmbedder`, etc.                                                 |
| `stores/`          | Implementaciones: `ChromaAdapter`, `PgVectorStore`, etc.                                 |
| `contextualizers/` | Lógica para construir prompts y generar respuestas con Gemini.                           |
| `http/`            | Adaptadores HTTP: `APIAdapter` (routers FastAPI), `SessionManager`.                      |

#### `services/`
| Archivo                | Función                                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `ingestion_service.py` | Toma una ley → chunk → embedding → guarda en base vectorial. Incluye versionado e idempotencia.                               |
| `retrieval_service.py` | Dada una consulta → busca los chunks relevantes → construye contexto → genera respuesta con LLM. |

---

---

## 📖 Uso

### Consultas de Ejemplo

Una vez que la aplicación esté corriendo, podés hacer preguntas como:

- *"¿Cuáles son los requisitos para la jubilación?"*
- *"Explicame el sistema de seguridad social argentino"*
- *"¿Qué documentación necesito para tramitar la jubilación?"*
- *"¿Cuál es la edad mínima para jubilarse?"*

### Endpoints de la API

- `GET /health` - Verificar estado del servidor
- `POST /api/v1/chat` - Enviar consulta al asistente
- `GET /api/v1/documents` - Listar documentos indexados
- `POST /api/v1/upload` - Subir nuevos documentos (en desarrollo)

Documentación completa en: http://localhost:8000/docs

---

## 🤝 Contribuciones

Este proyecto está en desarrollo activo. La arquitectura hexagonal facilita agregar nuevos adapters (embedders, chunkers, vector stores) sin modificar la lógica de negocio.

---

## 📝 Notas

- **Arquitectura Hexagonal:** Facilita testing y permite cambiar implementaciones (ej: de ChromaDB a PostgreSQL con pgvector) sin tocar el core.
- **Document-Level Retrieval:** Se recuperan leyes completas en lugar de fragmentos pequeños para mejor contexto.



