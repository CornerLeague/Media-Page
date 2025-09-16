"""Fan experiences model."""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import ExperienceType


class Experience(BaseModel):
    """Fan experiences and events model."""

    __tablename__ = "experience"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    team_id: Mapped[Optional[UUID]] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True
    )
    game_id: Mapped[Optional[UUID]] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("games.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[ExperienceType] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    location_geo: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    quality_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=3, scale=2), nullable=True
    )
    price_range: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    source: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="experiences")
    game: Mapped[Optional["Game"]] = relationship("Game", back_populates="experiences")

    def __repr__(self) -> str:
        return f"<Experience(id={self.id}, type={self.type}, title={self.title})>"