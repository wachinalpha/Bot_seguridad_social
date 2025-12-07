import logging
import time
from typing import Optional

from rag_app.domain.models import LawDocument, QueryResult

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieval: Query → Vector → Cache → Answer"""
    
    def __init__(self, embedder, vector_store, contextualizer):
        """
        Initialize retrieval service with dependencies.
        
        Args:
            embedder: Implementation of EmbedderPort
            vector_store: Implementation of VectorStorePort
            contextualizer: Implementation of ContextualizerPort
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.contextualizer = contextualizer
    
    def query(self, user_query: str, top_k: int = 1) -> QueryResult:
        """
        Process a user query and return an answer.
        
        Flow:
        1. Embed the query
        2. Search vector store for most relevant law
        3. Get or create cache for that law
        4. Generate answer using cached context
        
        Args:
            user_query: User's question
            top_k: Number of laws to consider (default 1 for single-law context)
            
        Returns:
            QueryResult with answer and metadata
        """
        start_time = time.time()
        logger.info(f"Processing query: {user_query[:100]}...")
        
        try:
            # Step 1: Embed query
            logger.info("Step 1: Embedding query")
            query_embedding = self.embedder.embed_text(user_query)
            
            # Step 2: Search for relevant law
            logger.info("Step 2: Searching vector store")
            similar_docs = self.vector_store.search(query_embedding, top_k=top_k)
            
            if not similar_docs:
                logger.warning("No relevant laws found")
                return self._create_error_result("No se encontraron leyes relevantes para tu consulta")
            
            law_doc = similar_docs[0]  # Use most relevant law
            logger.info(f"Found relevant law: {law_doc.titulo}")
            
            # Step 3: Get or create cache
            logger.info("Step 3: Getting or creating cache")
            cache_session = self.contextualizer.get_or_create_cache(law_doc)
            cache_was_reused = not cache_session.is_expired
            
            # Step 4: Generate answer
            logger.info("Step 4: Generating answer with cached context")
            answer = self.contextualizer.generate_answer(cache_session, user_query)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Create result
            result = QueryResult(
                answer=answer,
                law_document=law_doc,
                confidence_score=1.0,  # Could be enhanced with similarity score
                cache_used=cache_was_reused,
                cache_id=cache_session.cache_id,
                response_time_ms=response_time_ms
            )
            
            logger.info(f"Query completed in {response_time_ms:.2f}ms (cache: {cache_was_reused})")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_result(
                f"Error al procesar tu consulta: {str(e)}",
                response_time_ms
            )
    
    def query_specific_law(self, user_query: str, law_id: str) -> QueryResult:
        """
        Query a specific law by ID.
        
        Args:
            user_query: User's question
            law_id: Specific law ID to query
            
        Returns:
            QueryResult with answer
        """
        start_time = time.time()
        logger.info(f"Querying specific law {law_id}: {user_query[:100]}...")
        
        try:
            # Get law document by ID
            law_doc = self.vector_store.get_by_id(law_id)
            
            if not law_doc:
                logger.warning(f"Law {law_id} not found")
                return self._create_error_result(f"Ley {law_id} no encontrada en la base de datos")
            
            # Get or create cache
            cache_session = self.contextualizer.get_or_create_cache(law_doc)
            cache_was_reused = not cache_session.is_expired
            
            # Generate answer
            answer = self.contextualizer.generate_answer(cache_session, user_query)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            result = QueryResult(
                answer=answer,
                law_document=law_doc,
                confidence_score=1.0,
                cache_used=cache_was_reused,
                cache_id=cache_session.cache_id,
                response_time_ms=response_time_ms
            )
            
            logger.info(f"Query completed in {response_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error querying specific law: {e}")
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_result(str(e), response_time_ms)
    
    def _create_error_result(self, error_message: str, response_time_ms: Optional[float] = None) -> QueryResult:
        """Create an error QueryResult."""
        dummy_law = LawDocument(
            id="error",
            titulo="Error",
            url="",
            summary="Error processing query"
        )
        
        return QueryResult(
            answer=error_message,
            law_document=dummy_law,
            confidence_score=0.0,
            cache_used=False,
            response_time_ms=response_time_ms
        )
