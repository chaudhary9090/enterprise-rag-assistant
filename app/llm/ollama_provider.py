import json
from typing import AsyncIterator
import httpx
from app.llm.base import LLMProvider
from app.core.config import settings


class OllamaProvider(LLMProvider):
    """
    Talks to a locally-running Ollama server (e.g. `ollama run llama3`).
    No API key needed — great for demoing the app with zero cloud cost.
    """

    def __init__(self, model: str = "llama3"):
        self.base_url = settings.ollama_base_url
        self.model = model

    async def generate(self, prompt: str, system: str = "") -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json()["response"]

    async def stream(self, prompt: str, system: str = "") -> AsyncIterator[str]:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": True},
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    if data.get("response"):
                        yield data["response"]
