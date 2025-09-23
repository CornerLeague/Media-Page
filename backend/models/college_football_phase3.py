"""
College Football Phase 3: Postseason Structure Models
Bowl Games, College Football Playoff, Conference Championships, and Rivalry Games
Extends existing College Football Phase 1 & 2 foundation
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, Date, DateTime, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    # Existing enums
    FootballSeasonType, BowlGameType, GameStatus, GameResult,

    # New Phase 3 enums
    BowlTier, BowlSelectionCriteria, PlayoffRound, CFPSeedType,
    ConferenceChampionshipFormat, RivalryType, TrophyStatus,
    PostseasonFormat, SelectionMethod, BracketPosition
)


# =============================================================================
# Bowl Game System Models
# =============================================================================

class BowlGame(Base, UUIDMixin, TimestampMixin):
    """
    Bowl game definitions with tie-ins, selection criteria, and history
    Supports the complex bowl system with 43+ bowl games
    """
    __tablename__ = "bowl_games"

    # Basic bowl information
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Official bowl game name (e.g., 'Rose Bowl Game')"
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        doc="URL-friendly slug for the bowl game"
    )

    sponsor_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Sponsor name if applicable (e.g., 'Capital One')"
    )

    full_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        doc="Full sponsored name (e.g., 'Capital One Orange Bowl')"
    )

    # Bowl classification
    bowl_tier: Mapped[BowlTier] = mapped_column(
        nullable=False,
        doc="Tier of bowl game (CFP, NY6, Major, etc.)"
    )

    is_cfp_bowl: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this bowl is part of the College Football Playoff rotation"
    )

    is_new_years_six: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a New Year's Six bowl"
    )

    # Location and venue
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="City where bowl is played"
    )

    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="State where bowl is played"
    )

    venue_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Stadium/venue name"
    )

    venue_capacity: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Stadium capacity for bowl game"
    )

    # Traditional date and timing
    typical_date: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Traditional date (e.g., 'January 1', 'December 26')"
    )

    kickoff_time: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Typical kickoff time"
    )

    # Selection criteria and tie-ins
    selection_criteria: Mapped[BowlSelectionCriteria] = mapped_column(
        nullable=False,
        doc="Primary selection criteria for this bowl"
    )

    selection_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Selection order within its tier/criteria"
    )

    # Bowl eligibility requirements
    min_wins_required: Mapped[int] = mapped_column(
        Integer,
        default=6,
        nullable=False,
        doc="Minimum wins required for eligibility"
    )

    academic_requirements: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Academic Performance Rating or other academic requirements"
    )

    # Conference tie-ins and selection
    primary_conference_tie_ins: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON array of primary conference tie-ins"
    )

    secondary_conference_tie_ins: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON array of secondary conference tie-ins"
    )

    at_large_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether bowl can select at-large teams"
    )

    group_of_five_access: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this provides Group of Five access (NY6)"
    )

    # Payout information
    total_payout: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        doc="Total payout to participating teams"
    )

    payout_per_team: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        doc="Payout per participating team"
    )

    payout_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year of the payout amount"
    )

    # Historical information
    first_played: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year the bowl was first played"
    )

    total_games_played: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of games played in bowl history"
    )

    # Media and broadcast
    primary_tv_network: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Primary television network"
    )

    broadcast_time_slot: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Typical broadcast time slot"
    )

    # Bowl characteristics
    trophy_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of the trophy awarded"
    )

    is_tradition_bowl: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a traditional bowl (Rose, Sugar, etc.)"
    )

    weather_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Typical weather conditions (dome, warm weather, etc.)"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier"
    )

    website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Official bowl website"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether bowl is currently active"
    )

    # Relationships
    bowl_selections: Mapped[List["BowlSelection"]] = relationship(
        "BowlSelection",
        back_populates="bowl_game",
        cascade="all, delete-orphan",
        lazy="select"
    )

    bowl_tie_ins: Mapped[List["BowlTieIn"]] = relationship(
        "BowlTieIn",
        back_populates="bowl_game",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_bowl_games_slug", "slug"),
        Index("idx_bowl_games_tier", "bowl_tier"),
        Index("idx_bowl_games_cfp", "is_cfp_bowl"),
        Index("idx_bowl_games_ny6", "is_new_years_six"),
        Index("idx_bowl_games_location", "state", "city"),
        Index("idx_bowl_games_selection_criteria", "selection_criteria"),
        Index("idx_bowl_games_selection_order", "selection_order"),
        Index("idx_bowl_games_active", "is_active"),
        Index("idx_bowl_games_tradition", "is_tradition_bowl"),
        Index("idx_bowl_games_external_id", "external_id"),
    )

    def __repr__(self) -> str:
        return f"<BowlGame(id={self.id}, name='{self.name}', tier='{self.bowl_tier}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the bowl"""
        return self.full_name

    @property
    def location_display(self) -> str:
        """Formatted location string"""
        return f"{self.city}, {self.state}"

    @property
    def is_major_bowl(self) -> bool:
        """Whether this is considered a major bowl"""
        return self.bowl_tier in [BowlTier.CFP, BowlTier.NEW_YEARS_SIX, BowlTier.MAJOR]

    @property
    def selection_criteria_display(self) -> str:
        """Human-readable selection criteria"""
        return self.selection_criteria.value.replace("_", " ").title()


