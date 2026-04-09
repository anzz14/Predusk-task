from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import DuplicateEmailError, InvalidCredentialsError, login_user, register_user
from app.database import AsyncSessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
	try:
		user = await register_user(db, request.email, request.password)
	except DuplicateEmailError as exc:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
	return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
	try:
		token = await login_user(db, request.email, request.password)
	except InvalidCredentialsError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
	return TokenResponse(access_token=token, token_type="bearer")