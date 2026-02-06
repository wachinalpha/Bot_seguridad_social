# Librería de Patrones

Este documento registra los patrones de diseño y desarrollo estandarizados en el proyecto. El objetivo es mantener consistencia y facilitar el onboarding.

## 1. Arquitectura Hexagonal (Ports & Adapters)

**Contexto:** El core del negocio (`rag_app`) debe ser independiente de frameworks externos (API, DB, AI providers).

**Patrón:**
- **Domain:** Modelos puros (Pydantic/Dataclasses) sin lógica de infraestructura.
- **Ports:** Interfaces (Protocol) definidas en `ports/` que declaran *qué* necesitamos.
- **Adapters:** Implementaciones concretas en `adapters/` que definen *cómo* lo hacemos.
- **Services:** Lógica de negocio que orquesta puertos. Inyección de dependencias en `__init__`.

**Ejemplo:**
`RetrievalService` depende de `EmbedderPort`, no de `OpenAIEmbedder`.

## 2. Configuración Tipada

**Contexto:** Evitar `os.environ.get()` dispersos y strings mágicos.

**Patrón:**
Usar Pydantic `BaseSettings` para cargar y validar variables de entorno al inicio.

**Ejemplo:**
```python
class Settings(BaseSettings):
    openai_api_key: SecretStr
    environment: str = "development"
```

## 3. RAG Pipeline: Ingestión vs Recuperación

**Contexto:** Clarificar la separación de fases en RAG.

**Patrón:**
- **Ingestión (Offline/Async):** Carga documentos, chunquea y guarda en VectorDB. Se ejecuta bajo demanda (scripts).
- **Recuperación (Online/Sync):** Recibe query, busca en VectorDB y genera respuesta. Se ejecuta en tiempo real (API).

## 4. Gestión de Errores

**Contexto:** La API no debe crashear ni exponer stack traces al usuario.

**Patrón:**
- Usar bloques `try/except` en la capa de adaptadores para capturar errores de librerías externas y relanzar excepciones de dominio.
- Usar exception handlers globales en FastAPI (`api_main.py`) para mapear excepciones de dominio a códigos HTTP (400, 404, 500).

## 5. Testing Strategy

**Contexto:** Tests confiables y rápidos.

**Patrón:**
- **Unitarios:** Mockear puertos. Probar lógica de dominio y servicios. Rápidos.
- **Integración:** Probar adaptadores reales con la API externa (usar `pytest.mark.integration`).

## 6. Herramientas y Scripts Disponibles

**Contexto:** Centralizar conocimiento sobre scripts de utilidad.

| Herramienta | Ubicación | Descripción |
|-------------|-----------|-------------|
| `manage.py` | Raíz | Task runner principal. Comandos: `setup`, `dev`, `context`, `test`. |
| `context_builder.py` | `tools/` | Genera `context_dump.txt` con todo el código para alimentar IAs. |
| `setup_from_md.py` | `rag_app/scripts/` | Ingesta documentos markdown a ChromaDB. |
| `reset_db.py` | `rag_app/scripts/` | Limpia y reinicializa la base de datos vectorial. |
| `bootstrap_env.py` | `rag_app/scripts/` | Configura variables de entorno iniciales. |

**Uso Rápido:**
```bash
py manage.py context   # Genera dump de contexto
py manage.py dev       # Inicia servidores
```
