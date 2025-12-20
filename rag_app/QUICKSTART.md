# Quick Start con Anses1.md (Offline Mode)

Como las páginas del gobierno están caídas, usa este método para probar el sistema con el archivo Markdown que ya tenés.

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
python -m rag_app.scripts.setup_from_md
```

Este script:
- ✅ Lee `rag_app/Anses1.md` (o `Documentos_Anses/Anses1.md`)
- ✅ Lo copia a `data/processed/`
- ✅ Genera embedding con Gemini
- ✅ Lo indexa en ChromaDB

### 4. Probar el Sistema

```bash
# Test de performance
python -m rag_app.tests.audit_performance

# Interfaz web
streamlit run rag_app/main.py
```

## 📝 Consultas de Ejemplo

Una vez en el UI de Streamlit, podés hacer preguntas como:
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

## 💡 Cuando las URLs vuelvan

Cuando las páginas del gobierno estén disponibles nuevamente, podés usar el script original:

```bash
python -m rag_app.scripts.setup_db
```

Este procesará las URLs configuradas en `config/leyes_config.json`.
