"""
User models for authentication and preferences
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Date, Integer, Numeric, String, ForeignKey, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import ContentFrequency, NewsType


class User(Base, UUIDMixin, TimestampMixin):
    """
    Users table - Firebase authentication integration
    """
    __tablename__ = "users"

    firebase_uid: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="Firebase authentication user ID"
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        index=True,
        doc="User's email address"
    )

    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="User's display name"
    )

    first_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="User's first name"
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="User's last name"
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to user's avatar image"
    )

    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="User's biographical information"
    )

    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="User's date of birth"
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="User's location (city, state)"
    )

    timezone: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="UTC",
        doc="User's preferred timezone"
    )

    content_frequency: Mapped[ContentFrequency] = mapped_column(
        default=ContentFrequency.STANDARD,
        doc="User's preferred content frequency"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Whether the user account is active"
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user's email is verified"
    )

    onboarding_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp when user completed onboarding"
    )

    current_onboarding_step: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current step in onboarding process (1-5, null when completed)"
    )

    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        index=True,
        doc="Timestamp of user's last activity"
    )

    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp when email was verified"
    )

    # Relationships
    sport_preferences: Mapped[List["UserSportPreference"]] = relationship(
        "UserSportPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    team_preferences: Mapped[List["UserTeamPreference"]] = relationship(
        "UserTeamPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    news_preferences: Mapped[List["UserNewsPreference"]] = relationship(
        "UserNewsPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    notification_settings: Mapped[Optional["UserNotificationSettings"]] = relationship(
        "UserNotificationSettings",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, firebase_uid='{self.firebase_uid}', display_name='{self.display_name}')>"

    @property
    def is_onboarded(self) -> bool:
        """Check if user has completed onboarding"""
        return self.onboarding_completed_at is not None

    @property
    def full_name(self) -> Optional[str]:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name

    @property
    def display_identifier(self) -> str:
        """Get the best identifier to display for the user"""
        return self.display_name or self.full_name or self.email or f"User {self.id}"


class UserSportPreference(Base, UUIDMixin, TimestampMixin):
    """
    User sport preferences with ranking
    """
    __tablename__ = "user_sport_preferences"
    __table_args__ = (
        UniqueConstraint('user_id', 'sport_id', name='uq_user_sport'),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user"
    )

    sport_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the sport"
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="User's ranking of this sport (1 = most preferred)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this preference is currently active"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sport_preferences",
        lazy="select"
    )

    sport: Mapped["Sport"] = relationship(
        "Sport",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<UserSportPreference(user_id={self.user_id}, sport_id={self.sport_id}, rank={self.rank})>"


class UserTeamPreference(Base, UUIDMixin, TimestampMixin):
    """
    User team preferences with affinity scores
    """
    __tablename__ = "user_team_preferences"
    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='uq_user_team'),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    affinity_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.5"),
        nullable=False,
        doc="User's affinity score for this team (0.0 to 1.0)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this preference is currently active"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="team_preferences",
        lazy="select"
    )

    team: Mapped["Team"] = relationship(
        "Team",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<UserTeamPreference(user_id={self.user_id}, team_id={self.team_id}, affinity={self.affinity_score})>"


class UserNewsPreference(Base, UUIDMixin, TimestampMixin):
    """
    User news type preferences
    """
    __tablename__ = "user_news_preferences"
    __table_args__ = (
        UniqueConstraint('user_id', 'news_type', name='uq_user_news_type'),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user"
    )

    news_type: Mapped[NewsType] = mapped_column(
        nullable=False,
        doc="Type of news content"
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this news type is enabled for the user"
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        doc="Priority level for this news type"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="news_preferences",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<UserNewsPreference(user_id={self.user_id}, news_type={self.news_type}, enabled={self.enabled})>"


class UserNotificationSettings(Base, UUIDMixin, TimestampMixin):
    """
    User notification preferences
    """
    __tablename__ = "user_notification_settings"

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Reference to the user"
    )

    push_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether push notifications are enabled"
    )

    email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether email notifications are enabled"
    )

    game_reminders: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether to send game reminder notifications"
    )

    news_alerts: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether to send breaking news alerts"
    )

    score_updates: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether to send live score updates"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notification_settings",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<UserNotificationSettings(user_id={self.user_id}, push={self.push_enabled}, email={self.email_enabled})>"