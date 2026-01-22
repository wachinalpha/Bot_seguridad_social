#!/bin/bash
# Docker initialization script for Bot Seguridad Social
set -e

echo "🐳 Inicializando Bot Seguridad Social con Docker..."
echo ""

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    echo "   Instalá Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado o es muy antiguo"
    echo "   Asegurate de tener Docker Compose v2+"
    exit 1
fi

echo "✅ Docker y Docker Compose detectados"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creando .env desde template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Editá .env y agregá tu GEMINI_API_KEY"
    echo "   Archivo: $(pwd)/.env"
    echo ""
    echo "   Obtené tu API key en: https://aistudio.google.com/app/apikey"
    echo ""
    read -p "Presioná Enter cuando hayas configurado tu API key..."
fi

# Verify GEMINI_API_KEY is set
source .env
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_api_key_here" ]; then
    echo "❌ Error: GEMINI_API_KEY no está configurada en .env"
    exit 1
fi

echo "✅ GEMINI_API_KEY configurada"
echo ""

# Create data directories
echo "📁 Creando carpetas de datos..."
mkdir -p data/chroma_db data/processed data/logs
echo "✅ Carpetas creadas"
echo ""

# Build containers
echo "🔨 Building containers..."
docker compose build --progress=plain
echo "✅ Build completado"
echo ""

# Start services
echo "🚀 Iniciando servicios..."
docker compose up -d
echo "✅ Servicios iniciados"
echo ""

# Wait for backend to be healthy
echo "⏳ Esperando que backend esté ready..."
sleep 5

max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend ready"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Intento $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Error: Backend no respondió a tiempo"
    echo "   Ejecutá: docker compose logs backend"
    exit 1
fi

echo ""
echo "📚 Ejecutando ingesta inicial..."
docker compose run --rm ingest
echo "✅ Ingesta completada"
echo ""

echo "✨ Setup completo!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📖 Frontend: http://localhost:5173"
echo "  🔧 API Docs: http://localhost:8000/docs"
echo "  ❤️  Health:   http://localhost:8000/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Comandos útiles:"
echo "  • Ver logs:           docker compose logs -f"
echo "  • Resetear BD:        docker compose run --rm ingest python -m rag_app.scripts.reset_db --force"
echo "  • Detener servicios:  docker compose down"
echo ""