class BowlTieIn(Base, UUIDMixin, TimestampMixin):
    """
    Conference tie-ins to bowl games with selection rules
    """
    __tablename__ = "bowl_tie_ins"

    bowl_game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("bowl_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the bowl game"
    )

    conference_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the conference"
    )

    # Tie-in details
    tie_in_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of tie-in (primary, secondary, alternate)"
    )

    selection_priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Priority order for selection (1 = highest)"
    )

    required_position: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Required conference position (champion, runner-up, etc.)"
    )

    # Selection rules
    min_conference_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Minimum conference wins required"
    )

    max_losses_allowed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Maximum losses allowed"
    )

    ranking_requirement: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Ranking requirements (CFP ranking, etc.)"
    )

    # Contract details
    contract_start_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year tie-in contract started"
    )

    contract_end_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year tie-in contract ends"
    )

    is_automatic: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is an automatic tie-in"
    )

    # Relationships
    bowl_game: Mapped["BowlGame"] = relationship(
        "BowlGame",
        back_populates="bowl_tie_ins",
        lazy="selectin"
    )

    conference: Mapped["CollegeConference"] = relationship(
        "CollegeConference",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_bowl_tie_ins_bowl_id", "bowl_game_id"),
        Index("idx_bowl_tie_ins_conference_id", "conference_id"),
        Index("idx_bowl_tie_ins_type", "tie_in_type"),
        Index("idx_bowl_tie_ins_priority", "selection_priority"),
        Index("idx_bowl_tie_ins_automatic", "is_automatic"),
        UniqueConstraint("bowl_game_id", "conference_id", "tie_in_type", name="uq_bowl_tie_ins_bowl_conf_type"),
    )

    def __repr__(self) -> str:
        return f"<BowlTieIn(bowl='{self.bowl_game.name if self.bowl_game else None}', conference='{self.conference.name if self.conference else None}', type='{self.tie_in_type}')>"


