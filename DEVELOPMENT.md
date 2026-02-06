# Guía de Desarrollo

Esta guía cubre el flujo de trabajo de desarrollo, herramientas, y mejores prácticas para contribuir al Bot de Seguridad Social.

## 📋 Tabla de Contenidos

- [Configuración del Entorno](#configuración-del-entorno)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Arquitectura del Código](#arquitectura-del-código)
- [Testing](#testing)
- [Debugging](#debugging)
- [Herramientas de Desarrollo](#herramientas-de-desarrollo)
- [Mejores Prácticas](#mejores-prácticas)

---

## Configuración del Entorno

### Requisitos

- **Python**: 3.13+ (verificar con `python --version`)
- **Node.js**: 18+ (verificar con `node --version`)
- **uv**: Gestor de paquetes Python ([instalar](https://github.com/astral-sh/uv))
- **Git**: Control de versiones
- **Editor**: VS Code recomendado (con extensiones Python y TypeScript)

### Setup Completo

```bash
# 1. Clonar repositorio
git clone https://github.com/wachinalpha/Bot_seguridad_social.git
cd Bot_seguridad_social

# 2. Configurar Python virtual environment
cd rag_app
uv sync  # Instala dependencias y crea .venv

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar GEMINI_API_KEY

# 4. Inicializar base de datos
cd ..
python -m rag_app.scripts.setup_from_md

# 5. Configurar frontend
cd front
npm install
```

### Extensiones VS Code Recomendadas

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss"
  ]
}
```

---

## Flujo de Trabajo

### 1. Crear una Nueva Feature

```bash
# Actualizar main
git checkout main
git pull origin main

# Crear rama de feature
git checkout -b feature/nombre-descriptivo

# Ejemplo:
git checkout -b feature/add-openai-embedder
```

### 2. Desarrollo Iterativo

**Backend (Python):**
```bash
cd rag_app

# Ejecutar con auto-reload
python api_main.py

# O con uvicorn directamente
uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (React):**
```bash
cd front

# Modo desarrollo con hot reload
npm run dev
```

### 3. Testing Durante Desarrollo

```bash
# Backend - ejecutar tests
cd rag_app
pytest tests/ -v

# Con coverage
pytest tests/ --cov=rag_app --cov-report=html

# Test específico
pytest tests/test_retrieval_service.py::test_query_success -v
```

### 4. Formateo y Linting

**Python:**
```bash
# Formatear código
black rag_app/

# Verificar estilo
flake8 rag_app/

# Type checking (opcional)
mypy rag_app/
```

**TypeScript:**
```bash
# Formatear con Prettier (configurado en Vite)
npm run format

# Lint
npm run lint
```

### 5. Commit y Push

```bash
# Agregar cambios
git add .

# Commit con mensaje descriptivo
git commit -m "feat(embedder): add OpenAI embedder adapter"

# Push a tu fork
git push origin feature/add-openai-embedder
```

### 6. Pull Request

1. Ir a GitHub y crear Pull Request
2. Completar template de PR
3. Esperar revisión de código
4. Hacer ajustes si es necesario
5. Merge cuando sea aprobado

---

## Arquitectura del Código

### Principios de Diseño

El proyecto sigue **Arquitectura Hexagonal (Ports & Adapters)**:

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER              │
│      (FastAPI / React Frontend)         │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        APPLICATION LAYER                │
│           (Services)                    │
│  • IngestionService                     │
│  • RetrievalService                     │
└──────────┬─────────────────┬────────────┘
           │                 │
    ┌──────▼──────┐   ┌─────▼────────┐
    │   DOMAIN    │   │    PORTS     │
    │  (Models)   │   │ (Interfaces) │
    └─────────────┘   └─────┬────────┘
                            │
                   ┌────────▼─────────┐
                   │    ADAPTERS      │
                   │ (Implementations)│
                   └──────────────────┘
```

### Reglas de Dependencia

1. **Domain** no depende de nada (solo stdlib)
2. **Ports** definen contratos (Protocols)
3. **Services** dependen de Ports, no de Adapters
4. **Adapters** implementan Ports
5. **Presentation** usa Services

### Ejemplo: Agregar un Nuevo Adapter

**Paso 1: Definir Port (si no existe)**

```python
# rag_app/ports/embedder.py
from typing import Protocol, List

class EmbedderPort(Protocol):
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        ...
```

**Paso 2: Implementar Adapter**

```python
# rag_app/adapters/embedders/openai_embedder.py
from typing import List
from rag_app.ports.embedder import EmbedderPort
import openai

class OpenAIEmbedder:
    """OpenAI embeddings adapter."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
```

**Paso 3: Usar en Service (Dependency Injection)**

```python
# rag_app/services/retrieval_service.py
from rag_app.ports.embedder import EmbedderPort

class RetrievalService:
    def __init__(self, embedder: EmbedderPort, ...):
        self.embedder = embedder  # Puede ser GeminiEmbedder u OpenAIEmbedder
```

**Paso 4: Configurar en Entry Point**

```python
# rag_app/api_main.py
from rag_app.adapters.embedders.openai_embedder import OpenAIEmbedder

# En lifespan startup:
embedder = OpenAIEmbedder(api_key=settings.openai_api_key)
retrieval_service = RetrievalService(embedder=embedder, ...)
```

---

## Testing

### Estructura de Tests

```
rag_app/tests/
├── __init__.py
├── conftest.py              # Fixtures compartidos
├── test_models.py           # Tests de domain models
├── test_retrieval_service.py
├── test_ingestion_service.py
└── adapters/
    ├── test_gemini_embedder.py
    └── test_chroma_adapter.py
```

### Escribir Tests

**Test Unitario (con Mocks):**

```python
# tests/test_retrieval_service.py
import pytest
from unittest.mock import Mock
from rag_app.services.retrieval_service import RetrievalService

def test_query_returns_answer():
    # Arrange
    mock_embedder = Mock()
    mock_embedder.embed_text.return_value = [0.1] * 768
    
    mock_store = Mock()
    mock_store.search.return_value = [fake_law_document()]
    
    mock_contextualizer = Mock()
    mock_contextualizer.generate_answer.return_value = "Test answer"
    
    service = RetrievalService(
        embedder=mock_embedder,
        vector_store=mock_store,
        contextualizer=mock_contextualizer
    )
    
    # Act
    result = service.query("test question")
    
    # Assert
    assert result.answer == "Test answer"
    mock_embedder.embed_text.assert_called_once_with("test question")
```

**Test de Integración (con API real):**

```python
# tests/test_integration.py
import pytest
from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder

@pytest.mark.integration
def test_gemini_embedder_real_api():
    embedder = GeminiEmbedder()
    result = embedder.embed_text("test")
    
    assert len(result) == 768
    assert all(isinstance(x, float) for x in result)
```

**Ejecutar Tests:**

```bash
# Todos los tests
pytest

# Solo unitarios (rápidos)
pytest -m "not integration"

# Solo integración
pytest -m integration

# Con coverage
pytest --cov=rag_app --cov-report=html
```

---

## Debugging

### Backend (Python)

**1. Logging:**

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detalle técnico")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error", exc_info=True)  # Con stack trace
```

**2. Debugger (pdb):**

```python
# Agregar breakpoint
import pdb; pdb.set_trace()

# O en Python 3.7+
breakpoint()
```

**3. VS Code Debugger:**

Crear `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "api_main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "cwd": "${workspaceFolder}/rag_app",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### Frontend (React)

**1. Console Logging:**

```typescript
console.log('Debug:', variable);
console.error('Error:', error);
console.table(arrayOfObjects);
```

**2. React DevTools:**

Instalar extensión de navegador: [React Developer Tools](https://react.dev/learn/react-developer-tools)

**3. Network Debugging:**

Usar DevTools → Network tab para inspeccionar requests a la API.

---

## Herramientas de Desarrollo

### Gestión de Base de Datos

```bash
# Ver documentos indexados
python -c "from rag_app.adapters.stores.chroma_adapter import ChromaAdapter; print(ChromaAdapter().count_documents())"

# Resetear base de datos
python -m rag_app.scripts.reset_db

# Re-ingestar documentos
python -m rag_app.scripts.setup_from_md
```

### API Testing

**Con curl:**

```bash
# Health check
curl http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Requisitos para jubilación?"}'
```

**Con HTTPie (más legible):**

```bash
http POST localhost:8000/api/v1/chat query="¿Requisitos para jubilación?"
```

**Swagger UI:**

Navegar a http://localhost:8000/docs para interfaz interactiva.

---

## Mejores Prácticas

### Python

1. **Type Hints siempre:**
   ```python
   def process(text: str) -> List[str]:
       ...
   ```

2. **Docstrings en Google Style:**
   ```python
   def function(arg1: str, arg2: int) -> bool:
       """Brief description.
       
       Args:
           arg1: Description of arg1
           arg2: Description of arg2
           
       Returns:
           Description of return value
       """
   ```

3. **Usar Path para rutas:**
   ```python
   from pathlib import Path
   file_path = Path("data") / "file.txt"
   ```

4. **Logging en lugar de print:**
   ```python
   logger.info(f"Processing {file_path}")  # ✅
   print(f"Processing {file_path}")        # ❌
   ```

### TypeScript/React

1. **Componentes funcionales con TypeScript:**
   ```typescript
   interface Props {
     message: string;
   }
   
   export const Component: React.FC<Props> = ({ message }) => {
     return <div>{message}</div>;
   };
   ```

2. **Hooks con tipos:**
   ```typescript
   const [state, setState] = useState<string>("");
   ```

3. **Async/await para API calls:**
   ```typescript
   const fetchData = async () => {
     try {
       const response = await fetch('/api/endpoint');
       const data = await response.json();
     } catch (error) {
       console.error('Error:', error);
     }
   };
   ```

### Git

1. **Commits pequeños y frecuentes**
2. **Mensajes descriptivos** (Conventional Commits)
3. **Branches por feature**
4. **Pull antes de push**

---

## Agentes de IA en este Proyecto

### Agentes de Desarrollo

Estos son asistentes de IA que ayudan a escribir código:

| Agente | Propósito | Configuración |
|--------|-----------|---------------|
| **Gemini/Antigravity** | Asistente principal de codificación | Lee `.agent/INSTRUCTIONS.md` |
| **GitHub Copilot** | Autocompletado de código | Configurar con `.github/copilot-instructions.md` si se usa |

Los agentes de desarrollo deben seguir las reglas definidas en `.agent/INSTRUCTIONS.md`.

### El Bot RAG (Producto)

El objetivo de este proyecto es construir un **chatbot de Seguridad Social** que:
1. Recibe preguntas de usuarios sobre ANSES.
2. Busca información relevante en una base de datos vectorial (ChromaDB).
3. Genera respuestas usando un LLM (Google Gemini).

Ver `rag_app/docs/TECHNICAL_ARCHITECTURE.md` para detalles de implementación.

### Workflows para Agentes

En `.agent/workflows/` hay guías paso a paso que los agentes pueden seguir:
- `dev_setup.md` - Configurar entorno de desarrollo
- `add_adapter.md` - Agregar un nuevo adapter (Hexagonal)

---

## Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

---

¿Preguntas? Abrí un issue con la etiqueta `question` 🙋‍♂️
