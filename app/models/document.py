import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, docx, txt, etc.
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    # simple status tracking for now: "uploaded" -> "processing" -> "indexed" -> "failed"
    # (this becomes meaningful once we add chunking/embeddings in a later step)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
