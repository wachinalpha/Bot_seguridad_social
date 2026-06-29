"""FastAPI application entry point for Legal RAG API.

This module creates and configures the FastAPI application with:
- CORS middleware for frontend communication
- API routers for all endpoints
- Dependency injection for services
- Error handling and logging
"""
import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from contextlib import asynccontextmanager

# Add parent directory to path (same as main.py)
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_app.config.settings import settings
from rag_app.utils.logger import configure_logging
from rag_app.adapters.model_factories import create_retrieval_service
from rag_app.adapters.http.api_adapter import APIAdapter
from rag_app.adapters.http.session_manager import SessionManager

# Configure logging
configure_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global service instances (initialized during startup)
api_adapter: APIAdapter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Initializes services on startup and cleans up on shutdown.
    """
    global api_adapter
    
    # Startup
    logger.info("Starting Legal RAG API...")
    logger.info(f"Environment: {settings.api_title} v{settings.api_version}")
    
    try:
        # Initialize services with dependency injection
        logger.info("Initializing services...")
        retrieval_service = create_retrieval_service()
        vector_store = retrieval_service.vector_store
        
        document_service = None
        
        session_manager = SessionManager(session_timeout_minutes=30)
        
        # Create API adapter
        api_adapter = APIAdapter(
            retrieval_service=retrieval_service,
            document_service=document_service,
            session_manager=session_manager
        )
        
        # Register routes immediately after adapter creation
        # Health check at root level (no prefix)
        app.include_router(
            api_adapter.router,
            prefix="", 
            tags=["Health"]
        )
        
        # API v1 routes with prefix
        app.include_router(
            api_adapter.router,
            prefix=settings.api_prefix,
            tags=["API v1"]
        )
        
        logger.info("✅ All services initialized successfully")
        logger.info(
            f"🧠 Models: embedding={settings.active_embedding_provider}/{settings.active_embedding_model}, "
            f"generation={settings.active_generation_provider}/{settings.active_generation_model}"
        )
        logger.info(f"📊 Indexed documents: {vector_store.count_documents()}")
        logger.info(f"🌐 Server ready at http://{settings.api_host}:{settings.api_port}")
        logger.info(f"📖 API docs at http://{settings.api_host}:{settings.api_port}/docs")
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Legal RAG API...")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    **Legal RAG API** for querying Argentine Social Security Laws.
    
    ## Features
    - 🤖 AI-powered legal question answering
    - 📚 Document-level retrieval (full law context)
    - 💬 Conversational sessions with history
    
    ## Architecture
    Built with Hexagonal Architecture (Ports & Adapters) using:
    - Configurable AI providers (Gemini/NVIDIA)
    - ChromaDB (Vector Store)
    - External corpus published by anses-corpus
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"type": type(exc).__name__}
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "api_main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
