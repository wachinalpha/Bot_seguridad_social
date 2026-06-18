#!/usr/bin/env python3
"""Index a fetched corpus into ChromaDB."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.config.settings import settings
from rag_app.services.corpus_indexing_service import CorpusIndexingService
from rag_app.utils.logger import configure_logging


def main():
    parser = argparse.ArgumentParser(description="Index a local corpus version into ChromaDB")
    parser.add_argument("--version", help="Corpus version to index. Defaults to CORPUS_VERSION.")
    args = parser.parse_args()

    if args.version and args.version != settings.corpus_version:
        raise SystemExit(
            f"Requested version '{args.version}' does not match active CORPUS_VERSION '{settings.corpus_version}'."
        )

    configure_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Starting corpus indexing into ChromaDB")
    logger.info("=" * 60)

    try:
        if not settings.gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables!")
            sys.exit(1)

        logger.info(f"Corpus path: {settings.corpus_dir_resolved}")
        logger.info(f"ChromaDB path: {settings.chroma_db_path_resolved}")

        embedder = GeminiEmbedder()
        vector_store = ChromaAdapter()
        corpus_indexing_service = CorpusIndexingService(
            embedder=embedder,
            vector_store=vector_store,
        )

        indexed_docs = corpus_indexing_service.index_current_corpus()

        logger.info("=" * 60)
        logger.info(f"✓ Indexed {len(indexed_docs)} documents")
        logger.info(f"Vector database contains {vector_store.count_documents()} documents")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Indexing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
