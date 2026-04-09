from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProcessingJob(Base):
	__tablename__ = "processing_jobs"

	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
	document_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
	celery_task_id: Mapped[str | None] = mapped_column(String, nullable=True)
	status: Mapped[str] = mapped_column(String, nullable=False, index=True, server_default=text("'queued'"))
	progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
	current_stage: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'job_queued'"))
	error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
	retry_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
	meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
	started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

	document: Mapped[Document] = relationship(back_populates="processing_jobs")