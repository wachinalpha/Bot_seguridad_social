import logging
import time
from typing import List

import requests

from rag_app.config.settings import settings


logger = logging.getLogger(__name__)


class NvidiaEmbedder:
    """Adapter for embeddings using NVIDIA NIM OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        base_url: str | None = None,
    ):
        api_key = api_key or settings.nvidia_api_key
        if not api_key:
            raise ValueError("NVIDIA_API_KEY is required for NVIDIA embeddings")

        self.api_key = api_key
        self.model_name = model_name or settings.active_embedding_model
        self.base_url = (base_url or settings.nvidia_base_url).rstrip("/")
        self.timeout = settings.request_timeout
        logger.info(f"Initialized NvidiaEmbedder with model: {self.model_name}")

    def embed_text(self, text: str, input_type: str | None = None) -> List[float]:
        try:
            return self._embed_batch([text], input_type=input_type)[0]
        except Exception as e:
            logger.error(f"Error embedding text with NVIDIA: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        return self.embed_text(text, input_type=settings.nvidia_embedding_query_input_type)

    def embed_document(self, text: str) -> List[float]:
        return self.embed_text(text, input_type=settings.nvidia_embedding_document_input_type)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self._embed_batch(texts, input_type=settings.nvidia_embedding_document_input_type)

    def _embed_batch(self, texts: List[str], input_type: str | None = None) -> List[List[float]]:
        payload = {
            "model": self.model_name,
            "input": texts,
            "encoding_format": "float",
            "truncate": settings.nvidia_embedding_truncate,
        }

        if input_type:
            payload["input_type"] = input_type
        if settings.nvidia_embedding_dimensions:
            payload["dimensions"] = settings.nvidia_embedding_dimensions

        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json().get("data") or []
        if len(data) != len(texts):
            raise ValueError(f"Expected {len(texts)} embeddings, got {len(data)}")

        data.sort(key=lambda item: item.get("index", 0))
        return [item["embedding"] for item in data]

    def embed_batch_with_delay(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for i, text in enumerate(texts):
            if i > 0:
                time.sleep(0.1)
            embeddings.append(self.embed_document(text))
        return embeddings
