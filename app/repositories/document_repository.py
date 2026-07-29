import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document


async def create_document(
    db: AsyncSession, workspace_id: uuid.UUID, uploaded_by: uuid.UUID,
    filename: str, file_type: str, file_size_bytes: int,
) -> Document:
    document = Document(
        workspace_id=workspace_id, uploaded_by=uploaded_by,
        filename=filename, file_type=file_type, file_size_bytes=file_size_bytes,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def update_status(db: AsyncSession, document_id: uuid.UUID, status: str):
    doc = await db.get(Document, document_id)
    if doc:
        doc.status = status
        await db.commit()


async def get_documents_for_workspace(db: AsyncSession, workspace_id: uuid.UUID) -> list[Document]:
    result = await db.execute(select(Document).where(Document.workspace_id == workspace_id))
    return list(result.scalars().all())
