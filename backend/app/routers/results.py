from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.result import ExtractedResultResponse, PatchResultRequest
from app.services import result_service
from app.services.result_service import AlreadyFinalizedError, StaleResultError


router = APIRouter(prefix="/documents", tags=["results"], dependencies=[Depends(get_current_user)])


@router.patch("/{document_id}/result", response_model=ExtractedResultResponse)
async def patch_result(document_id: str, request: PatchResultRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await result_service.patch_summary(db, document_id, current_user.id, request.user_edited_summary)
	if result is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
	return ExtractedResultResponse.model_validate(result)


@router.post("/{document_id}/finalize", response_model=ExtractedResultResponse)
async def finalize_document(document_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		result = await result_service.finalize(db, document_id, current_user.id)
	except AlreadyFinalizedError as exc:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
	except StaleResultError as exc:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from exc
	if result is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
	return ExtractedResultResponse.model_validate(result)