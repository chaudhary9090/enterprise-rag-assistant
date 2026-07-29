"""
Repository layer: the ONLY place that writes raw database queries for Users.
Services call these functions instead of touching SQLAlchemy queries directly —
this keeps business logic (in services/) separate from data access (here).
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, hashed_password: str, full_name: str | None) -> User:
    user = User(email=email, hashed_password=hashed_password, full_name=full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
