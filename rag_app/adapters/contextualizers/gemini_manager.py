from google import genai
from google.genai import types
import logging
from typing import Sequence

from rag_app.domain.models import LawDocument
from rag_app.config.settings import settings
from rag_app.adapters.contextualizers.prompts import SYSTEM_PROMPT, build_task_prompt

logger = logging.getLogger(__name__)


class GeminiManager:
    """Adapter for generating answers using Gemini API."""
    
    def __init__(self, api_key: str = None, model_name: str | None = None):
        api_key = api_key or settings.gemini_api_key
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini generation")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name or settings.active_generation_model
        logger.info(f"Initialized GeminiManager with model: {self.model_name}")
    
    def generate_answer(self, query: str, law_docs: Sequence[LawDocument]) -> str:
        """
        Generate answer to a query using full law context from multiple documents.
        
        Args:
            query: User's question
            law_docs: List of law documents with file_path to markdown content
            
        Returns:
            Generated answer from the LLM
        """
        try:
            task_prompt, context_count, titles = build_task_prompt(query, law_docs)
            logger.info(f"Generating answer using {context_count} laws: {titles}")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=task_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
            
            logger.info(f"Generated answer using {context_count} law(s)")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
