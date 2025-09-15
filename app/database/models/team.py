"""Team-related SQLAlchemy models."""

import uuid
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, SearchableMixin
from .enums import Sport, League, TeamStatus


class Team(BaseModel, SearchableMixin):
    """Team model for sports teams."""

    __tablename__ = "teams"

    # External integration
    external_id: Mapped[Optional[str]] = mapped_column(
        Text,
        unique=True,
        nullable=True,
        doc="External API team ID"
    )

    # Basic team information
    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Team name"
    )

    city: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Team city"
    )

    abbreviation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
        doc="Team abbreviation (e.g., NYY, LAL)"
    )

    # Sports classification
    sport: Mapped[Sport] = mapped_column(
        Enum(Sport, name='sport_type'),
        nullable=False,
        index=True,
        doc="Sport type"
    )

    league: Mapped[League] = mapped_column(
        Enum(League, name='league_type'),
        nullable=False,
        index=True,
        doc="League"
    )

    conference: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Conference (e.g., AFC, NFC, Eastern, Western)"
    )

    division: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Division (e.g., East, West, North, South)"
    )

    # Visual branding
    logo_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Team logo URL"
    )

    primary_color: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Primary team color (hex code)"
    )

    secondary_color: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Secondary team color (hex code)"
    )

    # Team state
    status: Mapped[TeamStatus] = mapped_column(
        Enum(TeamStatus, name='team_status'),
        default=TeamStatus.ACTIVE,
        nullable=False,
        index=True,
        doc="Team status"
    )

    # Metrics
    follower_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of users following this team"
    )

    # Full-text search
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True,
        doc="Full-text search vector (computed)"
    )

    # Relationships
    user_relationships: Mapped[List["UserTeam"]] = relationship(
        "UserTeam",
        back_populates="team",
        cascade="all, delete-orphan",
        doc="Users following this team"
    )

    home_games: Mapped[List["Game"]] = relationship(
        "Game",
        foreign_keys="Game.home_team_id",
        back_populates="home_team",
        doc="Games where this team plays at home"
    )

    away_games: Mapped[List["Game"]] = relationship(
        "Game",
        foreign_keys="Game.away_team_id",
        back_populates="away_team",
        doc="Games where this team plays away"
    )

    team_stats: Mapped[List["TeamStats"]] = relationship(
        "TeamStats",
        back_populates="team",
        cascade="all, delete-orphan",
        doc="Team statistics by season"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('name', 'league', name='uq_team_name_league'),
        UniqueConstraint('abbreviation', 'league', name='uq_team_abbr_league'),
    )

    @property
    def full_name(self) -> str:
        """Get team's full name with city."""
        if self.city:
            return f"{self.city} {self.name}"
        return self.name

    @property
    def display_name(self) -> str:
        """Get team's display name for UI."""
        return self.full_name

    def get_current_season_stats(self, season: str) -> Optional["TeamStats"]:
        """Get team stats for a specific season."""
        for stats in self.team_stats:
            if stats.season == season:
                return stats
        return None

    @classmethod
    def search(cls, query: str, limit: int = 50):
        """Search teams by name, city, or abbreviation."""
        from sqlalchemy import func, select
        from ..database import get_session

        with get_session() as session:
            # Use full-text search with ranking
            search_query = func.plainto_tsquery('english', query)

            return session.execute(
                select(cls)
                .where(
                    cls.search_vector.op('@@')(search_query) &
                    (cls.status == TeamStatus.ACTIVE)
                )
                .order_by(
                    func.ts_rank(cls.search_vector, search_query).desc()
                )
                .limit(limit)
            ).scalars().all()

    def is_active(self) -> bool:
        """Check if team is active."""
        return self.status == TeamStatus.ACTIVE


class TeamStats(BaseModel):
    """Team statistics by season."""

    __tablename__ = "team_stats"

    # Foreign key
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Team ID"
    )

    # Season identifier
    season: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Season identifier (e.g., '2024', '2023-24')"
    )

    # Basic stats
    games_played: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of games played"
    )

    wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of wins"
    )

    losses: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of losses"
    )

    ties: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of ties (if applicable)"
    )

    # Scoring stats
    points_for: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=8, scale=2),
        default=0,
        nullable=True,
        doc="Total points scored"
    )

    points_against: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=8, scale=2),
        default=0,
        nullable=True,
        doc="Total points allowed"
    )

    # Computed win percentage (handled by database)
    win_percentage: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=4, scale=3),
        nullable=True,
        doc="Win percentage (computed)"
    )

    # Extended stats as flexible JSON
    extended_stats: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        doc="Additional sport-specific statistics"
    )

    # Relationship
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="team_stats",
        doc="Team these stats belong to"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('team_id', 'season', name='uq_team_season'),
    )

    @property
    def total_games(self) -> int:
        """Total games played (wins + losses + ties)."""
        return self.wins + self.losses + self.ties

    @property
    def calculated_win_percentage(self) -> float:
        """Calculate win percentage manually."""
        if self.total_games == 0:
            return 0.0
        return round((self.wins + self.ties * 0.5) / self.total_games, 3)

    @property
    def points_differential(self) -> Optional[float]:
        """Points differential (points for - points against)."""
        if self.points_for is not None and self.points_against is not None:
            return self.points_for - self.points_against
        return None

    def update_stats(self, game_result: dict) -> None:
        """Update team stats based on game result."""
        self.games_played += 1

        # Determine game outcome
        if game_result.get('is_win'):
            self.wins += 1
        elif game_result.get('is_tie'):
            self.ties += 1
        else:
            self.losses += 1

        # Update scoring stats
        if 'points_scored' in game_result:
            self.points_for = (self.points_for or 0) + game_result['points_scored']

        if 'points_allowed' in game_result:
            self.points_against = (self.points_against or 0) + game_result['points_allowed']

        # Update extended stats
        if 'extended_stats' in game_result:
            for key, value in game_result['extended_stats'].items():
                if key in self.extended_stats:
                    # Accumulate numeric values
                    if isinstance(value, (int, float)) and isinstance(self.extended_stats[key], (int, float)):
                        self.extended_stats[key] += value
                    else:
                        self.extended_stats[key] = value
                else:
                    self.extended_stats[key] = value