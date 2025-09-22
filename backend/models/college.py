"""
College Basketball specific models
Phase 1: Foundation models for divisions, conferences, colleges, and teams
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    DivisionLevel, ConferenceType, CollegeType, Region, ConferenceStatus,
    SeasonType, SemesterType, AcademicYearStatus, ConferenceMembershipType
)


class Division(Base, UUIDMixin, TimestampMixin):
    """
    NCAA Divisions (D1, D2, D3, etc.)
    """
    __tablename__ = "divisions"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        doc="Display name of the division (e.g., 'Division I')"
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        doc="URL-friendly slug for the division"
    )

    level: Mapped[DivisionLevel] = mapped_column(
        nullable=False,
        doc="Division level enum (D1, D2, D3, etc.)"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of the division"
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
    conferences: Mapped[List["CollegeConference"]] = relationship(
        "CollegeConference",
        back_populates="division",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Division(id={self.id}, name='{self.name}', level='{self.level}')>"


class CollegeConference(Base, UUIDMixin, TimestampMixin):
    """
    College Conferences (e.g., ACC, Big Ten, SEC)
    """
    __tablename__ = "college_conferences"

    division_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("divisions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the division this conference belongs to"
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="Display name of the conference"
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="URL-friendly slug for the conference"
    )

    abbreviation: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Short abbreviation for the conference (e.g., 'ACC', 'SEC')"
    )

    conference_type: Mapped[ConferenceType] = mapped_column(
        nullable=False,
        doc="Type of conference (power_five, mid_major, etc.)"
    )

    region: Mapped[Optional[Region]] = mapped_column(
        doc="Geographic region of the conference"
    )

    founded_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year the conference was founded"
    )

    headquarters_city: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="City where conference headquarters is located"
    )

    headquarters_state: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="State where conference headquarters is located"
    )

    website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Official conference website URL"
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to the conference's logo image"
    )

    primary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Primary conference color in hex format"
    )

    secondary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Secondary conference color in hex format"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this conference is currently active"
    )

    # Basketball specific fields
    tournament_format: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Conference tournament format"
    )

    auto_bid_tournament: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether conference tournament winner gets automatic NCAA bid"
    )

    # Relationships
    division: Mapped["Division"] = relationship(
        "Division",
        back_populates="conferences",
        lazy="selectin"
    )

    colleges: Mapped[List["College"]] = relationship(
        "College",
        back_populates="conference",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_college_conferences_division_id", "division_id"),
        Index("idx_college_conferences_slug", "slug"),
        Index("idx_college_conferences_abbreviation", "abbreviation"),
        Index("idx_college_conferences_type_region", "conference_type", "region"),
        UniqueConstraint("division_id", "slug", name="uq_college_conferences_division_slug"),
    )

    def __repr__(self) -> str:
        return f"<CollegeConference(id={self.id}, name='{self.name}', type='{self.conference_type}')>"


class College(Base, UUIDMixin, TimestampMixin):
    """
    Colleges/Universities
    """
    __tablename__ = "colleges"

    conference_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the conference this college belongs to"
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Official name of the college/university"
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="URL-friendly slug for the college"
    )

    short_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Common short name of the college"
    )

    abbreviation: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Short abbreviation for the college"
    )

    college_type: Mapped[CollegeType] = mapped_column(
        nullable=False,
        doc="Type of college (public, private, etc.)"
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="City where the college is located"
    )

    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="State where the college is located"
    )

    country: Mapped[str] = mapped_column(
        String(3),
        default="USA",
        nullable=False,
        doc="Country code where the college is located"
    )

    zip_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="ZIP code of the college"
    )

    founded_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year the college was founded"
    )

    enrollment: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total student enrollment"
    )

    website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Official college website URL"
    )

    athletics_website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Official athletics website URL"
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to the college's logo image"
    )

    primary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Primary school color in hex format"
    )

    secondary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Secondary school color in hex format"
    )

    mascot: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="School mascot name"
    )

    nickname: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Athletic team nickname (e.g., 'Wildcats', 'Blue Devils')"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this college is currently active"
    )

    # Basketball specific fields
    arena_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of the basketball arena/venue"
    )

    arena_capacity: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Seating capacity of the basketball arena"
    )

    head_coach: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Current head basketball coach name"
    )

    coach_since_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Year the current coach started"
    )

    # Historical performance fields
    ncaa_championships: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of NCAA basketball championships"
    )

    final_four_appearances: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of Final Four appearances"
    )

    ncaa_tournament_appearances: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of NCAA tournament appearances"
    )

    conference_championships: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of conference championships"
    )

    # Relationships
    conference: Mapped["CollegeConference"] = relationship(
        "CollegeConference",
        back_populates="colleges",
        lazy="selectin"
    )

    teams: Mapped[List["CollegeTeam"]] = relationship(
        "CollegeTeam",
        back_populates="college",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Phase 2: Conference membership history
    conference_memberships: Mapped[List["ConferenceMembership"]] = relationship(
        "ConferenceMembership",
        back_populates="college",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="ConferenceMembership.start_date.desc()"
    )

    # Indexes
    __table_args__ = (
        Index("idx_colleges_conference_id", "conference_id"),
        Index("idx_colleges_slug", "slug"),
        Index("idx_colleges_state_city", "state", "city"),
        Index("idx_colleges_name_search", "name"),
        Index("idx_colleges_nickname", "nickname"),
        UniqueConstraint("conference_id", "slug", name="uq_colleges_conference_slug"),
    )

    def __repr__(self) -> str:
        return f"<College(id={self.id}, name='{self.name}', state='{self.state}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the college"""
        return self.short_name or self.name

    @property
    def location(self) -> str:
        """Formatted location string"""
        return f"{self.city}, {self.state}"


