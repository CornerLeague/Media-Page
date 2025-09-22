"""
College Football Phase 2: Play-by-Play and Advanced Statistics
Extends Phase 1 with comprehensive play tracking, drive analytics, and advanced metrics
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, DateTime, Numeric, Float, Time
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    # Existing football enums
    FootballPosition, FootballPositionGroup, FootballPlayType, FootballFormation,
    GameStatus, StatisticType,

    # New Phase 2 enums
    PlayResult, DriveResult, FieldPosition, DownType, PlayDirection,
    PassLength, RushType, DefensivePlayType, PenaltyType, StatisticCategory,
    AdvancedMetricType, GameSituation
)


# =============================================================================
# Play-by-Play Models
# =============================================================================

class PlayByPlay(Base, UUIDMixin, TimestampMixin):
    """
    Individual play tracking with comprehensive situational context
    Foundation for all advanced football analytics
    """
    __tablename__ = "football_play_by_play"

    # Game context
    game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football game"
    )

    drive_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_drive_data.id", ondelete="CASCADE"),
        doc="Reference to the drive this play belongs to"
    )

    # Play identification
    play_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Sequential play number within the game"
    )

    drive_play_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Play number within the current drive"
    )

    # Team context
    offense_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Team with possession of the ball"
    )

    defense_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Defending team"
    )

    # Game timing
    quarter: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Quarter (1-4, 5+ for overtime)"
    )

    time_remaining: Mapped[Optional[time]] = mapped_column(
        Time,
        doc="Time remaining in quarter (MM:SS)"
    )

    game_clock_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total seconds remaining in game"
    )

    # Down and distance
    down: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Down number (1-4)"
    )

    distance: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Yards to go for first down"
    )

    down_type: Mapped[DownType] = mapped_column(
        nullable=False,
        doc="Categorized down and distance context"
    )

    # Field position
    yard_line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Yard line where play starts (0-100, relative to offense)"
    )

    yard_line_side: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="Side of field (offense/defense)"
    )

    field_position: Mapped[FieldPosition] = mapped_column(
        nullable=False,
        doc="Categorized field position zone"
    )

    # Play details
    play_type: Mapped[FootballPlayType] = mapped_column(
        nullable=False,
        doc="Primary type of play"
    )

    play_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Full text description of the play"
    )

    play_result: Mapped[PlayResult] = mapped_column(
        nullable=False,
        doc="Outcome of the play"
    )

    # Yardage and movement
    yards_gained: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards gained on the play (can be negative)"
    )

    yards_to_endzone_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Yards to endzone at start of play"
    )

    yards_to_endzone_end: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Yards to endzone at end of play"
    )

    # Play direction and location
    play_direction: Mapped[Optional[PlayDirection]] = mapped_column(
        doc="Direction of the play"
    )

    gap_location: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Specific gap or area where play was run"
    )

    # Passing play details
    is_pass: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was a passing play"
    )

    pass_length: Mapped[Optional[PassLength]] = mapped_column(
        doc="Length category for pass plays"
    )

    air_yards: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Yards in the air for pass plays"
    )

    yards_after_catch: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Yards gained after the catch"
    )

    is_completion: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        doc="Whether pass was completed"
    )

    # Rushing play details
    is_rush: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was a rushing play"
    )

    rush_type: Mapped[Optional[RushType]] = mapped_column(
        doc="Type of rushing play"
    )

    # Special teams details
    is_special_teams: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was a special teams play"
    )

    # Player involvement
    primary_player_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="SET NULL"),
        doc="Primary player (usually ball carrier/passer)"
    )

    secondary_player_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="SET NULL"),
        doc="Secondary player (usually receiver/tackler)"
    )

    # Scoring
    is_touchdown: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play resulted in touchdown"
    )

    points_scored: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Points scored on this play"
    )

    # Turnover information
    is_turnover: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play resulted in turnover"
    )

    turnover_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Type of turnover (fumble, interception, etc.)"
    )

    # Penalty information
    is_penalty: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether penalty occurred on play"
    )

    penalty_type: Mapped[Optional[PenaltyType]] = mapped_column(
        doc="Type of penalty"
    )

    penalty_yards: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Yards assessed for penalty"
    )

    penalty_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Team that committed the penalty"
    )

    # Formation and strategy
    offensive_formation: Mapped[Optional[FootballFormation]] = mapped_column(
        doc="Offensive formation used"
    )

    defensive_formation: Mapped[Optional[FootballFormation]] = mapped_column(
        doc="Defensive formation/alignment"
    )

    defensive_play_type: Mapped[Optional[DefensivePlayType]] = mapped_column(
        doc="Type of defensive play called"
    )

    # Game situation context
    game_situation: Mapped[Optional[GameSituation]] = mapped_column(
        doc="Overall game situation context"
    )

    score_differential: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Score differential for offense team at start of play"
    )

    # Advanced context
    is_red_zone: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play occurred in red zone"
    )

    is_goal_line: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play occurred on goal line"
    )

    is_two_minute_warning: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play occurred during two-minute warning"
    )

    # Expected points and win probability
    expected_points_before: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Expected points before the play"
    )

    expected_points_after: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Expected points after the play"
    )

    expected_points_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Expected Points Added (EPA) for this play"
    )

    win_probability_before: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Win probability before the play (0-1)"
    )

    win_probability_after: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Win probability after the play (0-1)"
    )

    win_probability_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        doc="Win Probability Added (WPA) for this play"
    )

    # Success metrics
    is_successful_play: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        doc="Whether play was successful (context-dependent)"
    )

    is_explosive_play: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play was explosive (20+ yard pass, 10+ yard rush)"
    )

    is_stuff: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play was stuffed (negative yards)"
    )

    # External references
    external_play_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this play"
    )

    pbp_data_raw: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Raw play-by-play data from external source"
    )

    # Relationships
    game: Mapped["FootballGame"] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    drive: Mapped[Optional["DriveData"]] = relationship(
        "DriveData",
        back_populates="plays",
        lazy="selectin"
    )

    offense_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[offense_team_id],
        lazy="selectin"
    )

    defense_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[defense_team_id],
        lazy="selectin"
    )

    primary_player: Mapped[Optional["FootballPlayer"]] = relationship(
        "FootballPlayer",
        foreign_keys=[primary_player_id],
        lazy="selectin"
    )

    secondary_player: Mapped[Optional["FootballPlayer"]] = relationship(
        "FootballPlayer",
        foreign_keys=[secondary_player_id],
        lazy="selectin"
    )

    penalty_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[penalty_team_id],
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_pbp_game_id", "game_id"),
        Index("idx_football_pbp_drive_id", "drive_id"),
        Index("idx_football_pbp_offense_team_id", "offense_team_id"),
        Index("idx_football_pbp_defense_team_id", "defense_team_id"),
        Index("idx_football_pbp_play_number", "play_number"),
        Index("idx_football_pbp_quarter", "quarter"),
        Index("idx_football_pbp_down", "down"),
        Index("idx_football_pbp_down_type", "down_type"),
        Index("idx_football_pbp_field_position", "field_position"),
        Index("idx_football_pbp_play_type", "play_type"),
        Index("idx_football_pbp_play_result", "play_result"),
        Index("idx_football_pbp_is_pass", "is_pass"),
        Index("idx_football_pbp_is_rush", "is_rush"),
        Index("idx_football_pbp_is_special_teams", "is_special_teams"),
        Index("idx_football_pbp_is_touchdown", "is_touchdown"),
        Index("idx_football_pbp_is_turnover", "is_turnover"),
        Index("idx_football_pbp_is_penalty", "is_penalty"),
        Index("idx_football_pbp_primary_player_id", "primary_player_id"),
        Index("idx_football_pbp_game_play", "game_id", "play_number"),
        Index("idx_football_pbp_game_quarter", "game_id", "quarter"),
        Index("idx_football_pbp_external_id", "external_play_id"),
        Index("idx_football_pbp_situational", "down", "distance", "field_position"),
        Index("idx_football_pbp_analytics", "is_successful_play", "is_explosive_play", "is_stuff"),
        UniqueConstraint("game_id", "play_number", name="uq_football_pbp_game_play_number"),
    )

    def __repr__(self) -> str:
        return f"<PlayByPlay(game={self.game_id}, play={self.play_number}, {self.down}&{self.distance}, {self.play_type})>"

    @property
    def down_and_distance(self) -> str:
        """Formatted down and distance"""
        if self.distance >= 10:
            return f"{self.down} & {self.distance}"
        else:
            return f"{self.down} & {self.distance}"

    @property
    def field_position_display(self) -> str:
        """Human-readable field position"""
        if self.yard_line_side == "offense":
            return f"Own {self.yard_line}"
        else:
            return f"Opp {self.yard_line}"

    @property
    def is_first_down_conversion(self) -> bool:
        """Whether play resulted in first down"""
        return self.yards_gained >= self.distance or self.is_touchdown

    @property
    def leverage_index(self) -> Optional[float]:
        """Calculate leverage index based on game situation"""
        if self.win_probability_before is None:
            return None

        # Higher leverage when win probability is close to 50%
        wp = float(self.win_probability_before)
        return 1.0 - abs(wp - 0.5) * 2


# =============================================================================
# Drive Analytics Models
# =============================================================================

class DriveData(Base, UUIDMixin, TimestampMixin):
    """
    Drive-level analytics and statistics
    Aggregates play-by-play data into drive summaries for strategic analysis
    """
    __tablename__ = "football_drive_data"

    # Game context
    game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football game"
    )

    # Drive identification
    drive_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Drive number within the game for the team"
    )

    offense_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Team with possession during the drive"
    )

    defense_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Defending team during the drive"
    )

    # Drive timing
    start_quarter: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Quarter when drive started"
    )

    end_quarter: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Quarter when drive ended"
    )

    start_time: Mapped[Optional[time]] = mapped_column(
        Time,
        doc="Game time when drive started"
    )

    end_time: Mapped[Optional[time]] = mapped_column(
        Time,
        doc="Game time when drive ended"
    )

    drive_duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Real time duration of drive in seconds"
    )

    # Field position
    start_yard_line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Yard line where drive started"
    )

    end_yard_line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Yard line where drive ended"
    )

    start_field_position: Mapped[FieldPosition] = mapped_column(
        nullable=False,
        doc="Categorized starting field position"
    )

    # Drive statistics
    total_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total number of plays in the drive"
    )

    total_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total yards gained during the drive"
    )

    passing_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of passing plays"
    )

    rushing_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of rushing plays"
    )

    passing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards gained passing"
    )

    rushing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards gained rushing"
    )

    penalty_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Net penalty yards during drive"
    )

    # Drive outcome
    drive_result: Mapped[DriveResult] = mapped_column(
        nullable=False,
        doc="How the drive ended"
    )

    points_scored: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Points scored on this drive"
    )

    # Down and distance tracking
    first_downs_gained: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of first downs gained"
    )

    third_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of third down attempts"
    )

    third_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of third down conversions"
    )

    fourth_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of fourth down attempts"
    )

    fourth_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of fourth down conversions"
    )

    # Situational context
    is_red_zone_drive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether drive entered the red zone"
    )

    is_goal_line_drive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether drive reached the goal line"
    )

    is_short_field: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether drive started in opponent territory"
    )

    is_two_minute_drive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether drive occurred during two-minute situation"
    )

    # Game situation
    score_differential_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Score differential when drive started"
    )

    score_differential_end: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Score differential when drive ended"
    )

    game_situation_start: Mapped[Optional[GameSituation]] = mapped_column(
        doc="Game situation when drive started"
    )

    # Advanced metrics
    expected_points_start: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Expected points at start of drive"
    )

    expected_points_end: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Expected points at end of drive"
    )

    expected_points_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Expected Points Added for the entire drive"
    )

    win_probability_start: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Win probability at start of drive"
    )

    win_probability_end: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Win probability at end of drive"
    )

    win_probability_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        doc="Win Probability Added for the entire drive"
    )

    # Efficiency metrics
    yards_per_play: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        doc="Average yards per play on the drive"
    )

    success_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 3),
        doc="Percentage of successful plays on the drive"
    )

    explosive_play_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of explosive plays (20+ pass, 10+ rush)"
    )

    stuff_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of stuffed plays (negative yards)"
    )

    # Turnover and penalty tracking
    turnovers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of turnovers during drive"
    )

    penalties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of penalties during drive"
    )

    # External references
    external_drive_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this drive"
    )

    # Relationships
    game: Mapped["FootballGame"] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    offense_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[offense_team_id],
        lazy="selectin"
    )

    defense_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[defense_team_id],
        lazy="selectin"
    )

    plays: Mapped[List["PlayByPlay"]] = relationship(
        "PlayByPlay",
        back_populates="drive",
        cascade="all, delete-orphan",
        order_by="PlayByPlay.play_number",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_drives_game_id", "game_id"),
        Index("idx_football_drives_offense_team_id", "offense_team_id"),
        Index("idx_football_drives_defense_team_id", "defense_team_id"),
        Index("idx_football_drives_drive_number", "drive_number"),
        Index("idx_football_drives_result", "drive_result"),
        Index("idx_football_drives_quarter", "start_quarter", "end_quarter"),
        Index("idx_football_drives_field_position", "start_field_position"),
        Index("idx_football_drives_points", "points_scored"),
        Index("idx_football_drives_situational", "is_red_zone_drive", "is_two_minute_drive"),
        Index("idx_football_drives_game_team_drive", "game_id", "offense_team_id", "drive_number"),
        Index("idx_football_drives_external_id", "external_drive_id"),
        UniqueConstraint("game_id", "offense_team_id", "drive_number", name="uq_football_drives_game_team_number"),
    )

    def __repr__(self) -> str:
        return f"<DriveData(game={self.game_id}, drive={self.drive_number}, {self.total_plays} plays, {self.total_yards} yards, {self.drive_result})>"

    @property
    def third_down_percentage(self) -> Optional[Decimal]:
        """Third down conversion percentage"""
        if self.third_down_attempts > 0:
            return Decimal(self.third_down_conversions) / Decimal(self.third_down_attempts)
        return None

    @property
    def fourth_down_percentage(self) -> Optional[Decimal]:
        """Fourth down conversion percentage"""
        if self.fourth_down_attempts > 0:
            return Decimal(self.fourth_down_conversions) / Decimal(self.fourth_down_attempts)
        return None

    @property
    def is_scoring_drive(self) -> bool:
        """Whether drive resulted in points"""
        return self.points_scored > 0

    @property
    def drive_efficiency(self) -> Optional[Decimal]:
        """Overall drive efficiency score (0-1)"""
        if self.total_plays == 0:
            return None

        # Combine multiple efficiency factors
        base_efficiency = min(1.0, self.total_yards / 75.0)  # 75 yards = efficient drive

        # Bonus for scoring
        scoring_bonus = 0.2 if self.is_scoring_drive else 0

        # Penalty for turnovers
        turnover_penalty = -0.3 * self.turnovers

        return Decimal(max(0, min(1.0, base_efficiency + scoring_bonus + turnover_penalty)))

    @property
    def time_of_possession_minutes(self) -> Optional[Decimal]:
        """Time of possession in minutes"""
        if self.drive_duration_seconds:
            return Decimal(self.drive_duration_seconds) / Decimal(60)
        return None


# =============================================================================
# Player Statistics Models
# =============================================================================

class FootballPlayerStatistics(Base, UUIDMixin, TimestampMixin):
    """
    Comprehensive football player statistics with position-specific metrics
    Handles the complexity of 22 different position types
    """
    __tablename__ = "football_player_statistics"

    # Player and context
    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football player"
    )

    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        doc="Reference to specific game (NULL for season stats)"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    season_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the season"
    )

    # Statistical context
    statistic_type: Mapped[StatisticType] = mapped_column(
        nullable=False,
        doc="Type of statistics (game, season, career, etc.)"
    )

    position_group: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Position group for relevant statistics"
    )

    games_played: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of games played"
    )

    games_started: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of games started"
    )

    # Passing statistics (QB)
    passing_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Pass attempts"
    )

    passing_completions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Pass completions"
    )

    passing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Passing yards"
    )

    passing_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Passing touchdowns"
    )

    passing_interceptions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Interceptions thrown"
    )

    passing_sacks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Times sacked"
    )

    passing_sack_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards lost to sacks"
    )

    passing_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest pass completion"
    )

    qbr: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Quarterback rating"
    )

    # Rushing statistics (RB, QB)
    rushing_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Rushing attempts"
    )

    rushing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Rushing yards"
    )

    rushing_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Rushing touchdowns"
    )

    rushing_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest rushing attempt"
    )

    rushing_fumbles: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumbles while rushing"
    )

    # Receiving statistics (WR, TE, RB)
    receiving_targets: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Times targeted"
    )

    receiving_receptions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Receptions"
    )

    receiving_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Receiving yards"
    )

    receiving_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Receiving touchdowns"
    )

    receiving_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest reception"
    )

    receiving_fumbles: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumbles after reception"
    )

    yards_after_catch: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total yards after catch"
    )

    drops: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Dropped passes"
    )

    # Defensive statistics (all defensive positions)
    tackles_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total tackles"
    )

    tackles_solo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Solo tackles"
    )

    tackles_assisted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Assisted tackles"
    )

    tackles_for_loss: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Tackles for loss"
    )

    tackles_for_loss_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards lost on tackles for loss"
    )

    sacks: Mapped[Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        default=0,
        doc="Sacks (can be fractional)"
    )

    sack_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards lost on sacks"
    )

    quarterback_hits: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Quarterback hits"
    )

    quarterback_hurries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Quarterback hurries"
    )

    # Pass defense (CB, S, LB)
    passes_defended: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Passes broken up"
    )

    interceptions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Interceptions"
    )

    interception_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Interception return yards"
    )

    interception_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Interception return touchdowns"
    )

    # Fumble recovery
    fumbles_recovered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumbles recovered"
    )

    fumble_return_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumble return yards"
    )

    fumble_return_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumble return touchdowns"
    )

    fumbles_forced: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumbles forced"
    )

    # Special teams statistics
    field_goal_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Field goal attempts"
    )

    field_goals_made: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Field goals made"
    )

    field_goal_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest field goal"
    )

    extra_point_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Extra point attempts"
    )

    extra_points_made: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Extra points made"
    )

    # Punting statistics
    punts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of punts"
    )

    punt_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total punt yards"
    )

    punt_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest punt"
    )

    punts_inside_20: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punts inside 20-yard line"
    )

    punt_touchbacks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punt touchbacks"
    )

    punt_fair_catches: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punts resulting in fair catch"
    )

    # Return statistics
    punt_returns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punt returns"
    )

    punt_return_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punt return yards"
    )

    punt_return_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punt return touchdowns"
    )

    punt_return_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest punt return"
    )

    kickoff_returns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Kickoff returns"
    )

    kickoff_return_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Kickoff return yards"
    )

    kickoff_return_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Kickoff return touchdowns"
    )

    kickoff_return_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest kickoff return"
    )

    # Offensive line statistics (when available)
    pass_blocking_snaps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Pass blocking snaps"
    )

    sacks_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Sacks allowed"
    )

    quarterback_hits_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="QB hits allowed"
    )

    hurries_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="QB hurries allowed"
    )

    # Penalty statistics
    penalties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Penalties committed"
    )

    penalty_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Penalty yards"
    )

    # Snap counts and usage
    offensive_snaps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Offensive snaps played"
    )

    defensive_snaps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Defensive snaps played"
    )

    special_teams_snaps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Special teams snaps played"
    )

    # Advanced metrics
    player_efficiency_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Position-specific efficiency rating"
    )

    pro_football_focus_grade: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="PFF overall grade"
    )

    # Relationships
    player: Mapped["FootballPlayer"] = relationship(
        "FootballPlayer",
        lazy="selectin"
    )

    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    game: Mapped[Optional["FootballGame"]] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    season: Mapped["Season"] = relationship(
        "Season",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_player_stats_player_id", "player_id"),
        Index("idx_football_player_stats_game_id", "game_id"),
        Index("idx_football_player_stats_team_id", "team_id"),
        Index("idx_football_player_stats_season_id", "season_id"),
        Index("idx_football_player_stats_type", "statistic_type"),
        Index("idx_football_player_stats_position", "position_group"),
        Index("idx_football_player_stats_player_season", "player_id", "season_id"),
        Index("idx_football_player_stats_player_game", "player_id", "game_id"),
        Index("idx_football_player_stats_team_season", "team_id", "season_id"),
        Index("idx_football_player_stats_passing", "passing_yards", "passing_touchdowns"),
        Index("idx_football_player_stats_rushing", "rushing_yards", "rushing_touchdowns"),
        Index("idx_football_player_stats_receiving", "receiving_yards", "receiving_touchdowns"),
        Index("idx_football_player_stats_defense", "tackles_total", "sacks", "interceptions"),
        UniqueConstraint("player_id", "game_id", "statistic_type", name="uq_football_player_stats_player_game_type"),
        UniqueConstraint("player_id", "season_id", "statistic_type", name="uq_football_player_stats_player_season_type"),
    )

    def __repr__(self) -> str:
        return f"<FootballPlayerStatistics(player={self.player_id}, season={self.season_id}, type={self.statistic_type})>"

    @property
    def passing_completion_percentage(self) -> Optional[Decimal]:
        """Passing completion percentage"""
        if self.passing_attempts > 0:
            return Decimal(self.passing_completions) / Decimal(self.passing_attempts) * 100
        return None

    @property
    def passing_yards_per_attempt(self) -> Optional[Decimal]:
        """Yards per passing attempt"""
        if self.passing_attempts > 0:
            return Decimal(self.passing_yards) / Decimal(self.passing_attempts)
        return None

    @property
    def rushing_yards_per_attempt(self) -> Optional[Decimal]:
        """Yards per rushing attempt"""
        if self.rushing_attempts > 0:
            return Decimal(self.rushing_yards) / Decimal(self.rushing_attempts)
        return None

    @property
    def receiving_yards_per_reception(self) -> Optional[Decimal]:
        """Yards per reception"""
        if self.receiving_receptions > 0:
            return Decimal(self.receiving_yards) / Decimal(self.receiving_receptions)
        return None

    @property
    def receiving_catch_percentage(self) -> Optional[Decimal]:
        """Reception percentage"""
        if self.receiving_targets > 0:
            return Decimal(self.receiving_receptions) / Decimal(self.receiving_targets) * 100
        return None

    @property
    def field_goal_percentage(self) -> Optional[Decimal]:
        """Field goal percentage"""
        if self.field_goal_attempts > 0:
            return Decimal(self.field_goals_made) / Decimal(self.field_goal_attempts) * 100
        return None

    @property
    def punt_average(self) -> Optional[Decimal]:
        """Punting average"""
        if self.punts > 0:
            return Decimal(self.punt_yards) / Decimal(self.punts)
        return None

    @property
    def total_touchdowns(self) -> int:
        """Total touchdowns scored"""
        return (self.passing_touchdowns + self.rushing_touchdowns +
                self.receiving_touchdowns + self.interception_touchdowns +
                self.fumble_return_touchdowns + self.punt_return_touchdowns +
                self.kickoff_return_touchdowns)

    @property
    def total_yards_from_scrimmage(self) -> int:
        """Total yards from scrimmage (rushing + receiving)"""
        return self.rushing_yards + self.receiving_yards

    @property
    def all_purpose_yards(self) -> int:
        """All-purpose yards (rushing + receiving + returns)"""
        return (self.rushing_yards + self.receiving_yards +
                self.punt_return_yards + self.kickoff_return_yards)


# =============================================================================
# Team Statistics Models
# =============================================================================

class FootballTeamStatistics(Base, UUIDMixin, TimestampMixin):
    """
    Team-level football statistics and performance metrics
    Aggregates individual and play-by-play data for team analysis
    """
    __tablename__ = "football_team_statistics"

    # Team and context
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football team"
    )

    opponent_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Reference to opponent (NULL for season stats)"
    )

    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        doc="Reference to specific game (NULL for season stats)"
    )

    season_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the season"
    )

    # Statistical context
    statistic_type: Mapped[StatisticType] = mapped_column(
        nullable=False,
        doc="Type of statistics (game, season, etc.)"
    )

    is_home_team: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        doc="Whether team was home team (NULL for season stats)"
    )

    # Basic game information
    games_played: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of games included in these statistics"
    )

    # Scoring
    points_for: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Points scored"
    )

    points_against: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Points allowed"
    )

    touchdowns_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total touchdowns scored"
    )

    field_goals_made: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Field goals made"
    )

    field_goals_attempted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Field goals attempted"
    )

    extra_points_made: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Extra points made"
    )

    extra_points_attempted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Extra points attempted"
    )

    safeties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Safeties scored"
    )

    # Offensive statistics
    total_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total offensive plays"
    )

    total_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total offensive yards"
    )

    first_downs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="First downs gained"
    )

    first_downs_passing: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="First downs by passing"
    )

    first_downs_rushing: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="First downs by rushing"
    )

    first_downs_penalty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="First downs by penalty"
    )

    # Passing offense
    passing_completions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Pass completions"
    )

    passing_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Pass attempts"
    )

    passing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Passing yards"
    )

    passing_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Passing touchdowns"
    )

    passing_interceptions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Interceptions thrown"
    )

    passing_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest pass completion"
    )

    sacks_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Sacks allowed"
    )

    sack_yards_lost: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards lost to sacks"
    )

    # Rushing offense
    rushing_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Rushing attempts"
    )

    rushing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Rushing yards"
    )

    rushing_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Rushing touchdowns"
    )

    rushing_longest: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Longest rush"
    )

    # Defensive statistics
    defensive_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total defensive plays faced"
    )

    defensive_yards_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total yards allowed"
    )

    passing_yards_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Passing yards allowed"
    )

    rushing_yards_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Rushing yards allowed"
    )

    sacks_recorded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Sacks recorded"
    )

    sack_yards_gained: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards gained from sacks"
    )

    tackles_for_loss: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Tackles for loss"
    )

    tackles_for_loss_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Yards lost on tackles for loss"
    )

    interceptions_made: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Interceptions made"
    )

    interception_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Interception return yards"
    )

    fumbles_recovered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumbles recovered"
    )

    fumble_return_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumble return yards"
    )

    fumbles_forced: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumbles forced"
    )

    passes_defended: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Passes broken up"
    )

    # Turnover statistics
    turnovers_gained: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Turnovers gained (INT + fumble recoveries)"
    )

    turnovers_lost: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Turnovers lost (INT + fumbles lost)"
    )

    fumbles_lost: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fumbles lost"
    )

    # Special teams
    punt_return_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punt return yards"
    )

    punt_return_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Punt return touchdowns"
    )

    kickoff_return_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Kickoff return yards"
    )

    kickoff_return_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Kickoff return touchdowns"
    )

    # Down and distance
    third_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Third down attempts"
    )

    third_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Third down conversions"
    )

    fourth_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fourth down attempts"
    )

    fourth_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Fourth down conversions"
    )

    # Red zone efficiency
    red_zone_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Red zone attempts"
    )

    red_zone_scores: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Red zone scores"
    )

    red_zone_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Red zone touchdowns"
    )

    # Penalties
    penalties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Penalties committed"
    )

    penalty_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Penalty yards"
    )

    # Time of possession
    time_of_possession_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Time of possession in seconds"
    )

    # Drives
    total_drives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total drives"
    )

    scoring_drives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Drives resulting in points"
    )

    touchdown_drives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Drives resulting in touchdowns"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[team_id],
        lazy="selectin"
    )

    opponent: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[opponent_id],
        lazy="selectin"
    )

    game: Mapped[Optional["FootballGame"]] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    season: Mapped["Season"] = relationship(
        "Season",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_team_stats_team_id", "team_id"),
        Index("idx_football_team_stats_opponent_id", "opponent_id"),
        Index("idx_football_team_stats_game_id", "game_id"),
        Index("idx_football_team_stats_season_id", "season_id"),
        Index("idx_football_team_stats_type", "statistic_type"),
        Index("idx_football_team_stats_team_season", "team_id", "season_id"),
        Index("idx_football_team_stats_team_game", "team_id", "game_id"),
        Index("idx_football_team_stats_offensive", "total_yards", "points_for"),
        Index("idx_football_team_stats_defensive", "defensive_yards_allowed", "points_against"),
        UniqueConstraint("team_id", "game_id", "statistic_type", name="uq_football_team_stats_team_game_type"),
        UniqueConstraint("team_id", "season_id", "statistic_type", name="uq_football_team_stats_team_season_type"),
    )

    def __repr__(self) -> str:
        return f"<FootballTeamStatistics(team={self.team_id}, season={self.season_id}, type={self.statistic_type})>"

    @property
    def yards_per_play(self) -> Optional[Decimal]:
        """Average yards per play"""
        if self.total_plays > 0:
            return Decimal(self.total_yards) / Decimal(self.total_plays)
        return None

    @property
    def passing_completion_percentage(self) -> Optional[Decimal]:
        """Passing completion percentage"""
        if self.passing_attempts > 0:
            return Decimal(self.passing_completions) / Decimal(self.passing_attempts) * 100
        return None

    @property
    def rushing_yards_per_attempt(self) -> Optional[Decimal]:
        """Rushing yards per attempt"""
        if self.rushing_attempts > 0:
            return Decimal(self.rushing_yards) / Decimal(self.rushing_attempts)
        return None

    @property
    def third_down_percentage(self) -> Optional[Decimal]:
        """Third down conversion percentage"""
        if self.third_down_attempts > 0:
            return Decimal(self.third_down_conversions) / Decimal(self.third_down_attempts) * 100
        return None

    @property
    def red_zone_percentage(self) -> Optional[Decimal]:
        """Red zone scoring percentage"""
        if self.red_zone_attempts > 0:
            return Decimal(self.red_zone_scores) / Decimal(self.red_zone_attempts) * 100
        return None

    @property
    def red_zone_touchdown_percentage(self) -> Optional[Decimal]:
        """Red zone touchdown percentage"""
        if self.red_zone_attempts > 0:
            return Decimal(self.red_zone_touchdowns) / Decimal(self.red_zone_attempts) * 100
        return None

    @property
    def turnover_margin(self) -> int:
        """Turnover margin (gained - lost)"""
        return self.turnovers_gained - self.turnovers_lost

    @property
    def points_per_game(self) -> Optional[Decimal]:
        """Points per game"""
        if self.games_played > 0:
            return Decimal(self.points_for) / Decimal(self.games_played)
        return None

    @property
    def points_allowed_per_game(self) -> Optional[Decimal]:
        """Points allowed per game"""
        if self.games_played > 0:
            return Decimal(self.points_against) / Decimal(self.games_played)
        return None

    @property
    def total_offense_per_game(self) -> Optional[Decimal]:
        """Total offense yards per game"""
        if self.games_played > 0:
            return Decimal(self.total_yards) / Decimal(self.games_played)
        return None

    @property
    def total_defense_per_game(self) -> Optional[Decimal]:
        """Total defense yards allowed per game"""
        if self.games_played > 0:
            return Decimal(self.defensive_yards_allowed) / Decimal(self.games_played)
        return None

    @property
    def time_of_possession_minutes(self) -> Optional[Decimal]:
        """Time of possession in minutes"""
        if self.time_of_possession_seconds:
            return Decimal(self.time_of_possession_seconds) / Decimal(60)
        return None


# =============================================================================
# Advanced Metrics Models
# =============================================================================

class FootballAdvancedMetrics(Base, UUIDMixin, TimestampMixin):
    """
    Advanced football analytics and metrics
    Includes EPA, WPA, DVOA, and other sophisticated measurements
    """
    __tablename__ = "football_advanced_metrics"

    # Context
    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="Reference to team (NULL for league-wide metrics)"
    )

    player_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="CASCADE"),
        doc="Reference to player (NULL for team metrics)"
    )

    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        doc="Reference to specific game (NULL for season metrics)"
    )

    season_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the season"
    )

    # Metric identification
    metric_type: Mapped[AdvancedMetricType] = mapped_column(
        nullable=False,
        doc="Type of advanced metric"
    )

    metric_category: Mapped[StatisticCategory] = mapped_column(
        nullable=False,
        doc="Category of the metric"
    )

    position_group: Mapped[Optional[FootballPositionGroup]] = mapped_column(
        doc="Position group for player-specific metrics"
    )

    # Situational context
    situation_filter: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Situational filter (e.g., 'red_zone', 'third_down', 'two_minute')"
    )

    opponent_strength: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Opponent strength classification"
    )

    # Core metric values
    metric_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        nullable=False,
        doc="Primary metric value"
    )

    sample_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Sample size for the metric (plays, attempts, etc.)"
    )

    confidence_interval_lower: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6),
        doc="Lower bound of confidence interval"
    )

    confidence_interval_upper: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6),
        doc="Upper bound of confidence interval"
    )

    # Expected Points metrics
    expected_points_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Expected Points Added"
    )

    expected_points_per_play: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        doc="Expected Points per play"
    )

    # Win Probability metrics
    win_probability_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 6),
        doc="Win Probability Added"
    )

    win_probability_per_play: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 6),
        doc="Win Probability per play"
    )

    # Success rate metrics
    success_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Success rate (0-1)"
    )

    explosive_play_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Explosive play rate (0-1)"
    )

    stuff_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Stuff rate (negative plays) (0-1)"
    )

    # Efficiency metrics
    yards_per_play: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Yards per play"
    )

    points_per_drive: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 3),
        doc="Points per drive"
    )

    plays_per_drive: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Plays per drive"
    )

    seconds_per_drive: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        doc="Seconds per drive"
    )

    # Down and distance efficiency
    first_down_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="First down conversion rate"
    )

    third_down_conversion_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Third down conversion rate"
    )

    fourth_down_conversion_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Fourth down conversion rate"
    )

    # Red zone and goal line
    red_zone_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Red zone scoring efficiency"
    )

    red_zone_touchdown_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Red zone touchdown rate"
    )

    goal_line_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Goal line scoring efficiency"
    )

    # Two-minute drill
    two_minute_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Two-minute drill efficiency"
    )

    # Field position metrics
    average_field_position: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        doc="Average field position (yard line)"
    )

    field_position_advantage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Field position advantage vs opponents"
    )

    # Pressure and pass rush metrics (defensive)
    pressure_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Pressure rate on QB (0-1)"
    )

    sack_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Sack rate (0-1)"
    )

    quarterback_hit_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="QB hit rate (0-1)"
    )

    hurry_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="QB hurry rate (0-1)"
    )

    # Coverage metrics (defensive)
    completion_percentage_allowed: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Completion percentage allowed"
    )

    yards_per_target_allowed: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Yards per target allowed"
    )

    passer_rating_allowed: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Passer rating allowed"
    )

    # HAVOC rate (defensive)
    havoc_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="HAVOC rate (TFL + FF + PBU + INT per play)"
    )

    tackles_for_loss_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Tackles for loss rate"
    )

    forced_fumble_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Forced fumble rate"
    )

    # DVOA-style metrics
    dvoa_offensive: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Defense-adjusted Value Over Average (offense)"
    )

    dvoa_defensive: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Defense-adjusted Value Over Average (defense)"
    )

    # Special teams efficiency
    field_goal_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Field goal efficiency"
    )

    punt_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Punt efficiency (net yards)"
    )

    return_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Return efficiency (average yards)"
    )

    # Coverage units
    punt_coverage_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Punt coverage efficiency"
    )

    kickoff_coverage_efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Kickoff coverage efficiency"
    )

    # Relative performance
    percentile_rank: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Percentile rank among peers (0-100)"
    )

    z_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Z-score relative to league average"
    )

    grade: Mapped[Optional[str]] = mapped_column(
        String(5),
        doc="Letter grade (A+ to F)"
    )

    # Time-based context
    calculation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="When the metric was calculated"
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="When the metric was last updated"
    )

    # Metadata
    calculation_method: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Method used to calculate the metric"
    )

    data_source: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Source of the underlying data"
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes about the metric"
    )

    # Relationships
    team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    player: Mapped[Optional["FootballPlayer"]] = relationship(
        "FootballPlayer",
        lazy="selectin"
    )

    game: Mapped[Optional["FootballGame"]] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    season: Mapped["Season"] = relationship(
        "Season",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_adv_metrics_team_id", "team_id"),
        Index("idx_football_adv_metrics_player_id", "player_id"),
        Index("idx_football_adv_metrics_game_id", "game_id"),
        Index("idx_football_adv_metrics_season_id", "season_id"),
        Index("idx_football_adv_metrics_type", "metric_type"),
        Index("idx_football_adv_metrics_category", "metric_category"),
        Index("idx_football_adv_metrics_position", "position_group"),
        Index("idx_football_adv_metrics_situation", "situation_filter"),
        Index("idx_football_adv_metrics_team_season", "team_id", "season_id"),
        Index("idx_football_adv_metrics_player_season", "player_id", "season_id"),
        Index("idx_football_adv_metrics_calculation_date", "calculation_date"),
        Index("idx_football_adv_metrics_value", "metric_value"),
        Index("idx_football_adv_metrics_percentile", "percentile_rank"),
        UniqueConstraint("team_id", "player_id", "game_id", "season_id", "metric_type", "situation_filter",
                        name="uq_football_adv_metrics_context_type"),
    )

    def __repr__(self) -> str:
        context = f"team={self.team_id}" if self.team_id else f"player={self.player_id}"
        return f"<FootballAdvancedMetrics({context}, {self.metric_type}, value={self.metric_value})>"

    @property
    def is_above_average(self) -> bool:
        """Whether the metric value is above average"""
        if self.percentile_rank:
            return self.percentile_rank > 50
        return False

    @property
    def performance_tier(self) -> str:
        """Performance tier based on percentile rank"""
        if not self.percentile_rank:
            return "Unknown"

        if self.percentile_rank >= 90:
            return "Elite"
        elif self.percentile_rank >= 75:
            return "Above Average"
        elif self.percentile_rank >= 25:
            return "Average"
        else:
            return "Below Average"

    @property
    def confidence_level(self) -> Optional[str]:
        """Confidence level based on sample size"""
        if self.sample_size >= 100:
            return "High"
        elif self.sample_size >= 50:
            return "Medium"
        elif self.sample_size >= 20:
            return "Low"
        else:
            return "Very Low"


# =============================================================================
# Game Statistics Models
# =============================================================================

class FootballGameStatistics(Base, UUIDMixin, TimestampMixin):
    """
    Comprehensive game-level statistics aggregating all play-by-play data
    Serves as the definitive record for game performance analytics
    """
    __tablename__ = "football_game_statistics"

    # Game context
    game_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football game"
    )

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

    season_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the season"
    )

    # Game outcome
    home_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Home team final score"
    )

    away_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Away team final score"
    )

    winner_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Reference to winning team"
    )

    margin_of_victory: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Margin of victory"
    )

    # Game flow and timing
    total_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Total plays in the game"
    )

    game_duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total game duration in minutes"
    )

    overtime_periods: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of overtime periods"
    )

    # Scoring breakdown
    home_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team touchdowns"
    )

    away_touchdowns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team touchdowns"
    )

    home_field_goals: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team field goals"
    )

    away_field_goals: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team field goals"
    )

    home_safeties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team safeties"
    )

    away_safeties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team safeties"
    )

    # Total yardage
    home_total_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team total yards"
    )

    away_total_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team total yards"
    )

    home_passing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team passing yards"
    )

    away_passing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team passing yards"
    )

    home_rushing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team rushing yards"
    )

    away_rushing_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team rushing yards"
    )

    # First downs
    home_first_downs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team first downs"
    )

    away_first_downs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team first downs"
    )

    # Third down efficiency
    home_third_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team third down attempts"
    )

    home_third_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team third down conversions"
    )

    away_third_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team third down attempts"
    )

    away_third_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team third down conversions"
    )

    # Fourth down efficiency
    home_fourth_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team fourth down attempts"
    )

    home_fourth_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team fourth down conversions"
    )

    away_fourth_down_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team fourth down attempts"
    )

    away_fourth_down_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team fourth down conversions"
    )

    # Red zone efficiency
    home_red_zone_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team red zone attempts"
    )

    home_red_zone_scores: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team red zone scores"
    )

    away_red_zone_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team red zone attempts"
    )

    away_red_zone_scores: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team red zone scores"
    )

    # Turnovers
    home_turnovers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team turnovers"
    )

    away_turnovers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team turnovers"
    )

    home_interceptions_thrown: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team interceptions thrown"
    )

    away_interceptions_thrown: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team interceptions thrown"
    )

    home_fumbles_lost: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team fumbles lost"
    )

    away_fumbles_lost: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team fumbles lost"
    )

    # Penalties
    home_penalties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team penalties"
    )

    home_penalty_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team penalty yards"
    )

    away_penalties: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team penalties"
    )

    away_penalty_yards: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team penalty yards"
    )

    # Time of possession
    home_time_of_possession_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Home team time of possession in seconds"
    )

    away_time_of_possession_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Away team time of possession in seconds"
    )

    # Drives
    home_total_drives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team total drives"
    )

    away_total_drives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team total drives"
    )

    home_scoring_drives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team scoring drives"
    )

    away_scoring_drives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team scoring drives"
    )

    # Sacks
    home_sacks_recorded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team sacks recorded"
    )

    away_sacks_recorded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team sacks recorded"
    )

    home_sacks_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team sacks allowed"
    )

    away_sacks_allowed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team sacks allowed"
    )

    # Advanced metrics
    home_expected_points_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Home team total EPA"
    )

    away_expected_points_added: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        doc="Away team total EPA"
    )

    home_success_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Home team success rate"
    )

    away_success_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        doc="Away team success rate"
    )

    home_explosive_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Home team explosive plays"
    )

    away_explosive_plays: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Away team explosive plays"
    )

    # Game context and significance
    game_importance: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Game importance level"
    )

    playoff_implications: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        doc="Whether game had playoff implications"
    )

    rivalry_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was a rivalry game"
    )

    conference_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this was a conference game"
    )

    # Weather impact
    weather_impact: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Assessment of weather impact"
    )

    # Data completeness
    play_by_play_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether play-by-play data is complete"
    )

    advanced_stats_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether advanced statistics are complete"
    )

    last_stats_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="When statistics were last updated"
    )

    # Relationships
    game: Mapped["FootballGame"] = relationship(
        "FootballGame",
        lazy="selectin"
    )

    home_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[home_team_id],
        lazy="selectin"
    )

    away_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[away_team_id],
        lazy="selectin"
    )

    winner: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[winner_id],
        lazy="selectin"
    )

    season: Mapped["Season"] = relationship(
        "Season",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_game_stats_game_id", "game_id"),
        Index("idx_football_game_stats_home_team_id", "home_team_id"),
        Index("idx_football_game_stats_away_team_id", "away_team_id"),
        Index("idx_football_game_stats_season_id", "season_id"),
        Index("idx_football_game_stats_winner_id", "winner_id"),
        Index("idx_football_game_stats_scores", "home_score", "away_score"),
        Index("idx_football_game_stats_margin", "margin_of_victory"),
        Index("idx_football_game_stats_rivalry", "rivalry_game"),
        Index("idx_football_game_stats_conference", "conference_game"),
        Index("idx_football_game_stats_teams", "home_team_id", "away_team_id"),
        Index("idx_football_game_stats_season_teams", "season_id", "home_team_id", "away_team_id"),
        UniqueConstraint("game_id", name="uq_football_game_stats_game"),
    )

    def __repr__(self) -> str:
        return f"<FootballGameStatistics(game={self.game_id}, {self.away_score}-{self.home_score})>"

    @property
    def total_points(self) -> int:
        """Total points scored in the game"""
        return self.home_score + self.away_score

    @property
    def is_high_scoring(self) -> bool:
        """Whether the game was high-scoring (>60 total points)"""
        return self.total_points > 60

    @property
    def is_low_scoring(self) -> bool:
        """Whether the game was low-scoring (<30 total points)"""
        return self.total_points < 30

    @property
    def is_blowout(self) -> bool:
        """Whether the game was a blowout (>21 point margin)"""
        return self.margin_of_victory > 21

    @property
    def is_close_game(self) -> bool:
        """Whether the game was close (≤7 point margin)"""
        return self.margin_of_victory <= 7

    @property
    def home_third_down_percentage(self) -> Optional[Decimal]:
        """Home team third down conversion percentage"""
        if self.home_third_down_attempts > 0:
            return Decimal(self.home_third_down_conversions) / Decimal(self.home_third_down_attempts) * 100
        return None

    @property
    def away_third_down_percentage(self) -> Optional[Decimal]:
        """Away team third down conversion percentage"""
        if self.away_third_down_attempts > 0:
            return Decimal(self.away_third_down_conversions) / Decimal(self.away_third_down_attempts) * 100
        return None

    @property
    def home_red_zone_percentage(self) -> Optional[Decimal]:
        """Home team red zone scoring percentage"""
        if self.home_red_zone_attempts > 0:
            return Decimal(self.home_red_zone_scores) / Decimal(self.home_red_zone_attempts) * 100
        return None

    @property
    def away_red_zone_percentage(self) -> Optional[Decimal]:
        """Away team red zone scoring percentage"""
        if self.away_red_zone_attempts > 0:
            return Decimal(self.away_red_zone_scores) / Decimal(self.away_red_zone_attempts) * 100
        return None

    @property
    def turnover_margin_home(self) -> int:
        """Turnover margin for home team"""
        return self.away_turnovers - self.home_turnovers

    @property
    def turnover_margin_away(self) -> int:
        """Turnover margin for away team"""
        return self.home_turnovers - self.away_turnovers

    @property
    def home_time_of_possession_minutes(self) -> Optional[Decimal]:
        """Home team time of possession in minutes"""
        if self.home_time_of_possession_seconds:
            return Decimal(self.home_time_of_possession_seconds) / Decimal(60)
        return None

    @property
    def away_time_of_possession_minutes(self) -> Optional[Decimal]:
        """Away team time of possession in minutes"""
        if self.away_time_of_possession_seconds:
            return Decimal(self.away_time_of_possession_seconds) / Decimal(60)
        return None

    @property
    def was_home_victory(self) -> bool:
        """Whether the home team won"""
        return self.home_score > self.away_score

    @property
    def yards_differential_home(self) -> int:
        """Yards differential for home team"""
        return self.home_total_yards - self.away_total_yards