from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    app_name: str = "Enterprise RAG Knowledge Assistant"
    environment: Literal["dev", "prod"] = "dev"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    database_url: str = "postgresql+asyncpg://rag_user:rag_pass@localhost:5432/rag_db"
    redis_url: str = "redis://localhost:6379/0"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"

    llm_provider: Literal["openai", "anthropic", "ollama", "groq"] = "openai"
    embedding_provider: Literal["openai", "bge"] = "openai"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    groq_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
