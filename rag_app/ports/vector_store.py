from typing import Protocol, List, Optional
from rag_app.domain.models import LawDocument


class VectorStorePort(Protocol):
    """Port for vector database operations."""
    
    def save_document(self, law_doc: LawDocument, embedding: List[float]) -> None:
        """
        Save a law document with its embedding to the vector store.
        
        Args:
            law_doc: LawDocument instance with metadata
            embedding: Embedding vector for the document's searchable text
        """
        ...
    
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[LawDocument]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of most similar LawDocument instances
        """
        ...
    
    def get_by_id(self, doc_id: str) -> Optional[LawDocument]:
        """
        Retrieve a document by its ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            LawDocument if found, None otherwise
        """
        ...
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        ...
    
    def count_documents(self) -> int:
        """
        Get total count of documents in the store.
        
        Returns:
            Number of documents
        """
        ...
