"""
College Football Phase 5: Content Integration Models
Football-specific content classification, injury reports, recruiting news, coaching updates,
depth charts, game previews, and bowl content extending existing content infrastructure
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, Date, DateTime, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB, ARRAY, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, CheckConstraint

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    FootballContentType, FootballPosition, FootballPositionGroup, FootballDepthChartStatus,
    FootballInjuryType, FootballInjurySeverity, FootballRecruitingEventType, FootballCoachingChangeType,
    FootballBowlNewsType, PlayerEligibilityStatus, GameStatus, BowlTier, PlayoffRound,
    RecruitingStarRating, CoachingPosition, CoachingLevel, IngestionStatus
)


# =============================================================================
# Football Phase 5: Content Models
# =============================================================================

class FootballContent(Base, UUIDMixin, TimestampMixin):
    """
    Enhanced content model for college football-specific content that extends base CollegeContent functionality
    Leverages existing content infrastructure while providing football-specific classification
    """
    __tablename__ = "football_content"
    __table_args__ = (
        Index('idx_football_content_teams', 'primary_team_id', 'secondary_team_id'),
        Index('idx_football_content_players', 'primary_player_id'),
        Index('idx_football_content_type_date', 'content_type', 'published_at'),
        Index('idx_football_content_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_football_content_title_trgm', 'title', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}),
        Index('idx_football_content_game', 'game_id'),
        Index('idx_football_content_bowl', 'bowl_game_id'),
        CheckConstraint('relevance_score >= 0 AND relevance_score <= 1', name='check_valid_relevance_score'),
        CheckConstraint('word_count >= 0', name='check_valid_word_count'),
        CheckConstraint('reading_time_minutes >= 0', name='check_valid_reading_time'),
        CheckConstraint('engagement_score >= 0', name='check_valid_engagement_score'),
    )

    # Link to base content infrastructure
    college_content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_content.id", ondelete="CASCADE"),
        doc="Reference to the base college content (if from standard pipeline)"
    )

    # Content identification
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Content title"
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Content summary/excerpt"
    )

    content: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Full content body"
    )

    # Football-specific classification
    content_type: Mapped[FootballContentType] = mapped_column(
        nullable=False,
        doc="Specific college football content type"
    )

    # Team associations (primary for single-team content, secondary for multi-team)
    primary_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="Primary football team this content is about"
    )

    secondary_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="Secondary football team (for games, transfers, etc.)"
    )

    # Player association (links to football players)
    primary_player_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="CASCADE"),
        doc="Primary football player this content is about"
    )

    # Game association
    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_games.id", ondelete="CASCADE"),
        doc="Football game this content is about"
    )

    # Bowl game association
    bowl_game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("bowl_games.id", ondelete="CASCADE"),
        doc="Bowl game this content is about"
    )

    # Content metadata
    author: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="Content author"
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Content source publication"
    )

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Original publication timestamp"
    )

    url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        doc="Original content URL"
    )

    image_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        doc="Featured image URL"
    )

    # Content analysis
    word_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Word count of the content"
    )

    reading_time_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Estimated reading time in minutes"
    )

    sentiment_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Sentiment analysis score (-1 to 1)"
    )

    relevance_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.5"),
        nullable=False,
        doc="Relevance score to college football (0-1)"
    )

    engagement_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        doc="Engagement metrics (views, shares, comments)"
    )

    # Football-specific content details
    position_groups_mentioned: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Football position groups mentioned in content"
    )

    recruiting_class_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Recruiting class year (for recruiting content)"
    )

    coaching_position_mentioned: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Coaching position mentioned (for coaching content)"
    )

    injury_status_impact: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Impact on team depth chart or playing time"
    )

    # Search and categorization
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        doc="Full-text search vector"
    )

    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Content tags for categorization"
    )

    mentioned_players: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Array of player names mentioned in content"
    )

    mentioned_coaches: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Array of coach names mentioned in content"
    )

    mentioned_recruits: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Array of recruit names mentioned in content"
    )

    # Metadata
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="External identifier from source"
    )

    content_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional structured metadata"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this content is active/published"
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this content is featured"
    )

    is_breaking_news: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is breaking news"
    )

    # Relationships
    college_content: Mapped[Optional["CollegeContent"]] = relationship(
        "CollegeContent",
        lazy="select"
    )

    primary_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[primary_team_id],
        lazy="selectin"
    )

    secondary_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[secondary_team_id],
        lazy="selectin"
    )

    primary_player: Mapped[Optional["FootballPlayer"]] = relationship(
        "FootballPlayer",
        lazy="selectin"
    )

    game: Mapped[Optional["FootballGame"]] = relationship(
        "FootballGame",
        lazy="select"
    )

    bowl_game: Mapped[Optional["BowlGame"]] = relationship(
        "BowlGame",
        lazy="select"
    )

    # Content associations
    injury_reports: Mapped[List["FootballInjuryReport"]] = relationship(
        "FootballInjuryReport",
        back_populates="content",
        lazy="select"
    )

    recruiting_news: Mapped[List["FootballRecruitingNews"]] = relationship(
        "FootballRecruitingNews",
        back_populates="content",
        lazy="select"
    )

    coaching_news: Mapped[List["FootballCoachingNews"]] = relationship(
        "FootballCoachingNews",
        back_populates="content",
        lazy="select"
    )

    depth_chart_updates: Mapped[List["FootballDepthChartUpdate"]] = relationship(
        "FootballDepthChartUpdate",
        back_populates="content",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FootballContent(id={self.id}, type={self.content_type}, title='{self.title[:50]}...')>"

    @property
    def excerpt(self) -> str:
        """Get content excerpt"""
        if self.summary:
            return self.summary
        if self.content:
            return self.content[:200] + "..." if len(self.content) > 200 else self.content
        return ""

    @property
    def is_recruiting_content(self) -> bool:
        """Check if this is recruiting-related content"""
        recruiting_types = [
            FootballContentType.RECRUITING_NEWS,
            FootballContentType.RECRUITING_COMMIT,
            FootballContentType.RECRUITING_DECOMMIT,
            FootballContentType.RECRUITING_VISIT,
            FootballContentType.RECRUITING_RANKING,
            FootballContentType.RECRUITING_CLASS_UPDATE,
            FootballContentType.SIGNING_DAY_NEWS,
            FootballContentType.TRANSFER_PORTAL_ENTRY,
            FootballContentType.TRANSFER_COMMITMENT,
            FootballContentType.TRANSFER_PORTAL_NEWS
        ]
        return self.content_type in recruiting_types

    @property
    def is_injury_content(self) -> bool:
        """Check if this is injury-related content"""
        injury_types = [
            FootballContentType.INJURY_REPORT,
            FootballContentType.INJURY_UPDATE,
            FootballContentType.RETURN_FROM_INJURY,
            FootballContentType.MEDICAL_CLEARANCE,
            FootballContentType.SURGERY_NEWS
        ]
        return self.content_type in injury_types


class FootballInjuryReport(Base, UUIDMixin, TimestampMixin):
    """
    Football player injury tracking and status updates with depth chart implications
    Extended from basketball injury reports to handle football's complexity
    """
    __tablename__ = "football_injury_reports"
    __table_args__ = (
        Index('idx_football_injury_reports_player', 'player_id'),
        Index('idx_football_injury_reports_team', 'team_id'),
        Index('idx_football_injury_reports_status', 'current_status'),
        Index('idx_football_injury_reports_date', 'injury_date'),
        Index('idx_football_injury_reports_position', 'position_affected'),
        CheckConstraint('games_missed >= 0', name='check_valid_games_missed'),
        UniqueConstraint('player_id', 'injury_date', 'injury_type', name='uq_football_player_injury_date_type'),
    )

    # Player and team
    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the injured football player"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the player's football team"
    )

    # Position impact
    position_affected: Mapped[FootballPosition] = mapped_column(
        nullable=False,
        doc="Football position affected by injury"
    )

    position_group_affected: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Position group affected for depth chart planning"
    )

    # Injury details
    injury_type: Mapped[FootballInjuryType] = mapped_column(
        nullable=False,
        doc="Type of football injury"
    )

    injury_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed description of the injury"
    )

    severity: Mapped[FootballInjurySeverity] = mapped_column(
        nullable=False,
        doc="Severity level of the injury"
    )

    # Timeline
    injury_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date the injury occurred"
    )

    reported_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        doc="Date the injury was officially reported"
    )

    expected_return_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Expected return date (if known)"
    )

    actual_return_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Actual return date"
    )

    # Status tracking
    current_status: Mapped[PlayerEligibilityStatus] = mapped_column(
        default=PlayerEligibilityStatus.INJURED,
        nullable=False,
        doc="Current player eligibility status"
    )

    depth_chart_status: Mapped[FootballDepthChartStatus] = mapped_column(
        default=FootballDepthChartStatus.INJURED_RESERVE,
        nullable=False,
        doc="Current depth chart status"
    )

    games_missed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of games missed due to injury"
    )

    practices_missed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of practices missed due to injury"
    )

    # Football-specific details
    requires_surgery: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the injury requires surgery"
    )

    surgery_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of surgery (if applicable)"
    )

    is_contact_injury: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether injury was caused by contact"
    )

    occurred_during_game: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether injury occurred during game vs practice"
    )

    # Impact assessment
    replacement_player_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="SET NULL"),
        doc="Player who replaced the injured player"
    )

    depth_chart_impact: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of impact on team depth chart"
    )

    recruiting_impact: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Impact on recruiting at the position"
    )

    # Recovery tracking
    recovery_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional recovery notes and updates"
    )

    recovery_milestones: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Recovery milestone tracking"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_content.id", ondelete="SET NULL"),
        doc="Reference to the content that reported this injury"
    )

    # Medical metadata
    medical_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional medical information (anonymized)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this injury report is current/active"
    )

    # Relationships
    player: Mapped["FootballPlayer"] = relationship(
        "FootballPlayer",
        foreign_keys=[player_id],
        lazy="selectin"
    )

    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    replacement_player: Mapped[Optional["FootballPlayer"]] = relationship(
        "FootballPlayer",
        foreign_keys=[replacement_player_id],
        lazy="select"
    )

    content: Mapped[Optional["FootballContent"]] = relationship(
        "FootballContent",
        back_populates="injury_reports",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FootballInjuryReport(id={self.id}, player_id={self.player_id}, type={self.injury_type}, severity={self.severity})>"

    @property
    def is_season_ending(self) -> bool:
        """Check if injury is season-ending"""
        return self.severity == FootballInjurySeverity.SEASON_ENDING

    @property
    def is_major_injury(self) -> bool:
        """Check if injury is major (7+ weeks)"""
        return self.severity in [
            FootballInjurySeverity.MAJOR,
            FootballInjurySeverity.SEVERE,
            FootballInjurySeverity.SEASON_ENDING,
            FootballInjurySeverity.CAREER_ENDING
        ]

    @property
    def recovery_duration_days(self) -> Optional[int]:
        """Calculate recovery duration in days"""
        if self.actual_return_date and self.injury_date:
            return (self.actual_return_date - self.injury_date).days
        elif self.expected_return_date and self.injury_date:
            return (self.expected_return_date - self.injury_date).days
        return None


class FootballRecruitingNews(Base, UUIDMixin, TimestampMixin):
    """
    Football recruiting updates, commits, transfers, and portal activity
    Extended from basketball recruiting to handle football's complexity
    """
    __tablename__ = "football_recruiting_news"
    __table_args__ = (
        Index('idx_football_recruiting_news_recruit', 'recruit_name'),
        Index('idx_football_recruiting_news_team', 'team_id'),
        Index('idx_football_recruiting_news_event_type', 'event_type'),
        Index('idx_football_recruiting_news_date', 'event_date'),
        Index('idx_football_recruiting_news_class', 'recruiting_class'),
        Index('idx_football_recruiting_news_position', 'recruit_position'),
        CheckConstraint('star_rating >= 2 AND star_rating <= 5', name='check_valid_star_rating'),
    )

    # Recruit information
    recruit_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Name of the recruit"
    )

    recruit_position: Mapped[FootballPosition] = mapped_column(
        nullable=False,
        doc="Recruit's football position"
    )

    recruit_position_group: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Recruit's position group"
    )

    recruit_height: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Recruit's height (e.g., '6-2')"
    )

    recruit_weight: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Recruit's weight in pounds"
    )

    forty_yard_dash_time: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="40-yard dash time in seconds"
    )

    # Academic information
    high_school: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="High school or previous institution"
    )

    hometown: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Recruit's hometown"
    )

    home_state: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Recruit's home state"
    )

    recruiting_class: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Recruiting class year (e.g., 2025)"
    )

    # Event details
    event_type: Mapped[FootballRecruitingEventType] = mapped_column(
        nullable=False,
        doc="Type of recruiting event"
    )

    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="Football team involved in the recruiting event"
    )

    previous_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="Previous team (for transfers)"
    )

    event_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of the recruiting event"
    )

    # Ratings and rankings
    star_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Star rating (2-5 stars)"
    )

    composite_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 3),
        doc="Composite rating score"
    )

    national_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="National ranking among all recruits"
    )

    position_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Ranking among position players"
    )

    state_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Ranking within home state"
    )

    # Football-specific metrics
    projected_impact: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Projected impact level (immediate, year 2, developmental)"
    )

    nfl_projection: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="NFL draft projection"
    )

    # Additional details
    scholarship_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Type of scholarship offered (full, partial, etc.)"
    )

    commitment_level: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Level of commitment (verbal, signed, etc.)"
    )

    other_offers: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Other schools that have offered"
    )

    top_schools: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Final schools being considered"
    )

    visit_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Details about visits (official/unofficial, dates, etc.)"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_content.id", ondelete="SET NULL"),
        doc="Reference to the content that reported this news"
    )

    # Transfer portal specific
    is_transfer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a transfer portal event"
    )

    transfer_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for transfer (if applicable)"
    )

    eligibility_remaining: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Years of eligibility remaining"
    )

    has_redshirt_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether player has redshirt year available"
    )

    # Decision factors
    decision_factors: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Factors influencing decision (playing time, coaching staff, etc.)"
    )

    family_influence: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Family influence on decision"
    )

    # Source and verification
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Source of the recruiting news"
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the information has been verified"
    )

    recruiting_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional structured metadata"
    )

    # Relationships
    team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[team_id],
        lazy="selectin"
    )

    previous_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[previous_team_id],
        lazy="selectin"
    )

    content: Mapped[Optional["FootballContent"]] = relationship(
        "FootballContent",
        back_populates="recruiting_news",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FootballRecruitingNews(id={self.id}, recruit='{self.recruit_name}', event={self.event_type}, team_id={self.team_id})>"

    @property
    def is_commitment(self) -> bool:
        """Check if this is a commitment event"""
        return self.event_type in [
            FootballRecruitingEventType.COMMIT,
            FootballRecruitingEventType.TRANSFER_COMMITMENT,
            FootballRecruitingEventType.RECOMMIT
        ]

    @property
    def is_decommitment(self) -> bool:
        """Check if this is a decommitment event"""
        return self.event_type in [
            FootballRecruitingEventType.DECOMMIT,
            FootballRecruitingEventType.TRANSFER_WITHDRAWAL,
            FootballRecruitingEventType.FLIP
        ]

    @property
    def is_high_profile(self) -> bool:
        """Check if this is a high-profile recruit"""
        return (self.star_rating and self.star_rating >= 4) or (self.national_ranking and self.national_ranking <= 100)


class FootballCoachingNews(Base, UUIDMixin, TimestampMixin):
    """
    Football coaching changes, hirings, firings, and staff updates
    Extended from basketball coaching news to handle football's coaching complexity
    """
    __tablename__ = "football_coaching_news"
    __table_args__ = (
        Index('idx_football_coaching_news_coach', 'coach_name'),
        Index('idx_football_coaching_news_team', 'team_id'),
        Index('idx_football_coaching_news_change_type', 'change_type'),
        Index('idx_football_coaching_news_date', 'effective_date'),
        Index('idx_football_coaching_news_position', 'position_title'),
        CheckConstraint('contract_years >= 0', name='check_valid_contract_years'),
        CheckConstraint('salary_amount >= 0', name='check_valid_salary'),
    )

    # Coach information
    coach_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Name of the coach"
    )

    position_title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Coaching position title"
    )

    coaching_position: Mapped[CoachingPosition] = mapped_column(
        nullable=False,
        doc="Specific coaching position"
    )

    coaching_level: Mapped[CoachingLevel] = mapped_column(
        nullable=False,
        doc="Level of coaching position"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Football team affected by the coaching change"
    )

    # Change details
    change_type: Mapped[FootballCoachingChangeType] = mapped_column(
        nullable=False,
        doc="Type of coaching change"
    )

    effective_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date the change becomes effective"
    )

    announced_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        doc="Date the change was announced"
    )

    # Previous/new positions
    previous_position: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Previous position or team"
    )

    previous_team: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Previous team name"
    )

    new_position: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="New position or team (for departures)"
    )

    new_team: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="New team name (for departures)"
    )

    # Contract details
    contract_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Length of contract in years"
    )

    salary_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        doc="Annual salary amount"
    )

    total_contract_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        doc="Total contract value"
    )

    buyout_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        doc="Contract buyout amount"
    )

    contract_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional contract details"
    )

    # Background
    coaching_background: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Coach's coaching background and experience"
    )

    playing_background: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Coach's playing background"
    )

    education_background: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Coach's educational background"
    )

    # Specializations
    recruiting_areas: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Geographic recruiting areas of responsibility"
    )

    position_groups_coached: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Position groups this coach is responsible for"
    )

    specialties: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Coaching specialties (red zone, third down, etc.)"
    )

    # Reason and impact
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for the coaching change"
    )

    team_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Team record at time of change (e.g., '8-4')"
    )

    tenure_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Years with the team (for departures)"
    )

    recruiting_impact: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Impact on recruiting efforts"
    )

    # Performance metrics
    wins_losses_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Overall wins-losses record as head coach"
    )

    bowl_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Bowl game record"
    )

    recruiting_success: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Summary of recruiting success"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_content.id", ondelete="SET NULL"),
        doc="Reference to the content that reported this news"
    )

    # Source and verification
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Source of the coaching news"
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the information has been verified"
    )

    coaching_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional structured metadata"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    content: Mapped[Optional["FootballContent"]] = relationship(
        "FootballContent",
        back_populates="coaching_news",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FootballCoachingNews(id={self.id}, coach='{self.coach_name}', change_type={self.change_type}, team_id={self.team_id})>"

    @property
    def is_hiring(self) -> bool:
        """Check if this is a hiring event"""
        return self.change_type in [
            FootballCoachingChangeType.HIRE,
            FootballCoachingChangeType.PROMOTION,
            FootballCoachingChangeType.LATERAL_MOVE
        ]

    @property
    def is_departure(self) -> bool:
        """Check if this is a departure event"""
        return self.change_type in [
            FootballCoachingChangeType.FIRE,
            FootballCoachingChangeType.RESIGNATION,
            FootballCoachingChangeType.RETIREMENT,
            FootballCoachingChangeType.MUTUAL_SEPARATION
        ]

    @property
    def is_coordinator_position(self) -> bool:
        """Check if this involves a coordinator position"""
        coordinator_positions = [
            CoachingPosition.OFFENSIVE_COORDINATOR,
            CoachingPosition.DEFENSIVE_COORDINATOR,
            CoachingPosition.SPECIAL_TEAMS_COORDINATOR,
            CoachingPosition.RECRUITING_COORDINATOR
        ]
        return self.coaching_position in coordinator_positions


class FootballDepthChartUpdate(Base, UUIDMixin, TimestampMixin):
    """
    Football depth chart updates and position battle tracking
    Handles football's complex roster with 85+ players across 22+ positions
    """
    __tablename__ = "football_depth_chart_updates"
    __table_args__ = (
        Index('idx_football_depth_chart_team', 'team_id'),
        Index('idx_football_depth_chart_player', 'player_id'),
        Index('idx_football_depth_chart_position', 'position'),
        Index('idx_football_depth_chart_date', 'update_date'),
        Index('idx_football_depth_chart_status', 'depth_chart_status'),
        UniqueConstraint('team_id', 'player_id', 'position', 'update_date', name='uq_football_depth_chart_update'),
    )

    # Team and player
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

    # Position details
    position: Mapped[FootballPosition] = mapped_column(
        nullable=False,
        doc="Specific position on depth chart"
    )

    position_group: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Position group"
    )

    # Depth chart status
    depth_chart_status: Mapped[FootballDepthChartStatus] = mapped_column(
        nullable=False,
        doc="Current status on depth chart"
    )

    previous_status: Mapped[Optional[FootballDepthChartStatus]] = mapped_column(
        doc="Previous depth chart status"
    )

    depth_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Order within the position (1=starter, 2=backup, etc.)"
    )

    previous_depth_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Previous depth order"
    )

    # Update details
    update_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        doc="Date of the depth chart update"
    )

    update_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of update (promotion, demotion, injury, suspension, etc.)"
    )

    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for the depth chart change"
    )

    # Position battle details
    is_position_battle: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this involves an ongoing position battle"
    )

    competing_players: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Other players competing for the position"
    )

    battle_status: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Status of the position battle"
    )

    # Performance impact
    expected_playing_time: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Expected playing time percentage"
    )

    impact_on_gameplan: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Impact on team's game plan or strategy"
    )

    # Special circumstances
    is_injury_related: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether change is due to injury"
    )

    is_disciplinary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether change is due to disciplinary action"
    )

    is_academic_related: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether change is due to academic issues"
    )

    is_performance_based: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether change is based on performance"
    )

    # Timeline expectations
    expected_duration: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Expected duration of this status (temporary, permanent, etc.)"
    )

    review_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when status will be reviewed"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_content.id", ondelete="SET NULL"),
        doc="Reference to the content that reported this update"
    )

    # Metadata
    update_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional structured metadata"
    )

    is_official: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is an official team announcement"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    player: Mapped["FootballPlayer"] = relationship(
        "FootballPlayer",
        lazy="selectin"
    )

    content: Mapped[Optional["FootballContent"]] = relationship(
        "FootballContent",
        back_populates="depth_chart_updates",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FootballDepthChartUpdate(id={self.id}, player_id={self.player_id}, position={self.position}, status={self.depth_chart_status})>"

    @property
    def is_promotion(self) -> bool:
        """Check if this is a promotion"""
        if self.previous_depth_order and self.depth_order:
            return self.depth_order < self.previous_depth_order
        return self.update_type == "promotion"

    @property
    def is_demotion(self) -> bool:
        """Check if this is a demotion"""
        if self.previous_depth_order and self.depth_order:
            return self.depth_order > self.previous_depth_order
        return self.update_type == "demotion"

    @property
    def is_starter(self) -> bool:
        """Check if player is now a starter"""
        return self.depth_chart_status == FootballDepthChartStatus.STARTER or self.depth_order == 1


class FootballGamePreview(Base, UUIDMixin, TimestampMixin):
    """
    Football game preview content with matchup analysis and predictions
    """
    __tablename__ = "football_game_previews"
    __table_args__ = (
        Index('idx_football_game_previews_game', 'game_id'),
        Index('idx_football_game_previews_home_team', 'home_team_id'),
        Index('idx_football_game_previews_away_team', 'away_team_id'),
        Index('idx_football_game_previews_date', 'game_date'),
        UniqueConstraint('game_id', 'content_id', name='uq_football_game_preview'),
    )

    # Game reference
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
        doc="Home team"
    )

    away_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Away team"
    )

    # Game details
    game_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Game date and time"
    )

    venue: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Game venue"
    )

    tv_coverage: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Television coverage details"
    )

    # Betting and predictions
    point_spread: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        doc="Point spread (negative for favorite)"
    )

    over_under: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        doc="Over/under total points"
    )

    predicted_winner: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Predicted winning team"
    )

    confidence_level: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Confidence level in prediction"
    )

    # Matchup analysis
    key_matchups: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Key position/player matchups to watch"
    )

    home_team_strengths: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Home team strengths"
    )

    home_team_weaknesses: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Home team weaknesses"
    )

    away_team_strengths: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Away team strengths"
    )

    away_team_weaknesses: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Away team weaknesses"
    )

    # Weather and conditions
    weather_forecast: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Weather forecast for game day"
    )

    field_conditions: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Expected field conditions"
    )

    # Storylines
    major_storylines: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Major storylines surrounding the game"
    )

    players_to_watch: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Key players to watch"
    )

    injury_concerns: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Injury concerns affecting the game"
    )

    # Historical context
    series_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="All-time series record (e.g., 'Home Team leads 15-10')"
    )

    recent_meetings: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Results of recent meetings between teams"
    )

    # Stakes and implications
    conference_implications: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Conference championship implications"
    )

    playoff_implications: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="College Football Playoff implications"
    )

    bowl_implications: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Bowl eligibility implications"
    )

    ranking_implications: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Ranking implications"
    )

    # Content association
    content_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_content.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the preview content"
    )

    # Metadata
    preview_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional structured metadata"
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

    predicted_winner_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[predicted_winner],
        lazy="select"
    )

    content: Mapped["FootballContent"] = relationship(
        "FootballContent",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FootballGamePreview(id={self.id}, game_id={self.game_id}, date={self.game_date})>"


class FootballBowlNews(Base, UUIDMixin, TimestampMixin):
    """
    Football bowl selection, playoff news, and postseason content
    """
    __tablename__ = "football_bowl_news"
    __table_args__ = (
        Index('idx_football_bowl_news_team', 'team_id'),
        Index('idx_football_bowl_news_bowl', 'bowl_game_id'),
        Index('idx_football_bowl_news_type', 'news_type'),
        Index('idx_football_bowl_news_date', 'announcement_date'),
    )

    # Team and bowl
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Football team involved in bowl news"
    )

    bowl_game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("bowl_games.id", ondelete="CASCADE"),
        doc="Bowl game (if applicable)"
    )

    opponent_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        doc="Opponent team in bowl game"
    )

    # News details
    news_type: Mapped[FootballBowlNewsType] = mapped_column(
        nullable=False,
        doc="Type of bowl news"
    )

    announcement_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        doc="Date of announcement"
    )

    # Selection details
    bowl_tier: Mapped[Optional[BowlTier]] = mapped_column(
        doc="Tier of bowl game"
    )

    selection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for bowl selection"
    )

    final_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Team's final regular season record"
    )

    conference_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Team's conference record"
    )

    # Playoff details
    playoff_round: Mapped[Optional[PlayoffRound]] = mapped_column(
        doc="Playoff round (if applicable)"
    )

    playoff_seed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Playoff seed"
    )

    ranking_at_selection: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Team ranking at time of selection"
    )

    # Bowl game details
    bowl_location: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Bowl game location"
    )

    bowl_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Bowl game date"
    )

    bowl_payout: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        doc="Bowl payout amount"
    )

    # Historical context
    last_bowl_appearance: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Team's last bowl appearance"
    )

    bowl_history: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Team's bowl game history"
    )

    # Ticket and travel info
    ticket_information: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Ticket sales and pricing information"
    )

    travel_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Travel arrangements and fan information"
    )

    # Preparation details
    opt_outs: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Players opting out of bowl game"
    )

    key_storylines: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Key storylines for the bowl game"
    )

    coaching_changes: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Coaching changes affecting bowl preparation"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_content.id", ondelete="SET NULL"),
        doc="Reference to the bowl news content"
    )

    # Source and verification
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Source of the bowl news"
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the information has been verified"
    )

    bowl_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional structured metadata"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[team_id],
        lazy="selectin"
    )

    bowl_game: Mapped[Optional["BowlGame"]] = relationship(
        "BowlGame",
        lazy="selectin"
    )

    opponent_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[opponent_team_id],
        lazy="selectin"
    )

    content: Mapped[Optional["FootballContent"]] = relationship(
        "FootballContent",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FootballBowlNews(id={self.id}, team_id={self.team_id}, news_type={self.news_type})>"

    @property
    def is_playoff_related(self) -> bool:
        """Check if this is playoff-related news"""
        playoff_types = [
            FootballBowlNewsType.PLAYOFF_SELECTION,
            FootballBowlNewsType.PLAYOFF_RANKING,
            FootballBowlNewsType.PLAYOFF_SEEDING,
            FootballBowlNewsType.PLAYOFF_SCHEDULE
        ]
        return self.news_type in playoff_types

    @property
    def is_bowl_selection(self) -> bool:
        """Check if this is bowl selection news"""
        return self.news_type == FootballBowlNewsType.BOWL_SELECTION