class BowlSelection(Base, UUIDMixin, TimestampMixin):
    """
    Bowl selection process and team assignments for each season
    """
    __tablename__ = "bowl_selections"

    # Season context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    bowl_game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("bowl_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the bowl game"
    )

    # Team selections
    team1_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="First selected team"
    )

    team2_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="Second selected team"
    )

    # Game reference
    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="SET NULL"),
        doc="Reference to the actual game played"
    )

    # Selection details
    selection_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date teams were selected for this bowl"
    )

    announcement_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date selection was publicly announced"
    )

    # Selection criteria used
    team1_selection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for team1 selection (tie-in, at-large, etc.)"
    )

    team2_selection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for team2 selection (tie-in, at-large, etc.)"
    )

    # Team records at selection
    team1_record_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team1 wins at time of selection"
    )

    team1_record_losses: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team1 losses at time of selection"
    )

    team2_record_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team2 wins at time of selection"
    )

    team2_record_losses: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team2 losses at time of selection"
    )

    # Rankings at selection
    team1_cfp_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team1 CFP ranking at selection"
    )

    team2_cfp_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team2 CFP ranking at selection"
    )

    team1_ap_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team1 AP ranking at selection"
    )

    team2_ap_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team2 AP ranking at selection"
    )

    # Financial details
    payout_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        doc="Total payout for this bowl game"
    )

    # Status
    is_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether selection is confirmed"
    )

    is_cancelled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether bowl game was cancelled"
    )

    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for cancellation if applicable"
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    bowl_game: Mapped["BowlGame"] = relationship(
        "BowlGame",
        back_populates="bowl_selections",
        lazy="selectin"
    )

    team1: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[team1_id],
        lazy="selectin"
    )

    team2: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[team2_id],
        lazy="selectin"
    )

    game: Mapped[Optional["FootballGame"]] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_bowl_selections_academic_year_id", "academic_year_id"),
        Index("idx_bowl_selections_bowl_game_id", "bowl_game_id"),
        Index("idx_bowl_selections_team1_id", "team1_id"),
        Index("idx_bowl_selections_team2_id", "team2_id"),
        Index("idx_bowl_selections_game_id", "game_id"),
        Index("idx_bowl_selections_selection_date", "selection_date"),
        Index("idx_bowl_selections_confirmed", "is_confirmed"),
        Index("idx_bowl_selections_cancelled", "is_cancelled"),
        UniqueConstraint("academic_year_id", "bowl_game_id", name="uq_bowl_selections_year_bowl"),
    )

    def __repr__(self) -> str:
        return f"<BowlSelection(bowl='{self.bowl_game.name if self.bowl_game else None}', year='{self.academic_year.name if self.academic_year else None}')>"

    @property
    def teams_display(self) -> str:
        """Display teams for this bowl selection"""
        if self.team1 and self.team2:
            return f"{self.team1.display_name} vs {self.team2.display_name}"
        elif self.team1:
            return f"{self.team1.display_name} vs TBD"
        elif self.team2:
            return f"TBD vs {self.team2.display_name}"
        return "TBD vs TBD"


# =============================================================================
# College Football Playoff Models
# =============================================================================

class CollegeFootballPlayoff(Base, UUIDMixin, TimestampMixin):
    """
    12-team College Football Playoff structure and management
    """
    __tablename__ = "college_football_playoffs"

    # Season context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Playoff format details
    total_teams: Mapped[int] = mapped_column(
        Integer,
        default=12,
        nullable=False,
        doc="Total number of teams in playoff"
    )

    automatic_qualifiers: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
        doc="Number of automatic qualifiers (conference champions)"
    )

    at_large_bids: Mapped[int] = mapped_column(
        Integer,
        default=8,
        nullable=False,
        doc="Number of at-large bids"
    )

    # Selection and dates
    selection_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date playoff field was selected"
    )

    bracket_release_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date bracket was released"
    )

    first_round_start: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Start date of first round games"
    )

    championship_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of championship game"
    )

    # Status tracking
    current_round: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current round (0=not started, 1=first round, etc.)"
    )

    total_rounds: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
        doc="Total number of rounds"
    )

    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether playoff is complete"
    )

    # Champion tracking
    champion_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="National champion team"
    )

    runner_up_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Runner-up team"
    )

    # Selection criteria used
    selection_criteria: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON object with selection criteria and metrics used"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier"
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    champion_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[champion_team_id],
        lazy="selectin"
    )

    runner_up_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[runner_up_team_id],
        lazy="selectin"
    )

    playoff_teams: Mapped[List["CFPTeam"]] = relationship(
        "CFPTeam",
        back_populates="playoff",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="CFPTeam.seed"
    )

    playoff_games: Mapped[List["CFPGame"]] = relationship(
        "CFPGame",
        back_populates="playoff",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_cfp_academic_year_id", "academic_year_id"),
        Index("idx_cfp_current_round", "current_round"),
        Index("idx_cfp_complete", "is_complete"),
        Index("idx_cfp_selection_date", "selection_date"),
        Index("idx_cfp_external_id", "external_id"),
        UniqueConstraint("academic_year_id", name="uq_cfp_academic_year"),
    )

    def __repr__(self) -> str:
        return f"<CollegeFootballPlayoff(year='{self.academic_year.name if self.academic_year else None}', round={self.current_round})>"

    @property
    def display_name(self) -> str:
        """Display name for the playoff"""
        if self.academic_year:
            return f"{self.academic_year.name} College Football Playoff"
        return "College Football Playoff"

    @property
    def round_name(self) -> str:
        """Current round name"""
        round_names = {
            0: "Selection",
            1: "First Round",
            2: "Quarterfinals",
            3: "Semifinals",
            4: "Championship"
        }
        return round_names.get(self.current_round, f"Round {self.current_round}")


