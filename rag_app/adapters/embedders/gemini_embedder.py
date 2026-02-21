from google import genai
from typing import List
import logging
import time

from rag_app.config.settings import settings

logger = logging.getLogger(__name__)


class GeminiEmbedder:
    """Adapter for generating embeddings using Gemini API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Gemini embedder.
        
        Args:
            api_key: Gemini API key (defaults to settings)
        """
        api_key = api_key or settings.gemini_api_key
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.embedding_model
        logger.info(f"Initialized GeminiEmbedder with model: {self.model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for i, text in enumerate(texts):
            try:
                # Add small delay to avoid rate limiting
                if i > 0:
                    time.sleep(0.1)
                
                embedding = self.embed_text(text)
                embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Embedded {i + 1}/{len(texts)} texts")
                    
            except Exception as e:
                logger.error(f"Error embedding text {i}: {e}")
                raise
        
        return embeddings
