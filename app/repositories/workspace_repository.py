import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace


async def create_workspace(db: AsyncSession, name: str, owner_id: uuid.UUID) -> Workspace:
    workspace = Workspace(name=name, owner_id=owner_id)
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)
    return workspace


async def get_workspaces_for_user(db: AsyncSession, owner_id: uuid.UUID) -> list[Workspace]:
    result = await db.execute(select(Workspace).where(Workspace.owner_id == owner_id))
    return list(result.scalars().all())


async def get_workspace_by_id(db: AsyncSession, workspace_id: uuid.UUID) -> Workspace | None:
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    return result.scalar_one_or_none()
