from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import engine, Base
from app.llm.factory import get_llm_provider
from app.api.auth import router as auth_router
from app.api.workspaces import router as workspaces_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router

# Importing models so SQLAlchemy knows about these tables before create_all() runs.
from app.models.user import User  # noqa: F401
from app.models.workspace import Workspace  # noqa: F401
from app.models.document import Document  # noqa: F401

app = FastAPI(title=settings.app_name)

# Allows the frontend (a local HTML file, or later a dev server on another
# port) to call this API. Wide open here since this is local dev only —
# a real production deployment would restrict this to the actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(documents_router)
app.include_router(chat_router)


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
