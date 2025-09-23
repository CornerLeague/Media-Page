"""
Games and scoring models
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import GameStatus


class Game(Base, UUIDMixin, TimestampMixin):
    """
    Games table for scheduled and completed games
    """
    __tablename__ = "games"

    sport_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the sport"
    )

    league_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the league"
    )

    home_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the home team"
    )

    away_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the away team"
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Scheduled start time of the game"
    )

    status: Mapped[GameStatus] = mapped_column(
        default=GameStatus.SCHEDULED,
        nullable=False,
        doc="Current status of the game"
    )

    period: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Current period/quarter/inning of the game"
    )

    time_remaining: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Time remaining in current period"
    )

    home_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Current score for home team"
    )

    away_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Current score for away team"
    )

    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this game"
    )

    venue: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="Venue where the game is played"
    )

    season: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Season year for the game"
    )

    week: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Week number in the season"
    )

    # Relationships
    sport: Mapped["Sport"] = relationship(
        "Sport",
        lazy="selectin"
    )

    league: Mapped["League"] = relationship(
        "League",
        lazy="selectin"
    )

    home_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[home_team_id],
        lazy="selectin"
    )

    away_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[away_team_id],
        lazy="selectin"
    )

    events: Mapped[List["GameEvent"]] = relationship(
        "GameEvent",
        back_populates="game",
        cascade="all, delete-orphan",
        order_by="GameEvent.created_at",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, {self.away_team.name if self.away_team else 'TBD'} @ {self.home_team.name if self.home_team else 'TBD'}, {self.scheduled_at})>"

    @property
    def is_live(self) -> bool:
        """Check if the game is currently live"""
        return self.status == GameStatus.LIVE

    @property
    def is_final(self) -> bool:
        """Check if the game is final"""
        return self.status == GameStatus.FINAL

    @property
    def score_differential(self) -> int:
        """Get the score differential (home - away)"""
        return self.home_score - self.away_score

    @property
    def display_name(self) -> str:
        """Display name for the game"""
        away_name = self.away_team.name if self.away_team else "TBD"
        home_name = self.home_team.name if self.home_team else "TBD"
        return f"{away_name} @ {home_name}"


class GameEvent(Base, UUIDMixin):
    """
    Game events for live scoring and play-by-play
    """
    __tablename__ = "game_events"

    game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the game"
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of event (score, penalty, substitution, etc.)"
    )

    event_time: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Game time when the event occurred"
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Description of the event"
    )

    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        doc="Team involved in the event (nullable for neutral events)"
    )

    player_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Player involved in the event"
    )

    points_value: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Point value of the event (for scoring events)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        doc="Timestamp when the event was recorded"
    )

    # Relationships
    game: Mapped["Game"] = relationship(
        "Game",
        back_populates="events",
        lazy="select"
    )

    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<GameEvent(id={self.id}, game_id={self.game_id}, type='{self.event_type}', time='{self.event_time}')>"

    @property
    def is_scoring_event(self) -> bool:
        """Check if this is a scoring event"""
        return self.points_value > 0