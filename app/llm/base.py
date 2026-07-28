"""
The LLM contract.

Every provider (OpenAI, Claude, Ollama) must implement `generate()` and
`stream()` with this exact signature. Nothing else in the app is allowed
to import openai/anthropic/ollama directly — only these adapter files do.
That rule is what lets us swap providers via one config value.
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system: str = "") -> str:
        """Return a full response as a single string."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, prompt: str, system: str = "") -> AsyncIterator[str]:
        """Yield the response token-by-token (for streaming to the frontend)."""
        raise NotImplementedError
        yield  # pragma: no cover  (makes this an async generator for type-checkers)
