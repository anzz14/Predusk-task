from __future__ import annotations

from uuid import UUID

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	email: EmailStr
	password: str = Field(min_length=8)


class LoginRequest(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	email: EmailStr
	password: str


class TokenResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	access_token: str
	token_type: Literal["bearer"]


class UserResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	email: str