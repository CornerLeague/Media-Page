"""Team depth chart model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel


class DepthChart(BaseModel):
    """Team depth chart model."""

    __tablename__ = "depth_chart"
    __table_args__ = (
        UniqueConstraint(
            "team_id", "position", "depth_order", "season_year", "week",
            name="uq_depth_chart_position"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    team_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[str] = mapped_column(Text, nullable=False)
    player_name: Mapped[str] = mapped_column(Text, nullable=False)
    player_number: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    depth_order: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    season_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="depth_charts")

    def __repr__(self) -> str:
        return f"<DepthChart(team_id={self.team_id}, position={self.position}, player={self.player_name}, depth={self.depth_order})>"