class CFPTeam(Base, UUIDMixin, TimestampMixin):
    """
    Teams in the College Football Playoff with seeding and progression
    """
    __tablename__ = "cfp_teams"

    playoff_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_football_playoffs.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the playoff"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    # Seeding and qualification
    seed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Playoff seed (1-12)"
    )

    seed_type: Mapped[CFPSeedType] = mapped_column(
        nullable=False,
        doc="Type of seed (auto_qualifier, at_large)"
    )

    # Qualification details
    conference_champion: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether team is a conference champion"
    )

    conference_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="SET NULL"),
        doc="Conference if champion"
    )

    # Team record at selection
    regular_season_wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Regular season wins"
    )

    regular_season_losses: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Regular season losses"
    )

    conference_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Conference wins"
    )

    conference_losses: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Conference losses"
    )

    # Rankings at selection
    cfp_ranking: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Final CFP ranking"
    )

    ap_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Final AP ranking"
    )

    # Playoff progression
    current_round: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        doc="Current round in playoff (1=first round)"
    )

    is_eliminated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether team is eliminated"
    )

    elimination_round: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Round in which team was eliminated"
    )

    # Selection metrics
    selection_metrics: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON object with team's selection metrics"
    )

    # Relationships
    playoff: Mapped["CollegeFootballPlayoff"] = relationship(
        "CollegeFootballPlayoff",
        back_populates="playoff_teams",
        lazy="selectin"
    )

    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    conference: Mapped[Optional["CollegeConference"]] = relationship(
        "CollegeConference",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_cfp_teams_playoff_id", "playoff_id"),
        Index("idx_cfp_teams_team_id", "team_id"),
        Index("idx_cfp_teams_seed", "seed"),
        Index("idx_cfp_teams_seed_type", "seed_type"),
        Index("idx_cfp_teams_conference_champion", "conference_champion"),
        Index("idx_cfp_teams_eliminated", "is_eliminated"),
        Index("idx_cfp_teams_current_round", "current_round"),
        UniqueConstraint("playoff_id", "team_id", name="uq_cfp_teams_playoff_team"),
        UniqueConstraint("playoff_id", "seed", name="uq_cfp_teams_playoff_seed"),
    )

    def __repr__(self) -> str:
        return f"<CFPTeam(team='{self.team.display_name if self.team else None}', seed={self.seed})>"

    @property
    def seed_display(self) -> str:
        """Display format for seed"""
        return f"#{self.seed}"

    @property
    def record_display(self) -> str:
        """Display team record"""
        return f"{self.regular_season_wins}-{self.regular_season_losses}"

    @property
    def qualification_display(self) -> str:
        """Display qualification method"""
        if self.conference_champion:
            return f"{self.conference.abbreviation if self.conference else 'Conference'} Champion"
        return "At-Large"


