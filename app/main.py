from fastapi import FastAPI
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import engine, Base
from app.llm.factory import get_llm_provider
from app.api.auth import router as auth_router

# Importing the model so SQLAlchemy knows about the `users` table
# before create_all() runs below.
from app.models.user import User  # noqa: F401

app = FastAPI(title=settings.app_name)
app.include_router(auth_router)


@app.on_event("startup")
async def on_startup():
    """
    Creates database tables if they don't exist yet.
    NOTE: this is a simple approach for now — a real production app would use
    Alembic migrations instead (so schema changes are tracked and reversible).
    We'll add Alembic in a later step once the schema has settled down.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    """Simple endpoint to prove the server is alive and show which LLM is active."""
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
    }


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask(request: AskRequest):
    """
    Temporary test route — NOT the real RAG endpoint yet.
    This just proves the LLM provider factory works end-to-end before
    we add retrieval on top of it in a later step.
    """
    try:
        llm = get_llm_provider()
        answer = await llm.generate(
            prompt=request.question,
            system="You are a helpful assistant.",
        )
        return {"answer": answer}
    except Exception as e:
        # Returning the real error in the response itself (instead of a
        # generic 500) so it's visible right in the browser/docs page —
        # no need to go dig through terminal logs.
        return {"error": str(e), "error_type": type(e).__name__}
