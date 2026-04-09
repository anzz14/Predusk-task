from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.job import JobResponse


class DocumentResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	user_id: UUID
	original_filename: str
	file_path: str
	file_size: int
	mime_type: str
	upload_timestamp: datetime
	created_at: datetime
	job: JobResponse | None = None


class DocumentListResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	items: list[DocumentResponse]
	total: int
	page: int
	page_size: int