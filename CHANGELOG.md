# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Planeado
- Autenticación de usuarios
- Rate limiting en API
- Caché de respuestas
- Métricas y monitoring

---

## [0.1.0] - 2025-12-27

### Agregado
- ✨ Implementación inicial del sistema RAG con arquitectura hexagonal
- 🤖 Integración con Google Gemini API (embeddings y generación)
- 💾 Soporte para ChromaDB como vector store
- 📄 Procesamiento de documentos con IBM Docling
- 🔄 Context Caching de Gemini para optimización de costos
- 🌐 API REST con FastAPI
- ⚛️ Frontend React con TypeScript
- 📚 Documentación técnica completa
- 🧪 Tests básicos de integración
- 🔧 Scripts de setup y gestión de base de datos

### Backend Features
- Arquitectura hexagonal (Ports & Adapters)
- Document-level RAG (leyes completas como contexto)
- Graceful degradation para Free Tier de Gemini
- Content hashing para cache invalidation
- Session management para conversaciones
- CORS configurado para desarrollo local
- Logging estructurado
- Manejo de errores robusto

### Frontend Features
- Interfaz de chat conversacional
- Integración con API backend
- Visualización de metadata de respuestas
- Indicadores de cache usage
- Responsive design

### Documentación
- README.md con guía completa de instalación
- QUICKSTART.md para inicio rápido
- TECHNICAL_ARCHITECTURE.md con detalles de implementación
- API.md con documentación de endpoints
- CONTRIBUTING.md con guías para contribuidores
- CODE_OF_CONDUCT.md
- LICENSE (MIT)

### Infraestructura
- Configuración con Pydantic Settings
- Variables de entorno con .env
- Gestión de dependencias con uv
- .gitignore configurado
- Estructura de proyecto modular

---

## Tipos de Cambios

- `Agregado` para nuevas funcionalidades
- `Cambiado` para cambios en funcionalidades existentes
- `Deprecado` para funcionalidades que serán removidas
- `Removido` para funcionalidades removidas
- `Corregido` para corrección de bugs
- `Seguridad` para vulnerabilidades

---

## Versionado

Este proyecto usa [Semantic Versioning](https://semver.org/):

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible con versiones anteriores
- **PATCH**: Correcciones de bugs compatibles con versiones anteriores

---

## Links

- [Unreleased]: Cambios en desarrollo
- [0.1.0]: Versión inicial - 2025-12-27
