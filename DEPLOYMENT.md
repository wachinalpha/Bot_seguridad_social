# Guía de Deployment

Esta guía cubre las diferentes opciones para desplegar el Bot de Seguridad Social en producción.

## 📋 Tabla de Contenidos

- [Opciones de Deployment](#opciones-de-deployment)
- [Deployment con Docker](#deployment-con-docker)
- [Deployment en Cloud](#deployment-en-cloud)
- [Variables de Entorno](#variables-de-entorno)
- [Configuración de Producción](#configuración-de-producción)
- [Monitoreo y Logs](#monitoreo-y-logs)
- [Troubleshooting](#troubleshooting)

---

## Opciones de Deployment

### 1. Docker (Recomendado)
- ✅ Fácil de configurar
- ✅ Portable entre entornos
- ✅ Incluye todas las dependencias

### 2. Cloud Platforms
- **Google Cloud Run**: Serverless, auto-scaling
- **AWS ECS/Fargate**: Contenedores administrados
- **Azure Container Instances**: Deployment rápido
- **Railway/Render**: Deployment simplificado

### 3. VPS Tradicional
- DigitalOcean, Linode, AWS EC2
- Requiere configuración manual

---

## Deployment con Docker

### Dockerfile - Backend

Crear `rag_app/Dockerfile`:

```dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./
COPY requirements.txt ./

# Install Python dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile - Frontend

Crear `front/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### docker-compose.yml

Crear en la raíz del proyecto:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./rag_app
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./front
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    environment:
      - VITE_API_URL=http://backend:8000

volumes:
  data:
  chroma_db:
```

### Ejecutar con Docker Compose

```bash
# 1. Crear archivo .env en la raíz
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env

# 2. Build y ejecutar
docker-compose up -d

# 3. Ver logs
docker-compose logs -f

# 4. Detener
docker-compose down
```

---

## Deployment en Cloud

### Google Cloud Run

**1. Preparar proyecto:**

```bash
# Instalar gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Autenticar
gcloud auth login

# Crear proyecto
gcloud projects create bot-seguridad-social
gcloud config set project bot-seguridad-social
```

**2. Deploy Backend:**

```bash
cd rag_app

# Build y push imagen
gcloud builds submit --tag gcr.io/bot-seguridad-social/backend

# Deploy a Cloud Run
gcloud run deploy backend \
  --image gcr.io/bot-seguridad-social/backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=tu_api_key
```

**3. Deploy Frontend:**

```bash
cd ../front

# Build y push
gcloud builds submit --tag gcr.io/bot-seguridad-social/frontend

# Deploy
gcloud run deploy frontend \
  --image gcr.io/bot-seguridad-social/frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars VITE_API_URL=https://backend-xxx.run.app
```

### Railway.app (Más Simple)

**1. Conectar repositorio:**
- Ir a [railway.app](https://railway.app)
- Conectar cuenta de GitHub
- Seleccionar repositorio

**2. Configurar servicios:**
- Crear servicio "Backend" → Root directory: `rag_app`
- Crear servicio "Frontend" → Root directory: `front`

**3. Variables de entorno:**
- Backend: `GEMINI_API_KEY`
- Frontend: `VITE_API_URL` (URL del backend de Railway)

**4. Deploy:**
- Railway detecta Dockerfile automáticamente
- Push a `main` → auto-deploy

### AWS ECS/Fargate

**1. Crear repositorio ECR:**

```bash
aws ecr create-repository --repository-name bot-seguridad-backend
aws ecr create-repository --repository-name bot-seguridad-frontend
```

**2. Push imágenes:**

```bash
# Login a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag y push
docker tag backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/bot-seguridad-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/bot-seguridad-backend:latest
```

**3. Crear Task Definition y Service en ECS Console**

---

## Variables de Entorno

### Backend (.env)

```bash
# API Keys (REQUERIDO)
GEMINI_API_KEY=tu_api_key_aqui

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_TITLE="Legal RAG API"
API_VERSION=1.0.0
API_PREFIX=/api/v1

# CORS Origins (separados por coma)
API_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://tu-dominio.com

# Model Configuration
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=models/text-embedding-004
CACHE_TTL_MINUTES=60

# Database Paths
CHROMA_DB_PATH=./chroma_db
PROCESSED_DOCS_PATH=./data/processed

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```bash
# API URL
VITE_API_URL=http://localhost:8000

# O en producción:
VITE_API_URL=https://api.tu-dominio.com
```

---

## Configuración de Producción

### Seguridad

**1. HTTPS:**
- Usar certificados SSL (Let's Encrypt gratis)
- Configurar nginx como reverse proxy

**2. Rate Limiting:**

Agregar en `api_main.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/chat")
@limiter.limit("10/minute")
async def chat(request: Request, ...):
    ...
```

**3. Autenticación (opcional):**

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/v1/chat")
async def chat(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validar token
    ...
```

### Performance

**1. Caching:**
- Usar Redis para caché de respuestas
- Configurar cache headers en nginx

**2. Database:**
- Usar PostgreSQL con pgvector en lugar de ChromaDB local
- Configurar connection pooling

**3. CDN:**
- Servir frontend desde CDN (Cloudflare, CloudFront)

### Nginx Configuration

Crear `nginx.conf` para frontend:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    root /usr/share/nginx/html;
    index index.html;

    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://backend:8000/health;
    }
}
```

---

## Monitoreo y Logs

### Logging

**Configurar logging estructurado:**

```python
# rag_app/utils/logger.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

# Usar en producción
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
```

### Monitoreo

**1. Health Checks:**

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "vector_store": check_vector_store(),
            "embedder": check_embedder(),
        }
    }
```

**2. Métricas (Prometheus):**

```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response
```

**3. Error Tracking (Sentry):**

```python
import sentry_sdk

sentry_sdk.init(
    dsn="tu_sentry_dsn",
    environment="production",
)
```

---

## Troubleshooting

### Error: "Out of Memory"

**Solución:**
- Aumentar memoria del contenedor
- Optimizar batch size de embeddings
- Usar streaming para respuestas largas

### Error: "Connection Timeout"

**Solución:**
- Aumentar timeout de nginx/load balancer
- Configurar keep-alive connections
- Usar async/await correctamente

### Error: "ChromaDB Lock"

**Solución:**
- Usar PostgreSQL con pgvector en producción
- Configurar persistent volumes correctamente

### Logs de Debugging

```bash
# Docker logs
docker-compose logs -f backend

# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Railway logs
railway logs
```

---

## Checklist de Deployment

- [ ] Variables de entorno configuradas
- [ ] HTTPS habilitado
- [ ] Rate limiting configurado
- [ ] Health checks funcionando
- [ ] Logs estructurados
- [ ] Monitoreo configurado
- [ ] Backups de base de datos
- [ ] Documentación actualizada
- [ ] Tests pasando
- [ ] Performance testing realizado

---

## Soporte

Para problemas de deployment, abrir issue con etiqueta `deployment` 🚀
