"""
Fan experiences and user registrations models
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import ExperienceType


class FanExperience(Base, UUIDMixin, TimestampMixin):
    """
    Fan experiences and events
    """
    __tablename__ = "fan_experiences"
    __table_args__ = (
        CheckConstraint('current_attendees <= max_attendees', name='check_valid_attendee_count'),
        CheckConstraint('price >= 0', name='check_valid_price'),
    )

    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        doc="Reference to the team (if team-specific experience)"
    )

    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        doc="Reference to the game (if game-specific experience)"
    )

    sport_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        doc="Reference to the sport (if sport-specific experience)"
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Title of the fan experience"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Detailed description of the experience"
    )

    experience_type: Mapped[ExperienceType] = mapped_column(
        nullable=False,
        doc="Type of fan experience"
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="When the experience starts"
    )

    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When the experience ends"
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Location of the experience"
    )

    organizer: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="Who is organizing the experience"
    )

    max_attendees: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Maximum number of attendees allowed"
    )

    current_attendees: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Current number of registered attendees"
    )

    price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        doc="Price to attend the experience"
    )

    external_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        doc="External URL for more information or registration"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this experience is currently active"
    )

    # Relationships
    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        lazy="selectin"
    )

    game: Mapped[Optional["Game"]] = relationship(
        "Game",
        lazy="selectin"
    )

    sport: Mapped[Optional["Sport"]] = relationship(
        "Sport",
        lazy="selectin"
    )

    registrations: Mapped[list["UserExperienceRegistration"]] = relationship(
        "UserExperienceRegistration",
        back_populates="experience",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FanExperience(id={self.id}, title='{self.title}', type={self.experience_type}, start_time={self.start_time})>"

    @property
    def is_full(self) -> bool:
        """Check if the experience is at capacity"""
        if not self.max_attendees:
            return False
        return self.current_attendees >= self.max_attendees

    @property
    def has_started(self) -> bool:
        """Check if the experience has started"""
        return datetime.now() >= self.start_time

    @property
    def has_ended(self) -> bool:
        """Check if the experience has ended"""
        if not self.end_time:
            return False
        return datetime.now() >= self.end_time

    @property
    def is_upcoming(self) -> bool:
        """Check if the experience is upcoming"""
        return not self.has_started

    @property
    def spots_remaining(self) -> Optional[int]:
        """Get number of spots remaining"""
        if not self.max_attendees:
            return None
        return max(0, self.max_attendees - self.current_attendees)

    @property
    def type_display(self) -> str:
        """Get display name for experience type"""
        type_map = {
            ExperienceType.WATCH_PARTY: "Watch Party",
            ExperienceType.TAILGATE: "Tailgate",
            ExperienceType.VIEWING: "Viewing Party",
            ExperienceType.MEETUP: "Fan Meetup"
        }
        return type_map.get(self.experience_type, self.experience_type.value)


class UserExperienceRegistration(Base, UUIDMixin):
    """
    User registrations for fan experiences
    """
    __tablename__ = "user_experience_registrations"
    __table_args__ = (
        UniqueConstraint('user_id', 'experience_id', name='uq_user_experience'),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user"
    )

    experience_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("fan_experiences.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the fan experience"
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        doc="Timestamp when user registered"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="registered",
        doc="Registration status (registered, attended, cancelled)"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )

    experience: Mapped["FanExperience"] = relationship(
        "FanExperience",
        back_populates="registrations",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<UserExperienceRegistration(user_id={self.user_id}, experience_id={self.experience_id}, status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if registration is active"""
        return self.status == "registered"

    @property
    def is_cancelled(self) -> bool:
        """Check if registration was cancelled"""
        return self.status == "cancelled"

    @property
    def did_attend(self) -> bool:
        """Check if user attended the experience"""
        return self.status == "attended"