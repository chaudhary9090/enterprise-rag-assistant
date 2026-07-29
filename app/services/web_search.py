"""
Wraps Tavily's search API (https://tavily.com) — a search API built
specifically for feeding results into LLMs, with a free tier that needs
no credit card. This is what gives the chatbot "real-time" knowledge,
the same way ChatGPT/Claude's web search features work: search live,
hand the results to the LLM as context, same as we do with document chunks.
"""
import httpx
from app.core.config import settings


async def web_search(query: str, max_results: int = 3) -> list[dict]:
    """Returns a list of {title, url, content} from a live web search.
    Returns an empty list (never raises) if no API key is set or the
    request fails — so the chatbot still works with documents-only
    if web search isn't configured or is temporarily down."""
    if not settings.tavily_api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
                for r in data.get("results", [])
            ]
    except Exception:
        return []
