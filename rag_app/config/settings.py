from pathlib import Path
import re

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_EMBEDDING_MODELS = {
    "gemini": "models/gemini-embedding-001",
    "nvidia": "nvidia/llama-nemotron-embed-1b-v2",
}

DEFAULT_GENERATION_MODELS = {
    "gemini": "gemini-2.5-flash",
    "nvidia": "nvidia/nemotron-3-nano-30b-a3b",
}

LEGACY_CHROMA_PROVIDER = "gemini"
LEGACY_CHROMA_MODEL = "models/gemini-embedding-001"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields like groq_key
    )
    
    # API Keys
    gemini_api_key: str | None = None
    nvidia_api_key: str | None = None
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    
    # Model Configuration
    embedding_provider: str = "gemini"
    embedding_model: str | None = None
    generation_provider: str = "gemini"
    generation_model: str | None = None
    llm_model: str | None = None  # Legacy alias kept for existing .env files
    generation_temperature: float = 0.2
    generation_max_tokens: int = 2048
    nvidia_embedding_truncate: str = "NONE"
    nvidia_embedding_dimensions: int | None = None
    nvidia_embedding_query_input_type: str = "query"
    nvidia_embedding_document_input_type: str = "passage"
    
    # Paths (support both relative and absolute for Docker compatibility)
    base_dir: Path = Path(__file__).parent.parent.parent
    corpus_storage_path: str = "data/corpora"  # Can be overridden with absolute path
    chroma_db_path: str = "data/chroma_db"  # Can be overridden with absolute path
    prompt_config_path: str = "rag_app/config/system_prompt.yml"
    
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
        return self.chroma_collection_name_for()

    @staticmethod
    def normalize_provider(provider: str | None) -> str:
        return (provider or "").strip().lower()

    @staticmethod
    def sanitize_model_id(value: str) -> str:
        sanitized = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-._").lower()
        return sanitized or "default"

    def default_embedding_model_for(self, provider: str | None = None) -> str:
        normalized_provider = self.normalize_provider(provider or self.embedding_provider)
        return DEFAULT_EMBEDDING_MODELS.get(normalized_provider, DEFAULT_EMBEDDING_MODELS["gemini"])

    def default_generation_model_for(self, provider: str | None = None) -> str:
        normalized_provider = self.normalize_provider(provider or self.generation_provider)
        return DEFAULT_GENERATION_MODELS.get(normalized_provider, DEFAULT_GENERATION_MODELS["gemini"])

    @property
    def active_embedding_provider(self) -> str:
        return self.normalize_provider(self.embedding_provider) or "gemini"

    @property
    def active_embedding_model(self) -> str:
        return self.embedding_model or self.default_embedding_model_for(self.embedding_provider)

    @property
    def active_generation_provider(self) -> str:
        return self.normalize_provider(self.generation_provider) or "gemini"

    @property
    def active_generation_model(self) -> str:
        return self.generation_model or self.llm_model or self.default_generation_model_for(self.generation_provider)

    def embedding_index_id(self, provider: str | None = None, model: str | None = None) -> str:
        active_provider = self.normalize_provider(provider or self.active_embedding_provider)
        active_model = model or self.active_embedding_model
        provider_slug = self.sanitize_model_id(active_provider)
        model_for_slug = active_model.replace("models/", "")
        provider_prefix = f"{active_provider}/"
        if model_for_slug.startswith(provider_prefix):
            model_for_slug = model_for_slug[len(provider_prefix):]
        model_slug = self.sanitize_model_id(model_for_slug)
        return f"{self.corpus_version}_{provider_slug}_{model_slug}"

    def chroma_collection_name_for(self, provider: str | None = None, model: str | None = None) -> str:
        active_provider = self.normalize_provider(provider or self.active_embedding_provider)
        active_model = model or self.active_embedding_model

        # Preserve the existing Gemini collection so current local/VPS indexes keep working.
        if active_provider == LEGACY_CHROMA_PROVIDER and active_model == LEGACY_CHROMA_MODEL:
            return f"{self.chroma_collection_name}_{self.corpus_version}"

        return f"{self.chroma_collection_name}_{self.embedding_index_id(active_provider, active_model)}"

    @property
    def active_embedding_index_id(self) -> str:
        return self.embedding_index_id()
    
    @property
    def corpus_storage_path_resolved(self) -> Path:
        """Resolve corpora root path (supports both relative and absolute)."""
        path = Path(self.corpus_storage_path)
        if path.is_absolute():
            return path
        return self.base_dir / path

    @property
    def corpus_dir_resolved(self) -> Path:
        """Resolve active corpus directory for the selected version."""
        return self.corpus_storage_path_resolved / self.corpus_version

    @property
    def corpus_documents_path_resolved(self) -> Path:
        """Resolve active corpus documents directory."""
        return self.corpus_dir_resolved / "documents"

    @property
    def corpus_documents_index_path_resolved(self) -> Path:
        """Resolve active corpus documents.json path."""
        return self.corpus_dir_resolved / "documents.json"

    @property
    def corpus_manifest_path_resolved(self) -> Path:
        """Resolve active corpus manifest.json path."""
        return self.corpus_dir_resolved / "manifest.json"
    
    @property
    def chroma_db_path_resolved(self) -> Path:
        """Resolve ChromaDB path (supports both relative and absolute)."""
        path = Path(self.chroma_db_path)
        if path.is_absolute():
            return path
        return self.base_dir / path

    @property
    def prompt_config_path_resolved(self) -> Path:
        """Resolve the YAML prompt configuration path."""
        path = Path(self.prompt_config_path)
        if path.is_absolute():
            return path
        return self.base_dir / path
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.corpus_documents_path_resolved.mkdir(parents=True, exist_ok=True)
        self.chroma_db_path_resolved.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
