"""
College Football Phase 1: Foundation Models
Extends existing college basketball infrastructure with football-specific capabilities
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, Date, DateTime, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    FootballPosition, FootballPositionGroup, FootballPlayType, FootballGameContext,
    FootballWeatherCondition, FootballFormation, BowlGameType, FootballSeasonType,
    RecruitingClass, ScholarshipType, FootballRankingSystem,
    PlayerEligibilityStatus, PlayerClass, GameStatus, GameResult
)


# =============================================================================
# Football Team Models
# =============================================================================

class FootballTeam(Base, UUIDMixin, TimestampMixin):
    """
    College Football Teams - extends the existing college infrastructure
    Links to existing CollegeTeam for shared attributes
    """
    __tablename__ = "football_teams"

    # Reference to existing college team infrastructure
    college_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the college team in the general sports system"
    )

    # Football-specific team attributes
    stadium_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of the football stadium"
    )

    stadium_capacity: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Seating capacity of the football stadium"
    )

    field_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Type of playing field (natural grass, artificial turf, etc.)"
    )

    # Coaching staff
    head_coach: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Current head football coach name"
    )

    offensive_coordinator: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Current offensive coordinator name"
    )

    defensive_coordinator: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Current defensive coordinator name"
    )

    coach_since_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year the current head coach started"
    )

    # Historical performance
    national_championships: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of national championships"
    )

    bowl_appearances: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of bowl game appearances"
    )

    bowl_wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of bowl game wins"
    )

    playoff_appearances: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of College Football Playoff appearances"
    )

    # Current season information
    current_record_wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current season wins"
    )

    current_record_losses: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current season losses"
    )

    conference_record_wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current conference record wins"
    )

    conference_record_losses: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current conference record losses"
    )

    # Rankings
    ap_poll_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current AP Poll ranking (1-25, NULL if unranked)"
    )

    coaches_poll_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current Coaches Poll ranking (1-25, NULL if unranked)"
    )

    cfp_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current College Football Playoff ranking"
    )

    # Team style and characteristics
    offensive_scheme: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Primary offensive scheme (spread, pro-style, option, etc.)"
    )

    defensive_scheme: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Primary defensive scheme (3-4, 4-3, etc.)"
    )

    # Recruiting and roster management
    scholarship_count: Mapped[int] = mapped_column(
        Integer,
        default=85,
        nullable=False,
        doc="Current number of scholarships awarded (max 85)"
    )

    roster_size: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total roster size including walk-ons"
    )

    # External identifiers
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this football team"
    )

    espn_team_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="ESPN team identifier"
    )

    cfb_data_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="CollegeFootballData.com team identifier"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this football team is currently active"
    )

    # Relationships
    college_team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    players: Mapped[List["FootballPlayer"]] = relationship(
        "FootballPlayer",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="select"
    )

    games_home: Mapped[List["FootballGame"]] = relationship(
        "FootballGame",
        foreign_keys="FootballGame.home_team_id",
        back_populates="home_team",
        lazy="select"
    )

    games_away: Mapped[List["FootballGame"]] = relationship(
        "FootballGame",
        foreign_keys="FootballGame.away_team_id",
        back_populates="away_team",
        lazy="select"
    )

    roster_entries: Mapped[List["FootballRoster"]] = relationship(
        "FootballRoster",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_teams_college_team_id", "college_team_id"),
        Index("idx_football_teams_external_id", "external_id"),
        Index("idx_football_teams_espn_id", "espn_team_id"),
        Index("idx_football_teams_cfb_data_id", "cfb_data_id"),
        Index("idx_football_teams_rankings", "ap_poll_rank", "coaches_poll_rank", "cfp_ranking"),
        Index("idx_football_teams_active", "is_active"),
        UniqueConstraint("college_team_id", name="uq_football_teams_college_team"),
    )

    def __repr__(self) -> str:
        return f"<FootballTeam(id={self.id}, college_team='{self.college_team.name if self.college_team else None}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the team"""
        if self.college_team and self.college_team.college:
            return f"{self.college_team.college.display_name} {self.college_team.name}"
        elif self.college_team:
            return self.college_team.name
        return "Unknown Team"

    @property
    def overall_record(self) -> str:
        """Formatted overall record string"""
        return f"{self.current_record_wins}-{self.current_record_losses}"

    @property
    def conference_record(self) -> str:
        """Formatted conference record string"""
        return f"{self.conference_record_wins}-{self.conference_record_losses}"

    @property
    def is_ranked(self) -> bool:
        """Whether the team is currently ranked in major polls"""
        return (self.ap_poll_rank is not None and self.ap_poll_rank <= 25) or \
               (self.coaches_poll_rank is not None and self.coaches_poll_rank <= 25) or \
               (self.cfp_ranking is not None and self.cfp_ranking <= 25)

    @property
    def scholarship_remaining(self) -> int:
        """Number of scholarships remaining"""
        return max(0, 85 - self.scholarship_count)

    @property
    def bowl_win_percentage(self) -> Optional[Decimal]:
        """Bowl game winning percentage"""
        if self.bowl_appearances > 0:
            return Decimal(self.bowl_wins) / Decimal(self.bowl_appearances)
        return None


