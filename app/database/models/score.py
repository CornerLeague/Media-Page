"""Score model for game scoring data."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Integer, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel


class Score(BaseModel):
    """Game scoring data model."""

    __tablename__ = "score"
    __table_args__ = (
        UniqueConstraint("game_id", "team_id", name="uq_game_team_score"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    game_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    team_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    pts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    period: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    period_pts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="scores")
    team: Mapped["Team"] = relationship("Team", back_populates="scores")

    def __repr__(self) -> str:
        return f"<Score(game_id={self.game_id}, team_id={self.team_id}, pts={self.pts})>"