class CollegeTeam(Base, UUIDMixin, TimestampMixin):
    """
    College Basketball Teams
    Links colleges to the sports system
    """
    __tablename__ = "college_teams"

    college_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the college this team represents"
    )

    sport_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the sport (should be 'college-basketball')"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Team name (usually the college nickname)"
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="URL-friendly slug for the team"
    )

    abbreviation: Mapped[Optional[str]] = mapped_column(
        String(10),
        doc="Short team abbreviation"
    )

    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External API identifier for this team"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this team is currently active"
    )

    # Current season information
    current_record_wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current season wins"
    )

    current_record_losses: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current season losses"
    )

    conference_record_wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current conference record wins"
    )

    conference_record_losses: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current conference record losses"
    )

    # Rankings
    ap_poll_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current AP Poll ranking (1-25, NULL if unranked)"
    )

    coaches_poll_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current Coaches Poll ranking (1-25, NULL if unranked)"
    )

    net_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current NET ranking"
    )

    kenpom_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current KenPom ranking"
    )

    rpi_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Current RPI ranking"
    )

    # Relationships
    college: Mapped["College"] = relationship(
        "College",
        back_populates="teams",
        lazy="selectin"
    )

    # Note: Sport relationship will be available through imports
    # sport: Mapped["Sport"] = relationship(
    #     "Sport",
    #     lazy="selectin"
    # )

    # Indexes
    __table_args__ = (
        Index("idx_college_teams_college_id", "college_id"),
        Index("idx_college_teams_sport_id", "sport_id"),
        Index("idx_college_teams_slug", "slug"),
        Index("idx_college_teams_external_id", "external_id"),
        Index("idx_college_teams_rankings", "ap_poll_rank", "coaches_poll_rank"),
        UniqueConstraint("college_id", "sport_id", name="uq_college_teams_college_sport"),
        UniqueConstraint("slug", name="uq_college_teams_slug"),
    )

    def __repr__(self) -> str:
        return f"<CollegeTeam(id={self.id}, name='{self.name}', college='{self.college.name if self.college else None}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the team"""
        if self.college:
            return f"{self.college.display_name} {self.name}"
        return self.name

    @property
    def overall_record(self) -> str:
        """Formatted overall record string"""
        return f"{self.current_record_wins}-{self.current_record_losses}"

    @property
    def conference_record(self) -> str:
        """Formatted conference record string"""
        return f"{self.conference_record_wins}-{self.conference_record_losses}"

    @property
    def is_ranked(self) -> bool:
        """Whether the team is currently ranked in major polls"""
        return (self.ap_poll_rank is not None and self.ap_poll_rank <= 25) or \
               (self.coaches_poll_rank is not None and self.coaches_poll_rank <= 25)


