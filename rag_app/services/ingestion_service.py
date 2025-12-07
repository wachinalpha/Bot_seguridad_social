import json
import logging
from pathlib import Path
from typing import List

from rag_app.domain.models import LawDocument
from rag_app.config.settings import settings

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting laws: Web → MD → Vector"""
    
    def __init__(self, document_processor, embedder, vector_store):
        """
        Initialize ingestion service with dependencies.
        
        Args:
            document_processor: Implementation of DocumentProcessorPort
            embedder: Implementation of EmbedderPort
            vector_store: Implementation of VectorStorePort
        """
        self.document_processor = document_processor
        self.embedder = embedder
        self.vector_store = vector_store
    
    def ingest_from_config(self, config_path: str = None) -> List[LawDocument]:
        """
        Ingest all laws from the configuration file.
        
        Args:
            config_path: Path to leyes_config.json (defaults to settings)
            
        Returns:
            List of processed LawDocument instances
        """
        if config_path is None:
            config_path = Path(settings.base_dir) / "rag_app" / "config" / "leyes_config.json"
        
        logger.info(f"Loading configuration from {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        laws = config.get('leyes', [])
        logger.info(f"Found {len(laws)} laws to process")
        
        processed_docs = []
        
        for law_config in laws:
            try:
                law_doc = self.ingest_law(law_config)
                processed_docs.append(law_doc)
                logger.info(f"✓ Successfully ingested law {law_doc.id}")
            except Exception as e:
                logger.error(f"✗ Failed to ingest law {law_config.get('numero')}: {e}")
        
        logger.info(f"Ingestion complete: {len(processed_docs)}/{len(laws)} laws processed")
        return processed_docs
    
    def ingest_law(self, law_config: dict) -> LawDocument:
        """
        Ingest a single law from configuration.
        
        Args:
            law_config: Dictionary with law metadata
            
        Returns:
            Processed and indexed LawDocument
        """
        # Extract law metadata
        numero = law_config['numero']
        nombre = law_config['nombre']
        url = law_config['url']
        law_id = f"ley_{numero}"
        
        logger.info(f"Processing law {law_id}: {nombre}")
        
        # Step 1: Process URL → Markdown
        file_path, markdown_content = self.document_processor.process_url(url, law_id)
        
        # Step 2: Extract summary (first 500 characters or first paragraph)
        summary = self._extract_summary(markdown_content, nombre)
        
        # Step 3: Create LawDocument
        law_doc = LawDocument(
            id=law_id,
            titulo=nombre,
            url=url,
            file_path=file_path,
            summary=summary,
            metadata={
                'numero': numero,
                'año': law_config.get('año'),
                'categoria': law_config.get('categoria'),
                'descripcion_breve': law_config.get('descripcion_breve', '')
            }
        )
        
        # Step 4: Generate embedding for searchable text (title + summary)
        searchable_text = law_doc.searchable_text
        embedding = self.embedder.embed_text(searchable_text)
        
        # Step 5: Save to vector store
        self.vector_store.save_document(law_doc, embedding)
        
        return law_doc
    
    def _extract_summary(self, markdown_content: str, title: str) -> str:
        """
        Extract a summary from markdown content.
        
        Args:
            markdown_content: Full markdown text
            title: Law title
            
        Returns:
            Brief summary text
        """
        # Take first 500 characters as summary, or find first meaningful paragraph
        lines = markdown_content.split('\n')
        
        summary_parts = []
        char_count = 0
        max_chars = 500
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and headers that match the title
            if not line or line.startswith('#'):
                continue
            
            summary_parts.append(line)
            char_count += len(line)
            
            if char_count >= max_chars:
                break
        
        summary = ' '.join(summary_parts)[:max_chars]
        
        if len(summary) < 50:
            # Fallback: use title if summary is too short
            summary = f"Texto completo de la {title}"
        
        return summary
