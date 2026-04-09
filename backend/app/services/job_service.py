from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.models.processing_job import ProcessingJob


def _coerce_uuid(value: UUID | str) -> UUID:
	return value if isinstance(value, UUID) else UUID(str(value))


async def create_job(
	db: AsyncSession,
	document_id: UUID | str,
	celery_task_id: str | None = None,
	status: str = "queued",
	current_stage: str = "job_queued",
) -> ProcessingJob:
	job = ProcessingJob(
		document_id=_coerce_uuid(document_id),
		celery_task_id=celery_task_id,
		status=status,
		progress_percentage=0,
		current_stage=current_stage,
		retry_count=0,
	)
	db.add(job)
	await db.commit()
	await db.refresh(job)
	return job


async def create_and_dispatch(db: AsyncSession, document: Document) -> ProcessingJob:
	job = await create_job(db, document.id)

	from app.workers.tasks import analyze_document

	task = analyze_document.delay(str(job.id), str(document.id), document.file_path)
	job.celery_task_id = task.id
	await db.commit()
	await db.refresh(job)
	return job


async def get_job(db: AsyncSession, job_id: UUID | str, user_id: UUID | str) -> ProcessingJob | None:
	query = (
		select(ProcessingJob)
		.join(Document)
		.options(selectinload(ProcessingJob.document))
		.where(ProcessingJob.id == _coerce_uuid(job_id), Document.user_id == _coerce_uuid(user_id))
	)
	result = await db.execute(query)
	return result.scalar_one_or_none()


async def reset_and_redispatch(db: AsyncSession, celery_app: object, job: ProcessingJob) -> ProcessingJob:
	if job.celery_task_id:
		celery_app.control.revoke(job.celery_task_id, terminate=True)

	document = job.document
	if document is None:
		document_result = await db.execute(select(Document).where(Document.id == job.document_id))
		document = document_result.scalar_one()

	job.status = "queued"
	job.progress_percentage = 0
	job.current_stage = "job_queued"
	job.error_message = None
	job.retry_count = 0
	job.started_at = None
	job.completed_at = None

	await db.flush()

	from app.workers.tasks import analyze_document

	task = analyze_document.delay(str(job.id), str(job.document_id), document.file_path)
	job.celery_task_id = task.id

	await db.commit()
	await db.refresh(job)
	return job