# =============================================================================
# Phase 2: Academic Framework Models
# =============================================================================

class AcademicYear(Base, UUIDMixin, TimestampMixin):
    """
    Academic years (e.g., 2024-25, 2025-26)
    Represents the overarching academic year that contains multiple seasons
    """
    __tablename__ = "academic_years"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        doc="Display name of the academic year (e.g., '2024-25')"
    )

    slug: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        doc="URL-friendly slug for the academic year"
    )

    start_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Starting year of the academic year (e.g., 2024 for '2024-25')"
    )

    end_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Ending year of the academic year (e.g., 2025 for '2024-25')"
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Official start date of the academic year"
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Official end date of the academic year"
    )

    status: Mapped[AcademicYearStatus] = mapped_column(
        nullable=False,
        default=AcademicYearStatus.FUTURE,
        doc="Status of this academic year"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this academic year is active"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description or notes about this academic year"
    )

    # Relationships
    seasons: Mapped[List["Season"]] = relationship(
        "Season",
        back_populates="academic_year",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Season.start_date"
    )

    conference_memberships: Mapped[List["ConferenceMembership"]] = relationship(
        "ConferenceMembership",
        back_populates="academic_year",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_academic_years_start_year", "start_year"),
        Index("idx_academic_years_status", "status"),
        Index("idx_academic_years_dates", "start_date", "end_date"),
        Index("idx_academic_years_slug", "slug"),
    )

    def __repr__(self) -> str:
        return f"<AcademicYear(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def is_current(self) -> bool:
        """Whether this is the current academic year"""
        return self.status == AcademicYearStatus.CURRENT

    @property
    def display_years(self) -> str:
        """Formatted display of years (e.g., '2024-25')"""
        return f"{self.start_year}-{str(self.end_year)[-2:]}"


class Season(Base, UUIDMixin, TimestampMixin):
    """
    Individual seasons within an academic year
    (e.g., Regular Season, Conference Tournament, NCAA Tournament)
    """
    __tablename__ = "seasons"

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year this season belongs to"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Display name of the season (e.g., 'Regular Season 2024-25')"
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="URL-friendly slug for the season"
    )

    season_type: Mapped[SeasonType] = mapped_column(
        nullable=False,
        doc="Type of season (regular_season, postseason, etc.)"
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Official start date of the season"
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Official end date of the season"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this season is active"
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is the current active season"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of the season"
    )

    # Season specific settings
    max_regular_season_games: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Maximum number of regular season games allowed"
    )

    conference_tournament_start: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Start date of conference tournaments"
    )

    selection_sunday: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of NCAA tournament selection announcement"
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        back_populates="seasons",
        lazy="selectin"
    )

    season_configurations: Mapped[List["SeasonConfiguration"]] = relationship(
        "SeasonConfiguration",
        back_populates="season",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_seasons_academic_year_id", "academic_year_id"),
        Index("idx_seasons_type", "season_type"),
        Index("idx_seasons_dates", "start_date", "end_date"),
        Index("idx_seasons_slug", "slug"),
        Index("idx_seasons_current", "is_current"),
        UniqueConstraint("academic_year_id", "slug", name="uq_seasons_academic_year_slug"),
        UniqueConstraint("academic_year_id", "season_type", name="uq_seasons_academic_year_type"),
    )

    def __repr__(self) -> str:
        return f"<Season(id={self.id}, name='{self.name}', type='{self.season_type}')>"

    @property
    def display_name(self) -> str:
        """Full display name for the season"""
        if self.academic_year:
            return f"{self.name} ({self.academic_year.name})"
        return self.name


