"""Sport and user sport preferences models."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import Sport as SportEnum


class Sport(BaseModel):
    """Sport reference table model."""

    __tablename__ = "sport"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    has_teams: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    season_structure: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user_sport_prefs: Mapped[List["UserSportPref"]] = relationship(
        "UserSportPref", back_populates="sport", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sport(id={self.id}, name={self.name})>"


class UserSportPref(BaseModel):
    """User sport preferences with ranking model."""

    __tablename__ = "user_sport_prefs"
    __table_args__ = (
        UniqueConstraint("user_id", "rank", name="uq_user_sport_rank"),
        UniqueConstraint("user_id", "sport_id", name="uq_user_sport"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    sport_id: Mapped[str] = mapped_column(
        Text, ForeignKey("sport.id", ondelete="CASCADE"), nullable=False
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sport_prefs")
    sport: Mapped["Sport"] = relationship("Sport", back_populates="user_sport_prefs")

    def __repr__(self) -> str:
        return f"<UserSportPref(user_id={self.user_id}, sport_id={self.sport_id}, rank={self.rank})>"