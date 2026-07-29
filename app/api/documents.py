import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services import document_service, workspace_service
from app.models.user import User

router = APIRouter(prefix="/workspaces/{workspace_id}/documents", tags=["documents"])


@router.post("")
async def upload_document(
    workspace_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Ensures the user actually owns this workspace before letting them upload into it.
    await workspace_service.get_workspace_or_403(db, workspace_id, current_user.id)
    document = await document_service.upload_and_process(db, workspace_id, current_user.id, file)
    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status,
        "file_size_bytes": document.file_size_bytes,
    }


@router.get("")
async def list_documents(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await workspace_service.get_workspace_or_403(db, workspace_id, current_user.id)
    docs = await document_service.list_documents(db, workspace_id)
    return [
        {"id": d.id, "filename": d.filename, "status": d.status, "file_size_bytes": d.file_size_bytes}
        for d in docs
    ]
