from functools import lru_cache

from app.ai.base import AIProvider, AIProviderError
from app.ai.gemini import GeminiProvider
from app.core.config import EMBEDDING_DIMENSIONS, get_settings

__all__ = ["AIProvider", "AIProviderError", "get_ai_provider"]


@lru_cache
def get_ai_provider() -> AIProvider:
    settings = get_settings()

    return GeminiProvider(
        api_key=settings.gemini_api_key,
        llm_model=settings.llm_model,
        embedding_model=settings.embedding_model,
        embedding_dimensions=EMBEDDING_DIMENSIONS,
    )