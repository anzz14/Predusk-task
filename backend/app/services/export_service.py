from __future__ import annotations

import csv
import io
import json
from typing import Any, AsyncGenerator
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.extracted_result import ExtractedResult


def _coerce_uuid(value: UUID | str) -> UUID:
	return value if isinstance(value, UUID) else UUID(str(value))


def _stringify(value: Any) -> str:
	if value is None:
		return ""
	if hasattr(value, "isoformat"):
		return value.isoformat()
	if isinstance(value, bool):
		return "true" if value else "false"
	return str(value)


def build_json_export(result: ExtractedResult) -> dict[str, Any]:
	return {
		"id": result.id,
		"document_id": result.document_id,
		"job_id": result.job_id,
		"word_count": result.word_count,
		"readability_score": result.readability_score,
		"primary_keywords": list(result.primary_keywords),
		"auto_summary": result.auto_summary,
		"user_edited_summary": result.user_edited_summary,
		"is_finalized": result.is_finalized,
		"finalized_at": result.finalized_at,
		"created_at": result.created_at,
		"updated_at": result.updated_at,
	}


async def stream_csv_rows(db: AsyncSession, user_id: UUID | str) -> AsyncGenerator[str, None]:
	page_size = 100
	offset = 0
	user_uuid = _coerce_uuid(user_id)
	fieldnames = [
		"id",
		"document_id",
		"job_id",
		"word_count",
		"readability_score",
		"primary_keywords",
		"auto_summary",
		"user_edited_summary",
		"is_finalized",
		"finalized_at",
		"created_at",
		"updated_at",
	]

	header_buffer = io.StringIO()
	csv.DictWriter(header_buffer, fieldnames=fieldnames).writeheader()
	yield header_buffer.getvalue()

	while True:
		query = (
			select(ExtractedResult)
			.join(Document)
			.where(Document.user_id == user_uuid, ExtractedResult.is_finalized.is_(True))
			.order_by(desc(ExtractedResult.created_at), desc(ExtractedResult.id))
			.offset(offset)
			.limit(page_size)
		)
		rows = (await db.execute(query)).scalars().all()
		if not rows:
			break

		for row in rows:
			export_row = {
				"id": _stringify(row.id),
				"document_id": _stringify(row.document_id),
				"job_id": _stringify(row.job_id),
				"word_count": _stringify(row.word_count),
				"readability_score": _stringify(row.readability_score),
				"primary_keywords": ", ".join(
					keyword.get("keyword", "") for keyword in (row.primary_keywords or []) if isinstance(keyword, dict)
				),
				"auto_summary": _stringify(row.auto_summary),
				"user_edited_summary": _stringify(row.user_edited_summary),
				"is_finalized": _stringify(row.is_finalized),
				"finalized_at": _stringify(row.finalized_at),
				"created_at": _stringify(row.created_at),
				"updated_at": _stringify(row.updated_at),
			}

			buffer = io.StringIO()
			writer = csv.DictWriter(buffer, fieldnames=fieldnames)
			writer.writerow(export_row)
			yield buffer.getvalue()

		offset += page_size
