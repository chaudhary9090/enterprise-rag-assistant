import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services import workspace_service, rag_chat_service
from app.models.user import User

router = APIRouter(prefix="/workspaces/{workspace_id}/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("")
async def chat(
    workspace_id: uuid.UUID,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    THE real chatbot: answers using only documents uploaded to this workspace,
    with source citations — unlike /ask, which is a general, ungrounded chatbot.
    """
    await workspace_service.get_workspace_or_403(db, workspace_id, current_user.id)
    result = await rag_chat_service.answer_question(str(workspace_id), payload.question)
    return result
