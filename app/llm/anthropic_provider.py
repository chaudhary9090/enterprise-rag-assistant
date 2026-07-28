from typing import AsyncIterator
from anthropic import AsyncAnthropic
from app.llm.base import LLMProvider
from app.core.config import settings


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = model

    async def generate(self, prompt: str, system: str = "") -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def stream(self, prompt: str, system: str = "") -> AsyncIterator[str]:
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
