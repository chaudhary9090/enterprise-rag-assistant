import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import document_repository
from app.services.text_extraction import extract_text
from app.services.chunking import chunk_text
from app.vectorstore import qdrant_store

UPLOAD_DIR = "uploaded_files"
ALLOWED_TYPES = {"pdf", "docx", "txt", "md"}


async def upload_and_process(db: AsyncSession, workspace_id: uuid.UUID, uploaded_by: uuid.UUID, file: UploadFile):
    file_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Allowed: {ALLOWED_TYPES}",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_filename = f"{uuid.uuid4()}_{file.filename}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    contents = await file.read()
    with open(saved_path, "wb") as f:
        f.write(contents)

    document = await document_repository.create_document(
        db, workspace_id=workspace_id, uploaded_by=uploaded_by,
        filename=file.filename, file_type=file_ext, file_size_bytes=len(contents),
    )

    # Process synchronously for now (fine for small files / a portfolio demo).
    # A production app would do this in a background task/queue instead,
    # so upload responds instantly while processing happens separately.
    try:
        await document_repository.update_status(db, document.id, "processing")
        text = extract_text(saved_path, file_ext)
        chunks = chunk_text(text)
        if chunks:
            qdrant_store.upsert_chunks(str(document.id), str(workspace_id), chunks)
        await document_repository.update_status(db, document.id, "indexed")
    except Exception as e:
        await document_repository.update_status(db, document.id, "failed")
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return document


async def list_documents(db: AsyncSession, workspace_id: uuid.UUID):
    return await document_repository.get_documents_for_workspace(db, workspace_id)
