"""
Central configuration for the whole app.

Why this file exists:
Instead of scattering `os.getenv("OPENAI_API_KEY")` calls all over the codebase,
we read every setting ONCE here, validate it, and import `settings` everywhere
else. This is the standard FastAPI pattern (uses pydantic-settings).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "Enterprise RAG Knowledge Assistant"
    environment: Literal["dev", "prod"] = "dev"

    # --- Security ---
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 1 day

    # --- Database ---
    database_url: str = "postgresql+asyncpg://rag_user:rag_pass@localhost:5432/rag_db"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Vector store ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"
    qdrant_local_path: str = "./qdrant_data"  # embedded mode: local folder, no server needed

    # --- LLM provider selection ---
    # This one field is what makes the whole app "provider-agnostic":
    # change it (or override via env var) and every LLM call in the app
    # routes to a different provider, with zero other code changes.
    llm_provider: Literal["openai", "anthropic", "ollama", "groq"] = "openai"
    embedding_provider: Literal["openai", "bge"] = "openai"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    groq_api_key: str = ""
    tavily_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Import this single object anywhere you need a setting:
#   from app.core.config import settings
#   settings.llm_provider
settings = Settings()
