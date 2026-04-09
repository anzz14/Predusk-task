from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.extracted_result import ExtractedResult
from app.models.processing_job import ProcessingJob


class AlreadyFinalizedError(Exception):
	pass


class StaleResultError(Exception):
	pass


def _coerce_uuid(value: UUID | str) -> UUID:
	return value if isinstance(value, UUID) else UUID(str(value))


async def _get_owned_result(
	db: AsyncSession,
	document_id: UUID | str,
	user_id: UUID | str,
) -> ExtractedResult | None:
	query = (
		select(ExtractedResult)
		.join(Document)
		.where(ExtractedResult.document_id == _coerce_uuid(document_id), Document.user_id == _coerce_uuid(user_id))
	)
	result = await db.execute(query)
	return result.scalar_one_or_none()


async def patch_summary(
	db: AsyncSession,
	document_id: UUID | str,
	user_id: UUID | str,
	summary: str,
) -> ExtractedResult | None:
	result = await _get_owned_result(db, document_id, user_id)
	if result is None:
		return None

	result.user_edited_summary = summary
	await db.commit()
	await db.refresh(result)
	return result


async def finalize(db: AsyncSession, document_id: UUID | str, user_id: UUID | str) -> ExtractedResult | None:
	result = await _get_owned_result(db, document_id, user_id)
	if result is None:
		return None

	if result.is_finalized:
		raise AlreadyFinalizedError()

	latest_job_query = (
		select(ProcessingJob)
		.where(ProcessingJob.document_id == result.document_id)
		.order_by(desc(ProcessingJob.created_at), desc(ProcessingJob.id))
		.limit(1)
	)
	latest_job_result = await db.execute(latest_job_query)
	latest_job = latest_job_result.scalar_one_or_none()
	if latest_job is None or latest_job.id != result.job_id:
		raise StaleResultError()

	result.is_finalized = True
	result.finalized_at = datetime.now(timezone.utc)
	latest_job.status = "finalized"

	await db.commit()
	await db.refresh(result)
	return result