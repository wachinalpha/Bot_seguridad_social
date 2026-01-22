#!/bin/bash
# Script de verificación de instalación

echo "🔍 Verificando instalación del Legal AI RAG..."
echo ""

# Check Python version
echo "✓ Python version:"
python --version
echo ""

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "✓ uv está instalado:"
    uv --version
else
    echo "⚠️  uv no está instalado (opcional)"
fi
echo ""

# Check dependencies
echo "✓ Dependencias instaladas:"
python -c "import google.generativeai; print('  - google-generativeai:', google.generativeai.__version__)"
python -c "import streamlit; print('  - streamlit:', streamlit.__version__)"
python -c "import chromadb; print('  - chromadb:', chromadb.__version__)"
python -c "import docling; print('  - docling:', docling.__version__)"
echo ""

# Check for .env file
if [ -f "rag_app/.env" ]; then
    echo "✓ Archivo .env encontrado"
    if grep -q "GEMINI_API_KEY=" rag_app/.env; then
        echo "  API key configurada"
    else
        echo "  ⚠️  GEMINI_API_KEY no configurado en .env"
    fi
else
    echo "⚠️  Archivo .env no encontrado en rag_app/"
    echo "   Crealo con: cd rag_app && echo 'GEMINI_API_KEY=tu_key' > .env"
fi
echo ""

# Check for Anses1.md
if [ -f "rag_app/Anses1.md" ]; then
    echo "✓ Anses1.md encontrado en rag_app/"
elif [ -f "Documentos_Anses/Anses1.md" ]; then
    echo "✓ Anses1.md encontrado en Documentos_Anses/"
else
    echo "⚠️  Anses1.md no encontrado"
fi
echo ""

echo "==================================="
echo "Próximos pasos:"
echo "1. Si no tenés .env: cd rag_app && echo 'GEMINI_API_KEY=tu_key' > .env"
echo "2. Ejecutar setup: python -m rag_app.scripts.setup_from_md"
echo "3. Probar: python -m rag_app.tests.audit_performance"
echo "4. Lanzar UI: streamlit run rag_app/main.py"
echo "==================================="
