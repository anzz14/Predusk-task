from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Float, Integer, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ExtractedResult(Base):
	__tablename__ = "extracted_results"
	__table_args__ = (UniqueConstraint("document_id", name="uq_extracted_results_document_id"),)

	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
	document_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
	job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("processing_jobs.id"), nullable=False)
	word_count: Mapped[int] = mapped_column(Integer, nullable=False)
	readability_score: Mapped[float] = mapped_column(Float, nullable=False)
	primary_keywords: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
	auto_summary: Mapped[str] = mapped_column(Text, nullable=False)
	user_edited_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
	is_finalized: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
	finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
	updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())

	document: Mapped[Document] = relationship(back_populates="extracted_result")