"""
College Basketball Phase 6: User Personalization Models
User preferences, bracket predictions, challenges, notifications, and engagement tracking
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index,
    Date, DateTime, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    EngagementLevel, BracketPredictionStatus, BracketChallengeStatus,
    ChallengePrivacy, NotificationFrequency, CollegeNotificationType,
    FeedContentType, EngagementMetricType, PersonalizationScore
)


class UserCollegePreferences(Base, UUIDMixin, TimestampMixin):
    """
    User preferences for following college basketball teams with engagement levels
    """
    __tablename__ = "user_college_preferences"
    __table_args__ = (
        UniqueConstraint('user_id', 'college_team_id', name='uq_user_college_team'),
        Index('idx_user_college_engagement', 'user_id', 'engagement_level'),
        Index('idx_user_college_active', 'user_id', 'is_active'),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user"
    )

    college_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the college team"
    )

    engagement_level: Mapped[EngagementLevel] = mapped_column(
        default=EngagementLevel.REGULAR,
        nullable=False,
        doc="User's engagement level with this team"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this preference is currently active"
    )

    followed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        doc="When the user started following this team"
    )

    # Notification preferences for this specific team
    game_reminders: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Send game reminder notifications for this team"
    )

    injury_updates: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Send injury update notifications for this team"
    )

    recruiting_news: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Send recruiting news notifications for this team"
    )

    coaching_updates: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Send coaching change notifications for this team"
    )

    # Calculated engagement metrics
    interaction_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        default=Decimal("0.5000"),
        nullable=False,
        doc="Calculated engagement score based on interactions (0.0-1.0)"
    )

    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Last time user interacted with content for this team"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="select"
    )

    college_team: Mapped["CollegeTeam"] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<UserCollegePreferences(user_id={self.user_id}, team_id={self.college_team_id}, engagement={self.engagement_level})>"

    @property
    def is_die_hard_fan(self) -> bool:
        """Check if user is a die-hard fan of this team"""
        return self.engagement_level == EngagementLevel.DIE_HARD


class BracketPrediction(Base, UUIDMixin, TimestampMixin):
    """
    User bracket predictions for NCAA tournaments
    """
    __tablename__ = "bracket_predictions"
    __table_args__ = (
        UniqueConstraint('user_id', 'tournament_id', name='uq_user_tournament_bracket'),
        Index('idx_bracket_status', 'status'),
        Index('idx_bracket_score', 'total_score', 'status'),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user who made the prediction"
    )

    tournament_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the tournament"
    )

    bracket_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="User-defined name for their bracket"
    )

    status: Mapped[BracketPredictionStatus] = mapped_column(
        default=BracketPredictionStatus.DRAFT,
        nullable=False,
        doc="Current status of the bracket prediction"
    )

    # Bracket data stored as JSON
    predictions: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Complete bracket predictions as JSON structure"
    )

    # Scoring information
    total_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total points earned from correct predictions"
    )

    possible_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Maximum possible points that could be earned"
    )

    correct_picks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of correct predictions made"
    )

    total_picks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of predictions made"
    )

    # Timing information
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When the bracket was submitted (final)"
    )

    locked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When the bracket was locked (tournament started)"
    )

    last_scored_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Last time bracket was scored"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="select"
    )

    tournament: Mapped["Tournament"] = relationship(
        "Tournament",
        lazy="selectin"
    )

    challenge_participations: Mapped[List["BracketChallengeParticipation"]] = relationship(
        "BracketChallengeParticipation",
        back_populates="bracket_prediction",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<BracketPrediction(user_id={self.user_id}, tournament_id={self.tournament_id}, score={self.total_score})>"

    @property
    def accuracy_percentage(self) -> Optional[float]:
        """Calculate prediction accuracy percentage"""
        if self.total_picks == 0:
            return None
        return (self.correct_picks / self.total_picks) * 100

    @property
    def score_percentage(self) -> Optional[float]:
        """Calculate score percentage of possible points"""
        if self.possible_score == 0:
            return None
        return (self.total_score / self.possible_score) * 100


class BracketChallenge(Base, UUIDMixin, TimestampMixin):
    """
    Group bracket challenges for March Madness competitions
    """
    __tablename__ = "bracket_challenges"
    __table_args__ = (
        Index('idx_challenge_status', 'status'),
        Index('idx_challenge_privacy', 'privacy_setting'),
        Index('idx_challenge_creator', 'creator_id'),
    )

    creator_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="User who created the challenge"
    )

    tournament_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        doc="Tournament this challenge is for"
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Name of the bracket challenge"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of the challenge"
    )

    status: Mapped[BracketChallengeStatus] = mapped_column(
        default=BracketChallengeStatus.OPEN,
        nullable=False,
        doc="Current status of the challenge"
    )

    privacy_setting: Mapped[ChallengePrivacy] = mapped_column(
        default=ChallengePrivacy.FRIENDS_ONLY,
        nullable=False,
        doc="Privacy setting for the challenge"
    )

    # Entry settings
    entry_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        doc="Entry fee for the challenge (if any)"
    )

    max_participants: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Maximum number of participants allowed"
    )

    # Timing
    registration_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Deadline for joining the challenge"
    )

    # Scoring settings
    scoring_system: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Scoring system configuration (points per round, etc.)"
    )

    # Prize information
    prize_structure: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        doc="Prize distribution structure"
    )

    # Challenge code for joining
    invite_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        doc="Unique code for joining the challenge"
    )

    # Statistics
    participant_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current number of participants"
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )

    tournament: Mapped["Tournament"] = relationship(
        "Tournament",
        lazy="selectin"
    )

    participations: Mapped[List["BracketChallengeParticipation"]] = relationship(
        "BracketChallengeParticipation",
        back_populates="challenge",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<BracketChallenge(id={self.id}, name='{self.name}', participants={self.participant_count})>"

    @property
    def is_full(self) -> bool:
        """Check if challenge has reached maximum participants"""
        return self.max_participants is not None and self.participant_count >= self.max_participants

    @property
    def is_open_for_registration(self) -> bool:
        """Check if challenge is still accepting new participants"""
        return (
            self.status == BracketChallengeStatus.OPEN and
            not self.is_full and
            (self.registration_deadline is None or datetime.now() < self.registration_deadline)
        )


class BracketChallengeParticipation(Base, UUIDMixin, TimestampMixin):
    """
    Junction table for users participating in bracket challenges
    """
    __tablename__ = "bracket_challenge_participations"
    __table_args__ = (
        UniqueConstraint('challenge_id', 'bracket_prediction_id', name='uq_challenge_bracket'),
        Index('idx_participation_challenge', 'challenge_id'),
        Index('idx_participation_score', 'challenge_id', 'current_score'),
    )

    challenge_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("bracket_challenges.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the bracket challenge"
    )

    bracket_prediction_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("bracket_predictions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user's bracket prediction"
    )

    # Participation details
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        doc="When the user joined this challenge"
    )

    # Current standings in this challenge
    current_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current score in this specific challenge"
    )

    current_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current rank in this challenge leaderboard"
    )

    # Relationships
    challenge: Mapped["BracketChallenge"] = relationship(
        "BracketChallenge",
        back_populates="participations",
        lazy="select"
    )

    bracket_prediction: Mapped["BracketPrediction"] = relationship(
        "BracketPrediction",
        back_populates="challenge_participations",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<BracketChallengeParticipation(challenge_id={self.challenge_id}, score={self.current_score})>"


class UserCollegeNotificationSettings(Base, UUIDMixin, TimestampMixin):
    """
    Enhanced notification settings specific to college basketball
    """
    __tablename__ = "user_college_notification_settings"

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Reference to the user"
    )

    # Global college basketball notification settings
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether college basketball notifications are enabled"
    )

    # Frequency preferences for different notification types
    game_reminders_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.GAME_DAY_ONLY,
        nullable=False,
        doc="Frequency for game reminder notifications"
    )

    score_updates_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.IMMEDIATE,
        nullable=False,
        doc="Frequency for live score updates"
    )

    injury_updates_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.IMMEDIATE,
        nullable=False,
        doc="Frequency for injury update notifications"
    )

    recruiting_news_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.DAILY_DIGEST,
        nullable=False,
        doc="Frequency for recruiting news notifications"
    )

    coaching_changes_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.IMMEDIATE,
        nullable=False,
        doc="Frequency for coaching change notifications"
    )

    ranking_changes_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.WEEKLY_DIGEST,
        nullable=False,
        doc="Frequency for ranking change notifications"
    )

    tournament_updates_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.IMMEDIATE,
        nullable=False,
        doc="Frequency for tournament update notifications"
    )

    bracket_challenge_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.IMMEDIATE,
        nullable=False,
        doc="Frequency for bracket challenge notifications"
    )

    transfer_portal_frequency: Mapped[NotificationFrequency] = mapped_column(
        default=NotificationFrequency.DAILY_DIGEST,
        nullable=False,
        doc="Frequency for transfer portal notifications"
    )

    # Delivery method preferences
    push_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether to send push notifications"
    )

    email_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether to send email notifications"
    )

    # Time-based preferences
    quiet_hours_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether to respect quiet hours"
    )

    quiet_hours_start: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Start hour for quiet time (0-23)"
    )

    quiet_hours_end: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="End hour for quiet time (0-23)"
    )

    # Game day specific settings
    pre_game_reminders: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Send reminders before games start"
    )

    pre_game_reminder_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        doc="Minutes before game to send reminder"
    )

    halftime_updates: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Send updates at halftime"
    )

    final_score_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Send notifications when games end"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<UserCollegeNotificationSettings(user_id={self.user_id}, enabled={self.enabled})>"

    def get_frequency_for_type(self, notification_type: CollegeNotificationType) -> NotificationFrequency:
        """Get the notification frequency for a specific notification type"""
        frequency_mapping = {
            CollegeNotificationType.GAME_REMINDERS: self.game_reminders_frequency,
            CollegeNotificationType.SCORE_UPDATES: self.score_updates_frequency,
            CollegeNotificationType.INJURY_UPDATES: self.injury_updates_frequency,
            CollegeNotificationType.RECRUITING_NEWS: self.recruiting_news_frequency,
            CollegeNotificationType.COACHING_CHANGES: self.coaching_changes_frequency,
            CollegeNotificationType.RANKING_CHANGES: self.ranking_changes_frequency,
            CollegeNotificationType.TOURNAMENT_UPDATES: self.tournament_updates_frequency,
            CollegeNotificationType.BRACKET_CHALLENGE: self.bracket_challenge_frequency,
            CollegeNotificationType.TRANSFER_PORTAL: self.transfer_portal_frequency,
        }
        return frequency_mapping.get(notification_type, NotificationFrequency.NEVER)


class PersonalizedFeed(Base, UUIDMixin, TimestampMixin):
    """
    Configuration for personalized content feeds
    """
    __tablename__ = "personalized_feeds"

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Reference to the user"
    )

    # Feed configuration
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether personalized feeds are enabled"
    )

    # Content type preferences with weights (0.0 - 1.0)
    articles_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("1.00"),
        nullable=False,
        doc="Weight for article content in feed"
    )

    game_updates_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.80"),
        nullable=False,
        doc="Weight for game update content in feed"
    )

    injury_reports_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.70"),
        nullable=False,
        doc="Weight for injury report content in feed"
    )

    recruiting_news_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.60"),
        nullable=False,
        doc="Weight for recruiting news content in feed"
    )

    coaching_news_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.75"),
        nullable=False,
        doc="Weight for coaching news content in feed"
    )

    rankings_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.65"),
        nullable=False,
        doc="Weight for ranking content in feed"
    )

    tournament_news_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.90"),
        nullable=False,
        doc="Weight for tournament news content in feed"
    )

    bracket_updates_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.85"),
        nullable=False,
        doc="Weight for bracket update content in feed"
    )

    # Algorithm preferences
    recency_factor: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.30"),
        nullable=False,
        doc="How much to weight recent content (0.0 - 1.0)"
    )

    engagement_factor: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.40"),
        nullable=False,
        doc="How much to weight user engagement history (0.0 - 1.0)"
    )

    team_preference_factor: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.50"),
        nullable=False,
        doc="How much to weight team preferences (0.0 - 1.0)"
    )

    # Feed size and refresh settings
    max_items_per_refresh: Mapped[int] = mapped_column(
        Integer,
        default=50,
        nullable=False,
        doc="Maximum items to include in each feed refresh"
    )

    refresh_interval_hours: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False,
        doc="Hours between automatic feed refreshes"
    )

    # Last refresh tracking
    last_refreshed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Last time the feed was refreshed"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<PersonalizedFeed(user_id={self.user_id}, enabled={self.enabled})>"

    def get_content_weight(self, content_type: FeedContentType) -> Decimal:
        """Get the weight for a specific content type"""
        weight_mapping = {
            FeedContentType.ARTICLES: self.articles_weight,
            FeedContentType.GAME_UPDATES: self.game_updates_weight,
            FeedContentType.INJURY_REPORTS: self.injury_reports_weight,
            FeedContentType.RECRUITING_NEWS: self.recruiting_news_weight,
            FeedContentType.COACHING_NEWS: self.coaching_news_weight,
            FeedContentType.RANKINGS: self.rankings_weight,
            FeedContentType.TOURNAMENT_NEWS: self.tournament_news_weight,
            FeedContentType.BRACKET_UPDATES: self.bracket_updates_weight,
        }
        return weight_mapping.get(content_type, Decimal("0.50"))


class UserEngagementMetrics(Base, UUIDMixin, TimestampMixin):
    """
    Track user engagement metrics for personalization and analytics
    """
    __tablename__ = "user_engagement_metrics"
    __table_args__ = (
        Index('idx_engagement_user_type', 'user_id', 'metric_type'),
        Index('idx_engagement_entity', 'entity_type', 'entity_id'),
        Index('idx_engagement_timestamp', 'occurred_at'),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user"
    )

    metric_type: Mapped[EngagementMetricType] = mapped_column(
        nullable=False,
        doc="Type of engagement metric"
    )

    # Entity being interacted with
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of entity (article, team, game, etc.)"
    )

    entity_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        doc="ID of the entity being interacted with"
    )

    # Interaction details
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        doc="When the interaction occurred"
    )

    # Optional metadata about the interaction
    interaction_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        doc="Additional metadata about the interaction"
    )

    # Engagement scoring
    engagement_value: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        default=Decimal("0.0000"),
        nullable=False,
        doc="Calculated engagement value for this interaction"
    )

    # Session information
    session_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Session identifier for grouping interactions"
    )

    # Personalization context
    college_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_teams.id", ondelete="SET NULL"),
        doc="Associated college team for this interaction"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="select"
    )

    college_team: Mapped[Optional["CollegeTeam"]] = relationship(
        "CollegeTeam",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<UserEngagementMetrics(user_id={self.user_id}, type={self.metric_type}, entity={self.entity_type})>"

    @property
    def is_content_interaction(self) -> bool:
        """Check if this is a content-related interaction"""
        content_metrics = {
            EngagementMetricType.ARTICLE_VIEW,
            EngagementMetricType.ARTICLE_SHARE,
            EngagementMetricType.ARTICLE_LIKE,
        }
        return self.metric_type in content_metrics

    @property
    def is_high_value_interaction(self) -> bool:
        """Check if this is a high-value interaction for personalization"""
        return self.engagement_value >= Decimal("0.7000")


class UserPersonalizationProfile(Base, UUIDMixin, TimestampMixin):
    """
    Aggregated personalization profile for efficient feed generation
    """
    __tablename__ = "user_personalization_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Reference to the user"
    )

    # Calculated preference scores by content type
    content_type_scores: Mapped[Dict[str, float]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Calculated preference scores for different content types"
    )

    # Team affinity scores (team_id -> score)
    team_affinity_scores: Mapped[Dict[str, float]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Calculated affinity scores for teams"
    )

    # Conference affinity scores
    conference_affinity_scores: Mapped[Dict[str, float]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Calculated affinity scores for conferences"
    )

    # Time-based engagement patterns
    engagement_patterns: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Time-based engagement patterns and preferences"
    )

    # Overall engagement metrics
    total_interactions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of tracked interactions"
    )

    average_session_duration: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        doc="Average session duration in minutes"
    )

    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Last recorded interaction time"
    )

    # Profile calculation metadata
    last_calculated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Last time profile was recalculated"
    )

    calculation_version: Mapped[str] = mapped_column(
        String(20),
        default="1.0",
        nullable=False,
        doc="Version of calculation algorithm used"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<UserPersonalizationProfile(user_id={self.user_id}, interactions={self.total_interactions})>"

    def get_team_affinity(self, team_id: str) -> float:
        """Get affinity score for a specific team"""
        return self.team_affinity_scores.get(team_id, 0.0)

    def get_content_type_score(self, content_type: str) -> float:
        """Get preference score for a specific content type"""
        return self.content_type_scores.get(content_type, 0.5)

    @property
    def is_active_user(self) -> bool:
        """Check if user has sufficient engagement for personalization"""
        return self.total_interactions >= 10

    @property
    def needs_recalculation(self) -> bool:
        """Check if profile needs to be recalculated"""
        if not self.last_calculated_at:
            return True

        # Recalculate if more than 24 hours old
        hours_since_calculation = (datetime.now() - self.last_calculated_at).total_seconds() / 3600
        return hours_since_calculation > 24