#!/usr/bin/env python3
"""Reset the ChromaDB database by removing all documents.

This script provides an interactive way to clear the entire vector database.
It can be run with confirmation prompts or forced with --force flag.

Usage:
    # Interactive mode (asks for confirmation)
    python -m rag_app.scripts.reset_db
    
    # Force mode (no confirmation)
    python -m rag_app.scripts.reset_db --force
    
    # Verbose mode
    python -m rag_app.scripts.reset_db --verbose
"""
import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_app.config.settings import settings
from rag_app.utils.logger import configure_logging
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.services.removal_service import RemovalService

logger = logging.getLogger(__name__)


def confirm_reset() -> bool:
    """
    Prompt user for confirmation before resetting database.
    
    Returns:
        True if user confirms, False otherwise
    """
    print("\n⚠️  WARNING: This will DELETE ALL documents from the vector database!")
    print(f"   Database location: {settings.chroma_db_path}")
    print(f"   Collection: {settings.chroma_collection_name}\n")
    
    response = input("Are you sure you want to continue? Type 'yes' to confirm: ")
    return response.lower() == 'yes'


def main():
    """Main function to reset the database."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Reset ChromaDB database by removing all documents"
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompt and delete immediately'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    configure_logging(level=log_level)
    
    logger.info("=" * 60)
    logger.info("ChromaDB Reset Script")
    logger.info("=" * 60)
    
    try:
        # Initialize services
        logger.info("Initializing vector store...")
        vector_store = ChromaAdapter()
        removal_service = RemovalService(vector_store=vector_store)
        
        # Get current document count
        doc_count = removal_service.get_document_count()
        logger.info(f"Current documents in database: {doc_count}")
        
        if doc_count == 0:
            print("\n✓ Database is already empty. Nothing to reset.")
            return 0
        
        # Show document list if verbose
        if args.verbose:
            doc_ids = removal_service.list_all_documents()
            print(f"\nDocuments to be deleted ({len(doc_ids)}):")
            for doc_id in doc_ids:
                print(f"  - {doc_id}")
            print()
        
        # Confirm or force
        if not args.force:
            if not confirm_reset():
                print("\n❌ Reset cancelled by user.")
                return 1
        else:
            logger.info("Force mode enabled - skipping confirmation")
        
        # Perform reset
        print("\n🗑️  Deleting all documents...")
        deleted_count = removal_service.remove_all_documents()
        
        # Verify
        final_count = removal_service.get_document_count()
        
        if final_count == 0:
            print(f"\n✅ Successfully deleted {deleted_count} documents")
            print("   Database and processed files have been cleaned.")
            logger.info("Database reset completed successfully")
            return 0
        else:
            print(f"\n⚠️  Warning: {final_count} documents still remain in database")
            logger.warning(f"Reset incomplete: {final_count} documents remain")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n❌ Reset cancelled by user (Ctrl+C)")
        return 1
        
    except Exception as e:
        logger.error(f"Error during reset: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