class CFPGame(Base, UUIDMixin, TimestampMixin):
    """
    College Football Playoff games with bracket progression
    """
    __tablename__ = "cfp_games"

    playoff_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_football_playoffs.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the playoff"
    )

    game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the actual game"
    )

    # Round and bracket information
    playoff_round: Mapped[PlayoffRound] = mapped_column(
        nullable=False,
        doc="Playoff round"
    )

    round_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Round number (1=first round, 4=championship)"
    )

    game_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Game number within round"
    )

    # Bracket positioning
    bracket_position: Mapped[Optional[BracketPosition]] = mapped_column(
        doc="Position within bracket"
    )

    # Team seedings
    higher_seed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Seed of higher-seeded team"
    )

    lower_seed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Seed of lower-seeded team"
    )

    # Venue details
    is_home_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether played at higher seed's home stadium (first round)"
    )

    is_neutral_site: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether played at neutral site"
    )

    # Bowl association (for quarterfinals/semifinals)
    host_bowl_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("bowl_games.id", ondelete="SET NULL"),
        doc="Host bowl for quarterfinal/semifinal games"
    )

    # Advancement tracking
    winner_advances_to: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("cfp_games.id", ondelete="SET NULL"),
        doc="Next game winner advances to"
    )

    # Game significance
    is_championship: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is the championship game"
    )

    is_semifinal: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a semifinal game"
    )

    # Relationships
    playoff: Mapped["CollegeFootballPlayoff"] = relationship(
        "CollegeFootballPlayoff",
        back_populates="playoff_games",
        lazy="selectin"
    )

    game: Mapped["FootballGame"] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    host_bowl: Mapped[Optional["BowlGame"]] = relationship(
        "BowlGame",
        lazy="selectin"
    )

    next_game: Mapped[Optional["CFPGame"]] = relationship(
        "CFPGame",
        foreign_keys=[winner_advances_to],
        remote_side="CFPGame.id",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_cfp_games_playoff_id", "playoff_id"),
        Index("idx_cfp_games_game_id", "game_id"),
        Index("idx_cfp_games_round", "playoff_round"),
        Index("idx_cfp_games_round_number", "round_number"),
        Index("idx_cfp_games_championship", "is_championship"),
        Index("idx_cfp_games_semifinal", "is_semifinal"),
        Index("idx_cfp_games_host_bowl_id", "host_bowl_id"),
        UniqueConstraint("playoff_id", "game_id", name="uq_cfp_games_playoff_game"),
    )

    def __repr__(self) -> str:
        return f"<CFPGame(round='{self.playoff_round}', game_id={self.game_id})>"

    @property
    def round_display(self) -> str:
        """Display round name"""
        return self.playoff_round.value.replace("_", " ").title()

    @property
    def matchup_display(self) -> str:
        """Display seed matchup"""
        if self.higher_seed and self.lower_seed:
            return f"#{self.higher_seed} vs #{self.lower_seed}"
        return "TBD"


# =============================================================================
# Conference Championship Models
# =============================================================================

