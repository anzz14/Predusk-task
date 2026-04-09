from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
	__tablename__ = "documents"

	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
	user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
	original_filename: Mapped[str] = mapped_column(String, nullable=False)
	file_path: Mapped[str] = mapped_column(String, nullable=False)
	file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
	mime_type: Mapped[str] = mapped_column(String, nullable=False)
	upload_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

	user: Mapped[User] = relationship(back_populates="documents")
	processing_jobs: Mapped[list[ProcessingJob]] = relationship(back_populates="document", cascade="all, delete-orphan")
	extracted_result: Mapped[ExtractedResult | None] = relationship(back_populates="document", uselist=False)