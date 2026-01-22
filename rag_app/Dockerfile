# Multi-stage Dockerfile for RAG Backend
# Python 3.13 with uv, FastAPI, ChromaDB, and Docling

FROM python:3.13-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies required by Docling
RUN apt-get update && apt-get install -y \
    # Docling dependencies (OpenCV, easyocr) - Debian Trixie compatible
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
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

# Copy entire project
COPY . /app/

# Set working directory
WORKDIR /app

# Copy dependency files if needed
# (pyproject.toml should already be there from COPY . /app/)

# Install Python dependencies with uv (will create lock if missing)
RUN cd rag_app && uv sync

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
COPY --chown=appuser:appuser rag_app/pyproject.toml ./

# Install Python dependencies (no dev dependencies)
# We need to install specifically from the copied toml
RUN uv pip install --system -r <(uv pip compile pyproject.toml)

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
