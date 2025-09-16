"""User-related SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .enums import UserRole, UserStatus


class User(BaseModel):
    """User model for authentication and preferences."""

    __tablename__ = "users"

    # Clerk integration
    clerk_user_id: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
        doc="Clerk user ID for authentication"
    )

    # Basic user information
    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
        doc="User email address"
    )

    username: Mapped[Optional[str]] = mapped_column(
        Text,
        unique=True,
        nullable=True,
        doc="Unique username"
    )

    first_name: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User first name"
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User last name"
    )

    image_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Profile image URL"
    )

    # User state
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name='user_role'),
        default=UserRole.USER,
        nullable=False,
        doc="User role"
    )

    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name='user_status'),
        default=UserStatus.ACTIVE,
        nullable=False,
        index=True,
        doc="User account status"
    )

    # User preferences stored as JSONB
    preferences: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "email_notifications": True,
            "push_notifications": True,
            "favorite_sports": [],
            "content_categories": [],
            "ai_summary_enabled": True
        },
        doc="User preferences as JSON"
    )

    # Activity tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last login timestamp"
    )

    # Relationships
    team_relationships: Mapped[List["UserTeam"]] = relationship(
        "UserTeam",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User's team relationships"
    )

    preference_history: Mapped[List["UserPreferenceHistory"]] = relationship(
        "UserPreferenceHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User preference change history"
    )

    search_analytics: Mapped[List["SearchAnalytics"]] = relationship(
        "SearchAnalytics",
        back_populates="user",
        doc="User's search activity"
    )

    sport_prefs: Mapped[List["UserSportPref"]] = relationship(
        "UserSportPref",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User's sport preferences with ranking"
    )

    @property
    def full_name(self) -> Optional[str]:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name

    @property
    def favorite_team_ids(self) -> List[str]:
        """Get list of favorite team IDs from preferences."""
        return self.preferences.get("favorite_teams", [])

    @property
    def favorite_sports(self) -> List[str]:
        """Get list of favorite sports from preferences."""
        return self.preferences.get("favorite_sports", [])

    def update_preferences(self, new_preferences: dict) -> None:
        """Update user preferences and track changes."""
        old_preferences = self.preferences.copy()
        self.preferences = {**self.preferences, **new_preferences}

        # Find changed fields
        changed_fields = []
        for key, value in new_preferences.items():
            if old_preferences.get(key) != value:
                changed_fields.append(key)

        return old_preferences, changed_fields

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def is_moderator(self) -> bool:
        """Check if user is a moderator or admin."""
        return self.role in (UserRole.ADMIN, UserRole.MODERATOR)

    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE


class UserTeam(BaseModel):
    """Many-to-many relationship between users and teams."""

    __tablename__ = "user_teams"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User ID"
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Team ID"
    )

    # Relationship metadata
    followed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="When user started following team"
    )

    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether notifications are enabled for this team"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="team_relationships",
        doc="User who follows the team"
    )

    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="user_relationships",
        doc="Team being followed"
    )

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='uq_user_team'),
    )


class UserPreferenceHistory(BaseModel):
    """Track changes to user preferences for analytics and rollback."""

    __tablename__ = "user_preference_history"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User ID"
    )

    # Preference data
    old_preferences: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Previous preferences"
    )

    new_preferences: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        doc="New preferences"
    )

    changed_fields: Mapped[List[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        doc="List of changed preference fields"
    )

    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="preference_history",
        doc="User whose preferences changed"
    )