from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExportRow(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: str
	document_id: str
	job_id: str
	word_count: str
	readability_score: str
	primary_keywords_json: str
	primary_keywords_csv: str
	auto_summary: str
	user_edited_summary: str
	is_finalized: str
	finalized_at: str
	created_at: str
	updated_at: str