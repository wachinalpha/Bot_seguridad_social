import logging
import time
from typing import List, Optional

from rag_app.domain.models import LawDocument, QueryResult

logger = logging.getLogger(__name__)

# ID of the base law for the ANSES assignment system.
# When this law appears in the candidate results it is promoted
# to position 1 so the LLM always has the foundational context first.
ANCHOR_LAW_ID = "ley_24714"


class RetrievalService:
    """Service for retrieval: Query → Vector Search → Answer"""
    
    def __init__(self, embedder, vector_store, contextualizer):
        """
        Initialize retrieval service with dependencies.
        
        Args:
            embedder: Implementation of EmbedderPort
            vector_store: Implementation of VectorStorePort
            contextualizer: GeminiManager for answer generation
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.contextualizer = contextualizer
    
    def _rerank(self, candidates: List[LawDocument], top_k: int) -> List[LawDocument]:
        """
        Rerank candidate documents, promoting ANCHOR_LAW_ID to position 1
        when it appears in the results, then trim to top_k.

        Strategy:
        - Search was done with top_k + 2 candidates.
        - If ley_24714 appears anywhere in candidates → move it to front.
        - Return the first top_k documents.
        """
        anchor = next((d for d in candidates if d.id == ANCHOR_LAW_ID), None)
        if anchor:
            others = [d for d in candidates if d.id != ANCHOR_LAW_ID]
            reranked = [anchor] + others
            logger.info(f"Reranking: promoted {ANCHOR_LAW_ID} to position 1")
        else:
            reranked = candidates
            logger.info(f"Reranking: {ANCHOR_LAW_ID} not in candidates, keeping original order")
        return reranked[:top_k]

    def query(self, user_query: str, top_k: int = 3) -> QueryResult:
        """
        Process a user query and return an answer.
        
        Flow:
        1. Embed the query
        2. Search vector store for most relevant law
        3. Generate answer using full law context
        
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
            
            # Step 2: Search for relevant laws (fetch extra candidates for reranking)
            logger.info("Step 2: Searching vector store")
            candidates = self.vector_store.search(query_embedding, top_k=top_k + 2)
            
            if not candidates:
                logger.warning("No relevant laws found")
                return self._create_error_result("No se encontraron leyes relevantes para tu consulta")
            
            # Step 2b: Rerank — promote ley_24714 if found in candidates
            logger.info("Step 2b: Reranking candidates")
            law_docs = self._rerank(candidates, top_k)
            titles = ', '.join(d.titulo for d in law_docs)
            logger.info(f"Final context: {len(law_docs)} law(s): {titles}")
            
            # Step 3: Generate answer
            logger.info("Step 3: Generating answer")
            answer = self.contextualizer.generate_answer(user_query, law_docs)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            result = QueryResult(
                answer=answer,
                law_documents=law_docs,
                confidence_score=1.0,
                response_time_ms=response_time_ms
            )
            
            logger.info(f"Query completed in {response_time_ms:.2f}ms")
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
            
            # Generate answer
            answer = self.contextualizer.generate_answer(user_query, [law_doc])
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            result = QueryResult(
                answer=answer,
                law_documents=[law_doc],
                confidence_score=1.0,
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
            law_documents=[dummy_law],
            confidence_score=0.0,
            response_time_ms=response_time_ms
        )
