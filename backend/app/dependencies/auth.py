from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User


async def get_current_user(
	authorization: str | None = Header(default=None),
	db: AsyncSession = Depends(get_db),
) -> User:
	if not authorization or not authorization.startswith("Bearer "):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

	token = authorization.removeprefix("Bearer ").strip()

	try:
		payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
		user_id = payload.get("sub")
		if not user_id:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

		user_uuid = UUID(user_id)
	except (JWTError, ExpiredSignatureError, ValueError, TypeError):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

	result = await db.execute(select(User).where(User.id == user_uuid))
	user = result.scalar_one_or_none()
	if user is None or not user.is_active:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

	return user