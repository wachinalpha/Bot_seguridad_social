# Quick Start - Bot Seguridad Social

Guía rápida para poner en marcha el sistema RAG con FastAPI + React.

## 🚀 Paso a Paso Rápido

### 1. Configurar API Key

```bash
# Crear archivo .env en rag_app/
cd rag_app
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env
```

### 2. Instalar Dependencias con uv

```bash
# uv instalará automáticamente desde pyproject.toml
uv sync
```

O si preferís pip tradicional:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar Setup con Anses1.md

```bash
# Desde el root del proyecto
cd ..
python -m rag_app.scripts.setup_from_md
```

Este script:
- ✅ Lee `rag_app/Anses1.md` (o `Documentos_Anses/Anses1.md`)
- ✅ Lo copia a `data/processed/`
- ✅ Genera embedding con Gemini
- ✅ Lo indexa en ChromaDB

### 4. Correr el Backend (FastAPI)

```bash
cd rag_app
python api_main.py
```

El backend estará disponible en:
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs

### 5. Correr el Frontend (React)

En otra terminal:

```bash
cd front
npm install
npm run dev
```

El frontend estará disponible en http://localhost:5173

## 📝 Consultas de Ejemplo

Una vez en la aplicación web, podés hacer preguntas como:
- "¿Cuáles son los requisitos para la jubilación?"
- "Explicame el sistema de seguridad social"
- "¿Qué documentación necesito para tramitar la jubilación?"

## 🔧 Troubleshooting

### Error: "Could not find Anses1.md"
El script busca en dos ubicaciones:
- `rag_app/Anses1.md`
- `Documentos_Anses/Anses1.md`

Asegurate que el archivo esté en alguna de estas ubicaciones.

### Error: "GEMINI_API_KEY not found"
Verificá que el archivo `.env` existe en `rag_app/` con tu API key.

### Error: "Port 8000 already in use"
Matá el proceso que está usando el puerto:
```bash
lsof -ti:8000 | xargs kill -9
```

## 💡 Cuando las URLs vuelvan

Cuando las páginas del gobierno estén disponibles nuevamente, podés usar el script original:

```bash
python -m rag_app.scripts.setup_db
```

Este procesará las URLs configuradas en `config/leyes_config.json`.
