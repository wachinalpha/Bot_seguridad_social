# Instrucciones para Agentes de IA

Este archivo contiene reglas y contexto para agentes de IA (como Gemini, Copilot, Claude) que trabajan en este repositorio.

## Contexto del Proyecto

**Bot de Seguridad Social** es un chatbot RAG (Retrieval-Augmented Generation) que responde preguntas sobre seguridad social argentina (ANSES).

### Stack Tecnológico
- **Backend**: Python 3.13+, FastAPI, ChromaDB, Google Gemini API
- **Frontend**: React + TypeScript + Vite
- **Gestión de dependencias**: `uv` (backend), `npm` (frontend)

### Estructura Clave
```
Bot_seguridad_social/
├── rag_app/           # Backend (Arquitectura Hexagonal)
│   ├── adapters/      # Implementaciones concretas
│   ├── ports/         # Interfaces (Protocols)
│   ├── services/      # Lógica de negocio
│   └── domain/        # Modelos de dominio
├── front/             # Frontend React
├── data/              # Documentos fuente (leyes, resoluciones)
├── docs/              # Documentación técnica
└── tools/             # Scripts de utilidad
```

---

## Reglas de Desarrollo

### 1. Arquitectura
- **Seguir Arquitectura Hexagonal** (Ports & Adapters). Ver `docs/PATTERNS.md`.
- Los servicios (`services/`) dependen de interfaces (`ports/`), NO de implementaciones (`adapters/`).
- Usar inyección de dependencias en constructores.

### 2. Código Python
- **Type Hints obligatorios** en todas las funciones públicas.
- **Docstrings en Google Style** para clases y funciones públicas.
- Usar `pathlib.Path` en lugar de strings para rutas.
- Usar `logging` en lugar de `print()`.
- Formatear con `black`. Lint con `flake8`.

### 3. Código TypeScript/React
- Componentes funcionales con TypeScript.
- Hooks tipados (`useState<Type>()`).
- Async/await para llamadas API.

### 4. Documentación
- Registrar decisiones arquitectónicas importantes en `docs/adr/` usando la plantilla.
- Actualizar `CHANGELOG.md` para cambios significativos.
- No modificar `rag_app/domain/` sin documentar el cambio.

### 5. Fuentes Legales
- Los documentos legales están en `data/` y `Documentos_Anses/`.
- Son la fuente de verdad del dominio. **No inventar información legal**.
- Siempre citar la fuente cuando se generen respuestas.

---

## Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `py manage.py setup` | Instalar todas las dependencias |
| `py manage.py dev` | Iniciar servidores de desarrollo |
| `py manage.py context` | Generar `context_dump.txt` para IA |
| `py manage.py test` | Ejecutar tests del backend |

---

## Workflows Disponibles

Ver `.agent/workflows/` para guías paso a paso:
- `dev_setup.md` - Configurar entorno de desarrollo
- `add_adapter.md` - Agregar un nuevo adapter (Hexagonal)

---

## Equipo

- **Senior IA**: Lidera decisiones técnicas.
- **Junior IA**: Ejecuta tareas siguiendo patrones documentados.
- **Experto Legal**: Valida contenido de dominio (no programa).

Cuando trabajes con el Junior, sé explícito y referencia documentación existente.
