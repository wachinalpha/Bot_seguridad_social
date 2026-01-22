from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
import hashlib


@dataclass
class LawDocument:
    """Represents a complete legal document (law) in the system."""
    id: str
    titulo: str
    url: str
    file_path: Optional[str] = None  # Path to the processed .md file
    summary: Optional[str] = None  # Brief summary for embedding
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure ID is set based on law number if not provided."""
        if not self.id and 'numero' in self.metadata:
            self.id = f"ley_{self.metadata['numero']}"
    
    @property
    def searchable_text(self) -> str:
        """Text used for embedding: title + summary."""
        parts = [self.titulo]
        if self.summary:
            parts.append(self.summary)
        return " | ".join(parts)


@dataclass
class CacheSession:
    """Represents a Gemini API cached content session."""
    cache_id: str  # Google's cache ID
    law_id: str  # Reference to LawDocument
    content_hash: str  # SHA256 hash of the markdown content
    expiration_time: datetime
    model_name: str = "models/gemini-1.5-pro"
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_expired(self) -> bool:
        """Check if the cache has expired."""
        return datetime.now() >= self.expiration_time
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute SHA256 hash of content for cache validation."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


@dataclass
class QueryResult:
    """Result of a user query against the RAG system."""
    answer: str
    law_document: LawDocument
    confidence_score: float = 0.0
    cache_used: bool = False
    cache_id: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'answer': self.answer,
            'law_title': self.law_document.titulo,
            'law_id': self.law_document.id,
            'confidence_score': self.confidence_score,
            'cache_used': self.cache_used,
            'response_time_ms': self.response_time_ms
        }
    