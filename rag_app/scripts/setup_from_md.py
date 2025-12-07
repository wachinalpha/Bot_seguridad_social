#!/usr/bin/env python3
"""
Setup script using existing Anses1.md file for testing.

This script bypasses URL downloading and uses the pre-existing
markdown file directly.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_app.config.settings import settings
from rag_app.utils.logger import configure_logging
from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.domain.models import LawDocument


def ingest_from_markdown_file(md_file_path: str, law_id: str, titulo: str, summary: str):
    """
    Ingest a law document from an existing markdown file.
    
    Args:
        md_file_path: Path to the markdown file
        law_id: Unique identifier for the law
        titulo: Title of the law
        summary: Brief summary for embedding
    """
    logger = logging.getLogger(__name__)
    
    # Read markdown file
    md_path = Path(md_file_path)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")
    
    markdown_content = md_path.read_text(encoding='utf-8')
    logger.info(f"Read {len(markdown_content)} characters from {md_path}")
    
    # Copy to processed directory
    processed_path = settings.processed_docs_path / f"{law_id}.md"
    processed_path.write_text(markdown_content, encoding='utf-8')
    logger.info(f"Copied to processed directory: {processed_path}")
    
    # Create LawDocument
    law_doc = LawDocument(
        id=law_id,
        titulo=titulo,
        url="file://" + str(md_path.absolute()),
        file_path=str(processed_path),
        summary=summary,
        metadata={
            'numero': 'ANSES-001',
            'año': 2024,
            'categoria': 'Seguridad Social',
            'descripcion_breve': 'Documento de ANSES sobre seguridad social'
        }
    )
    
    # Generate embedding for searchable text
    logger.info("Generating embedding...")
    embedder = GeminiEmbedder()
    searchable_text = law_doc.searchable_text
    embedding = embedder.embed_text(searchable_text)
    logger.info(f"Generated embedding of dimension {len(embedding)}")
    
    # Save to vector store
    logger.info("Saving to vector store...")
    vector_store = ChromaAdapter()
    vector_store.save_document(law_doc, embedding)
    logger.info(f"✓ Successfully saved {law_id} to vector store")
    
    return law_doc


def main():
    """Main setup function."""
    configure_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("ANSES1.md Test Setup - Using Pre-existing Markdown")
    logger.info("=" * 60)
    
    try:
        # Check for API key
        if not settings.gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables!")
            logger.error("Please set GEMINI_API_KEY before running this script.")
            sys.exit(1)
        
        logger.info(f"Processed docs path: {settings.processed_docs_path}")
        logger.info(f"ChromaDB path: {settings.chroma_db_path}")
        
        # Find Anses1.md file
        md_file = Path("rag_app/Anses1.md")
        if not md_file.exists():
            # Try alternative location
            md_file = Path("Documentos_Anses/Anses1.md")
        
        if not md_file.exists():
            logger.error("Could not find Anses1.md file!")
            logger.error("Searched in: rag_app/Anses1.md and Documentos_Anses/Anses1.md")
            sys.exit(1)
        
        logger.info(f"Found markdown file: {md_file.absolute()}")
        logger.info("")
        
        # Ingest the document
        logger.info("[1/3] Processing Anses1.md...")
        law_doc = ingest_from_markdown_file(
            md_file_path=str(md_file),
            law_id="ley_anses_001",
            titulo="Documento ANSES - Seguridad Social",
            summary="Documento completo de ANSES sobre leyes y regulaciones de seguridad social en Argentina"
        )
        
        logger.info("")
        logger.info("[2/3] Document Information:")
        logger.info(f"  ID: {law_doc.id}")
        logger.info(f"  Title: {law_doc.titulo}")
        logger.info(f"  File: {law_doc.file_path}")
        logger.info(f"  Summary: {law_doc.summary[:100]}...")
        
        logger.info("")
        logger.info("[3/3] Verification:")
        vector_store = ChromaAdapter()
        total_docs = vector_store.count_documents()
        logger.info(f"  Vector database contains {total_docs} document(s)")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ Setup completed successfully!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Test with: python -m rag_app.tests.audit_performance")
        logger.info("2. Launch UI: streamlit run rag_app/main.py")
        logger.info("")
        
    except Exception as e:
        logger.error(f"\n✗ Setup failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
