"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Chat Endpoints
# ============================================================================

class ChatRequest(BaseModel):
    """Request schema for /api/v1/chat endpoint."""
    query: str = Field(..., description="User's question about legal documents", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cuáles son los requisitos para jubilarse?",
                "session_id": "user-session-123"
            }
        }


class LawDocumentResponse(BaseModel):
    """Schema for law document in responses."""
    id: str
    titulo: str
    url: str
    summary: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Response schema for /api/v1/chat endpoint."""
    answer: str = Field(..., description="Generated answer from RAG system")
    law_document: LawDocumentResponse = Field(..., description="Source law document")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    cache_used: bool = Field(..., description="Whether cached context was used")
    cache_id: Optional[str] = Field(None, description="Cache ID if applicable")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    session_id: Optional[str] = Field(None, description="Session ID if provided")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Los requisitos para jubilarse incluyen...",
                "law_document": {
                    "id": "ley_24241",
                    "titulo": "Ley 24241 - Sistema Integrado de Jubilaciones y Pensiones",
                    "url": "https://example.com/ley24241",
                    "summary": "Norma que regula el sistema previsional argentino",
                    "metadata": {"categoria": "Jubilaciones"}
                },
                "confidence_score": 0.95,
                "cache_used": True,
                "cache_id": "cache_abc123",
                "response_time_ms": 234.5,
                "session_id": "user-session-123"
            }
        }


# ============================================================================
# Document Management Endpoints
# ============================================================================

class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    success: bool
    message: str
    document_id: Optional[str] = None
    titulo: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Documento procesado e indexado exitosamente",
                "document_id": "ley_27000",
                "titulo": "Ley 27000 - Nueva Ley de Seguridad Social"
            }
        }


class DocumentListItem(BaseModel):
    """Schema for individual document in list."""
    id: str
    titulo: str
    url: str
    summary: Optional[str] = None
    categoria: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Response schema for /api/v1/documents endpoint."""
    documents: List[DocumentListItem]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": "ley_24241",
                        "titulo": "Ley 24241 - Sistema Integrado de Jubilaciones y Pensiones",
                        "url": "https://example.com/ley24241",
                        "summary": "Norma que regula el sistema previsional argentino",
                        "categoria": "Jubilaciones"
                    }
                ],
                "total": 1
            }
        }


class DocumentDetailResponse(BaseModel):
    """Response schema for /api/v1/documents/{law_id} endpoint."""
    id: str
    titulo: str
    url: str
    file_path: Optional[str] = None
    summary: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ley_24241",
                "titulo": "Ley 24241 - Sistema Integrado de Jubilaciones y Pensiones",
                "url": "https://example.com/ley24241",
                "file_path": "/data/processed/ley_24241.md",
                "summary": "Norma que regula el sistema previsional argentino",
                "metadata": {
                    "numero": "24241",
                    "año": "1993",
                    "categoria": "Jubilaciones"
                }
            }
        }


# ============================================================================
# System Endpoints
# ============================================================================

class HealthResponse(BaseModel):
    """Response schema for /health endpoint."""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0",
                "services": {
                    "vector_store": "ok",
                    "embedder": "ok",
                    "contextualizer": "ok"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standardized error response schema."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "La consulta no puede estar vacía",
                "details": {"field": "query"}
            }
        }
