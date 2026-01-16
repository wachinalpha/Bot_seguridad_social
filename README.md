# Bot Seguridad Social Argentina 🇦🇷

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Promotor de Seguridad Social basado en RAG (Retrieval Augmented Generation) para responder consultas sobre la seguridad social Argentina. Utiliza Google Gemini API con Context Caching, ChromaDB para almacenamiento vectorial, e IBM Docling para procesamiento de documentos.

## 📚 Documentación

- **[Inicio Rápido](rag_app/QUICKSTART.md)** - Guía rápida para comenzar en 5 minutos
- **[FAQ](FAQ.md)** - Preguntas frecuentes y respuestas
- **[Guía de Desarrollo](DEVELOPMENT.md)** - Flujo de trabajo y mejores prácticas
- **[Guía de Deployment](DEPLOYMENT.md)** - Opciones de despliegue en producción
- **[Arquitectura Técnica](rag_app/docs/TECHNICAL_ARCHITECTURE.md)** - Detalles de implementación
- **[API Documentation](rag_app/docs/API.md)** - Referencia de endpoints
- **[Cómo Contribuir](CONTRIBUTING.md)** - Guía para contribuidores
- **[Roadmap](ROADMAP.md)** - Plan de desarrollo futuro
- **[Changelog](CHANGELOG.md)** - Historial de versiones
- **[Security Policy](SECURITY.md)** - Política de seguridad

## 📋 Tabla de Contenidos

- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración](#-instalación-y-configuración)
  - [Backend (RAG App)](#1-backend-rag-app)
  - [Frontend (React + TypeScript)](#2-frontend-react--typescript)
- [Ejecución de la Aplicación](#-ejecución-de-la-aplicación)
- [Estructura de Carpetas](#-estructura-de-carpetas)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Troubleshooting](#-troubleshooting)

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

## 📦 Requisitos Previos

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

### 1. Backend (RAG App)

#### Paso 1.1: Clonar el repositorio (si aún no lo hiciste)

```bash
git clone https://github.com/wachinalpha/Bot_seguridad_social.git
cd Bot_seguridad_social
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
| `contextualizers/` | Lógica para construir prompts y aplicar Context Caching de Gemini.                       |
| `http/`            | Adaptadores HTTP: `APIAdapter` (routers FastAPI), `SessionManager`.                      |

#### `services/`
| Archivo                | Función                                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `ingestion_service.py` | Toma una ley → chunk → embedding → guarda en base vectorial. Incluye versionado e idempotencia.                               |
| `retrieval_service.py` | Dada una consulta → busca los chunks relevantes → construye contexto → genera respuesta con LLM. |

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Este proyecto está abierto a mejoras, correcciones de bugs, y nuevas funcionalidades.

### Cómo Contribuir

1. **Fork** el repositorio
2. **Crea una rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'feat: Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre un Pull Request**

Por favor lee nuestra [Guía de Contribución](CONTRIBUTING.md) para más detalles sobre:
- Estándares de código
- Proceso de desarrollo
- Arquitectura del proyecto
- Testing y debugging

### Código de Conducta

Este proyecto adhiere a un [Código de Conducta](CODE_OF_CONDUCT.md). Al participar, se espera que mantengas este código.

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 Bot Seguridad Social Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🔧 Troubleshooting

### Backend

#### Error: `GEMINI_API_KEY not found`
**Solución:** Verificá que el archivo `.env` existe en `rag_app/` y contiene tu API key:
```bash
cd rag_app
cat .env
```

#### Error: `Could not find Anses1.md`
**Solución:** El script `setup_from_md.py` busca en:
- `rag_app/Anses1.md`
- `Documentos_Anses/Anses1.md`

Asegurate que el archivo esté en una de estas ubicaciones.

#### Error: `Module 'rag_app' has no attribute...`
**Solución:** Ejecutá los scripts desde el **directorio raíz del proyecto** usando:
```bash
python -m rag_app.scripts.setup_from_md
```
No ejecutes directamente con `python rag_app/scripts/setup_from_md.py`.

#### Error: `Port 8000 already in use`
**Solución:** Cambiá el puerto en `api_main.py` o matá el proceso que está usando el puerto:
```bash
lsof -ti:8000 | xargs kill -9
```

### Frontend

#### Error: `npm install` falla
**Solución:** Verificá tu versión de Node.js:
```bash
node --version  # Debe ser >= 18
```

#### Error: `API connection failed`
**Solución:** Verificá que:
1. El backend esté corriendo en `http://localhost:8000`
2. CORS esté configurado correctamente en `api_main.py`
3. El archivo `services/api.ts` apunte a la URL correcta del backend

#### La app carga pero no responde
**Solución:** Abrí las DevTools del navegador (F12) y revisá la consola para errores. Verificá que el backend tenga documentos indexados:
```bash
# Verificar logs del backend buscando:
# "📊 Indexed documents: N"
```

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
- **Context Caching de Gemini:** Permite cachear documentos grandes (leyes completas) para reducir costos y latencia.
- **Document-Level Retrieval:** Se recuperan leyes completas en lugar de fragmentos pequeños para mejor contexto.



