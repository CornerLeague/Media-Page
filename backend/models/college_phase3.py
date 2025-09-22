"""
College Basketball Phase 3: Competition Structure Models
Venues, Tournaments, Brackets, and Tournament Games
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    VenueType, TournamentType, TournamentStatus, TournamentFormat,
    GameType, BracketRegion, GameImportance, HomeCourtAdvantage
)


class Venue(Base, UUIDMixin, TimestampMixin):
    """
    Basketball venues - arenas, gymnasiums, and playing locations
    """
    __tablename__ = "venues"

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Official name of the venue"
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        doc="URL-friendly slug for the venue"
    )

    venue_type: Mapped[VenueType] = mapped_column(
        nullable=False,
        doc="Type of venue (arena, gymnasium, etc.)"
    )

    # Location information
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="City where the venue is located"
    )

    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="State where the venue is located"
    )

    country: Mapped[str] = mapped_column(
        String(3),
        default="USA",
        nullable=False,
        doc="Country code where the venue is located"
    )

    zip_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="ZIP code of the venue"
    )

    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Street address of the venue"
    )

    # Venue details
    capacity: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total seating capacity for basketball"
    )

    opened_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year the venue was opened"
    )

    surface_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="hardwood",
        doc="Type of playing surface"
    )

    # Primary college association
    college_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="SET NULL"),
        doc="Primary college that uses this venue (NULL for neutral sites)"
    )

    # Venue characteristics
    is_neutral_site: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a neutral site venue"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this venue is currently active"
    )

    # Facility details
    court_dimensions: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Court dimensions (e.g., '94x50 feet')"
    )

    elevation_feet: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Elevation above sea level in feet"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this venue"
    )

    website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Official venue website URL"
    )

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to venue image"
    )

    # Configuration and notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes about the venue"
    )

    # Relationships
    college: Mapped[Optional["College"]] = relationship(
        "College",
        lazy="selectin"
    )

    home_games: Mapped[List["CollegeGame"]] = relationship(
        "CollegeGame",
        back_populates="venue",
        lazy="select"
    )

    tournaments: Mapped[List["TournamentVenue"]] = relationship(
        "TournamentVenue",
        back_populates="venue",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_venues_slug", "slug"),
        Index("idx_venues_college_id", "college_id"),
        Index("idx_venues_location", "state", "city"),
        Index("idx_venues_type", "venue_type"),
        Index("idx_venues_neutral_site", "is_neutral_site"),
        Index("idx_venues_capacity", "capacity"),
        Index("idx_venues_external_id", "external_id"),
    )

    def __repr__(self) -> str:
        return f"<Venue(id={self.id}, name='{self.name}', capacity={self.capacity})>"

    @property
    def display_name(self) -> str:
        """Full display name for the venue"""
        return self.name

    @property
    def location(self) -> str:
        """Formatted location string"""
        return f"{self.city}, {self.state}"

    @property
    def full_location(self) -> str:
        """Full location with address if available"""
        if self.address:
            return f"{self.address}, {self.city}, {self.state}"
        return self.location


class Tournament(Base, UUIDMixin, TimestampMixin):
    """
    Basketball tournaments (NCAA, conference tournaments, etc.)
    """
    __tablename__ = "tournaments"

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    season_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        doc="Reference to the specific season (postseason, etc.)"
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Tournament name (e.g., 'NCAA Division I Men's Basketball Tournament')"
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="URL-friendly slug for the tournament"
    )

    short_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Short name for the tournament (e.g., 'March Madness')"
    )

    tournament_type: Mapped[TournamentType] = mapped_column(
        nullable=False,
        doc="Type of tournament"
    )

    format: Mapped[TournamentFormat] = mapped_column(
        nullable=False,
        default=TournamentFormat.SINGLE_ELIMINATION,
        doc="Tournament format/bracket structure"
    )

    status: Mapped[TournamentStatus] = mapped_column(
        nullable=False,
        default=TournamentStatus.SCHEDULED,
        doc="Current status of the tournament"
    )

    # Conference association (for conference tournaments)
    conference_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="CASCADE"),
        doc="Reference to conference (for conference tournaments)"
    )

    # Tournament details
    total_teams: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total number of teams in the tournament"
    )

    total_rounds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total number of rounds in the tournament"
    )

    current_round: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0,
        doc="Current round number (0 = not started)"
    )

    # Dates
    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Tournament start date"
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Tournament end date"
    )

    selection_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date teams/bracket was announced"
    )

    # Tournament settings
    auto_bid_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this tournament provides automatic bids"
    )

    has_bracket: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this tournament uses a bracket structure"
    )

    # Winner tracking
    champion_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="SET NULL"),
        doc="Tournament champion (set when completed)"
    )

    runner_up_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="SET NULL"),
        doc="Tournament runner-up (set when completed)"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this tournament"
    )

    # Configuration and metadata
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Tournament description"
    )

    rules: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Tournament rules and regulations"
    )

    prize_money: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        doc="Total prize money for the tournament"
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    season: Mapped[Optional["Season"]] = relationship(
        "Season",
        lazy="selectin"
    )

    conference: Mapped[Optional["CollegeConference"]] = relationship(
        "CollegeConference",
        lazy="selectin"
    )

    champion_team: Mapped[Optional["CollegeTeam"]] = relationship(
        "CollegeTeam",
        foreign_keys=[champion_team_id],
        lazy="selectin"
    )

    runner_up_team: Mapped[Optional["CollegeTeam"]] = relationship(
        "CollegeTeam",
        foreign_keys=[runner_up_team_id],
        lazy="selectin"
    )

    brackets: Mapped[List["TournamentBracket"]] = relationship(
        "TournamentBracket",
        back_populates="tournament",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="TournamentBracket.round_number, TournamentBracket.position"
    )

    games: Mapped[List["TournamentGame"]] = relationship(
        "TournamentGame",
        back_populates="tournament",
        cascade="all, delete-orphan",
        lazy="select"
    )

    venues: Mapped[List["TournamentVenue"]] = relationship(
        "TournamentVenue",
        back_populates="tournament",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_tournaments_academic_year_id", "academic_year_id"),
        Index("idx_tournaments_season_id", "season_id"),
        Index("idx_tournaments_conference_id", "conference_id"),
        Index("idx_tournaments_slug", "slug"),
        Index("idx_tournaments_type", "tournament_type"),
        Index("idx_tournaments_status", "status"),
        Index("idx_tournaments_dates", "start_date", "end_date"),
        Index("idx_tournaments_current_round", "current_round"),
        UniqueConstraint("academic_year_id", "slug", name="uq_tournaments_academic_year_slug"),
    )

    def __repr__(self) -> str:
        return f"<Tournament(id={self.id}, name='{self.name}', type='{self.tournament_type}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the tournament"""
        if self.academic_year:
            return f"{self.name} ({self.academic_year.name})"
        return self.name

    @property
    def is_active(self) -> bool:
        """Whether the tournament is currently active"""
        return self.status in [TournamentStatus.IN_PROGRESS, TournamentStatus.SCHEDULED]

    @property
    def is_completed(self) -> bool:
        """Whether the tournament is completed"""
        return self.status == TournamentStatus.COMPLETED


