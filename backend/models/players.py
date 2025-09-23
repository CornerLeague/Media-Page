"""
Player and depth chart models
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class Player(Base, UUIDMixin, TimestampMixin):
    """
    Players table for team rosters
    """
    __tablename__ = "players"

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Player's full name"
    )

    jersey_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Player's jersey number"
    )

    position: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Player's primary position"
    )

    experience_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Years of professional experience"
    )

    height: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Player's height (e.g., '6-2')"
    )

    weight: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Player's weight in pounds"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the player is currently active on the roster"
    )

    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this player"
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        lazy="selectin"
    )

    depth_chart_entries: Mapped[list["DepthChartEntry"]] = relationship(
        "DepthChartEntry",
        back_populates="player",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.name}', team='{self.team.name if self.team else None}', position='{self.position}')>"

    @property
    def display_name(self) -> str:
        """Display name with jersey number if available"""
        if self.jersey_number:
            return f"#{self.jersey_number} {self.name}"
        return self.name


class DepthChartEntry(Base, UUIDMixin, TimestampMixin):
    """
    Depth chart entries for player positions
    """
    __tablename__ = "depth_chart_entries"
    __table_args__ = (
        UniqueConstraint('team_id', 'player_id', 'position', 'week', 'season', name='uq_depth_chart_entry'),
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the player"
    )

    position: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Position on the depth chart"
    )

    depth_order: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        doc="Depth order at this position (1 = starter)"
    )

    week: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Week number for weekly depth charts"
    )

    season: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Season year for this depth chart entry"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this depth chart entry is currently active"
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        lazy="selectin"
    )

    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="depth_chart_entries",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<DepthChartEntry(team_id={self.team_id}, player='{self.player.name if self.player else None}', position='{self.position}', depth={self.depth_order})>"

    @property
    def is_starter(self) -> bool:
        """Check if this is a starting position"""
        return self.depth_order == 1

    @property
    def depth_description(self) -> str:
        """Get description of depth position"""
        if self.depth_order == 1:
            return "Starter"
        elif self.depth_order == 2:
            return "Backup"
        elif self.depth_order == 3:
            return "Third String"
        else:
            return f"{self.depth_order}th String"