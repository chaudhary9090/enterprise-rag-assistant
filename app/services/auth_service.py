"""
Business logic for authentication. Routes call these functions; these
functions call the repository. Routes never talk to the database directly.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories import user_repository
from app.core.security import hash_password, verify_password, create_access_token


async def signup(db: AsyncSession, email: str, password: str, full_name: str | None):
    existing = await user_repository.get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = await user_repository.create_user(
        db, email=email, hashed_password=hash_password(password), full_name=full_name
    )
    token = create_access_token({"sub": str(user.id)})
    return user, token


async def login(db: AsyncSession, email: str, password: str):
    user = await user_repository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token({"sub": str(user.id)})
    return user, token
