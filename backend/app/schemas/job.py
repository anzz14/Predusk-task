from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	document_id: UUID
	celery_task_id: str | None = None
	status: str
	progress_percentage: int
	current_stage: str
	error_message: str | None = None
	retry_count: int
	started_at: datetime | None = None
	completed_at: datetime | None = None
	created_at: datetime


class JobStatusResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	status: str
	progress_percentage: int