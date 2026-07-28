from functools import lru_cache
from app.llm.base import LLMProvider
from app.core.config import settings


@lru_cache
def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider

    if provider == "openai":
        from app.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()

    if provider == "groq":
        from app.llm.openai_provider import OpenAIProvider
        return OpenAIProvider(
            model="llama-3.1-8b-instant",
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    if provider == "anthropic":
        from app.llm.anthropic_provider import AnthropicProvider
        return AnthropicProvider()

    if provider == "ollama":
        from app.llm.ollama_provider import OllamaProvider
        return OllamaProvider()

    raise ValueError(f"Unknown LLM provider: {provider}")
