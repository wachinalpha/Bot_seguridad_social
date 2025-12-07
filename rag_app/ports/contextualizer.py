from typing import Protocol, List, Optional
from rag_app.domain.models import LawDocument, CacheSession


class ContextualizerPort(Protocol):
    """Port for managing Gemini API context caching and answer generation."""
    
    def get_or_create_cache(self, law_doc: LawDocument) -> CacheSession:
        """
        Get existing cache or create new one for a law document.
        
        This method:
        1. Reads the markdown file from law_doc.file_path
        2. Computes content hash
        3. Checks if an active cache exists for this content
        4. Returns existing cache or creates new one
        
        Args:
            law_doc: LawDocument with file_path to the markdown content
            
        Returns:
            CacheSession with cache metadata
        """
        ...
    
    def generate_answer(self, cache_session: CacheSession, query: str) -> str:
        """
        Generate answer to a query using the cached context.
        
        Args:
            cache_session: Active cache session
            query: User's question
            
        Returns:
            Generated answer from the LLM
        """
        ...
    
    def list_active_caches(self) -> List[CacheSession]:
        """
        List all active (non-expired) cache sessions.
        
        Returns:
            List of active CacheSession instances
        """
        ...
    
    def delete_cache(self, cache_id: str) -> bool:
        """
        Delete a specific cache from Gemini API.
        
        Args:
            cache_id: Google cache identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        ...
