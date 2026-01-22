from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),  # Explicitly rag_app/.env
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields like groq_key
    )
    
    # API Keys
    gemini_api_key: str
    
    # Model Configuration
    embedding_model: str = "models/text-embedding-004"
    llm_model: str = "gemini-2.5-flash"  # Gemini 2.5 con soporte completo de caching
    cache_ttl_minutes: int = 60
    
    # Paths (support both relative and absolute for Docker compatibility)
    base_dir: Path = Path(__file__).parent.parent.parent
    processed_docs_path: str = "data/processed"  # Can be overridden with absolute path
    chroma_db_path: str = "data/chroma_db"  # Can be overridden with absolute path
    corpus_raw_path: str = "data/corpus_raw"  # Source documents for traceability
    
    # Corpus Versioning for ChromaDB collection isolation
    corpus_version: str = "v1"
    
    # ChromaDB Configuration
    chroma_collection_name: str = "legal_documents"  # Base name, will be prefixed with version
    
    # Retrieval Configuration
    top_k_results: int = 3
    
    # Gemini API Configuration
    max_retries: int = 3
    request_timeout: int = 30
    
    # API Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    api_prefix: str = "/api/v1"
    api_title: str = "Legal RAG API"
    api_version: str = "1.0.0"
    
    @property
    def chroma_collection_name_versioned(self) -> str:
        """Get versioned collection name for ChromaDB isolation."""
        return f"{self.chroma_collection_name}_{self.corpus_version}"
    
    @property
    def processed_docs_path_resolved(self) -> Path:
        """Resolve processed docs path (supports both relative and absolute)."""
        path = Path(self.processed_docs_path)
        if path.is_absolute():
            return path
        return self.base_dir / path
    
    @property
    def chroma_db_path_resolved(self) -> Path:
        """Resolve ChromaDB path (supports both relative and absolute)."""
        path = Path(self.chroma_db_path)
        if path.is_absolute():
            return path
        return self.base_dir / path
    
    @property
    def corpus_raw_path_resolved(self) -> Path:
        """Resolve corpus raw path (supports both relative and absolute)."""
        path = Path(self.corpus_raw_path)
        if path.is_absolute():
            return path
        return self.base_dir / path
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.processed_docs_path_resolved.mkdir(parents=True, exist_ok=True)
        self.chroma_db_path_resolved.mkdir(parents=True, exist_ok=True)
        self.corpus_raw_path_resolved.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
