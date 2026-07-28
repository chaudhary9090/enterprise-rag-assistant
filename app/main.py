from fastapi import FastAPI
from pydantic import BaseModel
from app.core.config import settings
from app.llm.factory import get_llm_provider

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
    }


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask(request: AskRequest):
    try:
        llm = get_llm_provider()
        answer = await llm.generate(
            prompt=request.question,
            system="You are a helpful assistant.",
        )
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e), "error_type": type(e).__name__}