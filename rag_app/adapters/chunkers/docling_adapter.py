from docling.document_converter import DocumentConverter
from pathlib import Path
from typing import Tuple
import logging

from rag_app.config.settings import settings

logger = logging.getLogger(__name__)


class DoclingAdapter:
    """Adapter for processing legal documents using Docling."""
    
    def __init__(self):
        """Initialize the Docling document converter."""
        self.converter = DocumentConverter()
        self.output_dir = Path(settings.processed_docs_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_url(self, url: str, law_id: str) -> Tuple[str, str]:
        """
        Process a law URL and convert to markdown.
        
        Args:
            url: URL of the legal document
            law_id: Unique identifier for the law
            
        Returns:
            Tuple of (file_path, markdown_content)
        """
        try:
            logger.info(f"Processing URL for law {law_id}: {url}")
            
            # Convert document using Docling
            result = self.converter.convert(url).document
            
            # Export to markdown
            markdown_content = result.export_to_markdown()
            
            # Save to file
            file_path = self.output_dir / f"{law_id}.md"
            file_path.write_text(markdown_content, encoding='utf-8')
            
            logger.info(f"Successfully processed {law_id} -> {file_path}")
            return str(file_path), markdown_content
            
        except Exception as e:
            logger.error(f"Error processing {law_id} from {url}: {e}")
            raise
