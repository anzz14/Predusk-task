from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractedResultResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	document_id: UUID
	job_id: UUID
	word_count: int
	readability_score: float
	primary_keywords: list[dict]
	auto_summary: str
	user_edited_summary: str | None = None
	is_finalized: bool
	finalized_at: datetime | None = None
	created_at: datetime
	updated_at: datetime | None = None


class PatchResultRequest(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	user_edited_summary: str