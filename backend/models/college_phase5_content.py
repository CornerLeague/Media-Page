"""
College Basketball Phase 5: Content Integration Models
Content classification, injury reports, recruiting news, coaching updates, and multi-team content relationships
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
    ContentCategory, IngestionStatus, PlayerEligibilityStatus, PlayerPosition, PlayerClass,
    CollegeContentType, InjuryType, InjurySeverity, RecruitingEventType, CoachingChangeType
)


# =============================================================================
# Phase 5: Content Models
# =============================================================================

class CollegeContent(Base, UUIDMixin, TimestampMixin):
    """
    Enhanced content model for college basketball-specific content that extends base Article functionality
    """
    __tablename__ = "college_content"
    __table_args__ = (
        Index('idx_college_content_teams', 'primary_team_id', 'secondary_team_id'),
        Index('idx_college_content_players', 'primary_player_id'),
        Index('idx_college_content_type_date', 'content_type', 'published_at'),
        Index('idx_college_content_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_college_content_title_trgm', 'title', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}),
        CheckConstraint('relevance_score >= 0 AND relevance_score <= 1', name='check_valid_relevance_score'),
        CheckConstraint('word_count >= 0', name='check_valid_word_count'),
        CheckConstraint('reading_time_minutes >= 0', name='check_valid_reading_time'),
        CheckConstraint('engagement_score >= 0', name='check_valid_engagement_score'),
    )

    # Link to base article
    article_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        doc="Reference to the base article (if from standard pipeline)"
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

    # College basketball specific classification
    content_type: Mapped[CollegeContentType] = mapped_column(
        nullable=False,
        doc="Specific college basketball content type"
    )

    # Team associations (primary for single-team content, secondary for multi-team)
    primary_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        doc="Primary team this content is about"
    )

    secondary_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        doc="Secondary team (for games, transfers, etc.)"
    )

    # Player association
    primary_player_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_players.id", ondelete="CASCADE"),
        doc="Primary player this content is about"
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
        doc="Relevance score to college basketball (0-1)"
    )

    engagement_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        doc="Engagement metrics (views, shares, comments)"
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

    # Relationships
    article: Mapped[Optional["Article"]] = relationship(
        "Article",
        lazy="select"
    )

    primary_team: Mapped[Optional["CollegeTeam"]] = relationship(
        "CollegeTeam",
        foreign_keys=[primary_team_id],
        lazy="selectin"
    )

    secondary_team: Mapped[Optional["CollegeTeam"]] = relationship(
        "CollegeTeam",
        foreign_keys=[secondary_team_id],
        lazy="selectin"
    )

    # Temporarily commented out due to Player model conflict
    # primary_player: Mapped[Optional["Player"]] = relationship(
    #     "Player",
    #     lazy="selectin"
    # )

    team_associations: Mapped[List["ContentTeamAssociation"]] = relationship(
        "ContentTeamAssociation",
        back_populates="content",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<CollegeContent(id={self.id}, type={self.content_type}, title='{self.title[:50]}...')>"

    @property
    def excerpt(self) -> str:
        """Get content excerpt"""
        if self.summary:
            return self.summary
        if self.content:
            return self.content[:200] + "..." if len(self.content) > 200 else self.content
        return ""


class InjuryReport(Base, UUIDMixin, TimestampMixin):
    """
    Player injury tracking and status updates
    """
    __tablename__ = "injury_reports"
    __table_args__ = (
        Index('idx_injury_reports_player', 'player_id'),
        Index('idx_injury_reports_team', 'team_id'),
        Index('idx_injury_reports_status', 'current_status'),
        Index('idx_injury_reports_date', 'injury_date'),
        CheckConstraint('games_missed >= 0', name='check_valid_games_missed'),
        UniqueConstraint('player_id', 'injury_date', 'injury_type', name='uq_player_injury_date_type'),
    )

    # Player and team
    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the injured player"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the player's team"
    )

    # Injury details
    injury_type: Mapped[InjuryType] = mapped_column(
        nullable=False,
        doc="Type of injury"
    )

    injury_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed description of the injury"
    )

    severity: Mapped[InjurySeverity] = mapped_column(
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

    games_missed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of games missed due to injury"
    )

    # Additional details
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

    recovery_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional recovery notes and updates"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_content.id", ondelete="SET NULL"),
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
    # Temporarily commented out due to Player model conflict
    # player: Mapped["Player"] = relationship(
    #     "Player",
    #     lazy="selectin"
    # )

    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    content: Mapped[Optional["CollegeContent"]] = relationship(
        "CollegeContent",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<InjuryReport(id={self.id}, player_id={self.player_id}, type={self.injury_type}, severity={self.severity})>"

    @property
    def is_season_ending(self) -> bool:
        """Check if injury is season-ending"""
        return self.severity == InjurySeverity.SEASON_ENDING

    @property
    def recovery_duration_days(self) -> Optional[int]:
        """Calculate recovery duration in days"""
        if self.actual_return_date and self.injury_date:
            return (self.actual_return_date - self.injury_date).days
        elif self.expected_return_date and self.injury_date:
            return (self.expected_return_date - self.injury_date).days
        return None


class RecruitingNews(Base, UUIDMixin, TimestampMixin):
    """
    Recruiting updates, commits, transfers, and portal activity
    """
    __tablename__ = "recruiting_news"
    __table_args__ = (
        Index('idx_recruiting_news_recruit', 'recruit_name'),
        Index('idx_recruiting_news_team', 'team_id'),
        Index('idx_recruiting_news_event_type', 'event_type'),
        Index('idx_recruiting_news_date', 'event_date'),
        Index('idx_recruiting_news_class', 'recruiting_class'),
        CheckConstraint('rating >= 0 AND rating <= 5', name='check_valid_rating'),
    )

    # Recruit information
    recruit_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Name of the recruit"
    )

    recruit_position: Mapped[Optional[PlayerPosition]] = mapped_column(
        doc="Recruit's playing position"
    )

    recruit_height: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Recruit's height (e.g., '6-8')"
    )

    recruit_weight: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Recruit's weight in pounds"
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

    recruiting_class: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Recruiting class year (e.g., 2025)"
    )

    # Event details
    event_type: Mapped[RecruitingEventType] = mapped_column(
        nullable=False,
        doc="Type of recruiting event"
    )

    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        doc="Team involved in the recruiting event"
    )

    previous_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        doc="Previous team (for transfers)"
    )

    event_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of the recruiting event"
    )

    # Ratings and rankings
    rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        doc="Star rating (0-5 stars)"
    )

    national_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="National ranking among recruits"
    )

    position_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Ranking among position players"
    )

    state_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Ranking within home state"
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

    visit_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Details about visits (official/unofficial, dates, etc.)"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_content.id", ondelete="SET NULL"),
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
    team: Mapped[Optional["CollegeTeam"]] = relationship(
        "CollegeTeam",
        foreign_keys=[team_id],
        lazy="selectin"
    )

    previous_team: Mapped[Optional["CollegeTeam"]] = relationship(
        "CollegeTeam",
        foreign_keys=[previous_team_id],
        lazy="selectin"
    )

    content: Mapped[Optional["CollegeContent"]] = relationship(
        "CollegeContent",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<RecruitingNews(id={self.id}, recruit='{self.recruit_name}', event={self.event_type}, team_id={self.team_id})>"

    @property
    def is_commitment(self) -> bool:
        """Check if this is a commitment event"""
        return self.event_type in [RecruitingEventType.COMMIT, RecruitingEventType.TRANSFER_COMMITMENT]

    @property
    def is_decommitment(self) -> bool:
        """Check if this is a decommitment event"""
        return self.event_type in [RecruitingEventType.DECOMMIT, RecruitingEventType.TRANSFER_WITHDRAWAL]


class CoachingNews(Base, UUIDMixin, TimestampMixin):
    """
    Coaching changes, hirings, firings, and staff updates
    """
    __tablename__ = "coaching_news"
    __table_args__ = (
        Index('idx_coaching_news_coach', 'coach_name'),
        Index('idx_coaching_news_team', 'team_id'),
        Index('idx_coaching_news_change_type', 'change_type'),
        Index('idx_coaching_news_date', 'effective_date'),
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
        doc="Coaching position (Head Coach, Assistant Coach, etc.)"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Team affected by the coaching change"
    )

    # Change details
    change_type: Mapped[CoachingChangeType] = mapped_column(
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

    new_position: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="New position or team (for departures)"
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

    contract_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional contract details"
    )

    # Background
    coaching_background: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Coach's background and experience"
    )

    playing_background: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Coach's playing background"
    )

    # Reason and impact
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for the coaching change"
    )

    team_record: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Team record at time of change (e.g., '15-12')"
    )

    tenure_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Years with the team (for departures)"
    )

    # Content association
    content_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_content.id", ondelete="SET NULL"),
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
    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    content: Mapped[Optional["CollegeContent"]] = relationship(
        "CollegeContent",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<CoachingNews(id={self.id}, coach='{self.coach_name}', change_type={self.change_type}, team_id={self.team_id})>"

    @property
    def is_hiring(self) -> bool:
        """Check if this is a hiring event"""
        return self.change_type in [CoachingChangeType.HIRE, CoachingChangeType.PROMOTION]

    @property
    def is_departure(self) -> bool:
        """Check if this is a departure event"""
        return self.change_type in [CoachingChangeType.FIRE, CoachingChangeType.RESIGNATION, CoachingChangeType.RETIREMENT]


class ContentTeamAssociation(Base, UUIDMixin):
    """
    Multi-team content relationships for tournaments, conference news, etc.
    """
    __tablename__ = "content_team_associations"
    __table_args__ = (
        UniqueConstraint('content_id', 'team_id', name='uq_content_team'),
        Index('idx_content_team_assoc_content', 'content_id'),
        Index('idx_content_team_assoc_team', 'team_id'),
        Index('idx_content_team_assoc_relevance', 'relevance_score'),
        CheckConstraint('relevance_score >= 0 AND relevance_score <= 1', name='check_valid_relevance_score'),
    )

    content_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_content.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the content"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    relevance_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.5"),
        nullable=False,
        doc="Relevance score of content to team (0-1)"
    )

    association_type: Mapped[str] = mapped_column(
        String(50),
        default="general",
        doc="Type of association (primary, secondary, mentioned, etc.)"
    )

    mentioned_players: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Array of player names mentioned for this team"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    content: Mapped["CollegeContent"] = relationship(
        "CollegeContent",
        back_populates="team_associations",
        lazy="select"
    )

    team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ContentTeamAssociation(content_id={self.content_id}, team_id={self.team_id}, relevance={self.relevance_score})>"


class ContentClassification(Base, UUIDMixin, TimestampMixin):
    """
    Enhanced content classification specific to college basketball content types
    """
    __tablename__ = "content_classifications"
    __table_args__ = (
        UniqueConstraint('content_id', 'classification_type', name='uq_content_classification_type'),
        Index('idx_content_class_content', 'content_id'),
        Index('idx_content_class_type', 'classification_type'),
        Index('idx_content_class_confidence', 'confidence_score'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_valid_confidence_score'),
    )

    content_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_content.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the content"
    )

    classification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of classification (sentiment, urgency, category, etc.)"
    )

    classification_value: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Classification result value"
    )

    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        doc="Confidence score for the classification (0-1)"
    )

    classifier_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Model or system that performed the classification"
    )

    classification_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        doc="Additional classification metadata"
    )

    # Relationships
    content: Mapped["CollegeContent"] = relationship(
        "CollegeContent",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<ContentClassification(content_id={self.content_id}, type={self.classification_type}, value={self.classification_value})>"