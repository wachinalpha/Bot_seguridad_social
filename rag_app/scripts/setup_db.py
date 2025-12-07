#!/usr/bin/env python3
"""
Setup script for initial database ingestion.

This script processes all laws from leyes_config.json and populates
the vector database.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_app.config.settings import settings
from rag_app.utils.logger import configure_logging
from rag_app.adapters.chunkers.docling_adapter import DoclingAdapter
from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.services.ingestion_service import IngestionService


def main():
    """Main setup function."""
    # Configure logging
    configure_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Starting Legal AI RAG Database Setup")
    logger.info("=" * 60)
    
    try:
        # Check for API key
        if not settings.gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables!")
            logger.error("Please set GEMINI_API_KEY before running this script.")
            sys.exit(1)
        
        logger.info(f"Processed docs path: {settings.processed_docs_path}")
        logger.info(f"ChromaDB path: {settings.chroma_db_path}")
        
        # Initialize adapters
        logger.info("\n[1/4] Initializing adapters...")
        document_processor = DoclingAdapter()
        embedder = GeminiEmbedder()
        vector_store = ChromaAdapter()
        
        # Create ingestion service
        logger.info("[2/4] Creating ingestion service...")
        ingestion_service = IngestionService(
            document_processor=document_processor,
            embedder=embedder,
            vector_store=vector_store
        )
        
        # Run ingestion
        logger.info("[3/4] Starting ingestion process...")
        processed_docs = ingestion_service.ingest_from_config()
        
        # Summary
        logger.info("\n[4/4] Ingestion Summary:")
        logger.info("=" * 60)
        logger.info(f"Total laws processed: {len(processed_docs)}")
        
        for doc in processed_docs:
            logger.info(f"  ✓ {doc.id}: {doc.titulo}")
            logger.info(f"    File: {doc.file_path}")
        
        logger.info("=" * 60)
        logger.info("✓ Database setup completed successfully!")
        logger.info("=" * 60)
        
        # Show database stats
        total_docs = vector_store.count_documents()
        logger.info(f"\nVector database contains {total_docs} documents")
        
    except Exception as e:
        logger.error(f"\n✗ Setup failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
