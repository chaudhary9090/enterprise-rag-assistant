from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.auth import UserSignup, UserLogin, UserOut, Token
from app.services import auth_service
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token)
async def signup(payload: UserSignup, db: AsyncSession = Depends(get_db)):
    user, token = await auth_service.signup(db, payload.email, payload.password, payload.full_name)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    user, token = await auth_service.login(db, payload.email, payload.password)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)):
    """
    Protected route: only reachable with a valid JWT in the
    'Authorization: Bearer <token>' header. Proves auth works end-to-end.
    """
    return current_user
