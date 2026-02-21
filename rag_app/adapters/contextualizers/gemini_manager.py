from google import genai
from google.genai import types
from pathlib import Path
import logging

from rag_app.domain.models import LawDocument
from rag_app.config.settings import settings

logger = logging.getLogger(__name__)


class GeminiManager:
    """Adapter for generating answers using Gemini API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Gemini manager.
        
        Args:
            api_key: Gemini API key (defaults to settings)
        """
        api_key = api_key or settings.gemini_api_key
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.llm_model
        logger.info(f"Initialized GeminiManager with model: {self.model_name}")
    
    def generate_answer(self, query: str, law_doc: LawDocument) -> str:
        """
        Generate answer to a query using full law context.
        
        Args:
            query: User's question
            law_doc: Law document with file_path to markdown content
            
        Returns:
            Generated answer from the LLM
        """
        try:
            # Read law content
            if not law_doc.file_path or not Path(law_doc.file_path).exists():
                raise ValueError(f"File path not found: {law_doc.file_path}")
            
            content = Path(law_doc.file_path).read_text(encoding='utf-8')
            
            system_instruction = f"""Eres un asistente experto en leyes de Seguridad Social de Argentina.

Tienes acceso al texto completo de la siguiente ley:
- Título: {law_doc.titulo}
- Número: {law_doc.metadata.get('numero', 'N/A')}

Tu trabajo es responder preguntas sobre esta ley de manera precisa y profesional.
Siempre cita los artículos específicos cuando sea relevante."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[content, query],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                ),
            )
            
            logger.info(f"Generated answer for law {law_doc.id}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