class ConferenceChampionship(Base, UUIDMixin, TimestampMixin):
    """
    Conference championship games and automatic CFP qualifiers
    """
    __tablename__ = "conference_championships"

    # Season and conference context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    conference_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the conference"
    )

    # Championship format
    championship_format: Mapped[ConferenceChampionshipFormat] = mapped_column(
        nullable=False,
        doc="Format of championship determination"
    )

    has_championship_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether conference has a championship game"
    )

    # Game details (if championship game exists)
    championship_game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="SET NULL"),
        doc="Reference to championship game"
    )

    game_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of championship game"
    )

    venue_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Venue for championship game"
    )

    # Division structure (if applicable)
    has_divisions: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether conference has divisions"
    )

    division_structure: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON description of division structure"
    )

    # Championship determination
    champion_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Conference champion team"
    )

    runner_up_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Conference runner-up team"
    )

    # Tie-breaking procedures
    tiebreaker_rules: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Conference tie-breaking procedures"
    )

    tiebreaker_applied: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Tie-breaking procedures that were applied"
    )

    # CFP implications
    cfp_automatic_qualifier: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether champion receives automatic CFP qualification"
    )

    cfp_ranking_requirement: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="CFP ranking requirement for automatic qualification"
    )

    # Champion record and rankings
    champion_record_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Champion's wins"
    )

    champion_record_losses: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Champion's losses"
    )

    champion_conference_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Champion's conference wins"
    )

    champion_conference_losses: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Champion's conference losses"
    )

    champion_cfp_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Champion's final CFP ranking"
    )

    # Status
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether championship is determined"
    )

    determination_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date champion was determined"
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    conference: Mapped["CollegeConference"] = relationship(
        "CollegeConference",
        lazy="selectin"
    )

    championship_game: Mapped[Optional["FootballGame"]] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    champion_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[champion_team_id],
        lazy="selectin"
    )

    runner_up_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[runner_up_team_id],
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_conf_champ_academic_year_id", "academic_year_id"),
        Index("idx_conf_champ_conference_id", "conference_id"),
        Index("idx_conf_champ_game_id", "championship_game_id"),
        Index("idx_conf_champ_format", "championship_format"),
        Index("idx_conf_champ_has_game", "has_championship_game"),
        Index("idx_conf_champ_cfp_auto", "cfp_automatic_qualifier"),
        Index("idx_conf_champ_completed", "is_completed"),
        Index("idx_conf_champ_date", "game_date"),
        UniqueConstraint("academic_year_id", "conference_id", name="uq_conf_champ_year_conference"),
    )

    def __repr__(self) -> str:
        return f"<ConferenceChampionship(conference='{self.conference.name if self.conference else None}', year='{self.academic_year.name if self.academic_year else None}')>"

    @property
    def display_name(self) -> str:
        """Display name for the championship"""
        if self.conference:
            return f"{self.conference.name} Championship"
        return "Conference Championship"

    @property
    def champion_record_display(self) -> Optional[str]:
        """Display champion's record"""
        if self.champion_record_wins is not None and self.champion_record_losses is not None:
            return f"{self.champion_record_wins}-{self.champion_record_losses}"
        return None


# =============================================================================
# Rivalry Game Models
# =============================================================================

