# Legal RAG API Documentation

## Overview

RESTful API for querying Argentine Social Security Laws using RAG (Retrieval Augmented Generation) with Google Gemini Context Caching.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**API Prefix**: `/api/v1`

## Authentication

Currently no authentication required (development mode).

## Endpoints

### System Endpoints

#### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "vector_store": "ok",
    "embedder": "ok",
    "contextualizer": "ok",
    "active_sessions": "5"
  }
}
```

### Chat Endpoints

#### Ask a Question
```http
POST /api/v1/chat
Content-Type: application/json
```

**Request Body**:
```json
{
  "query": "¿Cuáles son los requisitos para jubilarse?",
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "answer": "Los requisitos para jubilarse en Argentina incluyen...",
  "law_document": {
    "id": "ley_24241",
    "titulo": "Ley 24241 - Sistema Integrado de Jubilaciones y Pensiones",
    "url": "https://example.com/ley24241",
    "summary": "Norma que regula el sistema previsional argentino",
    "metadata": {
      "categoria": "Jubilaciones",
      "numero": "24241",
      "año": "1993"
    }
  },
  "confidence_score": 0.95,
  "cache_used": true,
  "cache_id": "cache_abc123",
  "response_time_ms": 234.5,
  "session_id": "session_xyz789"
}
```

**Session Management**:
- Omit `session_id` for one-off questions
- Provide `session_id` to maintain conversation context
- Sessions expire after 30 minutes of inactivity

### Document Endpoints

#### List All Documents
```http
GET /api/v1/documents
```

**Response**:
```json
{
  "documents": [
    {
      "id": "ley_24241",
      "titulo": "Ley 24241 - Sistema Integrado de Jubilaciones y Pensiones",
      "url": "https://example.com/ley24241",
      "summary": "Norma que regula el sistema previsional argentino",
      "categoria": "Jubilaciones"
    }
  ],
  "total": 1
}
```

#### Get Document Details
```http
GET /api/v1/documents/{law_id}
```

**Response**:
```json
{
  "id": "ley_24241",
  "titulo": "Ley 24241 - Sistema Integrado de Jubilaciones y Pensiones",
  "url": "https://example.com/ley24241",
  "file_path": "/data/processed/ley_24241.md",
  "summary": "Norma que regula el sistema previsional argentino",
  "metadata": {
    "numero": "24241",
    "año": "1993",
    "categoria": "Jubilaciones"
  }
}
```

#### Upload Document
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data
```

**Request**:
```
file: <binary file data>
```

**Supported formats**: PDF, DOCX, MD, TXT

**Response**:
```json
{
  "success": true,
  "message": "Documento procesado e indexado exitosamente",
  "document_id": "ley_27000",
  "titulo": "Ley 27000 - Nueva Ley de Seguridad Social"
}
```

**Note**: Upload functionality is currently a placeholder. Use ingestion scripts for production.

## Error Responses

All errors follow this format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "field": "additional_info"
  }
}
```

**HTTP Status Codes**:
- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error
- `501` - Not Implemented
- `503` - Service Unavailable

## CORS

CORS is enabled for:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

## Rate Limiting

Not currently implemented. Will be added in future versions.

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## TypeScript Integration

See the TypeScript client example in the implementation plan for frontend integration.

## Running the Server

```bash
# Using uv
cd rag_app
uv sync
uv run uvicorn api_main:app --reload --host 0.0.0.0 --port 8000

# Or with Python directly
python -m uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

## Architecture

The API follows **Hexagonal Architecture** (Ports & Adapters):

```
┌─────────────┐
│   FastAPI   │ ← HTTP Adapter
│  (api_main) │
└──────┬──────┘
       │
┌──────▼──────┐
│  Services   │ ← Application Layer
│  (Retrieval)│
└──────┬──────┘
       │
┌──────▼──────┐
│   Ports     │ ← Domain Layer
│  (Embedder, │
│   Store)    │
└──────┬──────┘
       │
┌──────▼──────┐
│  Adapters   │ ← Infrastructure
│  (Gemini,   │
│   ChromaDB) │
└─────────────┘
```

## Support

For issues or questions, contact the development team at Exdata.
