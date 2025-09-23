"""
College Basketball Phase 4: Statistics & Rankings Models
Players, Statistics, Rankings, Advanced Metrics, and Season Records
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
    PlayerPosition, PlayerEligibilityStatus, PlayerClass,
    RankingSystem, StatisticType, StatisticCategory, RecordType
)


# =============================================================================
# Phase 4: Player Models
# =============================================================================

class Player(Base, UUIDMixin, TimestampMixin):
    """
    Individual basketball players with biographical and eligibility data
    """
    __tablename__ = "college_players"

    # Team association
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the current team"
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

    # Playing position
    primary_position: Mapped[PlayerPosition] = mapped_column(
        nullable=False,
        doc="Player's primary position"
    )

    secondary_position: Mapped[Optional[PlayerPosition]] = mapped_column(
        doc="Player's secondary position (if applicable)"
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

    # Recruiting and rankings
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

    # Professional prospects
    nba_draft_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether player is NBA draft eligible"
    )

    nba_draft_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year of NBA draft declaration/eligibility"
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

    ncaa_player_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="NCAA official player identifier"
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

    # Relationships
    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
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

    player_statistics: Mapped[List["PlayerStatistics"]] = relationship(
        "PlayerStatistics",
        back_populates="player",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_players_team_id", "team_id"),
        Index("idx_players_academic_year_id", "academic_year_id"),
        Index("idx_players_full_name", "full_name"),
        Index("idx_players_last_name", "last_name"),
        Index("idx_players_jersey_number", "jersey_number"),
        Index("idx_players_position", "primary_position"),
        Index("idx_players_class", "player_class"),
        Index("idx_players_eligibility", "eligibility_status"),
        Index("idx_players_transfer", "is_transfer"),
        Index("idx_players_active", "is_active"),
        Index("idx_players_external_id", "external_id"),
        Index("idx_players_espn_id", "espn_player_id"),
        Index("idx_players_ncaa_id", "ncaa_player_id"),
        Index("idx_players_team_jersey", "team_id", "jersey_number"),
        UniqueConstraint("team_id", "jersey_number", "academic_year_id", name="uq_players_team_jersey_year"),
    )

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.full_name}', jersey={self.jersey_number}, team='{self.team.name if self.team else None}')>"

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
        return self.eligibility_status == PlayerEligibilityStatus.ELIGIBLE and self.is_active


# =============================================================================
# Phase 4: Statistics Models
# =============================================================================

class TeamStatistics(Base, UUIDMixin, TimestampMixin):
    """
    Team-level statistics for seasons and games
    """
    __tablename__ = "team_statistics"

    # References
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    season_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        doc="Reference to specific season (NULL for season totals)"
    )

    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_games.id", ondelete="CASCADE"),
        doc="Reference to specific game (NULL for season stats)"
    )

    # Statistic metadata
    statistic_type: Mapped[StatisticType] = mapped_column(
        nullable=False,
        doc="Type of statistic (season total, average, etc.)"
    )

    # Game count and context
    games_played: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of games played (for averages)"
    )

    # Scoring statistics
    points: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=0,
        nullable=False,
        doc="Total points or points per game"
    )

    field_goals_made: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Field goals made"
    )

    field_goals_attempted: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Field goals attempted"
    )

    field_goal_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Field goal percentage"
    )

    three_pointers_made: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Three-pointers made"
    )

    three_pointers_attempted: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Three-pointers attempted"
    )

    three_point_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Three-point percentage"
    )

    free_throws_made: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Free throws made"
    )

    free_throws_attempted: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Free throws attempted"
    )

    free_throw_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Free throw percentage"
    )

    # Rebounding statistics
    offensive_rebounds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Offensive rebounds"
    )

    defensive_rebounds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Defensive rebounds"
    )

    total_rebounds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Total rebounds"
    )

    # Playmaking and defense
    assists: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Assists"
    )

    steals: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Steals"
    )

    blocks: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Blocks"
    )

    turnovers: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Turnovers"
    )

    personal_fouls: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Personal fouls"
    )

    # Team-specific statistics
    points_allowed: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Points allowed by defense"
    )

    # Updated timestamp
    stats_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date these statistics are current as of"
    )

    # Relationships
    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
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

    game: Mapped[Optional["CollegeGame"]] = relationship(
        "CollegeGame",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_team_statistics_team_id", "team_id"),
        Index("idx_team_statistics_academic_year_id", "academic_year_id"),
        Index("idx_team_statistics_season_id", "season_id"),
        Index("idx_team_statistics_game_id", "game_id"),
        Index("idx_team_statistics_type", "statistic_type"),
        Index("idx_team_statistics_stats_date", "stats_date"),
        Index("idx_team_statistics_team_year", "team_id", "academic_year_id"),
        UniqueConstraint("team_id", "game_id", "statistic_type", name="uq_team_statistics_team_game_type"),
        UniqueConstraint("team_id", "season_id", "statistic_type", name="uq_team_statistics_team_season_type"),
    )

    def __repr__(self) -> str:
        context = "Season" if self.season_id else ("Game" if self.game_id else "Total")
        return f"<TeamStatistics(team='{self.team.name if self.team else None}', type='{self.statistic_type}', context='{context}')>"


class PlayerStatistics(Base, UUIDMixin, TimestampMixin):
    """
    Individual player statistics for seasons and games
    """
    __tablename__ = "player_statistics"

    # References
    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the player"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team (for transfers)"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    season_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        doc="Reference to specific season (NULL for season totals)"
    )

    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_games.id", ondelete="CASCADE"),
        doc="Reference to specific game (NULL for season stats)"
    )

    # Statistic metadata
    statistic_type: Mapped[StatisticType] = mapped_column(
        nullable=False,
        doc="Type of statistic (season total, average, etc.)"
    )

    # Playing time
    minutes_played: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        doc="Minutes played"
    )

    games_played: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of games played (for averages)"
    )

    games_started: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of games started"
    )

    # Scoring statistics
    points: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=0,
        nullable=False,
        doc="Total points or points per game"
    )

    field_goals_made: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Field goals made"
    )

    field_goals_attempted: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Field goals attempted"
    )

    field_goal_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Field goal percentage"
    )

    three_pointers_made: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Three-pointers made"
    )

    three_pointers_attempted: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Three-pointers attempted"
    )

    three_point_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Three-point percentage"
    )

    free_throws_made: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Free throws made"
    )

    free_throws_attempted: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Free throws attempted"
    )

    free_throw_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Free throw percentage"
    )

    # Rebounding statistics
    offensive_rebounds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Offensive rebounds"
    )

    defensive_rebounds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Defensive rebounds"
    )

    total_rebounds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Total rebounds"
    )

    # Playmaking and defense
    assists: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Assists"
    )

    steals: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Steals"
    )

    blocks: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Blocks"
    )

    turnovers: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Turnovers"
    )

    personal_fouls: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Personal fouls"
    )

    # Updated timestamp
    stats_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date these statistics are current as of"
    )

    # Relationships
    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="player_statistics",
        lazy="selectin"
    )

    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
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

    game: Mapped[Optional["CollegeGame"]] = relationship(
        "CollegeGame",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_player_statistics_player_id", "player_id"),
        Index("idx_player_statistics_team_id", "team_id"),
        Index("idx_player_statistics_academic_year_id", "academic_year_id"),
        Index("idx_player_statistics_season_id", "season_id"),
        Index("idx_player_statistics_game_id", "game_id"),
        Index("idx_player_statistics_type", "statistic_type"),
        Index("idx_player_statistics_stats_date", "stats_date"),
        Index("idx_player_statistics_player_year", "player_id", "academic_year_id"),
        UniqueConstraint("player_id", "game_id", "statistic_type", name="uq_player_statistics_player_game_type"),
        UniqueConstraint("player_id", "season_id", "statistic_type", name="uq_player_statistics_player_season_type"),
    )

    def __repr__(self) -> str:
        context = "Season" if self.season_id else ("Game" if self.game_id else "Total")
        return f"<PlayerStatistics(player='{self.player.full_name if self.player else None}', type='{self.statistic_type}', context='{context}')>"


# =============================================================================
# Phase 4: Rankings and Advanced Metrics Models
# =============================================================================

class Rankings(Base, UUIDMixin, TimestampMixin):
    """
    Team rankings from various ranking systems
    """
    __tablename__ = "rankings"

    # References
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Ranking system
    ranking_system: Mapped[RankingSystem] = mapped_column(
        nullable=False,
        doc="Ranking system (AP, Coaches, NET, KenPom, etc.)"
    )

    # Ranking data
    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Numerical ranking (1 = best)"
    )

    rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4),
        doc="Rating/score from the ranking system"
    )

    # Ranking week/date
    ranking_week: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Week of the season (for weekly polls)"
    )

    ranking_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of this ranking"
    )

    # Previous ranking for trend analysis
    previous_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Previous ranking for comparison"
    )

    rank_change: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Change from previous ranking (+/- positions)"
    )

    # Poll-specific data
    first_place_votes: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of first place votes (for polls)"
    )

    total_points: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total poll points received"
    )

    # Status flags
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is the current ranking"
    )

    is_ranked: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether team is ranked (vs receiving votes)"
    )

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes about the ranking"
    )

    # Relationships
    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_rankings_team_id", "team_id"),
        Index("idx_rankings_academic_year_id", "academic_year_id"),
        Index("idx_rankings_system", "ranking_system"),
        Index("idx_rankings_rank", "rank"),
        Index("idx_rankings_date", "ranking_date"),
        Index("idx_rankings_current", "is_current"),
        Index("idx_rankings_ranked", "is_ranked"),
        Index("idx_rankings_team_system", "team_id", "ranking_system"),
        Index("idx_rankings_system_date", "ranking_system", "ranking_date"),
        UniqueConstraint("team_id", "ranking_system", "ranking_date", name="uq_rankings_team_system_date"),
    )

    def __repr__(self) -> str:
        return f"<Rankings(team='{self.team.name if self.team else None}', system='{self.ranking_system}', rank={self.rank}, date={self.ranking_date})>"

    @property
    def rank_display(self) -> str:
        """Display ranking with appropriate formatting"""
        if self.is_ranked:
            return f"#{self.rank}"
        else:
            return "RV"  # Receiving Votes

    @property
    def trend_display(self) -> str:
        """Display ranking trend"""
        if self.rank_change is None:
            return "—"
        elif self.rank_change > 0:
            return f"↑{self.rank_change}"
        elif self.rank_change < 0:
            return f"↓{abs(self.rank_change)}"
        else:
            return "—"


class AdvancedMetrics(Base, UUIDMixin, TimestampMixin):
    """
    Advanced analytics and efficiency metrics for teams
    """
    __tablename__ = "advanced_metrics"

    # References
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Calculation date
    calculation_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date these metrics were calculated"
    )

    # Efficiency metrics
    offensive_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Points per 100 possessions (offense)"
    )

    defensive_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Points allowed per 100 possessions (defense)"
    )

    net_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Net efficiency (offensive - defensive)"
    )

    # Tempo and pace
    tempo: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Possessions per 40 minutes"
    )

    pace: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Possessions per game"
    )

    # Advanced shooting metrics
    effective_field_goal_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Effective field goal percentage"
    )

    true_shooting_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="True shooting percentage"
    )

    # Four Factors (Dean Smith)
    # Offense
    offensive_four_factor_efg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Offensive effective field goal percentage"
    )

    offensive_four_factor_tov: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Offensive turnover rate"
    )

    offensive_four_factor_orb: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Offensive rebounding percentage"
    )

    offensive_four_factor_ft: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Free throw rate (FTA/FGA)"
    )

    # Defense
    defensive_four_factor_efg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Defensive effective field goal percentage allowed"
    )

    defensive_four_factor_tov: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Defensive turnover rate forced"
    )

    defensive_four_factor_drb: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Defensive rebounding percentage"
    )

    defensive_four_factor_ft: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Opponent free throw rate allowed"
    )

    # Strength of schedule
    strength_of_schedule: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Strength of schedule rating"
    )

    strength_of_record: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Strength of record rating"
    )

    # Win probability metrics
    pythagorean_wins: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        doc="Expected wins based on Pythagorean theorem"
    )

    luck_factor: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Difference between actual and expected wins"
    )

    # Game control metrics
    average_lead: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        doc="Average lead during games"
    )

    lead_changes_per_game: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        doc="Average lead changes per game"
    )

    # Clutch performance
    close_game_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Record in close games (within 5 points)"
    )

    comeback_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of comeback wins (trailed by 10+)"
    )

    # Consistency metrics
    performance_variance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Variance in game performance"
    )

    # Updated status
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether these are the current metrics"
    )

    # Relationships
    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_advanced_metrics_team_id", "team_id"),
        Index("idx_advanced_metrics_academic_year_id", "academic_year_id"),
        Index("idx_advanced_metrics_calculation_date", "calculation_date"),
        Index("idx_advanced_metrics_current", "is_current"),
        Index("idx_advanced_metrics_offensive_efficiency", "offensive_efficiency"),
        Index("idx_advanced_metrics_defensive_efficiency", "defensive_efficiency"),
        Index("idx_advanced_metrics_net_efficiency", "net_efficiency"),
        Index("idx_advanced_metrics_team_year", "team_id", "academic_year_id"),
        UniqueConstraint("team_id", "academic_year_id", "calculation_date", name="uq_advanced_metrics_team_year_date"),
    )

    def __repr__(self) -> str:
        return f"<AdvancedMetrics(team='{self.team.name if self.team else None}', date={self.calculation_date}, net_eff={self.net_efficiency})>"


class SeasonRecords(Base, UUIDMixin, TimestampMixin):
    """
    Detailed win-loss records with various breakdowns
    """
    __tablename__ = "season_records"

    # References
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Record type
    record_type: Mapped[RecordType] = mapped_column(
        nullable=False,
        doc="Type of record (overall, conference, home, away, etc.)"
    )

    # Basic record
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

    # Streak tracking
    current_streak: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Current streak (e.g., 'W5', 'L2')"
    )

    longest_win_streak: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Longest winning streak this season"
    )

    longest_loss_streak: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Longest losing streak this season"
    )

    # Additional context for specific record types
    opponent_rank_range: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Opponent ranking range (e.g., 'Top 25', 'RPI 1-50')"
    )

    # Quality metrics (for specific record types)
    quad_1_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Quadrant 1 wins (for NET-based records)"
    )

    quad_1_losses: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Quadrant 1 losses"
    )

    quad_2_wins: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Quadrant 2 wins"
    )

    quad_2_losses: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Quadrant 2 losses"
    )

    # Updated timestamp
    record_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date this record is current as of"
    )

    # Status
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is the current record"
    )

    # Relationships
    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_season_records_team_id", "team_id"),
        Index("idx_season_records_academic_year_id", "academic_year_id"),
        Index("idx_season_records_type", "record_type"),
        Index("idx_season_records_date", "record_date"),
        Index("idx_season_records_current", "is_current"),
        Index("idx_season_records_wins", "wins"),
        Index("idx_season_records_losses", "losses"),
        Index("idx_season_records_team_type", "team_id", "record_type"),
        UniqueConstraint("team_id", "academic_year_id", "record_type", "record_date", name="uq_season_records_team_type_date"),
    )

    def __repr__(self) -> str:
        return f"<SeasonRecords(team='{self.team.name if self.team else None}', type='{self.record_type}', record='{self.wins}-{self.losses}')>"

    @property
    def record_display(self) -> str:
        """Display the record in standard format"""
        return f"{self.wins}-{self.losses}"

    @property
    def win_percentage(self) -> Optional[Decimal]:
        """Calculate winning percentage"""
        total_games = self.wins + self.losses
        if total_games > 0:
            return Decimal(self.wins) / Decimal(total_games)
        return None

    @property
    def games_played(self) -> int:
        """Total games played"""
        return self.wins + self.losses

    @property
    def above_500(self) -> bool:
        """Whether the team is above .500"""
        return self.wins > self.losses