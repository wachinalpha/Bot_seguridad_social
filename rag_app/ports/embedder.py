from typing import Protocol, List


class EmbedderPort(Protocol):
    """Port for generating text embeddings."""
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        ...
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        ...
