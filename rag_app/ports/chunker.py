from typing import Protocol, Tuple
from rag_app.domain.models import LawDocument


class DocumentProcessorPort(Protocol):
    """Port for processing legal documents from web URLs to structured markdown."""
    
    def process_url(self, url: str, law_id: str) -> Tuple[str, str]:
        """
        Process a law URL and convert to markdown.
        
        Args:
            url: URL of the legal document
            law_id: Unique identifier for the law
            
        Returns:
            Tuple of (file_path, markdown_content)
        """
        ...