class RivalryGame(Base, UUIDMixin, TimestampMixin):
    """
    Traditional rivalry tracking and trophy games
    """
    __tablename__ = "rivalry_games"

    # Basic rivalry information
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Name of the rivalry (e.g., 'The Game', 'Iron Bowl')"
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        doc="URL-friendly slug for the rivalry"
    )

    nickname: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Common nickname for the rivalry"
    )

    # Teams involved
    team1_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="First team in rivalry"
    )

    team2_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Second team in rivalry"
    )

    # Rivalry classification
    rivalry_type: Mapped[RivalryType] = mapped_column(
        nullable=False,
        doc="Type of rivalry (conference, regional, national, etc.)"
    )

    intensity_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        doc="Intensity level of rivalry (1-10 scale)"
    )

    # Trophy information
    has_trophy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether rivalry has a trophy"
    )

    trophy_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of the trophy"
    )

    trophy_description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of the trophy and its history"
    )

    trophy_holder_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Current trophy holder"
    )

    trophy_status: Mapped[Optional[TrophyStatus]] = mapped_column(
        doc="Current status of the trophy"
    )

    # Historical information
    first_meeting: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year of first meeting"
    )

    total_meetings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of meetings"
    )

    team1_wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Team1 wins in series"
    )

    team2_wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Team2 wins in series"
    )

    ties: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Ties in series"
    )

    # Current streaks
    current_winner_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Team with current winning streak"
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Length of current winning streak"
    )

    longest_streak_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Team with longest winning streak"
    )

    longest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Length of longest winning streak"
    )

    # Game scheduling
    is_annual: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether teams play annually"
    )

    typical_date: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Typical date/time of year played"
    )

    alternates_venue: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether venue alternates between teams"
    )

    neutral_site_games: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether games are played at neutral sites"
    )

    # Significance and context
    conference_implications: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether game typically has conference championship implications"
    )

    playoff_implications: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether game typically has playoff implications"
    )

    recruiting_impact: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Regional recruiting impact description"
    )

    # Media and cultural significance
    tv_tradition: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Television broadcast tradition"
    )

    cultural_significance: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Cultural and historical significance"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether rivalry is currently active"
    )

    last_played_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year rivalry was last played"
    )

    hiatus_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for hiatus if not currently active"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier"
    )

    # Relationships
    team1: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[team1_id],
        lazy="selectin"
    )

    team2: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[team2_id],
        lazy="selectin"
    )

    trophy_holder: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[trophy_holder_id],
        lazy="selectin"
    )

    current_winner: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[current_winner_id],
        lazy="selectin"
    )

    longest_streak_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[longest_streak_team_id],
        lazy="selectin"
    )

    rivalry_games: Mapped[List["RivalryGameHistory"]] = relationship(
        "RivalryGameHistory",
        back_populates="rivalry",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_rivalry_games_slug", "slug"),
        Index("idx_rivalry_games_team1_id", "team1_id"),
        Index("idx_rivalry_games_team2_id", "team2_id"),
        Index("idx_rivalry_games_type", "rivalry_type"),
        Index("idx_rivalry_games_intensity", "intensity_level"),
        Index("idx_rivalry_games_trophy", "has_trophy"),
        Index("idx_rivalry_games_active", "is_active"),
        Index("idx_rivalry_games_annual", "is_annual"),
        Index("idx_rivalry_games_external_id", "external_id"),
        UniqueConstraint("team1_id", "team2_id", name="uq_rivalry_games_teams"),
    )

    def __repr__(self) -> str:
        return f"<RivalryGame(name='{self.name}', teams='{self.team1.display_name if self.team1 else None} vs {self.team2.display_name if self.team2 else None}')>"

    @property
    def display_name(self) -> str:
        """Display name for the rivalry"""
        return self.name

    @property
    def teams_display(self) -> str:
        """Display teams in rivalry"""
        team1_name = self.team1.display_name if self.team1 else "Team 1"
        team2_name = self.team2.display_name if self.team2 else "Team 2"
        return f"{team1_name} vs {team2_name}"

    @property
    def series_record_display(self) -> str:
        """Display overall series record"""
        if self.ties > 0:
            return f"{self.team1_wins}-{self.team2_wins}-{self.ties}"
        return f"{self.team1_wins}-{self.team2_wins}"

    @property
    def series_leader(self) -> Optional["FootballTeam"]:
        """Team leading the overall series"""
        if self.team1_wins > self.team2_wins:
            return self.team1
        elif self.team2_wins > self.team1_wins:
            return self.team2
        return None


class RivalryGameHistory(Base, UUIDMixin, TimestampMixin):
    """
    Historical record of individual rivalry games
    """
    __tablename__ = "rivalry_game_history"

    rivalry_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("rivalry_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the rivalry"
    )

    game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the actual game"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Game context
    game_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Number of this meeting in the series"
    )

    # Pre-game context
    team1_record_before: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Team1 record before this game"
    )

    team2_record_before: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Team2 record before this game"
    )

    team1_ranking_before: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team1 ranking before this game"
    )

    team2_ranking_before: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team2 ranking before this game"
    )

    # Game significance
    conference_implications: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Conference championship implications"
    )

    playoff_implications: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Playoff/bowl implications"
    )

    # Trophy tracking
    trophy_on_line: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether trophy was on the line"
    )

    trophy_changed_hands: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether trophy changed hands"
    )

    # Game outcome
    winning_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Winner of this rivalry game"
    )

    margin_of_victory: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Margin of victory"
    )

    # Notable aspects
    overtime_periods: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of overtime periods if applicable"
    )

    notable_performances: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notable individual performances"
    )

    game_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notable aspects of this game"
    )

    # Relationships
    rivalry: Mapped["RivalryGame"] = relationship(
        "RivalryGame",
        back_populates="rivalry_games",
        lazy="selectin"
    )

    game: Mapped["FootballGame"] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    winning_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_rivalry_history_rivalry_id", "rivalry_id"),
        Index("idx_rivalry_history_game_id", "game_id"),
        Index("idx_rivalry_history_academic_year_id", "academic_year_id"),
        Index("idx_rivalry_history_game_number", "game_number"),
        Index("idx_rivalry_history_trophy", "trophy_on_line"),
        Index("idx_rivalry_history_winning_team_id", "winning_team_id"),
        UniqueConstraint("rivalry_id", "game_id", name="uq_rivalry_history_rivalry_game"),
        UniqueConstraint("rivalry_id", "academic_year_id", name="uq_rivalry_history_rivalry_year"),
    )

    def __repr__(self) -> str:
        return f"<RivalryGameHistory(rivalry='{self.rivalry.name if self.rivalry else None}', game_number={self.game_number})>"


