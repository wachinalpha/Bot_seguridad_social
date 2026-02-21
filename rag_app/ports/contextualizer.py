from typing import Protocol
from rag_app.domain.models import LawDocument


class ContextualizerPort(Protocol):
    """Port for generating answers using an LLM with full law context."""
    
    def generate_answer(self, query: str, law_doc: LawDocument) -> str:
        """
        Generate answer to a query using the full law document context.
        
        Args:
            query: User's question
            law_doc: LawDocument with file_path to the markdown content
            
        Returns:
            Generated answer from the LLM
        """
        ...
