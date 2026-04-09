from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services import document_service, job_service


router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[Depends(get_current_user)])


def _attach_latest_job(document) -> None:
	jobs = list(document.processing_jobs or [])
	if not jobs:
		setattr(document, "job", None)
		return
	latest_job = max(jobs, key=lambda job: (job.created_at or datetime.min, str(job.id)))
	setattr(document, "job", latest_job)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documents(
	files: list[UploadFile] = File(...),
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
):
	results: list[dict[str, str]] = []
	for file in files:
		document = await document_service.create_document(db, file, current_user.id)
		job = await job_service.create_and_dispatch(db, document)
		results.append({"document_id": str(document.id), "job_id": str(job.id)})
	return results


@router.get("", response_model=DocumentListResponse)
async def list_documents(
	search: str | None = None,
	status: str | None = None,
	sort_by: str | None = None,
	sort_order: str = "asc",
	page: int = 1,
	page_size: int = 10,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
):
	documents, total = await document_service.list_documents(
		db,
		user_id=current_user.id,
		search=search,
		status=status,
		sort_by=sort_by,
		sort_order=sort_order,
		page=page,
		page_size=page_size,
	)
	for document in documents:
		_attach_latest_job(document)
	return DocumentListResponse(items=[DocumentResponse.model_validate(document) for document in documents], total=total, page=page, page_size=page_size)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	document = await document_service.get_document(db, document_id, current_user.id)
	if document is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
	_attach_latest_job(document)
	return DocumentResponse.model_validate(document)