class ConferenceMembership(Base, UUIDMixin, TimestampMixin):
    """
    Historical tracking of team conference membership
    Supports conference realignment scenarios
    """
    __tablename__ = "conference_memberships"

    college_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the college"
    )

    conference_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the conference"
    )

    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    membership_type: Mapped[ConferenceMembershipType] = mapped_column(
        nullable=False,
        default=ConferenceMembershipType.FULL_MEMBER,
        doc="Type of conference membership"
    )

    status: Mapped[ConferenceStatus] = mapped_column(
        nullable=False,
        default=ConferenceStatus.ACTIVE,
        doc="Status of the membership"
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date when membership started"
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when membership ended (NULL if still active)"
    )

    announced_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when the membership change was announced"
    )

    is_primary_sport: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is for the primary sport (basketball)"
    )

    sport_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        doc="Reference to specific sport (if not all sports)"
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes about the membership"
    )

    # Relationships
    college: Mapped["College"] = relationship(
        "College",
        lazy="selectin"
    )

    conference: Mapped["CollegeConference"] = relationship(
        "CollegeConference",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        back_populates="conference_memberships",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_conference_memberships_college_id", "college_id"),
        Index("idx_conference_memberships_conference_id", "conference_id"),
        Index("idx_conference_memberships_academic_year_id", "academic_year_id"),
        Index("idx_conference_memberships_status", "status"),
        Index("idx_conference_memberships_dates", "start_date", "end_date"),
        Index("idx_conference_memberships_primary_sport", "is_primary_sport"),
        UniqueConstraint(
            "college_id", "conference_id", "academic_year_id", "sport_id",
            name="uq_conference_memberships_college_conference_year_sport"
        ),
    )

    def __repr__(self) -> str:
        return f"<ConferenceMembership(college={self.college.name if self.college else None}, conference={self.conference.name if self.conference else None}, year={self.academic_year.name if self.academic_year else None})>"

    @property
    def is_active(self) -> bool:
        """Whether this membership is currently active"""
        return self.status == ConferenceStatus.ACTIVE and self.end_date is None

    @property
    def duration_days(self) -> Optional[int]:
        """Duration of membership in days"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None


class SeasonConfiguration(Base, UUIDMixin, TimestampMixin):
    """
    Season-specific configuration and settings
    Allows for different rules and settings per season
    """
    __tablename__ = "season_configurations"

    season_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the season"
    )

    conference_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("college_conferences.id", ondelete="CASCADE"),
        doc="Reference to specific conference (NULL for global settings)"
    )

    setting_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Configuration setting key"
    )

    setting_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Configuration setting value (JSON string for complex values)"
    )

    setting_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="string",
        doc="Type of the setting value (string, integer, boolean, json)"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of what this setting controls"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this configuration is active"
    )

    # Relationships
    season: Mapped["Season"] = relationship(
        "Season",
        back_populates="season_configurations",
        lazy="selectin"
    )

    conference: Mapped[Optional["CollegeConference"]] = relationship(
        "CollegeConference",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_season_configurations_season_id", "season_id"),
        Index("idx_season_configurations_conference_id", "conference_id"),
        Index("idx_season_configurations_key", "setting_key"),
        Index("idx_season_configurations_active", "is_active"),
        UniqueConstraint(
            "season_id", "conference_id", "setting_key",
            name="uq_season_configurations_season_conference_key"
        ),
    )

    def __repr__(self) -> str:
        return f"<SeasonConfiguration(season={self.season.name if self.season else None}, key='{self.setting_key}', value='{self.setting_value[:50]}...')>"

    @property
    def parsed_value(self):
        """Parse the setting value based on its type"""
        if self.setting_type == "boolean":
            return self.setting_value.lower() in ("true", "1", "yes")
        elif self.setting_type == "integer":
            try:
                return int(self.setting_value)
            except ValueError:
                return None
        elif self.setting_type == "json":
            try:
                import json
                return json.loads(self.setting_value)
            except (json.JSONDecodeError, ImportError):
                return None
        else:
            return self.setting_value