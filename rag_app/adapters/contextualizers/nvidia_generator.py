import logging
from typing import Sequence

import requests

from rag_app.adapters.contextualizers.prompts import SYSTEM_PROMPT, build_task_prompt, extract_final_answer
from rag_app.config.settings import settings
from rag_app.domain.models import LawDocument


logger = logging.getLogger(__name__)


class NvidiaGenerator:
    """Adapter for answer generation using NVIDIA NIM OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        base_url: str | None = None,
    ):
        api_key = api_key or settings.nvidia_api_key
        if not api_key:
            raise ValueError("NVIDIA_API_KEY is required for NVIDIA generation")

        self.api_key = api_key
        self.model_name = model_name or settings.active_generation_model
        self.base_url = (base_url or settings.nvidia_base_url).rstrip("/")
        self.timeout = settings.request_timeout
        logger.info(f"Initialized NvidiaGenerator with model: {self.model_name}")

    def generate_answer(self, query: str, law_docs: Sequence[LawDocument]) -> str:
        try:
            task_prompt, context_count, titles = build_task_prompt(query, law_docs)
            logger.info(f"Generating answer using {context_count} laws: {titles}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": task_prompt},
                    ],
                    "temperature": settings.generation_temperature,
                    "max_tokens": settings.generation_max_tokens,
                    "chat_template_kwargs": {"enable_thinking": False},
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()

            choices = payload.get("choices") or []
            if not choices:
                raise ValueError("NVIDIA response did not include choices")

            message = choices[0].get("message") or {}
            answer = message.get("content") or choices[0].get("text")
            if not answer:
                raise ValueError("NVIDIA response did not include answer text")

            logger.info(f"Generated answer using {context_count} law(s)")
            return extract_final_answer(answer)

        except Exception as e:
            logger.error(f"Error generating NVIDIA answer: {e}")
            raise
