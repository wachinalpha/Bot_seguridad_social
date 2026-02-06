---
description: Cómo agregar un nuevo adapter siguiendo Arquitectura Hexagonal
---

# Workflow: Agregar un Nuevo Adapter

Este workflow te guía para agregar una nueva implementación de un puerto existente (ej: un nuevo embedder, un nuevo vector store).

## Contexto

En Arquitectura Hexagonal:
- **Port**: Interfaz que define QUÉ necesitamos (en `ports/`)
- **Adapter**: Implementación que define CÓMO lo hacemos (en `adapters/`)

## Ejemplo: Agregar OpenAI Embedder

### 1. Verificar que el Port Existe

Revisar `rag_app/ports/embedder.py`:

```python
from typing import Protocol, List

class EmbedderPort(Protocol):
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        ...
```

Si el port no existe, crearlo primero.

### 2. Crear el Adapter

Crear archivo `rag_app/adapters/embedders/openai_embedder.py`:

```python
from typing import List
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

### 3. Agregar Dependencia (si es nueva)

```bash
cd rag_app
uv add openai
```

### 4. Registrar en Entry Point

Editar `rag_app/api_main.py` para usar el nuevo adapter:

```python
from rag_app.adapters.embedders.openai_embedder import OpenAIEmbedder

# En lifespan/startup:
embedder = OpenAIEmbedder(api_key=settings.openai_api_key)
```

### 5. Agregar Tests

Crear `rag_app/tests/adapters/test_openai_embedder.py`:

```python
import pytest
from unittest.mock import Mock, patch

def test_embed_text_returns_floats():
    # Arrange
    with patch('openai.OpenAI') as mock_client:
        mock_client.return_value.embeddings.create.return_value = Mock(
            data=[Mock(embedding=[0.1] * 768)]
        )
        
        from rag_app.adapters.embedders.openai_embedder import OpenAIEmbedder
        embedder = OpenAIEmbedder(api_key="fake")
        
        # Act
        result = embedder.embed_text("test")
        
        # Assert
        assert len(result) == 768
        assert all(isinstance(x, float) for x in result)
```

### 6. Documentar la Decisión (ADR)

Crear `docs/adr/000X-add-openai-embedder.md` usando la plantilla.

## Checklist Final

- [ ] Adapter implementa la interfaz del Port
- [ ] Type hints en todas las funciones
- [ ] Docstrings en Google Style
- [ ] Tests unitarios con mocks
- [ ] Dependencia agregada a `pyproject.toml`
- [ ] ADR documentando la decisión
