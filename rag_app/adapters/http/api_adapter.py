"""FastAPI adapter for HTTP REST API."""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
from pathlib import Path
import tempfile

from rag_app.domain.api_schemas import (
    ChatRequest,
    ChatResponse,
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentListItem,
    DocumentDetailResponse,
    HealthResponse,
    ErrorResponse,
    LawDocumentResponse
)
from rag_app.domain.models import QueryResult, LawDocument
from rag_app.services.retrieval_service import RetrievalService
from rag_app.services.ingestion_service import IngestionService
from rag_app.adapters.http.session_manager import SessionManager
from rag_app.config.settings import settings

logger = logging.getLogger(__name__)


class APIAdapter:
    """FastAPI adapter implementing REST endpoints for RAG system."""
    
    def __init__(
        self,
        retrieval_service: RetrievalService,
        ingestion_service: IngestionService,
        session_manager: Optional[SessionManager] = None
    ):
        """
        Initialize API adapter.
        
        Args:
            retrieval_service: Service for RAG queries
            ingestion_service: Service for document ingestion
            session_manager: Optional session manager for chat context
        """
        self.retrieval_service = retrieval_service
        self.ingestion_service = ingestion_service
        self.session_manager = session_manager or SessionManager()
        
        # Create API router
        self.router = APIRouter()
        
        # Register routes
        self._register_routes()
        
        logger.info("APIAdapter initialized")
    
    def _register_routes(self):
        """Register all API routes."""
        
        # Health check (no prefix)
        @self.router.get(
            "/health",
            response_model=HealthResponse,
            tags=["System"],
            summary="Health check endpoint"
        )
        async def health_check():
            """Check system health and service status."""
            try:
                return HealthResponse(
                    status="healthy",
                    timestamp=datetime.now(),
                    version=settings.api_version,
                    services={
                        "vector_store": "ok",
                        "embedder": "ok",
                        "contextualizer": "ok",
                        "active_sessions": str(self.session_manager.get_session_count())
                    }
                )
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unhealthy")
        
        # Chat endpoint
        @self.router.post(
            "/chat",
            response_model=ChatResponse,
            tags=["Chat"],
            summary="Ask questions about legal documents"
        )
        async def chat(request: ChatRequest):
            """
            Process a user query using RAG system.
            
            Supports conversation context via session_id.
            """
            try:
                logger.info(f"Chat request: query='{request.query[:50]}...', session={request.session_id}")
                
                # Get or create session
                session = self.session_manager.get_or_create_session(request.session_id)
                
                # Add user message to history
                session.add_message("user", request.query)
                
                # Process query
                result: QueryResult = self.retrieval_service.query(request.query,top_k=3)
                
                # Add assistant response to history
                session.add_message("assistant", result.answer)
                if result.law_documents:
                    session.last_law_id = result.law_documents[0].id
                
                # Convert domain model to API response
                return ChatResponse(
                    answer=result.answer,
                    law_documents=[
                        LawDocumentResponse(
                            id=doc.id,
                            titulo=doc.titulo,
                            url=doc.url,
                            summary=doc.summary,
                            metadata=doc.metadata
                        )
                        for doc in result.law_documents
                    ],
                    confidence_score=result.confidence_score,
                    response_time_ms=result.response_time_ms,
                    session_id=session.session_id
                )
                
            except Exception as e:
                logger.error(f"Error processing chat request: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing query: {str(e)}"
                )
        
        # List all documents
        @self.router.get(
            "/documents",
            response_model=DocumentListResponse,
            tags=["Documents"],
            summary="List all indexed documents"
        )
        async def list_documents():
            """Get a list of all indexed legal documents."""
            try:
                # Get all documents from vector store
                vector_store = self.retrieval_service.vector_store
                total_count = vector_store.count_documents()
                
                # For now, return basic info
                # In a production system, you'd implement pagination
                documents = []
                
                # Try to get some sample documents
                # Note: ChromaDB doesn't have a direct "list all" method
                # We'll need to work around this
                try:
                    collection = vector_store.collection
                    results = collection.get(limit=100)  # Get first 100
                    
                    if results['ids']:
                        for i, doc_id in enumerate(results['ids']):
                            metadata = results['metadatas'][i] if results['metadatas'] else {}
                            documents.append(
                                DocumentListItem(
                                    id=doc_id,
                                    titulo=metadata.get('titulo', 'Unknown'),
                                    url=metadata.get('url', ''),
                                    summary=metadata.get('summary'),
                                    categoria=metadata.get('categoria')
                                )
                            )
                except Exception as e:
                    logger.warning(f"Could not fetch document list: {e}")
                
                return DocumentListResponse(
                    documents=documents,
                    total=total_count
                )
                
            except Exception as e:
                logger.error(f"Error listing documents: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error retrieving documents: {str(e)}"
                )
        
        # Get specific document
        @self.router.get(
            "/documents/{law_id}",
            response_model=DocumentDetailResponse,
            tags=["Documents"],
            summary="Get details of a specific document"
        )
        async def get_document(law_id: str):
            """Get detailed information about a specific legal document."""
            try:
                vector_store = self.retrieval_service.vector_store
                law_doc = vector_store.get_by_id(law_id)
                
                if not law_doc:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Document '{law_id}' not found"
                    )
                
                return DocumentDetailResponse(
                    id=law_doc.id,
                    titulo=law_doc.titulo,
                    url=law_doc.url,
                    file_path=law_doc.file_path,
                    summary=law_doc.summary,
                    metadata=law_doc.metadata
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting document {law_id}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error retrieving document: {str(e)}"
                )
        
        # Upload document
        @self.router.post(
            "/documents/upload",
            response_model=DocumentUploadResponse,
            tags=["Documents"],
            summary="Upload and index a new legal document"
        )
        async def upload_document(file: UploadFile = File(...)):
            """
            Upload a legal document for processing and indexing.
            
            Supports: PDF, DOCX, MD files.
            """
            try:
                logger.info(f"Document upload: filename={file.filename}, content_type={file.content_type}")
                
                # Validate file type
                allowed_extensions = {'.pdf', '.docx', '.md', '.txt'}
                file_ext = Path(file.filename).suffix.lower()
                
                if file_ext not in allowed_extensions:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File type '{file_ext}' not supported. Allowed: {allowed_extensions}"
                    )
                
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                    content = await file.read()
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                
                try:
                    # Process document using ingestion service
                    law_doc = await self._process_uploaded_document(tmp_file_path, file.filename)
                    
                    return DocumentUploadResponse(
                        success=True,
                        message="Documento procesado e indexado exitosamente",
                        document_id=law_doc.id,
                        titulo=law_doc.titulo
                    )
                    
                finally:
                    # Clean up temp file
                    Path(tmp_file_path).unlink(missing_ok=True)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error uploading document: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing document: {str(e)}"
                )
    
    async def _process_uploaded_document(self, file_path: str, original_filename: str) -> LawDocument:
        """
        Process an uploaded document (placeholder implementation).
        
        In a full implementation, this would:
        1. Convert to markdown using Docling
        2. Extract metadata
        3. Create LawDocument
        4. Ingest into system
        
        Args:
            file_path: Path to temporary file
            original_filename: Original filename
            
        Returns:
            LawDocument instance
        """
        # For now, this is a simplified implementation
        # You'll need to integrate with your ingestion service
        
        raise HTTPException(
            status_code=501,
            detail="Document upload not yet fully implemented. Use ingestion scripts for now."
        )
