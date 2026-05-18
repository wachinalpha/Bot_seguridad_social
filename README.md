# Bot Seguridad Social Argentina

Bot RAG para responder consultas de seguridad social de ANSES.

Este repo ya no parsea fuentes legales ni genera Markdown desde URLs. Esa responsabilidad vive en `anses-corpus`, que publica un corpus versionado. Este repo consume ese corpus, lo indexa en ChromaDB y sirve la API/backend/frontend.

## Repos

- app: `wachinalpha/Bot_seguridad_social`
- corpus: `wachinalpha/anses-corpus`

## Arquitectura

```text
Bot_seguridad_social/
├── data/
│   ├── corpora/
│   │   └── v1/
│   │       ├── manifest.json
│   │       ├── documents.json
│   │       └── documents/
│   └── chroma_db/
│       └── v1/
├── rag_app/
└── front/
```

- `data/corpora/<version>`: corpus descargado o copiado desde `anses-corpus`
- `data/chroma_db/<version>`: indice vectorial local, reconstruible

## Flujo

### 0. Requisitos

- Docker y Docker Compose
- `GEMINI_API_KEY` en `.env`
- `GITHUB_TOKEN` si `anses-corpus` es privado

### 1. Exportar token de GitHub si el corpus es privado

```bash
export GITHUB_TOKEN=tu_token
```

### 2. Descargar el corpus publicado

```bash
docker compose run --rm -e GITHUB_TOKEN=$GITHUB_TOKEN corpus-tools \
  uv run python /app/rag_app/scripts/fetch_corpus.py \
  --version v1 \
  --repo wachinalpha/anses-corpus
```

### 3. Indexar el corpus

```bash
docker compose run --rm corpus-tools \
  uv run python /app/rag_app/scripts/index_corpus.py --version v1
```

### 4. Levantar backend + frontend

```bash
docker compose up --build
```

### 5. Verificar API

```bash
curl http://localhost:8000/health
```

### 6. Probar una consulta

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"Quienes pueden cobrar asignaciones familiares?"}'
```

### Alternativa: corpus ya descargado localmente

Si ya tenes el corpus local, copialo a:

```text
data/corpora/v1/
```

Este repo versiona `data/corpora/v1` para facilitar demos y pruebas.

## Variables de entorno importantes

- `CORPUS_VERSION`: version activa del corpus, por ejemplo `v1`
- `CORPUS_STORAGE_PATH`: raiz local de corpora, por defecto `data/corpora`
- `CHROMA_DB_PATH`: raiz de indices vectoriales, por defecto `data/chroma_db`
- `GITHUB_TOKEN`: necesario para descargar releases de `anses-corpus` si el repo es privado

## Comandos utiles

### Descargar corpus

```bash
docker compose run --rm -e GITHUB_TOKEN=$GITHUB_TOKEN corpus-tools \
  uv run python /app/rag_app/scripts/fetch_corpus.py \
  --version v1 \
  --repo wachinalpha/anses-corpus
```

### Indexar corpus

```bash
docker compose run --rm corpus-tools \
  uv run python /app/rag_app/scripts/index_corpus.py --version v1
```

### Resetear indice

```bash
docker compose run --rm corpus-tools \
  uv run python /app/rag_app/scripts/reset_db.py --force
```

### Levantar servicios

```bash
docker compose up --build
```

### Levantar servicios en background

```bash
docker compose up --build -d
```

### Ver logs del backend

```bash
docker compose logs -f backend
```

### Ver logs del frontend

```bash
docker compose logs -f frontend
```

### Bajar servicios

```bash
docker compose down
```

### Borrar volumen de la venv del backend

```bash
docker volume rm bot_seguridad_social_backend_venv
```

## Desarrollo

### Reconstruir el indice para una version

```bash
docker compose run --rm corpus-tools uv run python /app/rag_app/scripts/reset_db.py --force
docker compose run --rm corpus-tools uv run python /app/rag_app/scripts/index_corpus.py --version v1
```

### Cambiar de version

```bash
CORPUS_VERSION=v2 docker compose run --rm -e GITHUB_TOKEN=$GITHUB_TOKEN corpus-tools \
  uv run python /app/rag_app/scripts/fetch_corpus.py \
  --version v2 \
  --repo wachinalpha/anses-corpus

CORPUS_VERSION=v2 docker compose run --rm corpus-tools \
  uv run python /app/rag_app/scripts/index_corpus.py --version v2

CORPUS_VERSION=v2 docker compose up --build
```

## Limpieza

Las carpetas legacy `data/processed` y `data/corpus_raw` ya no forman parte del flujo. El repo usa:

- `data/corpora/`
- `data/chroma_db/`
- `data/logs/`

## Repo productor del corpus

La generacion del corpus vive en un repo separado:

- `anses-corpus`

Ese repo:
- parsea fuentes
- normaliza a Markdown
- genera `manifest.json` y `documents.json`
- genera `failed_documents.json`
- publica zips versionados en GitHub Releases
