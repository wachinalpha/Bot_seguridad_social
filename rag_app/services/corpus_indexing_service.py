import json
import logging
from pathlib import Path

from rag_app.config.settings import settings
from rag_app.domain.models import LawDocument

logger = logging.getLogger(__name__)


class CorpusIndexingService:
    """Indexes a pre-built corpus into the vector store."""

    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

    def index_current_corpus(self) -> list[LawDocument]:
        index_path = settings.corpus_documents_index_path_resolved
        logger.info(f"Loading corpus index from {index_path}")

        if not index_path.exists():
            raise FileNotFoundError(
                f"Corpus index not found: {index_path}. Fetch or copy the corpus first."
            )

        raw_documents = json.loads(index_path.read_text(encoding="utf-8"))
        indexed_documents: list[LawDocument] = []

        for raw_document in raw_documents:
            law_document = self.index_document(raw_document)
            indexed_documents.append(law_document)

        logger.info(f"Indexed {len(indexed_documents)} documents for corpus {settings.corpus_version}")
        return indexed_documents

    def index_document(self, raw_document: dict) -> LawDocument:
        file_path = settings.corpus_dir_resolved / raw_document["path"]
        if not file_path.exists():
            raise FileNotFoundError(f"Corpus document file not found: {file_path}")

        law_document = LawDocument(
            id=raw_document["id"],
            titulo=raw_document.get("title", raw_document["id"]),
            url=raw_document.get("source_url", ""),
            file_path=str(file_path),
            summary=raw_document.get("summary"),
            metadata={
                "categoria": raw_document.get("category"),
                "año": raw_document.get("year"),
                "descripcion_breve": raw_document.get("description", ""),
                "corpus_version": raw_document.get("corpus_version", settings.corpus_version),
            },
        )

        embed_document = getattr(self.embedder, "embed_document", self.embedder.embed_text)
        embedding = embed_document(law_document.searchable_text)
        self.vector_store.save_document(law_document, embedding)
        return law_document