# =============================================================================
# General Postseason Tournament Framework
# =============================================================================

class PostseasonTournament(Base, UUIDMixin, TimestampMixin):
    """
    General postseason tournament framework extending basketball Tournament model
    Supports both football-specific tournaments and shared tournament infrastructure
    """
    __tablename__ = "postseason_tournaments"

    # References to existing Tournament infrastructure
    tournament_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        doc="Reference to base tournament (for basketball compatibility)"
    )

    # Season context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    season_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        doc="Reference to the specific season"
    )

    # Tournament identification
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Tournament name"
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="URL-friendly slug"
    )

    sport_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Sport type (football, basketball, etc.)"
    )

    # Tournament format
    postseason_format: Mapped[PostseasonFormat] = mapped_column(
        nullable=False,
        doc="Format of postseason tournament"
    )

    selection_method: Mapped[SelectionMethod] = mapped_column(
        nullable=False,
        doc="Method for team selection"
    )

    total_participants: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total number of participating teams"
    )

    # Selection details
    automatic_qualifiers: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of automatic qualifiers"
    )

    at_large_selections: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of at-large selections"
    )

    selection_criteria: Mapped[Optional[str]] = mapped_column(
        JSONB,
        doc="JSON object describing selection criteria"
    )

    # Tournament progression
    current_stage: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Current stage of tournament"
    )

    total_stages: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total number of tournament stages"
    )

    # Dates and timing
    selection_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date field/participants were selected"
    )

    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Tournament start date"
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Tournament end date"
    )

    # Championship tracking
    champion_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Tournament champion"
    )

    runner_up_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Tournament runner-up"
    )

    # Status
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether tournament is completed"
    )

    is_cancelled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether tournament was cancelled"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier"
    )

    # Relationships
    tournament: Mapped[Optional["Tournament"]] = relationship(
        "Tournament",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    season: Mapped[Optional["Season"]] = relationship(
        "Season",
        lazy="selectin"
    )

    champion_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[champion_team_id],
        lazy="selectin"
    )

    runner_up_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[runner_up_team_id],
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_postseason_tournaments_tournament_id", "tournament_id"),
        Index("idx_postseason_tournaments_academic_year_id", "academic_year_id"),
        Index("idx_postseason_tournaments_season_id", "season_id"),
        Index("idx_postseason_tournaments_slug", "slug"),
        Index("idx_postseason_tournaments_sport", "sport_type"),
        Index("idx_postseason_tournaments_format", "postseason_format"),
        Index("idx_postseason_tournaments_completed", "is_completed"),
        Index("idx_postseason_tournaments_external_id", "external_id"),
        UniqueConstraint("academic_year_id", "slug", name="uq_postseason_tournaments_year_slug"),
    )

    def __repr__(self) -> str:
        return f"<PostseasonTournament(name='{self.name}', sport='{self.sport_type}', year='{self.academic_year.name if self.academic_year else None}')>"

    @property
    def display_name(self) -> str:
        """Display name for the tournament"""
        if self.academic_year:
            return f"{self.name} ({self.academic_year.name})"
        return self.name

    @property
    def format_display(self) -> str:
        """Human-readable format description"""
        return self.postseason_format.value.replace("_", " ").title()