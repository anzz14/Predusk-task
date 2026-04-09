from __future__ import annotations

from datetime import datetime, timedelta

from jose import jwt
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User


class DuplicateEmailError(Exception):
	pass


class InvalidCredentialsError(Exception):
	pass


async def register_user(db: AsyncSession, email: str, password: str) -> User:
	result = await db.execute(select(User).where(User.email == email))
	existing_user = result.scalar_one_or_none()
	if existing_user is not None:
		raise DuplicateEmailError()

	user = User(email=email, hashed_password=bcrypt.hash(password))
	db.add(user)
	await db.commit()
	await db.refresh(user)
	return user


async def login_user(db: AsyncSession, email: str, password: str) -> str:
	result = await db.execute(select(User).where(User.email == email))
	user = result.scalar_one_or_none()
	if user is None or not bcrypt.verify(password, user.hashed_password):
		raise InvalidCredentialsError()

	payload = {
		"sub": str(user.id),
		"exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS),
	}
	return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)