# 🔧 Documentación Técnica

Esta guía es para desarrolladores que necesitan entender cómo funciona el sistema por dentro.

---

## Arquitectura General

El proyecto usa **Arquitectura Hexagonal** (también llamada "Ports & Adapters"). La idea es simple: separar la lógica de negocio de los detalles técnicos.

```
┌─────────────────────────────────────────┐
│           FRONTEND (React)              │
│         Puerto 5173 (desarrollo)        │
└──────────────────┬──────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────┐
│           BACKEND (FastAPI)             │
│            Puerto 8000                  │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │         SERVICIOS               │    │
│  │  • RetrievalService             │    │
│  │  • IngestionService             │    │
│  └──────────────┬──────────────────┘    │
│                 │                       │
│  ┌──────────────▼──────────────────┐    │
│  │         ADAPTADORES             │    │
│  │  • GeminiEmbedder (embeddings)  │    │
│  │  • ChromaAdapter (vector DB)    │    │
│  │  • GeminiCacheManager (LLM)     │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## Estructura de Carpetas

```
rag_app/
├── config/           # Configuración (settings.py, .env)
├── domain/           # Modelos de datos (LawDocument, QueryResult)
├── ports/            # Interfaces/Contratos (abstractos)
├── adapters/         # Implementaciones concretas
│   ├── embedders/    # Generación de embeddings (Gemini)
│   ├── stores/       # Base de datos vectorial (ChromaDB)
│   ├── contextualizers/  # Manejo de contexto LLM
│   └── http/         # Rutas de la API (FastAPI)
├── services/         # Lógica de negocio
├── scripts/          # Scripts de utilidad (setup, reset)
└── api_main.py       # Punto de entrada
```

---

## Flujo de una Consulta

Cuando un usuario pregunta "¿Requisitos para jubilarse?":

1. **Frontend** envía POST a `/api/v1/chat`
2. **RetrievalService** recibe la consulta
3. **GeminiEmbedder** convierte la pregunta en un vector (embedding)
4. **ChromaAdapter** busca documentos similares en la base vectorial
5. **GeminiCacheManager** lee el documento completo y lo pasa al LLM
6. **Gemini API** genera la respuesta basándose en el documento
7. La respuesta vuelve al frontend

---

## Endpoints de la API

### `GET /health`
Verificar que el servidor esté funcionando.

### `POST /api/v1/chat`
Enviar una pregunta al bot.

**Request:**
```json
{
  "query": "¿Requisitos para jubilarse?",
  "session_id": "opcional-para-conversaciones"
}
```

**Response:**
```json
{
  "answer": "Los requisitos son...",
  "law_document": { "id": "ley_xxx", "titulo": "..." },
  "confidence_score": 0.95,
  "cache_used": true,
  "response_time_ms": 1234
}
```

### `GET /api/v1/documents`
Listar todos los documentos indexados.

**Documentación interactiva:** `http://localhost:8000/docs`

---

## Base de Datos Vectorial

Usamos **ChromaDB** para almacenar embeddings de los documentos.

**Ubicación:** `data/chroma_db/`

### Comandos útiles

```powershell
# Ver cuántos documentos hay
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -c "from rag_app.adapters.stores.chroma_adapter import ChromaAdapter; print(ChromaAdapter().count_documents())"

# Resetear la base de datos
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.reset_db --force

# Recargar documentos
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.setup_from_md
```

---

## Agregar un Nuevo Adapter

Si querés cambiar de proveedor (ej: de Gemini a OpenAI):

1. Creá un nuevo archivo en `adapters/embedders/openai_embedder.py`
2. Implementá la misma interfaz que `GeminiEmbedder`
3. Cambiá la instanciación en `api_main.py`

```python
# Antes
embedder = GeminiEmbedder()

# Después
embedder = OpenAIEmbedder()
```

Los servicios no cambian porque dependen de la interfaz, no de la implementación concreta.

---

## Deployment con Docker

### Archivo Dockerfile (Backend)

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Ejecutar

```bash
docker build -t bot-seguridad-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=tu_key bot-seguridad-backend
```

---

## Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `GEMINI_API_KEY` | API Key de Google Gemini | Sí |
| `API_HOST` | Host del servidor (default: 0.0.0.0) | No |
| `API_PORT` | Puerto del servidor (default: 8000) | No |
| `LLM_MODEL` | Modelo de Gemini (default: gemini-2.5-flash) | No |

---

## Testing

```bash
# Ejecutar todos los tests
cd rag_app
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=rag_app
```

---

## Logs

Los logs se imprimen por consola con el formato:
```
2025-12-27 13:35:09 - rag_app.services.retrieval_service - INFO - Processing query...
```

Niveles: DEBUG, INFO, WARNING, ERROR

Para cambiar el nivel, modificar `utils/logger.py`.

---

## Recursos Externos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [Arquitectura Hexagonal](https://alistair.cockburn.us/hexagonal-architecture/)
