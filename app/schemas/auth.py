from pydantic import BaseModel, EmailStr
import uuid


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None

    class Config:
        from_attributes = True  # lets this schema build directly from a SQLAlchemy User object


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
