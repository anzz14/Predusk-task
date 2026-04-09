from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from redis.asyncio import from_url as redis_from_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.job import JobResponse
from app.services import event_publisher, job_service
from app.workers.celery_app import celery_app


router = APIRouter(prefix="/jobs", tags=["jobs"], dependencies=[Depends(get_current_user)])


def _build_event(job) -> dict[str, object]:
	stage_map = {
		"completed": "job_completed",
		"failed": "job_failed",
		"finalized": "job_finalized",
	}
	stage = job.current_stage or stage_map.get(job.status, f"job_{job.status}")
	return {
		"job_id": str(job.id),
		"stage": stage,
		"progress": job.progress_percentage,
		"message": job.error_message or stage,
	}


def _is_terminal_stage(stage: str) -> bool:
	return stage in {"job_completed", "job_failed", "job_finalized"}


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(job_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	job = await job_service.get_job(db, job_id, current_user.id)
	if job is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
	if job.status != "failed":
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only failed jobs can be retried")
	job = await job_service.reset_and_redispatch(db, celery_app, job)
	return JobResponse.model_validate(job)


@router.get("/{job_id}/progress/stream")
async def stream_progress(job_id: str, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	job = await job_service.get_job(db, job_id, current_user.id)
	if job is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

	redis_client = redis_from_url(settings.REDIS_URL, decode_responses=True)

	async def event_generator():
		pubsub = None
		try:
			initial_event = _build_event(job)
			if _is_terminal_stage(str(initial_event["stage"])):
				yield f"data: {json.dumps(initial_event)}\n\n"
				return

			pubsub = await event_publisher.subscribe_to_job(job_id, redis_client)
			try:
				while True:
					if await request.is_disconnected():
						break

					message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
					if not message:
						continue

					payload = message.get("data")
					if isinstance(payload, bytes):
						payload = payload.decode("utf-8")
					if not isinstance(payload, str):
						payload = json.dumps(payload)
					yield f"data: {payload}\n\n"
					try:
						parsed = json.loads(payload)
					except json.JSONDecodeError:
						parsed = {}
					if _is_terminal_stage(str(parsed.get("stage", ""))):
						break
			finally:
				if pubsub is not None:
					await pubsub.unsubscribe()
					await pubsub.close()
		finally:
			await redis_client.close()

	return StreamingResponse(event_generator(), media_type="text/event-stream")