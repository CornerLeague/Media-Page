"""
Sports, Leagues, and Teams models
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, Table
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

    icon_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to sport icon image for onboarding"
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Brief description of the sport for onboarding"
    )

    popularity_rank: Mapped[int] = mapped_column(
        Integer,
        default=999,
        doc="Popularity ranking for ordering in onboarding (lower = more popular)"
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

    # Enhanced metadata fields from Phase 2
    country_code: Mapped[Optional[str]] = mapped_column(
        String(3),
        doc="ISO country code for the league"
    )

    league_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        doc="League tier level (1 = top tier)"
    )

    competition_type: Mapped[str] = mapped_column(
        String(20),
        default="league",
        doc="Type of competition (league, cup, international)"
    )

    # Relationships
    sport: Mapped["Sport"] = relationship(
        "Sport",
        back_populates="leagues",
        lazy="selectin"
    )

    # Note: Direct teams relationship removed in Phase 4 - use team_memberships instead

    # Multi-league support via junction table
    team_memberships: Mapped[List["TeamLeagueMembership"]] = relationship(
        "TeamLeagueMembership",
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

    # Note: league_id column removed in Phase 4 - primary league now determined dynamically

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

    # Enhanced metadata fields from Phase 2
    official_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        doc="Official full name of the team"
    )

    short_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Short name of the team"
    )

    country_code: Mapped[Optional[str]] = mapped_column(
        String(3),
        doc="ISO country code for the team"
    )

    founding_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year the team was founded"
    )

    # Relationships
    sport: Mapped["Sport"] = relationship(
        "Sport",
        back_populates="teams",
        lazy="selectin"
    )

    # Note: Direct league relationship removed in Phase 4 - use league_memberships instead

    # Multi-league support via junction table
    league_memberships: Mapped[List["TeamLeagueMembership"]] = relationship(
        "TeamLeagueMembership",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.market} {self.name}', sport='{self.sport.name if self.sport else None}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the team"""
        return f"{self.market} {self.name}"

    @property
    def computed_short_name(self) -> str:
        """Computed short name for the team"""
        return self.short_name or self.abbreviation or self.name

    @property
    def computed_official_name(self) -> str:
        """Computed official name for the team"""
        return self.official_name or self.display_name


class TeamLeagueMembership(Base, UUIDMixin, TimestampMixin):
    """
    Junction table for team-league relationships (many-to-many)
    Supports teams playing in multiple leagues
    """
    __tablename__ = "team_league_memberships"

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    league_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the league"
    )

    season_start_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Year when team joined this league"
    )

    season_end_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year when team left this league (NULL for ongoing)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this membership is currently active"
    )

    position_last_season: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Final league position if applicable"
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="league_memberships",
        lazy="selectin"
    )

    league: Mapped["League"] = relationship(
        "League",
        back_populates="team_memberships",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<TeamLeagueMembership(team='{self.team.display_name if self.team else None}', league='{self.league.name if self.league else None}', active={self.is_active})>"

    @property
    def is_current(self) -> bool:
        """Whether this is a current membership (no end year)"""
        return self.is_active and self.season_end_year is None


class ProfessionalDivision(Base, UUIDMixin, TimestampMixin):
    """
    Professional Sports Divisions (e.g., NHL Atlantic, NFL AFC East)
    Different from college divisions (D1, D2, D3)
    """
    __tablename__ = "professional_divisions"

    league_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the league this division belongs to"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Display name of the division (e.g., 'Atlantic', 'Metropolitan')"
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="URL-friendly slug for the division"
    )

    abbreviation: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Short abbreviation for the division"
    )

    conference: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Parent conference if applicable (e.g., 'Eastern', 'Western')"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this division is currently active"
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Order for displaying divisions in UI"
    )

    # Relationships
    league: Mapped["League"] = relationship(
        "League",
        lazy="selectin"
    )

    team_divisions: Mapped[List["TeamDivisionMembership"]] = relationship(
        "TeamDivisionMembership",
        back_populates="division",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<ProfessionalDivision(id={self.id}, name='{self.name}', league='{self.league.name if self.league else None}')>"


class TeamDivisionMembership(Base, UUIDMixin, TimestampMixin):
    """
    Junction table for team-division relationships
    Links teams to their divisions within leagues
    """
    __tablename__ = "team_division_memberships"

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    division_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("professional_divisions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the division"
    )

    season_start_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Year when team joined this division"
    )

    season_end_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year when team left this division (NULL for ongoing)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this division membership is currently active"
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        lazy="selectin"
    )

    division: Mapped["ProfessionalDivision"] = relationship(
        "ProfessionalDivision",
        back_populates="team_divisions",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<TeamDivisionMembership(team='{self.team.display_name if self.team else None}', division='{self.division.name if self.division else None}', active={self.is_active})>"

    @property
    def is_current(self) -> bool:
        """Whether this is a current division membership (no end year)"""
        return self.is_active and self.season_end_year is None