"""
College Basketball specific game models
Extends the base Game model with college basketball specific functionality
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    GameStatus, GameType, GameImportance, HomeCourtAdvantage
)


class CollegeGame(Base, UUIDMixin, TimestampMixin):
    """
    College Basketball specific games with extended functionality
    """
    __tablename__ = "college_games"

    # Core game references
    base_game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        doc="Reference to base game (if using shared games table)"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    season_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the season"
    )

    # Team references (college teams)
    home_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the home team"
    )

    away_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the away team"
    )

    # Venue
    venue_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("venues.id", ondelete="SET NULL"),
        doc="Reference to the venue where the game is played"
    )

    # Game details
    game_type: Mapped[GameType] = mapped_column(
        nullable=False,
        default=GameType.REGULAR_SEASON,
        doc="Type of game (regular season, tournament, etc.)"
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

    # Game progression
    period: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current period/half (1 = first half, 2 = second half)"
    )

    time_remaining: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Time remaining in current period (MM:SS format)"
    )

    # Scoring
    home_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current score for home team"
    )

    away_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current score for away team"
    )

    # Halftime scores
    home_score_halftime: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Home team score at halftime"
    )

    away_score_halftime: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Away team score at halftime"
    )

    # Overtime tracking
    number_of_overtimes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of overtime periods played"
    )

    # Game context
    importance: Mapped[GameImportance] = mapped_column(
        nullable=False,
        default=GameImportance.MEDIUM,
        doc="Importance level of this game"
    )

    home_court_advantage: Mapped[HomeCourtAdvantage] = mapped_column(
        nullable=False,
        default=HomeCourtAdvantage.HOME,
        doc="Type of home court advantage"
    )

    # Conference game tracking
    is_conference_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a conference game"
    )

    conference_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="SET NULL"),
        doc="Conference this game counts toward (if conference game)"
    )

    # Game metadata
    tv_coverage: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="TV network or streaming coverage"
    )

    attendance: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Actual attendance at the game"
    )

    sellout: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the game was a sellout"
    )

    # Weather (for outdoor games or impact)
    temperature_fahrenheit: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Temperature at game time (for outdoor or weather-related impact)"
    )

    weather_conditions: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Weather conditions during the game"
    )

    # Game officials
    referees: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON array of game officials/referees"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this game"
    )

    espn_game_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="ESPN game identifier"
    )

    ncaa_game_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="NCAA official game identifier"
    )

    # Statistical tracking
    total_fouls_home: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total fouls committed by home team"
    )

    total_fouls_away: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total fouls committed by away team"
    )

    total_timeouts_home: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Timeouts remaining for home team"
    )

    total_timeouts_away: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Timeouts remaining for away team"
    )

    # Game notes and narrative
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes about the game"
    )

    game_recap: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Game recap or summary"
    )

    # Impact metrics
    upset_alert: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was flagged as a potential upset"
    )

    margin_of_victory: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Final margin of victory (calculated after game completion)"
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    season: Mapped["Season"] = relationship(
        "Season",
        lazy="selectin"
    )

    home_team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        foreign_keys=[home_team_id],
        lazy="selectin"
    )

    away_team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        foreign_keys=[away_team_id],
        lazy="selectin"
    )

    venue: Mapped[Optional["Venue"]] = relationship(
        "Venue",
        back_populates="home_games",
        lazy="selectin"
    )

    conference: Mapped[Optional["CollegeConference"]] = relationship(
        "CollegeConference",
        lazy="selectin"
    )

    # Tournament context (if applicable)
    tournament_game: Mapped[Optional["TournamentGame"]] = relationship(
        "TournamentGame",
        back_populates="game",
        uselist=False,
        lazy="selectin"
    )

    # Base game relationship (if using shared games table)
    base_game: Mapped[Optional["Game"]] = relationship(
        "Game",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_college_games_academic_year_id", "academic_year_id"),
        Index("idx_college_games_season_id", "season_id"),
        Index("idx_college_games_home_team_id", "home_team_id"),
        Index("idx_college_games_away_team_id", "away_team_id"),
        Index("idx_college_games_venue_id", "venue_id"),
        Index("idx_college_games_conference_id", "conference_id"),
        Index("idx_college_games_scheduled_at", "scheduled_at"),
        Index("idx_college_games_status", "status"),
        Index("idx_college_games_game_type", "game_type"),
        Index("idx_college_games_conference_game", "is_conference_game"),
        Index("idx_college_games_importance", "importance"),
        Index("idx_college_games_teams", "home_team_id", "away_team_id"),
        Index("idx_college_games_external_id", "external_id"),
        Index("idx_college_games_espn_id", "espn_game_id"),
        Index("idx_college_games_ncaa_id", "ncaa_game_id"),
        UniqueConstraint("home_team_id", "away_team_id", "scheduled_at", name="uq_college_games_teams_time"),
    )

    def __repr__(self) -> str:
        away_name = self.away_team.name if self.away_team else "TBD"
        home_name = self.home_team.name if self.home_team else "TBD"
        return f"<CollegeGame(id={self.id}, {away_name} @ {home_name}, {self.scheduled_at})>"

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

    @property
    def display_score(self) -> str:
        """Display formatted score"""
        if self.is_final:
            return f"{self.away_score}-{self.home_score} (Final)"
        elif self.is_live:
            time_display = f" - {self.time_remaining}" if self.time_remaining else ""
            period_display = f"H{self.period}" if self.period else ""
            return f"{self.away_score}-{self.home_score} ({period_display}{time_display})"
        else:
            return "Not Started"

    @property
    def winner_team(self) -> Optional["CollegeTeam"]:
        """Get the winning team (if game is final)"""
        if not self.is_final:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None  # Tie (shouldn't happen in basketball)

    @property
    def loser_team(self) -> Optional["CollegeTeam"]:
        """Get the losing team (if game is final)"""
        if not self.is_final:
            return None
        if self.home_score > self.away_score:
            return self.away_team
        elif self.away_score > self.home_score:
            return self.home_team
        return None  # Tie (shouldn't happen in basketball)

    @property
    def is_overtime(self) -> bool:
        """Check if the game went to overtime"""
        return self.number_of_overtimes > 0

    @property
    def is_upset(self) -> bool:
        """Check if this was an upset based on rankings or seeding"""
        # This would need more complex logic based on rankings/seeding
        return self.upset_alert

    @property
    def attendance_percentage(self) -> Optional[float]:
        """Calculate attendance as percentage of venue capacity"""
        if self.attendance and self.venue and self.venue.capacity:
            return (self.attendance / self.venue.capacity) * 100
        return None

    @property
    def total_points(self) -> int:
        """Total points scored in the game"""
        return self.home_score + self.away_score

    @property
    def is_high_scoring(self) -> bool:
        """Check if this is a high-scoring game (>150 total points)"""
        return self.total_points > 150

    @property
    def is_low_scoring(self) -> bool:
        """Check if this is a low-scoring game (<120 total points)"""
        return self.total_points < 120

    def calculate_margin_of_victory(self) -> Optional[int]:
        """Calculate and update margin of victory (for completed games)"""
        if self.is_final:
            self.margin_of_victory = abs(self.home_score - self.away_score)
            return self.margin_of_victory
        return None