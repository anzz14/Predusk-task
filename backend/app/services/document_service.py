from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document
from app.models.processing_job import ProcessingJob


class FileTooLargeError(Exception):
	pass


class InvalidFileTypeError(Exception):
	pass


def _coerce_uuid(value: UUID | str) -> UUID:
	return value if isinstance(value, UUID) else UUID(str(value))


def _sanitize_filename(filename: str) -> str:
	cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", filename.strip())
	return cleaned or "upload.txt"


async def create_document(db: AsyncSession, file: UploadFile, user_id: UUID | str) -> Document:
	content_type = file.content_type or ""
	if content_type != "text/plain":
		raise InvalidFileTypeError()

	file_bytes = await file.read()
	if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
		raise FileTooLargeError()

	upload_dir = Path(settings.UPLOAD_DIR)
	upload_dir.mkdir(parents=True, exist_ok=True)

	document_id = uuid4()
	filename = _sanitize_filename(file.filename or "upload.txt")
	file_path = upload_dir / f"{document_id}_{filename}"
	file_path.write_bytes(file_bytes)

	document = Document(
		id=document_id,
		user_id=_coerce_uuid(user_id),
		original_filename=file.filename or filename,
		file_path=str(file_path),
		file_size=len(file_bytes),
		mime_type=content_type,
		upload_timestamp=datetime.now(timezone.utc),
	)
	db.add(document)
	await db.commit()
	await db.refresh(document)
	return document


save_and_create = create_document


async def list_documents(
	db: AsyncSession,
	user_id: UUID | str,
	search: str | None = None,
	status: str | None = None,
	sort_by: str | None = None,
	sort_order: str = "asc",
	page: int = 1,
	page_size: int = 10,
) -> tuple[list[Document], int]:
	sort_by = sort_by or "created_at"
	sort_order = sort_order.lower()

	latest_job_subquery = (
		select(
			ProcessingJob.document_id.label("document_id"),
			func.max(ProcessingJob.created_at).label("max_created_at"),
		)
		.group_by(ProcessingJob.document_id)
		.subquery()
	)
	latest_job = aliased(ProcessingJob)

	sort_columns = {
		"created_at": Document.created_at,
		"upload_timestamp": Document.upload_timestamp,
		"original_filename": Document.original_filename,
		"file_size": Document.file_size,
		"status": latest_job.status,
	}
	sort_column = sort_columns.get(sort_by, Document.created_at)
	if sort_order == "desc":
		sort_column = sort_column.desc()
	else:
		sort_column = sort_column.asc()

	filters = [Document.user_id == _coerce_uuid(user_id)]
	if search:
		filters.append(Document.original_filename.ilike(f"%{search}%"))
	if status:
		filters.append(latest_job.status == status)

	base_query = (
		select(Document)
		.join(latest_job_subquery, latest_job_subquery.c.document_id == Document.id, isouter=True)
		.join(
			latest_job,
			(latest_job.document_id == latest_job_subquery.c.document_id)
			& (latest_job.created_at == latest_job_subquery.c.max_created_at),
			isouter=True,
		)
		.options(selectinload(Document.processing_jobs), selectinload(Document.extracted_result))
		.where(*filters)
		.order_by(sort_column, Document.created_at.desc())
	)

	count_query = (
		select(func.count(func.distinct(Document.id)))
		.select_from(Document)
		.join(latest_job_subquery, latest_job_subquery.c.document_id == Document.id, isouter=True)
		.join(
			latest_job,
			(latest_job.document_id == latest_job_subquery.c.document_id)
			& (latest_job.created_at == latest_job_subquery.c.max_created_at),
			isouter=True,
		)
		.where(*filters)
	)

	result = await db.execute(base_query.offset((page - 1) * page_size).limit(page_size))
	documents = result.scalars().unique().all()

	total = await db.scalar(count_query)
	return documents, int(total or 0)


async def get_document(db: AsyncSession, document_id: UUID | str, user_id: UUID | str) -> Document | None:
	query = (
		select(Document)
		.options(selectinload(Document.processing_jobs), selectinload(Document.extracted_result))
		.where(Document.id == _coerce_uuid(document_id), Document.user_id == _coerce_uuid(user_id))
	)
	result = await db.execute(query)
	return result.scalar_one_or_none()