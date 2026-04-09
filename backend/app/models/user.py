from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
	__tablename__ = "users"
	__table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
	email: Mapped[str] = mapped_column(String, nullable=False)
	hashed_password: Mapped[str] = mapped_column(String, nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

	documents: Mapped[list[Document]] = relationship(back_populates="user", cascade="all, delete-orphan")