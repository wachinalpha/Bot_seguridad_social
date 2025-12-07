import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional
import logging

from rag_app.domain.models import LawDocument
from rag_app.config.settings import settings

logger = logging.getLogger(__name__)


class ChromaAdapter:
    """Adapter for vector storage using ChromaDB."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_db_path),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "Legal documents for RAG system"}
        )
        
        logger.info(f"Initialized ChromaDB at {settings.chroma_db_path}")
        logger.info(f"Collection: {settings.chroma_collection_name}")
    
    def save_document(self, law_doc: LawDocument, embedding: List[float]) -> None:
        """
        Save a law document with its embedding to the vector store.
        
        Args:
            law_doc: LawDocument instance with metadata
            embedding: Embedding vector for the document's searchable text
        """
        try:
            # Prepare metadata (ChromaDB requires dict values to be str, int, float, or bool)
            metadata = {
                "titulo": law_doc.titulo,
                "url": law_doc.url,
                "file_path": law_doc.file_path or "",
                "summary": law_doc.summary or "",
            }
            
            # Add additional metadata from law_doc.metadata
            for key, value in law_doc.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
                else:
                    metadata[key] = str(value)
            
            # Add to collection
            self.collection.add(
                ids=[law_doc.id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[law_doc.searchable_text]
            )
            
            logger.info(f"Saved document {law_doc.id} to vector store")
            
        except Exception as e:
            logger.error(f"Error saving document {law_doc.id}: {e}")
            raise
    
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[LawDocument]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of most similar LawDocument instances
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Convert results to LawDocument instances
            documents = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    doc_id = results['ids'][0][i]
                    metadata = results['metadatas'][0][i]
                    
                    # Extract metadata back
                    law_metadata = {}
                    for key in ['numero', 'año', 'categoria']:
                        if key in metadata:
                            law_metadata[key] = metadata[key]
                    
                    law_doc = LawDocument(
                        id=doc_id,
                        titulo=metadata.get('titulo', ''),
                        url=metadata.get('url', ''),
                        file_path=metadata.get('file_path'),
                        summary=metadata.get('summary'),
                        metadata=law_metadata
                    )
                    documents.append(law_doc)
            
            logger.info(f"Found {len(documents)} similar documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def get_by_id(self, doc_id: str) -> Optional[LawDocument]:
        """
        Retrieve a document by its ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            LawDocument if found, None otherwise
        """
        try:
            results = self.collection.get(ids=[doc_id])
            
            if results['ids'] and len(results['ids']) > 0:
                metadata = results['metadatas'][0]
                
                law_metadata = {}
                for key in ['numero', 'año', 'categoria']:
                    if key in metadata:
                        law_metadata[key] = metadata[key]
                
                return LawDocument(
                    id=doc_id,
                    titulo=metadata.get('titulo', ''),
                    url=metadata.get('url', ''),
                    file_path=metadata.get('file_path'),
                    summary=metadata.get('summary'),
                    metadata=law_metadata
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def count_documents(self) -> int:
        """
        Get total count of documents in the store.
        
        Returns:
            Number of documents
        """
        return self.collection.count()
