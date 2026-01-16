# Guía de Contribución

¡Gracias por tu interés en contribuir al Bot de Seguridad Social Argentina! 🎉

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Estándares de Código](#estándares-de-código)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Testing](#testing)

---

## Código de Conducta

Este proyecto adhiere a un Código de Conducta. Al participar, se espera que mantengas este código. Por favor reporta comportamientos inaceptables.

---

## Cómo Contribuir

### Reportar Bugs

Si encontrás un bug, por favor creá un issue con:

- **Título descriptivo**
- **Pasos para reproducir** el problema
- **Comportamiento esperado** vs **comportamiento actual**
- **Versión** de Python, Node.js, y dependencias relevantes
- **Logs** o mensajes de error (si aplica)

### Sugerir Mejoras

Para sugerir nuevas funcionalidades:

1. Verificá que no exista un issue similar
2. Creá un nuevo issue describiendo:
   - El problema que resuelve
   - La solución propuesta
   - Alternativas consideradas
   - Impacto en la arquitectura existente

### Contribuir Código

1. **Fork** el repositorio
2. **Creá una rama** desde `main`:
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
3. **Hacé tus cambios** siguiendo los estándares de código
4. **Escribí tests** para tu código
5. **Commiteá** con mensajes descriptivos
6. **Pusheá** a tu fork
7. **Abrí un Pull Request**

---

## Configuración del Entorno de Desarrollo

### Requisitos Previos

- Python 3.13+
- Node.js 18+
- uv (gestor de paquetes Python)
- Git

### Setup Inicial

```bash
# 1. Clonar el repositorio
git clone https://github.com/wachinalpha/Bot_seguridad_social.git
cd Bot_seguridad_social

# 2. Configurar Backend
cd rag_app
cp .env.example .env
# Editá .env y agregá tu GEMINI_API_KEY
uv sync

# 3. Configurar Frontend
cd ../front
npm install

# 4. Inicializar base de datos
cd ..
python -m rag_app.scripts.setup_from_md
```

### Ejecutar en Modo Desarrollo

**Terminal 1 - Backend:**
```bash
cd rag_app
python api_main.py
```

**Terminal 2 - Frontend:**
```bash
cd front
npm run dev
```

---

## Proceso de Pull Request

### Antes de Enviar

- [ ] El código sigue los estándares del proyecto
- [ ] Los tests pasan (`pytest` para backend, `npm test` para frontend)
- [ ] La documentación está actualizada
- [ ] Los commits tienen mensajes descriptivos
- [ ] No hay conflictos con `main`

### Formato de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(alcance): descripción breve

Descripción detallada (opcional)

Fixes #123
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato, punto y coma faltantes, etc.
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Mantenimiento, dependencias, etc.

**Ejemplos:**
```
feat(retrieval): agregar soporte para multi-law queries
fix(embedder): corregir encoding UTF-8 en documentos
docs(readme): actualizar instrucciones de instalación
```

### Revisión de Código

Tu PR será revisado por los mantenedores. Podemos solicitar cambios para:

- Mejorar la claridad del código
- Agregar tests faltantes
- Ajustar a los estándares del proyecto
- Optimizar performance

---

## Estándares de Código

### Python (Backend)

**Formateador:** Black
```bash
black rag_app/
```

**Linter:** Flake8
```bash
flake8 rag_app/
```

**Convenciones:**
- Nombres de variables/funciones: `snake_case`
- Nombres de clases: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Docstrings: Google Style
- Type hints en todas las funciones públicas

**Ejemplo:**
```python
def process_document(url: str, law_id: str) -> Tuple[str, str]:
    """Procesa un documento legal desde una URL.
    
    Args:
        url: URL del documento a procesar
        law_id: Identificador único de la ley
        
    Returns:
        Tupla con (file_path, markdown_content)
        
    Raises:
        ValueError: Si la URL es inválida
    """
    ...
```

### TypeScript (Frontend)

**Formateador:** Prettier (configurado en Vite)

**Convenciones:**
- Nombres de componentes: `PascalCase`
- Nombres de funciones/variables: `camelCase`
- Interfaces: `IPascalCase` o `PascalCase`
- Props: Definir con TypeScript interfaces

**Ejemplo:**
```typescript
interface ChatMessageProps {
  message: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  sender, 
  timestamp 
}) => {
  // ...
};
```

---

## Estructura del Proyecto

El proyecto sigue **Arquitectura Hexagonal (Ports & Adapters)**:

```
rag_app/
├── domain/          # Modelos de solución (sin dependencias externas)
├── ports/           # Interfaces/Abstracciones
├── adapters/        # Implementaciones concretas
│   ├── embedders/   # Gemini, OpenAI, etc.
│   ├── stores/      # ChromaDB, Pinecone, etc.
│   └── http/        # FastAPI routers
├── services/        # Lógica de solución
├── config/          # Configuración
└── scripts/         # Scripts de utilidad
```

### Principios de Diseño

1. **Dependency Inversion**: Los servicios dependen de ports (interfaces), no de adapters concretos
2. **Single Responsibility**: Cada módulo tiene una responsabilidad clara
3. **Open/Closed**: Abierto a extensión, cerrado a modificación
4. **Interface Segregation**: Interfaces pequeñas y específicas

### Agregar un Nuevo Adapter

**Ejemplo: Agregar soporte para OpenAI Embeddings**

1. Crear `rag_app/adapters/embedders/openai_embedder.py`:
```python
from rag_app.ports.embedder import EmbedderPort
from typing import List

class OpenAIEmbedder:
    """Implementación de EmbedderPort usando OpenAI API."""
    
    def embed_text(self, text: str) -> List[float]:
        # Implementación
        ...
```

2. Actualizar `rag_app/config/settings.py` si es necesario
3. Agregar tests en `rag_app/tests/test_openai_embedder.py`
4. Documentar en `rag_app/docs/TECHNICAL_ARCHITECTURE.md`

---

## Testing

### Backend (Python)

**Framework:** pytest

```bash
# Ejecutar todos los tests
pytest rag_app/tests/

# Con coverage
pytest --cov=rag_app rag_app/tests/

# Test específico
pytest rag_app/tests/test_retrieval_service.py
```

**Estructura de Tests:**
```python
def test_retrieval_service_query():
    # Arrange
    fake_embedder = FakeEmbedder()
    fake_store = FakeVectorStore()
    service = RetrievalService(fake_embedder, fake_store)
    
    # Act
    result = service.query("test question")
    
    # Assert
    assert result.answer is not None
    assert result.confidence_score > 0
```

### Frontend (React)

**Framework:** Vitest (configurar si es necesario)

```bash
npm test
```

---

## Áreas de Contribución

### 🔴 Alta Prioridad
EJEMPLO
- [ ] Mejorar cobertura de tests (objetivo: 80%+)
- [ ] Agregar autenticación de usuarios
- [ ] Implementar rate limiting en API
- [ ] Soporte para múltiples idiomas

### 🟡 Media Prioridad
EJEMPLO
- [ ] Agregar más adapters (OpenAI, Anthropic)
- [ ] Implementar caché de respuestas
- [ ] Mejorar UI/UX del frontend
- [ ] Agregar métricas y monitoring

### 🟢 Baja Prioridad

- [ ] Dockerización completa
- [ ] CI/CD pipeline
- [ ] Documentación en inglés
- [ ] Ejemplos de uso avanzado

---

## Recursos Útiles

- [Documentación Técnica](rag_app/docs/TECHNICAL_ARCHITECTURE.md)
- [API Documentation](rag_app/docs/API.md)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)

---

## Preguntas?

Si tenés dudas sobre cómo contribuir, no dudes en:

- Abrir un issue con la etiqueta `question`
- Contactar a los mantenedores
- Revisar issues existentes con la etiqueta `good first issue`

¡Gracias por contribuir! 🚀
