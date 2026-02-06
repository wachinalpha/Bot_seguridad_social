---
description: Cómo configurar el entorno de desarrollo desde cero
---

# Workflow: Configurar Entorno de Desarrollo

Este workflow te guía para configurar el entorno de desarrollo completo.

## Prerrequisitos

- Python 3.13+ instalado (`py --version`)
- Node.js 18+ instalado (`node --version`)
- Git configurado

## Pasos

### 1. Clonar el Repositorio

```bash
git clone https://github.com/wachinalpha/Bot_seguridad_social.git
cd Bot_seguridad_social
```

### 2. Configurar Variables de Entorno

```bash
cd rag_app
copy .env.example .env
```

Editar `.env` y agregar:
- `GEMINI_API_KEY`: Tu API key de Google Gemini

### 3. Instalar Dependencias

// turbo
```bash
py manage.py setup
```

Esto instalará:
- Backend: dependencias Python via `uv sync`
- Frontend: dependencias Node via `npm install`

### 4. Inicializar Base de Datos (Opcional)

Si necesitas cargar documentos iniciales:

```bash
cd rag_app
py -m rag_app.scripts.setup_from_md
```

### 5. Iniciar Servidores de Desarrollo

// turbo
```bash
py manage.py dev
```

Esto abrirá:
- Backend: http://localhost:8000 (FastAPI + Swagger en /docs)
- Frontend: http://localhost:5173 (Vite dev server)

## Verificación

1. Abrir http://localhost:8000/docs - Deberías ver Swagger UI.
2. Abrir http://localhost:5173 - Deberías ver la interfaz del chat.
3. Hacer una pregunta de prueba en el chat.

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `python` no encontrado | Usar `py` en Windows |
| `uv` no encontrado | Se instalará automáticamente con `manage.py setup` |
| Error de API key | Verificar `.env` tiene `GEMINI_API_KEY` válida |
