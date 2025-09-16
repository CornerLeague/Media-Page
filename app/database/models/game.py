"""Game-related SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import Dict, Optional, Any, List

from sqlalchemy import (
    CheckConstraint, Enum, ForeignKey, Integer, String, Text, DateTime
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .enums import GameStatus


class Game(BaseModel):
    """Game model for sports matches/games."""

    __tablename__ = "games"

    # External integration
    external_id: Mapped[Optional[str]] = mapped_column(
        Text,
        unique=True,
        nullable=True,
        doc="External API game ID"
    )

    # Team relationships
    home_team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
        doc="Home team ID"
    )

    away_team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
        doc="Away team ID"
    )

    # Game scheduling
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Scheduled game start time"
    )

    venue: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Game venue/stadium"
    )

    # Season context
    season: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
        doc="Season identifier (e.g., '2024', '2023-24')"
    )

    week: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        doc="Week number (for sports with weeks)"
    )

    # Game state
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus, name='game_status'),
        default=GameStatus.SCHEDULED,
        nullable=False,
        index=True,
        doc="Current game status"
    )

    quarter: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Current quarter/period"
    )

    time_remaining: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Time remaining in current period"
    )

    # Scores
    home_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=True,
        doc="Home team score"
    )

    away_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=True,
        doc="Away team score"
    )

    # Detailed scoring information
    final_score: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Detailed final score breakdown"
    )

    # Game statistics
    stats: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        doc="Game statistics and metadata"
    )

    # Relationships
    home_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[home_team_id],
        back_populates="home_games",
        doc="Home team"
    )

    away_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[away_team_id],
        back_populates="away_games",
        doc="Away team"
    )

    scores: Mapped[List["Score"]] = relationship(
        "Score",
        back_populates="game",
        cascade="all, delete-orphan",
        doc="Game scores for both teams"
    )

    ticket_deals: Mapped[List["TicketDeal"]] = relationship(
        "TicketDeal",
        back_populates="game",
        cascade="all, delete-orphan",
        doc="Ticket deals for this game"
    )

    experiences: Mapped[List["Experience"]] = relationship(
        "Experience",
        back_populates="game",
        doc="Fan experiences related to this game"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('home_team_id != away_team_id', name='different_teams'),
    )

    @property
    def is_live(self) -> bool:
        """Check if game is currently live."""
        return self.status == GameStatus.LIVE

    @property
    def is_completed(self) -> bool:
        """Check if game is completed."""
        return self.status == GameStatus.COMPLETED

    @property
    def is_scheduled(self) -> bool:
        """Check if game is scheduled."""
        return self.status == GameStatus.SCHEDULED

    @property
    def home_team_winning(self) -> bool:
        """Check if home team is winning."""
        return (self.home_score or 0) > (self.away_score or 0)

    @property
    def away_team_winning(self) -> bool:
        """Check if away team is winning."""
        return (self.away_score or 0) > (self.home_score or 0)

    @property
    def is_tied(self) -> bool:
        """Check if game is tied."""
        return (self.home_score or 0) == (self.away_score or 0)

    @property
    def score_differential(self) -> int:
        """Get score differential (home - away)."""
        return (self.home_score or 0) - (self.away_score or 0)

    @property
    def winner_id(self) -> Optional[uuid.UUID]:
        """Get ID of winning team (if game is completed)."""
        if not self.is_completed or self.is_tied:
            return None

        if self.home_team_winning:
            return self.home_team_id
        else:
            return self.away_team_id

    @property
    def loser_id(self) -> Optional[uuid.UUID]:
        """Get ID of losing team (if game is completed)."""
        if not self.is_completed or self.is_tied:
            return None

        if self.home_team_winning:
            return self.away_team_id
        else:
            return self.home_team_id

    def update_score(self, home_score: int, away_score: int) -> None:
        """Update game score."""
        self.home_score = home_score
        self.away_score = away_score

    def update_game_state(self,
                         status: Optional[GameStatus] = None,
                         quarter: Optional[int] = None,
                         time_remaining: Optional[str] = None) -> None:
        """Update game state information."""
        if status is not None:
            self.status = status
        if quarter is not None:
            self.quarter = quarter
        if time_remaining is not None:
            self.time_remaining = time_remaining

    def set_final_score(self, score_details: Dict[str, Any]) -> None:
        """Set final score with detailed breakdown."""
        self.final_score = score_details
        self.status = GameStatus.COMPLETED

    def add_stats(self, stats_data: Dict[str, Any]) -> None:
        """Add or update game statistics."""
        if self.stats is None:
            self.stats = {}
        self.stats.update(stats_data)

    def get_team_result(self, team_id: uuid.UUID) -> Optional[str]:
        """Get result for specific team ('win', 'loss', 'tie', or None if not completed)."""
        if not self.is_completed:
            return None

        if self.is_tied:
            return 'tie'

        if team_id == self.winner_id:
            return 'win'
        elif team_id == self.loser_id:
            return 'loss'

        return None

    def get_team_score(self, team_id: uuid.UUID) -> Optional[int]:
        """Get score for specific team."""
        if team_id == self.home_team_id:
            return self.home_score
        elif team_id == self.away_team_id:
            return self.away_score
        return None

    def get_opponent_id(self, team_id: uuid.UUID) -> Optional[uuid.UUID]:
        """Get opponent team ID for given team."""
        if team_id == self.home_team_id:
            return self.away_team_id
        elif team_id == self.away_team_id:
            return self.home_team_id
        return None

    @classmethod
    def get_team_games(cls, team_id: uuid.UUID, season: Optional[str] = None, limit: int = 50):
        """Get games for a specific team."""
        from sqlalchemy import select, or_, and_
        from ..database import get_session

        with get_session() as session:
            conditions = [
                or_(cls.home_team_id == team_id, cls.away_team_id == team_id)
            ]

            if season:
                conditions.append(cls.season == season)

            return session.execute(
                select(cls)
                .where(and_(*conditions))
                .order_by(cls.scheduled_at.desc())
                .limit(limit)
            ).scalars().all()

    @classmethod
    def get_recent_games(cls, limit: int = 20):
        """Get recent completed games."""
        from sqlalchemy import select
        from ..database import get_session

        with get_session() as session:
            return session.execute(
                select(cls)
                .where(cls.status == GameStatus.COMPLETED)
                .order_by(cls.scheduled_at.desc())
                .limit(limit)
            ).scalars().all()

    @classmethod
    def get_live_games(cls):
        """Get currently live games."""
        from sqlalchemy import select
        from ..database import get_session

        with get_session() as session:
            return session.execute(
                select(cls)
                .where(cls.status == GameStatus.LIVE)
                .order_by(cls.scheduled_at)
            ).scalars().all()

    @classmethod
    def get_upcoming_games(cls, limit: int = 20):
        """Get upcoming scheduled games."""
        from sqlalchemy import select
        from ..database import get_session

        with get_session() as session:
            return session.execute(
                select(cls)
                .where(cls.status == GameStatus.SCHEDULED)
                .order_by(cls.scheduled_at)
                .limit(limit)
            ).scalars().all()