"""
Sets up the database connection.

Why async: FastAPI is async end-to-end, so we use `asyncpg` (a fast async
Postgres driver) instead of the traditional blocking `psycopg2`. This means
the server can handle other requests while waiting on a database query,
instead of freezing.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    """Every SQLAlchemy model (User, Workspace, Document...) inherits from this."""
    pass


async def get_db():
    """
    FastAPI dependency: gives each request its own database session,
    and guarantees it's closed afterward, even if an error occurs.
    Used like: `db: AsyncSession = Depends(get_db)` in route functions.
    """
    async with AsyncSessionLocal() as session:
        yield session
