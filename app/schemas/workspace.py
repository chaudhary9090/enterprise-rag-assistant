from pydantic import BaseModel
from datetime import datetime
import uuid


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceOut(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
