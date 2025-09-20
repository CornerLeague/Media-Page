"""
Sports, Leagues, and Teams models
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class Sport(Base, UUIDMixin, TimestampMixin):
    """
    Sports table (e.g., Basketball, Football, Baseball)
    """
    __tablename__ = "sports"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        doc="Display name of the sport"
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        doc="URL-friendly slug for the sport"
    )

    has_teams: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this sport has team-based competition"
    )

    icon: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="Icon identifier or URL for the sport"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this sport is currently active in the system"
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Order for displaying sports in UI"
    )

    # Relationships
    leagues: Mapped[List["League"]] = relationship(
        "League",
        back_populates="sport",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    teams: Mapped[List["Team"]] = relationship(
        "Team",
        back_populates="sport",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Sport(id={self.id}, name='{self.name}', has_teams={self.has_teams})>"


class League(Base, UUIDMixin, TimestampMixin):
    """
    Leagues table (e.g., NFL, NBA, MLB)
    """
    __tablename__ = "leagues"

    sport_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the sport this league belongs to"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Display name of the league"
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="URL-friendly slug for the league"
    )

    abbreviation: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Short abbreviation for the league (e.g., NFL, NBA)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this league is currently active"
    )

    season_start_month: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Month when the season typically starts (1-12)"
    )

    season_end_month: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Month when the season typically ends (1-12)"
    )

    # Relationships
    sport: Mapped["Sport"] = relationship(
        "Sport",
        back_populates="leagues",
        lazy="selectin"
    )

    teams: Mapped[List["Team"]] = relationship(
        "Team",
        back_populates="league",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<League(id={self.id}, name='{self.name}', sport='{self.sport.name if self.sport else None}')>"


class Team(Base, UUIDMixin, TimestampMixin):
    """
    Teams table
    """
    __tablename__ = "teams"

    sport_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the sport this team plays"
    )

    league_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the league this team belongs to"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Team name (e.g., 'Patriots', 'Lakers')"
    )

    market: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="City or region the team represents"
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="URL-friendly slug for the team"
    )

    abbreviation: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Short team abbreviation (e.g., 'NE', 'LAL')"
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to the team's logo image"
    )

    primary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Primary team color in hex format"
    )

    secondary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Secondary team color in hex format"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this team is currently active"
    )

    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this team"
    )

    # Relationships
    sport: Mapped["Sport"] = relationship(
        "Sport",
        back_populates="teams",
        lazy="selectin"
    )

    league: Mapped["League"] = relationship(
        "League",
        back_populates="teams",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.market} {self.name}', league='{self.league.name if self.league else None}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the team"""
        return f"{self.market} {self.name}"

    @property
    def short_name(self) -> str:
        """Short name for the team"""
        return self.abbreviation or self.name