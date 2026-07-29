from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.workspace import WorkspaceCreate, WorkspaceOut
from app.services import workspace_service
from app.models.user import User

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceOut)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await workspace_service.create_workspace(db, payload.name, current_user.id)


@router.get("", response_model=list[WorkspaceOut])
async def list_my_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await workspace_service.list_my_workspaces(db, current_user.id)