class TournamentBracket(Base, UUIDMixin, TimestampMixin):
    """
    Tournament bracket structure and seeding
    """
    __tablename__ = "tournament_brackets"

    tournament_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the tournament"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team in this bracket position"
    )

    # Bracket positioning
    seed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Tournament seed (1-16 for NCAA regions, varies for other tournaments)"
    )

    region: Mapped[Optional[BracketRegion]] = mapped_column(
        doc="Bracket region (for NCAA tournament)"
    )

    round_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        doc="Round number where team enters (1 = first round)"
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Position within the round/region"
    )

    # Status tracking
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this team is still active in the tournament"
    )

    eliminated_round: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Round in which the team was eliminated (NULL if still active)"
    )

    # Bracket metadata
    automatic_bid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was an automatic bid"
    )

    at_large_bid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was an at-large bid"
    )

    # Selection metrics
    selection_criteria: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON object containing selection metrics (NET, SOS, etc.)"
    )

    # Relationships
    tournament: Mapped["Tournament"] = relationship(
        "Tournament",
        back_populates="brackets",
        lazy="selectin"
    )

    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_tournament_brackets_tournament_id", "tournament_id"),
        Index("idx_tournament_brackets_team_id", "team_id"),
        Index("idx_tournament_brackets_seed", "seed"),
        Index("idx_tournament_brackets_region", "region"),
        Index("idx_tournament_brackets_round", "round_number"),
        Index("idx_tournament_brackets_position", "position"),
        Index("idx_tournament_brackets_active", "is_active"),
        UniqueConstraint("tournament_id", "team_id", name="uq_tournament_brackets_tournament_team"),
        UniqueConstraint("tournament_id", "region", "seed", name="uq_tournament_brackets_tournament_region_seed"),
    )

    def __repr__(self) -> str:
        return f"<TournamentBracket(tournament='{self.tournament.name if self.tournament else None}', team='{self.team.name if self.team else None}', seed={self.seed})>"

    @property
    def seed_display(self) -> str:
        """Display format for seed"""
        if self.seed and self.region:
            return f"{self.region.title()} {self.seed}"
        elif self.seed:
            return f"#{self.seed}"
        return "TBD"

    @property
    def bid_type(self) -> str:
        """Display the type of bid"""
        if self.automatic_bid:
            return "Automatic"
        elif self.at_large_bid:
            return "At-Large"
        return "Unknown"


