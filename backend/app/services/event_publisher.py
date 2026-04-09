from __future__ import annotations

import inspect
import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processing_job import ProcessingJob


logger = logging.getLogger(__name__)


def _coerce_uuid(value: UUID | str) -> UUID:
	return value if isinstance(value, UUID) else UUID(str(value))


async def publish_and_persist(
	db: AsyncSession,
	redis_client: Any,
	job_id: UUID | str,
	stage: str,
	progress: int,
	message: str,
) -> None:
	job_uuid = _coerce_uuid(job_id)
	await db.execute(
		update(ProcessingJob)
		.where(ProcessingJob.id == job_uuid)
		.values(progress_percentage=progress, current_stage=stage)
	)
	await db.commit()

	payload = {
		"job_id": str(job_uuid),
		"stage": stage,
		"progress": progress,
		"message": message,
		"timestamp": datetime.now(timezone.utc).isoformat(),
	}
	try:
		publish_result = redis_client.publish(f"job_progress:{job_uuid}", json.dumps(payload))
		if inspect.isawaitable(publish_result):
			await publish_result
	except Exception:
		logger.exception("Failed to publish job progress event for %s", job_uuid)


async def subscribe_to_job(job_id: UUID | str, redis_client: Any) -> Any:
	job_uuid = _coerce_uuid(job_id)
	pubsub = redis_client.pubsub()
	subscribe_result = pubsub.subscribe(f"job_progress:{job_uuid}")
	if inspect.isawaitable(subscribe_result):
		await subscribe_result
	return pubsub