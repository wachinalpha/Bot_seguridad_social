import google.generativeai as genai
from google.generativeai import caching
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

from rag_app.domain.models import LawDocument, CacheSession
from rag_app.config.settings import settings

logger = logging.getLogger(__name__)


class GeminiCacheManager:
    """Adapter for managing Gemini API context caching."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Gemini cache manager.
        
        Args:
            api_key: Gemini API key (defaults to settings)
        """
        api_key = api_key or settings.gemini_api_key
        genai.configure(api_key=api_key)
        self.model_name = settings.llm_model
        self.cache_ttl_minutes = settings.cache_ttl_minutes
        logger.info(f"Initialized GeminiCacheManager with model: {self.model_name}")
    
    def get_or_create_cache(self, law_doc: LawDocument) -> CacheSession:
        """
        Get existing cache or create new one for a law document.
        
        Args:
            law_doc: LawDocument with file_path to the markdown content
            
        Returns:
            CacheSession with cache metadata
        """
        try:
            # Read markdown content
            if not law_doc.file_path or not Path(law_doc.file_path).exists():
                raise ValueError(f"File path not found: {law_doc.file_path}")
            
            content = Path(law_doc.file_path).read_text(encoding='utf-8')
            content_hash = CacheSession.compute_content_hash(content)
            
            # Check for existing active caches
            existing_cache = self._find_active_cache(law_doc.id, content_hash)
            
            if existing_cache:
                logger.info(f"Reusing existing cache: {existing_cache.cache_id}")
                return existing_cache
            
            # Create new cache
            logger.info(f"Creating new cache for law {law_doc.id}")
            cache_session = self._create_cache(law_doc, content, content_hash)
            return cache_session
            
        except Exception as e:
            logger.error(f"Error in get_or_create_cache for {law_doc.id}: {e}")
            raise
    
    def _find_active_cache(self, law_id: str, content_hash: str) -> Optional[CacheSession]:
        """Find an active cache for the given law and content hash."""
        try:
            # List all caches
            caches = caching.CachedContent.list()
            
            for cache in caches:
                # Check if cache metadata matches
                if hasattr(cache, 'name') and hasattr(cache, 'expire_time'):
                    # Parse cache name to extract law_id and content_hash
                    # Expected format: "law_{law_id}_{content_hash[:8]}"
                    cache_name_parts = cache.name.split('/')[-1].split('_')
                    
                    if len(cache_name_parts) >= 3:
                        cached_law_id = f"{cache_name_parts[0]}_{cache_name_parts[1]}"
                        cached_hash_prefix = cache_name_parts[2] if len(cache_name_parts) > 2 else ""
                        
                        # Check if it matches and is not expired
                        if (cached_law_id == law_id and 
                            content_hash.startswith(cached_hash_prefix)):
                            
                            expiration = cache.expire_time
                            
                            # Convert to datetime if needed
                            if isinstance(expiration, str):
                                expiration = datetime.fromisoformat(expiration.replace('Z', '+00:00'))
                            
                            # Check if not expired
                            if expiration > datetime.now(expiration.tzinfo):
                                return CacheSession(
                                    cache_id=cache.name,
                                    law_id=law_id,
                                    content_hash=content_hash,
                                    expiration_time=expiration.replace(tzinfo=None),
                                    model_name=self.model_name
                                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Error finding active cache: {e}")
            return None
    
    def _create_cache(self, law_doc: LawDocument, content: str, content_hash: str) -> CacheSession:
        """Create a new cache in Gemini API."""
        try:
            # Prepare the system instruction
            system_instruction = f"""Eres un asistente experto en leyes de Seguridad Social de Argentina.

Tienes acceso al texto completo de la siguiente ley:
- Título: {law_doc.titulo}
- Número: {law_doc.metadata.get('numero', 'N/A')}

Tu trabajo es responder preguntas sobre esta ley de manera precisa y profesional.
Siempre cita los artículos específicos cuando sea relevante."""

            # Create cached content
            cache = caching.CachedContent.create(
                model=self.model_name,
                display_name=f"{law_doc.id}_{content_hash[:8]}",
                system_instruction=system_instruction,
                contents=[content],
                ttl=timedelta(minutes=self.cache_ttl_minutes)
            )
            
            # Calculate expiration time
            expiration = datetime.now() + timedelta(minutes=self.cache_ttl_minutes)
            
            cache_session = CacheSession(
                cache_id=cache.name,
                law_id=law_doc.id,
                content_hash=content_hash,
                expiration_time=expiration,
                model_name=self.model_name
            )
            
            logger.info(f"Created cache {cache.name} for {law_doc.id}, expires at {expiration}")
            return cache_session
            
        except Exception as e:
            logger.error(f"Error creating cache: {e}")
            raise
    
    def generate_answer(self, cache_session: CacheSession, query: str) -> str:
        """
        Generate answer to a query using the cached context.
        
        Args:
            cache_session: Active cache session
            query: User's question
            
        Returns:
            Generated answer from the LLM
        """
        try:
            # Create model from cache
            model = genai.GenerativeModel.from_cached_content(
                cached_content=cache_session.cache_id
            )
            
            # Generate response
            response = model.generate_content(query)
            
            logger.info(f"Generated answer using cache {cache_session.cache_id}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def list_active_caches(self) -> List[CacheSession]:
        """
        List all active (non-expired) cache sessions.
        
        Returns:
            List of active CacheSession instances
        """
        active_caches = []
        
        try:
            caches = caching.CachedContent.list()
            
            for cache in caches:
                if hasattr(cache, 'expire_time'):
                    expiration = cache.expire_time
                    
                    if isinstance(expiration, str):
                        expiration = datetime.fromisoformat(expiration.replace('Z', '+00:00'))
                    
                    if expiration > datetime.now(expiration.tzinfo):
                        # Parse cache name to extract law_id
                        cache_name_parts = cache.name.split('/')[-1].split('_')
                        law_id = f"{cache_name_parts[0]}_{cache_name_parts[1]}" if len(cache_name_parts) >= 2 else "unknown"
                        
                        cache_session = CacheSession(
                            cache_id=cache.name,
                            law_id=law_id,
                            content_hash="",  # We don't store this in the cache metadata
                            expiration_time=expiration.replace(tzinfo=None),
                            model_name=self.model_name
                        )
                        active_caches.append(cache_session)
            
            logger.info(f"Found {len(active_caches)} active caches")
            return active_caches
            
        except Exception as e:
            logger.error(f"Error listing caches: {e}")
            return []
    
    def delete_cache(self, cache_id: str) -> bool:
        """
        Delete a specific cache from Gemini API.
        
        Args:
            cache_id: Google cache identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            cache = caching.CachedContent(name=cache_id)
            cache.delete()
            logger.info(f"Deleted cache {cache_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache {cache_id}: {e}")
            return False
