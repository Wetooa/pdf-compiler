"""SQLAlchemy models for batches and blobs."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all models."""
    pass


class Batch(Base):
    """Batch metadata for a PDF processing job."""
    __tablename__ = "batches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="processing"
    )  # processing | completed | completed_with_errors | failed
    pdf_count: Mapped[int] = mapped_column(default=0, nullable=False)
    pdf_names: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    failed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compiled_pdf: Mapped[Optional[bool]] = mapped_column(
        default=False, nullable=False
    )  # True if a compiled_pdf blob exists
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    blobs: Mapped[List["Blob"]] = relationship(
        "Blob", back_populates="batch", cascade="all, delete-orphan"
    )


class Blob(Base):
    """Binary artifact for a batch (e.g. compiled PDF)."""
    __tablename__ = "blobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # e.g. compiled_pdf
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    batch: Mapped["Batch"] = relationship("Batch", back_populates="blobs")
