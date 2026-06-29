from dataclasses import dataclass

from rag_app.adapters.contextualizers.gemini_manager import GeminiManager
from rag_app.adapters.contextualizers.nvidia_generator import NvidiaGenerator
from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder
from rag_app.adapters.embedders.nvidia_embedder import NvidiaEmbedder
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.config.settings import settings
from rag_app.services.retrieval_service import RetrievalService


@dataclass(frozen=True)
class ModelOption:
    provider: str
    model: str
    label: str


EMBEDDING_MODEL_OPTIONS = [
    ModelOption("gemini", "models/gemini-embedding-001", "Gemini embedding 001"),
    ModelOption("nvidia", "nvidia/llama-nemotron-embed-1b-v2", "NVIDIA Llama Nemotron Embed 1B v2"),
]

GENERATION_MODEL_OPTIONS = [
    ModelOption("gemini", "gemini-2.5-flash", "Gemini 2.5 Flash"),
    ModelOption("gemini", "models/gemini-1.5-pro", "Gemini 1.5 Pro"),
    ModelOption("nvidia", "nvidia/nemotron-3-nano-30b-a3b", "NVIDIA Nemotron 3 Nano 30B A3B"),
]


def _normalize(provider: str | None) -> str:
    return settings.normalize_provider(provider)


def create_embedder(provider: str | None = None, model: str | None = None):
    active_provider = _normalize(provider or settings.active_embedding_provider)
    active_model = model or _default_embedding_model_for(active_provider, provider is not None)

    if active_provider == "gemini":
        return GeminiEmbedder(model_name=active_model)
    if active_provider == "nvidia":
        return NvidiaEmbedder(model_name=active_model)

    raise ValueError(f"Unsupported embedding provider: {active_provider}")


def create_generator(provider: str | None = None, model: str | None = None):
    active_provider = _normalize(provider or settings.active_generation_provider)
    active_model = model or _default_generation_model_for(active_provider, provider is not None)

    if active_provider == "gemini":
        return GeminiManager(model_name=active_model)
    if active_provider == "nvidia":
        return NvidiaGenerator(model_name=active_model)

    raise ValueError(f"Unsupported generation provider: {active_provider}")


def create_retrieval_service(
    embedding_provider: str | None = None,
    embedding_model: str | None = None,
    generation_provider: str | None = None,
    generation_model: str | None = None,
) -> RetrievalService:
    active_embedding_provider = _normalize(embedding_provider or settings.active_embedding_provider)
    active_embedding_model = embedding_model or _default_embedding_model_for(
        active_embedding_provider,
        embedding_provider is not None,
    )

    embedder = create_embedder(active_embedding_provider, active_embedding_model)
    vector_store = ChromaAdapter(
        embedding_provider=active_embedding_provider,
        embedding_model=active_embedding_model,
    )
    contextualizer = create_generator(generation_provider, generation_model)

    return RetrievalService(
        embedder=embedder,
        vector_store=vector_store,
        contextualizer=contextualizer,
    )


def _default_embedding_model_for(provider: str, provider_was_supplied: bool) -> str:
    if not provider_was_supplied or provider == settings.active_embedding_provider:
        return settings.active_embedding_model
    return settings.default_embedding_model_for(provider)


def _default_generation_model_for(provider: str, provider_was_supplied: bool) -> str:
    if not provider_was_supplied or provider == settings.active_generation_provider:
        return settings.active_generation_model
    return settings.default_generation_model_for(provider)


def get_embedding_model_options() -> list[ModelOption]:
    return _with_active_option(
        EMBEDDING_MODEL_OPTIONS,
        settings.active_embedding_provider,
        settings.active_embedding_model,
        "Configured embedding model",
    )


def get_generation_model_options() -> list[ModelOption]:
    return _with_active_option(
        GENERATION_MODEL_OPTIONS,
        settings.active_generation_provider,
        settings.active_generation_model,
        "Configured generation model",
    )


def _with_active_option(
    options: list[ModelOption],
    provider: str,
    model: str,
    label: str,
) -> list[ModelOption]:
    if any(option.provider == provider and option.model == model for option in options):
        return options
    return [ModelOption(provider, model, label), *options]
