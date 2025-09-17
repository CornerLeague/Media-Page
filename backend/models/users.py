"""
User models for authentication and preferences
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import ContentFrequency, NewsType


class User(Base, UUIDMixin, TimestampMixin):
    """
    Users table - extends Clerk authentication
    """
    __tablename__ = "users"

    clerk_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        doc="Clerk authentication user ID"
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="User's email address"
    )

    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="User's display name"
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to user's avatar image"
    )

    content_frequency: Mapped[ContentFrequency] = mapped_column(
        default=ContentFrequency.STANDARD,
        doc="User's preferred content frequency"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active"
    )

    onboarding_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp when user completed onboarding"
    )

    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        doc="Timestamp of user's last activity"
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
        return f"<User(id={self.id}, clerk_id='{self.clerk_user_id}', display_name='{self.display_name}')>"

    @property
    def is_onboarded(self) -> bool:
        """Check if user has completed onboarding"""
        return self.onboarding_completed_at is not None


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