class TournamentGame(Base, UUIDMixin, TimestampMixin):
    """
    Games played within tournament context with bracket positioning
    """
    __tablename__ = "tournament_games"

    tournament_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the tournament"
    )

    game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the actual game"
    )

    # Tournament context
    round_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Tournament round number"
    )

    round_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Name of the round (e.g., 'First Round', 'Elite Eight', 'Final Four')"
    )

    region: Mapped[Optional[BracketRegion]] = mapped_column(
        doc="Bracket region (for NCAA tournament)"
    )

    # Game positioning
    game_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Game number within the round"
    )

    # Bracket progression
    winner_advances_to: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournament_games.id", ondelete="SET NULL"),
        doc="Next game the winner advances to"
    )

    loser_advances_to: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournament_games.id", ondelete="SET NULL"),
        doc="Next game the loser advances to (for consolation brackets)"
    )

    # Game importance
    importance: Mapped[GameImportance] = mapped_column(
        nullable=False,
        default=GameImportance.MEDIUM,
        doc="Importance level of this game"
    )

    # Championship game indicators
    is_championship: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a championship game"
    )

    is_semifinal: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a semifinal game"
    )

    # External metadata
    tv_coverage: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="TV network or streaming coverage"
    )

    # Relationships
    tournament: Mapped["Tournament"] = relationship(
        "Tournament",
        back_populates="games",
        lazy="selectin"
    )

    game: Mapped["CollegeGame"] = relationship(
        "CollegeGame",
        back_populates="tournament_game",
        lazy="selectin"
    )

    next_game_winner: Mapped[Optional["TournamentGame"]] = relationship(
        "TournamentGame",
        foreign_keys=[winner_advances_to],
        remote_side="TournamentGame.id",
        lazy="selectin"
    )

    next_game_loser: Mapped[Optional["TournamentGame"]] = relationship(
        "TournamentGame",
        foreign_keys=[loser_advances_to],
        remote_side="TournamentGame.id",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_tournament_games_tournament_id", "tournament_id"),
        Index("idx_tournament_games_game_id", "game_id"),
        Index("idx_tournament_games_round", "round_number"),
        Index("idx_tournament_games_region", "region"),
        Index("idx_tournament_games_championship", "is_championship"),
        Index("idx_tournament_games_importance", "importance"),
        UniqueConstraint("tournament_id", "game_id", name="uq_tournament_games_tournament_game"),
    )

    def __repr__(self) -> str:
        return f"<TournamentGame(tournament='{self.tournament.name if self.tournament else None}', round={self.round_number}, game_id={self.game_id})>"

    @property
    def display_round(self) -> str:
        """Display format for tournament round"""
        if self.round_name:
            return self.round_name
        return f"Round {self.round_number}"

    @property
    def bracket_position(self) -> str:
        """Display bracket position"""
        if self.region and self.round_number:
            return f"{self.region.title()} - {self.display_round}"
        return self.display_round


class TournamentVenue(Base, UUIDMixin, TimestampMixin):
    """
    Association between tournaments and venues used for games
    """
    __tablename__ = "tournament_venues"

    tournament_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the tournament"
    )

    venue_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("venues.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the venue"
    )

    # Venue usage details
    rounds_hosted: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Which rounds this venue hosts (e.g., 'First Round, Second Round')"
    )

    is_primary_venue: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is the primary/championship venue"
    )

    capacity_used: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Actual capacity used for tournament games"
    )

    # Relationships
    tournament: Mapped["Tournament"] = relationship(
        "Tournament",
        back_populates="venues",
        lazy="selectin"
    )

    venue: Mapped["Venue"] = relationship(
        "Venue",
        back_populates="tournaments",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_tournament_venues_tournament_id", "tournament_id"),
        Index("idx_tournament_venues_venue_id", "venue_id"),
        Index("idx_tournament_venues_primary", "is_primary_venue"),
        UniqueConstraint("tournament_id", "venue_id", name="uq_tournament_venues_tournament_venue"),
    )

    def __repr__(self) -> str:
        return f"<TournamentVenue(tournament='{self.tournament.name if self.tournament else None}', venue='{self.venue.name if self.venue else None}')>"