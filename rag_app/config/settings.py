from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # API Keys
    gemini_api_key: str
    
    # Model Configuration
    embedding_model: str = "models/text-embedding-004"
    llm_model: str = "models/gemini-1.5-pro"
    cache_ttl_minutes: int = 60
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    processed_docs_path: Path = base_dir / "data" / "processed"
    chroma_db_path: Path = base_dir / "data" / "chroma_db"
    
    # ChromaDB Configuration
    chroma_collection_name: str = "legal_documents"
    
    # Retrieval Configuration
    top_k_results: int = 3
    
    # Gemini API Configuration
    max_retries: int = 3
    request_timeout: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.processed_docs_path.mkdir(parents=True, exist_ok=True)
        self.chroma_db_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
