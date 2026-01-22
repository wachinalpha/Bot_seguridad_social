"""Service for removing documents from the vector database.

This service handles document removal operations, following the hexagonal
architecture pattern by accepting a vector store port dependency.
"""
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class RemovalService:
    """Service for removing documents from the vector store."""
    
    def __init__(self, vector_store):
        """
        Initialize removal service with dependencies.
        
        Args:
            vector_store: Implementation of VectorStorePort (e.g., ChromaAdapter)
        """
        self.vector_store = vector_store
    
    def remove_document(self, doc_id: str) -> bool:
        """
        Remove a single document by its ID and its associated file.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if document was deleted successfully, False otherwise
        """
        try:
            logger.info(f"Removing document: {doc_id}")
            
            # Get document BEFORE deleting to retrieve file_path
            law_doc = self.vector_store.get_by_id(doc_id)
            
            # Delete from vector store
            result = self.vector_store.delete_document(doc_id)
            
            if result:
                # Delete associated markdown file if it exists
                if law_doc and law_doc.file_path:
                    self._delete_file(law_doc.file_path)
                logger.info(f"✓ Successfully removed document and file: {doc_id}")
            else:
                logger.warning(f"✗ Document not found or could not be deleted: {doc_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error removing document {doc_id}: {e}")
            return False
    
    def remove_all_documents(self) -> int:
        """
        Remove all documents from the vector store and their associated files.
        
        Returns:
            Number of documents deleted
        """
        try:
            logger.info("Removing all documents from vector store...")
            
            # Get current count
            count_before = self.vector_store.count_documents()
            logger.info(f"Found {count_before} documents to remove")
            
            if count_before == 0:
                logger.info("Vector store is already empty")
                return 0
            
            # Get all document IDs and their file paths BEFORE deleting
            doc_ids = self.list_all_documents()
            file_paths = []
            
            for doc_id in doc_ids:
                law_doc = self.vector_store.get_by_id(doc_id)
                if law_doc and law_doc.file_path:
                    file_paths.append(law_doc.file_path)
            
            # Delete all documents from vector store
            deleted_count = self.vector_store.delete_all_documents()
            
            # Delete all associated files
            files_deleted = 0
            for file_path in file_paths:
                if self._delete_file(file_path):
                    files_deleted += 1
            
            logger.info(f"✓ Successfully removed {deleted_count} documents and {files_deleted} files")
            
            # Verify deletion
            count_after = self.vector_store.count_documents()
            
            if count_after != 0:
                logger.warning(f"⚠ Some documents may remain: {count_after} documents still in store")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error removing all documents: {e}")
            raise
    
    def list_all_documents(self) -> List[str]:
        """
        Get list of all document IDs in the vector store.
        
        Returns:
            List of document IDs
        """
        try:
            doc_ids = self.vector_store.get_all_document_ids()
            logger.info(f"Found {len(doc_ids)} documents in vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        """
        Get total count of documents in the vector store.
        
        Returns:
            Number of documents
        """
        try:
            count = self.vector_store.count_documents()
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def _delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the file system.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if file was deleted, False otherwise
        """
        if not file_path:
            return False
        
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.debug(f"Deleted file: {file_path}")
                return True
            else:
                logger.debug(f"File not found, skipping: {file_path}")
                return False
        except Exception as e:
            logger.warning(f"Could not delete file {file_path}: {e}")
            return False