# =============================================================================
# Football Player Models
# =============================================================================

class FootballPlayer(Base, UUIDMixin, TimestampMixin):
    """
    Individual football players with football-specific attributes
    """
    __tablename__ = "football_players"

    # Team association
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football team"
    )

    # Basic information
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Player's first name"
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Player's last name"
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Player's full name (computed or provided)"
    )

    jersey_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Player's jersey number"
    )

    # Football positions
    primary_position: Mapped[FootballPosition] = mapped_column(
        nullable=False,
        doc="Player's primary position"
    )

    secondary_position: Mapped[Optional[FootballPosition]] = mapped_column(
        doc="Player's secondary position (if applicable)"
    )

    position_group: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Position group for depth chart organization"
    )

    # Physical attributes
    height_inches: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Player's height in total inches"
    )

    weight_pounds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Player's weight in pounds"
    )

    # Speed metrics
    forty_yard_dash: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        doc="40-yard dash time in seconds"
    )

    bench_press: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Bench press repetitions at 225 lbs"
    )

    vertical_jump: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        doc="Vertical jump in inches"
    )

    # Biographical information
    birth_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Player's birth date"
    )

    hometown: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Player's hometown"
    )

    home_state: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Player's home state"
    )

    home_country: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="USA",
        doc="Player's home country"
    )

    high_school: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Player's high school"
    )

    junior_college: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Junior college attended (if applicable)"
    )

    previous_college: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Previous college (for transfers)"
    )

    # Academic and eligibility
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the current academic year"
    )

    player_class: Mapped[PlayerClass] = mapped_column(
        nullable=False,
        doc="Academic class standing"
    )

    eligibility_status: Mapped[PlayerEligibilityStatus] = mapped_column(
        nullable=False,
        default=PlayerEligibilityStatus.ELIGIBLE,
        doc="Current eligibility status"
    )

    years_of_eligibility_remaining: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
        doc="Years of eligibility remaining"
    )

    # Scholarship information
    scholarship_type: Mapped[ScholarshipType] = mapped_column(
        nullable=False,
        default=ScholarshipType.WALK_ON,
        doc="Type of scholarship or status"
    )

    scholarship_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Percentage of full scholarship (0-100)"
    )

    # Transfer information
    is_transfer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether player is a transfer"
    )

    transfer_from_college_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="SET NULL"),
        doc="College transferred from (if applicable)"
    )

    transfer_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year of transfer"
    )

    is_juco_transfer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether player transferred from junior college"
    )

    # Recruiting information
    recruiting_class_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="High school recruiting class year"
    )

    recruiting_stars: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Recruiting star rating (1-5)"
    )

    recruiting_rank_national: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="National recruiting ranking"
    )

    recruiting_rank_position: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Position-specific recruiting ranking"
    )

    recruiting_rank_state: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="State recruiting ranking"
    )

    # Professional prospects
    nfl_draft_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether player is NFL draft eligible"
    )

    nfl_draft_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year of NFL draft declaration/eligibility"
    )

    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this player"
    )

    espn_player_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="ESPN player identifier"
    )

    cfb_data_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="CollegeFootballData.com player identifier"
    )

    # Media and social
    photo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to player's photo"
    )

    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Player biography/background"
    )

    # Status tracking
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether player is currently active"
    )

    injury_status: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Current injury status description"
    )

    is_suspended: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether player is currently suspended"
    )

    suspension_details: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Details about current suspension"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        back_populates="players",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    transfer_from_college: Mapped[Optional["College"]] = relationship(
        "College",
        lazy="selectin"
    )

    roster_entries: Mapped[List["FootballRoster"]] = relationship(
        "FootballRoster",
        back_populates="player",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_players_team_id", "team_id"),
        Index("idx_football_players_academic_year_id", "academic_year_id"),
        Index("idx_football_players_full_name", "full_name"),
        Index("idx_football_players_last_name", "last_name"),
        Index("idx_football_players_jersey_number", "jersey_number"),
        Index("idx_football_players_position", "primary_position"),
        Index("idx_football_players_position_group", "position_group"),
        Index("idx_football_players_class", "player_class"),
        Index("idx_football_players_eligibility", "eligibility_status"),
        Index("idx_football_players_scholarship", "scholarship_type"),
        Index("idx_football_players_transfer", "is_transfer"),
        Index("idx_football_players_active", "is_active"),
        Index("idx_football_players_external_id", "external_id"),
        Index("idx_football_players_espn_id", "espn_player_id"),
        Index("idx_football_players_cfb_data_id", "cfb_data_id"),
        Index("idx_football_players_team_jersey", "team_id", "jersey_number"),
        UniqueConstraint("team_id", "jersey_number", "academic_year_id", name="uq_football_players_team_jersey_year"),
    )

    def __repr__(self) -> str:
        return f"<FootballPlayer(id={self.id}, name='{self.full_name}', jersey={self.jersey_number}, position='{self.primary_position}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the player"""
        return self.full_name

    @property
    def display_name_with_jersey(self) -> str:
        """Player name with jersey number"""
        if self.jersey_number:
            return f"#{self.jersey_number} {self.full_name}"
        return self.full_name

    @property
    def height_display(self) -> Optional[str]:
        """Display height in feet and inches"""
        if self.height_inches:
            feet = self.height_inches // 12
            inches = self.height_inches % 12
            return f"{feet}'{inches}\""
        return None

    @property
    def age(self) -> Optional[int]:
        """Calculate player's current age"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def is_injured(self) -> bool:
        """Check if player is currently injured"""
        return self.eligibility_status == PlayerEligibilityStatus.INJURED or self.injury_status is not None

    @property
    def is_eligible_to_play(self) -> bool:
        """Check if player is eligible to play"""
        return (self.eligibility_status == PlayerEligibilityStatus.ELIGIBLE and
                self.is_active and not self.is_suspended)

    @property
    def is_on_scholarship(self) -> bool:
        """Check if player has any type of scholarship"""
        return self.scholarship_type in [ScholarshipType.FULL_SCHOLARSHIP, ScholarshipType.PARTIAL_SCHOLARSHIP]


# =============================================================================
# Football Game Models
# =============================================================================

class FootballGame(Base, UUIDMixin, TimestampMixin):
    """
    Football games with football-specific attributes
    """
    __tablename__ = "football_games"

    # Team associations
    home_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the home team"
    )

    away_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the away team"
    )

    # Academic context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    season_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        doc="Reference to specific season"
    )

    # Game scheduling
    game_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of the game"
    )

    kickoff_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Scheduled kickoff time"
    )

    week_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Week number of the season"
    )

    # Game classification
    season_type: Mapped[FootballSeasonType] = mapped_column(
        nullable=False,
        default=FootballSeasonType.REGULAR_SEASON,
        doc="Type of season this game belongs to"
    )

    bowl_game_type: Mapped[Optional[BowlGameType]] = mapped_column(
        doc="Type of bowl game (if applicable)"
    )

    bowl_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of the bowl game"
    )

    is_conference_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a conference game"
    )

    is_rivalry_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a rivalry game"
    )

    rivalry_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of the rivalry (if applicable)"
    )

    # Venue information
    venue_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of the venue"
    )

    venue_city: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="City where the game is played"
    )

    venue_state: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="State where the game is played"
    )

    is_neutral_site: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is played at a neutral site"
    )

    # Game status and results
    status: Mapped[GameStatus] = mapped_column(
        nullable=False,
        default=GameStatus.SCHEDULED,
        doc="Current status of the game"
    )

    home_team_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Home team final score"
    )

    away_team_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Away team final score"
    )

    # Weather conditions
    weather_condition: Mapped[Optional[FootballWeatherCondition]] = mapped_column(
        doc="Weather conditions during the game"
    )

    temperature: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Temperature in Fahrenheit"
    )

    wind_speed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Wind speed in mph"
    )

    precipitation: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Precipitation description"
    )

    # Attendance and broadcast
    attendance: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Actual attendance"
    )

    tv_network: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Television network broadcasting the game"
    )

    broadcast_time: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Broadcast time slot"
    )

    # Game importance and context
    game_importance: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Importance level of the game"
    )

    playoff_implications: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Playoff implications of the game"
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

    cfb_data_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="CollegeFootballData.com game identifier"
    )

    # Relationships
    home_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[home_team_id],
        back_populates="games_home",
        lazy="selectin"
    )

    away_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[away_team_id],
        back_populates="games_away",
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

    # Indexes
    __table_args__ = (
        Index("idx_football_games_home_team_id", "home_team_id"),
        Index("idx_football_games_away_team_id", "away_team_id"),
        Index("idx_football_games_academic_year_id", "academic_year_id"),
        Index("idx_football_games_season_id", "season_id"),
        Index("idx_football_games_date", "game_date"),
        Index("idx_football_games_week", "week_number"),
        Index("idx_football_games_status", "status"),
        Index("idx_football_games_season_type", "season_type"),
        Index("idx_football_games_conference", "is_conference_game"),
        Index("idx_football_games_bowl", "bowl_game_type"),
        Index("idx_football_games_external_id", "external_id"),
        Index("idx_football_games_espn_id", "espn_game_id"),
        Index("idx_football_games_cfb_data_id", "cfb_data_id"),
        Index("idx_football_games_teams", "home_team_id", "away_team_id"),
        Index("idx_football_games_date_teams", "game_date", "home_team_id", "away_team_id"),
        UniqueConstraint("home_team_id", "away_team_id", "game_date", name="uq_football_games_teams_date"),
    )

    def __repr__(self) -> str:
        return f"<FootballGame(id={self.id}, {self.away_team.display_name if self.away_team else 'Away'} @ {self.home_team.display_name if self.home_team else 'Home'}, {self.game_date})>"

    @property
    def display_name(self) -> str:
        """Display name for the game"""
        away_name = self.away_team.display_name if self.away_team else "Away Team"
        home_name = self.home_team.display_name if self.home_team else "Home Team"
        return f"{away_name} @ {home_name}"

    @property
    def score_display(self) -> Optional[str]:
        """Display the score if game is completed"""
        if self.status == GameStatus.FINAL and self.home_team_score is not None and self.away_team_score is not None:
            return f"{self.away_team_score}-{self.home_team_score}"
        return None

    @property
    def winner_id(self) -> Optional[UUID]:
        """ID of the winning team"""
        if self.status == GameStatus.FINAL and self.home_team_score is not None and self.away_team_score is not None:
            if self.home_team_score > self.away_team_score:
                return self.home_team_id
            elif self.away_team_score > self.home_team_score:
                return self.away_team_id
        return None

    @property
    def is_completed(self) -> bool:
        """Whether the game is completed"""
        return self.status == GameStatus.FINAL

    @property
    def margin_of_victory(self) -> Optional[int]:
        """Margin of victory for the winning team"""
        if self.status == GameStatus.FINAL and self.home_team_score is not None and self.away_team_score is not None:
            return abs(self.home_team_score - self.away_team_score)
        return None


# =============================================================================
# Football Roster Management
# =============================================================================

class FootballRoster(Base, UUIDMixin, TimestampMixin):
    """
    Football roster management with scholarship tracking
    Supports the 85-scholarship limit for football
    """
    __tablename__ = "football_rosters"

    # References
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football team"
    )

    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football player"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Roster status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether player is active on roster"
    )

    roster_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        doc="Roster status (active, injured, suspended, etc.)"
    )

    # Depth chart information
    position_group: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Position group for depth chart"
    )

    depth_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        doc="Depth order within position group (1 = starter)"
    )

    is_starter: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether player is a starter"
    )

    # Special teams roles
    special_teams_roles: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Special teams roles (JSON array of roles)"
    )

    is_captain: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether player is a team captain"
    )

    # Scholarship tracking
    scholarship_type: Mapped[ScholarshipType] = mapped_column(
        nullable=False,
        default=ScholarshipType.WALK_ON,
        doc="Type of scholarship"
    )

    scholarship_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Percentage of full scholarship (0-100)"
    )

    scholarship_count: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        default=0,
        nullable=False,
        doc="Scholarship count towards 85 limit (partial scholarships < 1.0)"
    )

    # Academic tracking
    academic_standing: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Academic standing status"
    )

    gpa: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Current GPA"
    )

    is_academically_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether player is academically eligible"
    )

    # Status dates
    roster_added_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date player was added to roster"
    )

    last_status_change: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of last status change"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        back_populates="roster_entries",
        lazy="selectin"
    )

    player: Mapped["FootballPlayer"] = relationship(
        "FootballPlayer",
        back_populates="roster_entries",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_rosters_team_id", "team_id"),
        Index("idx_football_rosters_player_id", "player_id"),
        Index("idx_football_rosters_academic_year_id", "academic_year_id"),
        Index("idx_football_rosters_active", "is_active"),
        Index("idx_football_rosters_position_group", "position_group"),
        Index("idx_football_rosters_depth", "position_group", "depth_order"),
        Index("idx_football_rosters_starters", "is_starter"),
        Index("idx_football_rosters_scholarship", "scholarship_type"),
        Index("idx_football_rosters_team_year", "team_id", "academic_year_id"),
        UniqueConstraint("team_id", "player_id", "academic_year_id", name="uq_football_rosters_team_player_year"),
    )

    def __repr__(self) -> str:
        return f"<FootballRoster(team='{self.team.display_name if self.team else None}', player='{self.player.full_name if self.player else None}', position='{self.position_group}', depth={self.depth_order})>"

    @property
    def is_on_scholarship(self) -> bool:
        """Whether player has any scholarship"""
        return self.scholarship_count > 0

    @property
    def scholarship_display(self) -> str:
        """Display scholarship information"""
        if self.scholarship_type == ScholarshipType.FULL_SCHOLARSHIP:
            return "Full Scholarship"
        elif self.scholarship_type == ScholarshipType.PARTIAL_SCHOLARSHIP:
            return f"Partial Scholarship ({self.scholarship_percentage}%)"
        else:
            return self.scholarship_type.value.replace("_", " ").title()


# =============================================================================
# Football Season Management
# =============================================================================

class FootballSeason(Base, UUIDMixin, TimestampMixin):
    """
    Football-specific season information and configuration
    """
    __tablename__ = "football_seasons"

    # Reference to base season
    season_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the base season"
    )

    # Football-specific season attributes
    regular_season_weeks: Mapped[int] = mapped_column(
        Integer,
        default=12,
        nullable=False,
        doc="Number of regular season weeks"
    )

    conference_championship_week: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Week number for conference championships"
    )

    bowl_selection_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when bowl selections are announced"
    )

    playoff_selection_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when playoff selections are announced"
    )

    national_championship_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of national championship game"
    )

    # Transfer portal windows
    transfer_portal_open_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date transfer portal opens"
    )

    transfer_portal_close_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date transfer portal closes"
    )

    # Recruiting calendar
    early_signing_period_start: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Start of early signing period"
    )

    early_signing_period_end: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="End of early signing period"
    )

    regular_signing_period_start: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Start of regular signing period"
    )

    # Spring practice
    spring_practice_start: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Start of spring practice"
    )

    spring_game_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of spring game"
    )

    # Fall practice
    fall_practice_start: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Start of fall practice"
    )

    # Rules and regulations for the season
    scholarship_limit: Mapped[int] = mapped_column(
        Integer,
        default=85,
        nullable=False,
        doc="Scholarship limit for the season"
    )

    roster_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total roster size limit"
    )

    # Bowl game information
    total_bowl_games: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total number of bowl games"
    )

    bowl_eligibility_requirement: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Requirement for bowl eligibility (e.g., '6 wins')"
    )

    # Playoff format
    playoff_teams: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of teams in playoff"
    )

    playoff_format: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of playoff format"
    )

    # Status
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is the current football season"
    )

    # Relationships
    season: Mapped["Season"] = relationship(
        "Season",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_seasons_season_id", "season_id"),
        Index("idx_football_seasons_current", "is_current"),
        Index("idx_football_seasons_bowl_selection", "bowl_selection_date"),
        Index("idx_football_seasons_playoff_selection", "playoff_selection_date"),
        UniqueConstraint("season_id", name="uq_football_seasons_season"),
    )

    def __repr__(self) -> str:
        return f"<FootballSeason(season='{self.season.name if self.season else None}', weeks={self.regular_season_weeks})>"

    @property
    def display_name(self) -> str:
        """Display name for the football season"""
        if self.season:
            return f"Football {self.season.name}"
        return "Football Season"

    @property
    def is_bowl_season(self) -> bool:
        """Whether it's currently bowl season"""
        if self.bowl_selection_date:
            return date.today() >= self.bowl_selection_date
        return False

    @property
    def is_playoff_season(self) -> bool:
        """Whether it's currently playoff season"""
        if self.playoff_selection_date:
            return date.today() >= self.playoff_selection_date
        return False