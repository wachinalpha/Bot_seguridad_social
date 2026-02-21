from dataclasses import dataclass, field
from typing import Optional, Dict, List


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
class QueryResult:
    """Result of a user query against the RAG system."""
    answer: str
    law_documents: List[LawDocument]
    confidence_score: float = 0.0
    response_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'answer': self.answer,
            'law_documents': [
                {'law_title': d.titulo, 'law_id': d.id}
                for d in self.law_documents
            ],
            'confidence_score': self.confidence_score,
            'response_time_ms': self.response_time_ms
        }