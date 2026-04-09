from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import document_service, export_service


router = APIRouter(prefix="", tags=["export"], dependencies=[Depends(get_current_user)])


def _attach_latest_job(document) -> None:
	jobs = list(document.processing_jobs or [])
	if not jobs:
		setattr(document, "job", None)
		return
	latest_job = max(jobs, key=lambda job: (job.created_at or datetime.min, str(job.id)))
	setattr(document, "job", latest_job)


def _get_result_or_404(document):
	result = getattr(document, "extracted_result", None)
	if result is None:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
	return result


@router.get("/documents/{document_id}/export")
async def export_document(document_id: str, format: Literal["json", "csv"] = "json", current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	document = await document_service.get_document(db, document_id, current_user.id)
	if document is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
	_attach_latest_job(document)
	result = _get_result_or_404(document)
	if not result.is_finalized:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

	if format == "json":
		payload = export_service.build_json_export(result)
		return Response(content=json.dumps(payload, default=str), media_type="application/json", headers={"Content-Disposition": f'attachment; filename="document_{document_id}.json"'})

	fieldnames = ["id", "document_id", "job_id", "word_count", "readability_score", "primary_keywords", "auto_summary", "user_edited_summary", "is_finalized", "finalized_at", "created_at", "updated_at"]
	buffer = io.StringIO()
	writer = csv.DictWriter(buffer, fieldnames=fieldnames)
	writer.writeheader()
	writer.writerow({
		"id": str(result.id),
		"document_id": str(result.document_id),
		"job_id": str(result.job_id),
		"word_count": result.word_count,
		"readability_score": result.readability_score,
		"primary_keywords": ", ".join(keyword.get("keyword", "") for keyword in (result.primary_keywords or []) if isinstance(keyword, dict)),
		"auto_summary": result.auto_summary,
		"user_edited_summary": result.user_edited_summary or "",
		"is_finalized": result.is_finalized,
		"finalized_at": result.finalized_at,
		"created_at": result.created_at,
		"updated_at": result.updated_at,
	})
	return Response(content=buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="document_{document_id}.csv"'})


@router.get("/export/bulk")
async def bulk_export(format: Literal["csv"] = "csv", current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	if format != "csv":
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
	stream = export_service.stream_csv_rows(db, current_user.id)
	return StreamingResponse(stream, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="bulk_export.csv"'})