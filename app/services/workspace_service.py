import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import workspace_repository


async def create_workspace(db: AsyncSession, name: str, owner_id: uuid.UUID):
    return await workspace_repository.create_workspace(db, name, owner_id)


async def list_my_workspaces(db: AsyncSession, owner_id: uuid.UUID):
    return await workspace_repository.get_workspaces_for_user(db, owner_id)


async def get_workspace_or_403(db: AsyncSession, workspace_id: uuid.UUID, current_user_id: uuid.UUID):
    """
    Fetches a workspace AND checks the current user actually owns it.
    Every future route that touches a workspace (or its documents) should
    call this first — it's the one place access control is enforced.
    """
    workspace = await workspace_repository.get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if workspace.owner_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your workspace")
    return workspace
