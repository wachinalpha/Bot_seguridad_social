# Multi-stage Dockerfile for RAG Backend
# Python 3.13 with uv, FastAPI, ChromaDB, and Docling

FROM python:3.13-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies required by Docling
RUN apt-get update && apt-get install -y \
    # Docling dependencies (OpenCV, easyocr)
    libgl1-mesa-glx \
    libglib2.0-0 \
    # Utilities for healthchecks and debugging
    curl \
    wget \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Development stage
FROM base AS development

# Copy dependency files
COPY pyproject.toml ./
# Copy uv.lock if it exists (from parent directory)
COPY ../uv.lock ./uv.lock 2>/dev/null || true

# Install Python dependencies with uv
RUN uv sync --frozen || uv sync

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn (hot reload enabled)
CMD ["uv", "run", "uvicorn", "rag_app.api_main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser ../uv.lock ./uv.lock 2>/dev/null || true

# Install Python dependencies (no dev dependencies)
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn (production settings)
CMD ["uv", "run", "uvicorn", "rag_app.api_main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
