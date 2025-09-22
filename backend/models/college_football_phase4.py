"""
College Football Phase 4: Recruiting and Transfer Portal Integration
Extends existing College Football Phase 1-3 foundation with comprehensive recruiting,
transfer portal, coaching staff, and NIL deal tracking
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint, Index, Date, DateTime, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    # Existing enums
    FootballPosition, FootballPositionGroup, ScholarshipType,
    PlayerEligibilityStatus, PlayerClass,

    # New Phase 4 enums
    RecruitingStarRating, RecruitingStatus, CommitmentStatus,
    VisitType, TransferReason, TransferStatus, EligibilityType,
    CoachingPosition, CoachingLevel, ContractStatus,
    NILDealType, NILCategory, ComplianceStatus,
    PortalEntryReason, RecruitingPeriod, SigningPeriod
)


# =============================================================================
# Recruiting Class Models
# =============================================================================

class FootballRecruitingClass(Base, UUIDMixin, TimestampMixin):
    """
    Annual football recruiting class with rankings and composition tracking
    Manages the complex 85-scholarship limit and position-specific needs
    """
    __tablename__ = "football_recruiting_classes"

    # Team association
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football team"
    )

    # Academic context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Class identification
    class_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="High school graduation year (e.g., 2024)"
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Recruiting class name (e.g., 'Class of 2024')"
    )

    # Signing periods tracking
    early_signing_period_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of commits during early signing period"
    )

    regular_signing_period_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of commits during regular signing period"
    )

    late_period_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of late period commits"
    )

    # Scholarship distribution
    full_scholarships_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of full scholarships awarded"
    )

    partial_scholarships_used: Mapped[Decimal] = mapped_column(
        Numeric(5, 3),
        default=0,
        nullable=False,
        doc="Total partial scholarship count (can be fractional)"
    )

    total_scholarship_count: Mapped[Decimal] = mapped_column(
        Numeric(5, 3),
        default=0,
        nullable=False,
        doc="Total scholarship count towards 85 limit"
    )

    # Class composition by position group
    offensive_line_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quarterback_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    running_back_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wide_receiver_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tight_end_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defensive_line_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    linebacker_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defensive_back_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    special_teams_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Geographic distribution
    in_state_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of in-state commits"
    )

    out_of_state_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of out-of-state commits"
    )

    international_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of international commits"
    )

    # Transfer additions
    transfer_additions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of transfer portal additions"
    )

    graduate_transfer_additions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of graduate transfer additions"
    )

    # Class rankings and metrics
    national_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="National recruiting class ranking"
    )

    conference_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Conference recruiting class ranking"
    )

    class_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3),
        doc="Composite class rating/score"
    )

    average_star_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Average star rating of commits"
    )

    # Quality metrics
    five_star_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    four_star_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    three_star_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    two_star_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unrated_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Top prospects
    top_100_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of top 100 national recruits"
    )

    top_300_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of top 300 national recruits"
    )

    # Class status
    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether recruiting class is considered complete"
    )

    completion_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when class was completed"
    )

    # Early enrollees
    early_enrollees: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of early enrollees (January enrollment)"
    )

    # Attrition tracking
    decommitments: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of decommitments from this class"
    )

    signings_not_qualified: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of signees who did not qualify academically"
    )

    # Notes and analysis
    class_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notes about the recruiting class"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    recruits: Mapped[List["FootballRecruit"]] = relationship(
        "FootballRecruit",
        back_populates="recruiting_class",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_recruiting_classes_team_id", "team_id"),
        Index("idx_football_recruiting_classes_academic_year_id", "academic_year_id"),
        Index("idx_football_recruiting_classes_class_year", "class_year"),
        Index("idx_football_recruiting_classes_team_year", "team_id", "class_year"),
        Index("idx_football_recruiting_classes_ranking", "national_ranking"),
        Index("idx_football_recruiting_classes_complete", "is_complete"),
        UniqueConstraint("team_id", "class_year", name="uq_football_recruiting_classes_team_year"),
    )

    def __repr__(self) -> str:
        return f"<FootballRecruitingClass(team='{self.team.display_name if self.team else None}', year={self.class_year})>"

    @property
    def total_commits(self) -> int:
        """Total number of commits in the class"""
        return (self.early_signing_period_commits +
                self.regular_signing_period_commits +
                self.late_period_commits)

    @property
    def scholarships_remaining(self) -> Decimal:
        """Scholarships remaining towards 85 limit"""
        return Decimal('85.0') - self.total_scholarship_count

    @property
    def class_quality_score(self) -> Optional[Decimal]:
        """Calculate quality score based on star distribution"""
        if self.total_commits == 0:
            return None

        total_points = (
            self.five_star_commits * 5 +
            self.four_star_commits * 4 +
            self.three_star_commits * 3 +
            self.two_star_commits * 2 +
            self.unrated_commits * 1
        )
        return Decimal(total_points) / Decimal(self.total_commits)


# =============================================================================
# Individual Recruit Models
# =============================================================================

class FootballRecruit(Base, UUIDMixin, TimestampMixin):
    """
    Individual football recruit with comprehensive tracking
    Manages the complex recruiting process from initial contact to enrollment
    """
    __tablename__ = "football_recruits"

    # Recruiting class association
    recruiting_class_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_recruiting_classes.id", ondelete="SET NULL"),
        doc="Reference to recruiting class (if committed)"
    )

    # Basic information
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Recruit's first name"
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Recruit's last name"
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Recruit's full name"
    )

    # High school information
    high_school: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="High school name"
    )

    high_school_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="High school city"
    )

    high_school_state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="High school state"
    )

    high_school_country: Mapped[str] = mapped_column(
        String(50),
        default="USA",
        nullable=False,
        doc="High school country"
    )

    graduation_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="High school graduation year"
    )

    # Position information
    primary_position: Mapped[FootballPosition] = mapped_column(
        nullable=False,
        doc="Primary football position"
    )

    secondary_position: Mapped[Optional[FootballPosition]] = mapped_column(
        doc="Secondary position (if applicable)"
    )

    position_group: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Position group for recruiting purposes"
    )

    # Physical attributes
    height_inches: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Height in total inches"
    )

    weight_pounds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Weight in pounds"
    )

    # Performance metrics
    forty_yard_dash: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        doc="40-yard dash time"
    )

    bench_press: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Bench press reps at 225 lbs"
    )

    vertical_jump: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        doc="Vertical jump in inches"
    )

    # Recruiting ratings and rankings
    composite_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        doc="Composite recruiting rating"
    )

    star_rating: Mapped[Optional[RecruitingStarRating]] = mapped_column(
        doc="Star rating (2-5 stars)"
    )

    national_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="National ranking among all recruits"
    )

    position_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Ranking within position group"
    )

    state_ranking: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Ranking within home state"
    )

    # Commitment status
    commitment_status: Mapped[CommitmentStatus] = mapped_column(
        nullable=False,
        default=CommitmentStatus.UNCOMMITTED,
        doc="Current commitment status"
    )

    committed_to_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="Team committed to (if committed)"
    )

    commitment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of commitment"
    )

    signing_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of signing (NLI)"
    )

    enrollment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Expected/actual enrollment date"
    )

    # Early enrollment
    is_early_enrollee: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether recruit is early enrollee (January)"
    )

    early_enrollment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Early enrollment date"
    )

    # Decommitment tracking
    decommitment_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of times recruit has decommitted"
    )

    last_decommitment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of most recent decommitment"
    )

    # Academic information
    academic_eligibility_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        doc="Academic eligibility status"
    )

    clearinghouse_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="NCAA Clearinghouse status"
    )

    core_gpa: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Core course GPA"
    )

    sat_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="SAT test score"
    )

    act_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="ACT test score"
    )

    # Scholarship information
    scholarship_offered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether scholarship has been offered"
    )

    scholarship_type: Mapped[Optional[ScholarshipType]] = mapped_column(
        doc="Type of scholarship offered"
    )

    scholarship_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Scholarship percentage offered"
    )

    # Other college programs pursuing
    total_offers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of scholarship offers"
    )

    top_schools: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON array of top schools being considered"
    )

    # Recruiting timeline
    first_contact_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of first contact from program"
    )

    first_offer_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of first scholarship offer"
    )

    official_visit_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of official visit"
    )

    # Visit tracking
    official_visits_taken: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of official visits taken"
    )

    unofficial_visits_taken: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of unofficial visits taken"
    )

    # Parent/guardian information
    parent_contact: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Parent/guardian contact information"
    )

    family_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notes about family situation"
    )

    # Social media and contact
    twitter_handle: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Twitter/X handle"
    )

    instagram_handle: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Instagram handle"
    )

    # Film and highlights
    hudl_profile: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Hudl profile URL"
    )

    highlight_film_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Highlight film URL"
    )

    # Additional recruiting factors
    recruiting_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Recruiting notes and observations"
    )

    character_concerns: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Any character or behavioral concerns"
    )

    injury_history: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Known injury history"
    )

    # External identifiers
    rivals_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Rivals.com recruit ID"
    )

    two_four_seven_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="247Sports recruit ID"
    )

    espn_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="ESPN recruit ID"
    )

    on3_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="On3 recruit ID"
    )

    # Status tracking
    is_active_recruit: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is an active recruiting target"
    )

    recruiting_priority: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Recruiting priority level (high, medium, low)"
    )

    # Relationships
    recruiting_class: Mapped[Optional["FootballRecruitingClass"]] = relationship(
        "FootballRecruitingClass",
        back_populates="recruits",
        lazy="selectin"
    )

    committed_to_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    visits: Mapped[List["FootballRecruitingVisit"]] = relationship(
        "FootballRecruitingVisit",
        back_populates="recruit",
        cascade="all, delete-orphan",
        lazy="select"
    )

    offers: Mapped[List["FootballRecruitingOffer"]] = relationship(
        "FootballRecruitingOffer",
        back_populates="recruit",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_recruits_recruiting_class_id", "recruiting_class_id"),
        Index("idx_football_recruits_full_name", "full_name"),
        Index("idx_football_recruits_last_name", "last_name"),
        Index("idx_football_recruits_graduation_year", "graduation_year"),
        Index("idx_football_recruits_position", "primary_position"),
        Index("idx_football_recruits_position_group", "position_group"),
        Index("idx_football_recruits_state", "high_school_state"),
        Index("idx_football_recruits_commitment", "commitment_status"),
        Index("idx_football_recruits_committed_team", "committed_to_team_id"),
        Index("idx_football_recruits_star_rating", "star_rating"),
        Index("idx_football_recruits_rankings", "national_ranking", "position_ranking"),
        Index("idx_football_recruits_active", "is_active_recruit"),
        Index("idx_football_recruits_graduation_position", "graduation_year", "position_group"),
    )

    def __repr__(self) -> str:
        return f"<FootballRecruit(name='{self.full_name}', position='{self.primary_position}', class={self.graduation_year})>"

    @property
    def height_display(self) -> Optional[str]:
        """Display height in feet and inches"""
        if self.height_inches:
            feet = self.height_inches // 12
            inches = self.height_inches % 12
            return f"{feet}'{inches}\""
        return None

    @property
    def is_committed(self) -> bool:
        """Check if recruit is committed"""
        return self.commitment_status in [CommitmentStatus.COMMITTED, CommitmentStatus.SIGNED]

    @property
    def is_signed(self) -> bool:
        """Check if recruit has signed NLI"""
        return self.commitment_status == CommitmentStatus.SIGNED

    @property
    def commitment_status_display(self) -> str:
        """Display-friendly commitment status"""
        if self.is_signed:
            return f"Signed with {self.committed_to_team.display_name if self.committed_to_team else 'Unknown'}"
        elif self.is_committed:
            return f"Committed to {self.committed_to_team.display_name if self.committed_to_team else 'Unknown'}"
        else:
            return "Uncommitted"


# =============================================================================
# Recruiting Offer and Visit Tracking
# =============================================================================

class FootballRecruitingOffer(Base, UUIDMixin, TimestampMixin):
    """
    Scholarship offers extended to recruits
    """
    __tablename__ = "football_recruiting_offers"

    # References
    recruit_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_recruits.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the recruit"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Team extending the offer"
    )

    # Offer details
    offer_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date offer was extended"
    )

    scholarship_type: Mapped[ScholarshipType] = mapped_column(
        nullable=False,
        doc="Type of scholarship offered"
    )

    scholarship_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Percentage of scholarship offered"
    )

    # Offer status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether offer is still active"
    )

    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Offer expiration date"
    )

    # Response tracking
    response_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date recruit responded to offer"
    )

    response_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Recruit's response (accepted, declined, pending)"
    )

    # Coach who extended offer
    recruiting_coach: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Coach who extended the offer"
    )

    offer_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notes about the offer"
    )

    # Relationships
    recruit: Mapped["FootballRecruit"] = relationship(
        "FootballRecruit",
        back_populates="offers",
        lazy="selectin"
    )

    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_recruiting_offers_recruit_id", "recruit_id"),
        Index("idx_football_recruiting_offers_team_id", "team_id"),
        Index("idx_football_recruiting_offers_date", "offer_date"),
        Index("idx_football_recruiting_offers_active", "is_active"),
        UniqueConstraint("recruit_id", "team_id", "offer_date", name="uq_football_recruiting_offers"),
    )


class FootballRecruitingVisit(Base, UUIDMixin, TimestampMixin):
    """
    Official and unofficial recruiting visits
    """
    __tablename__ = "football_recruiting_visits"

    # References
    recruit_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_recruits.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the recruit"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Team being visited"
    )

    # Visit details
    visit_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of visit"
    )

    visit_type: Mapped[VisitType] = mapped_column(
        nullable=False,
        doc="Type of visit (official or unofficial)"
    )

    # Visit logistics
    duration_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Duration of visit in days"
    )

    host_player: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Player who hosted the visit"
    )

    primary_coach_contact: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Primary coach contact during visit"
    )

    # Visit activities
    attended_practice: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether recruit attended practice"
    )

    attended_game: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether recruit attended a game"
    )

    game_attended: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Specific game attended"
    )

    met_with_academics: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether recruit met with academic advisors"
    )

    campus_tour: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether recruit received campus tour"
    )

    # Family involvement
    family_members_attended: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Family members who attended visit"
    )

    family_accommodation: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Where family stayed during visit"
    )

    # Visit outcome
    visit_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Visit rating/quality (1-10 scale)"
    )

    positive_feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Positive feedback from visit"
    )

    concerns_noted: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Any concerns noted during visit"
    )

    follow_up_planned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether follow-up is planned"
    )

    visit_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="General notes about the visit"
    )

    # Relationships
    recruit: Mapped["FootballRecruit"] = relationship(
        "FootballRecruit",
        back_populates="visits",
        lazy="selectin"
    )

    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_recruiting_visits_recruit_id", "recruit_id"),
        Index("idx_football_recruiting_visits_team_id", "team_id"),
        Index("idx_football_recruiting_visits_date", "visit_date"),
        Index("idx_football_recruiting_visits_type", "visit_type"),
        UniqueConstraint("recruit_id", "team_id", "visit_date", name="uq_football_recruiting_visits"),
    )


# =============================================================================
# Transfer Portal Models
# =============================================================================

class FootballTransferPortalEntry(Base, UUIDMixin, TimestampMixin):
    """
    Football transfer portal entries with comprehensive tracking
    Manages the complex eligibility and timeline of transfers
    """
    __tablename__ = "football_transfer_portal_entries"

    # Player information
    player_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="SET NULL"),
        doc="Reference to existing player (if applicable)"
    )

    # Basic information
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Player's first name"
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Player's last name"
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Player's full name"
    )

    # Previous college information
    previous_team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Team player is transferring from"
    )

    previous_college_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Name of previous college"
    )

    # Portal entry details
    portal_entry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date entered transfer portal"
    )

    portal_entry_reason: Mapped[PortalEntryReason] = mapped_column(
        nullable=False,
        doc="Reason for entering portal"
    )

    is_graduate_transfer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a graduate transfer"
    )

    # Position and academic info
    primary_position: Mapped[FootballPosition] = mapped_column(
        nullable=False,
        doc="Player's primary position"
    )

    position_group: Mapped[FootballPositionGroup] = mapped_column(
        nullable=False,
        doc="Position group"
    )

    current_class: Mapped[PlayerClass] = mapped_column(
        nullable=False,
        doc="Current academic class"
    )

    years_of_eligibility_remaining: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Years of eligibility remaining"
    )

    # Physical attributes
    height_inches: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Height in inches"
    )

    weight_pounds: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Weight in pounds"
    )

    # Previous college performance
    previous_college_stats: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON of previous college statistics"
    )

    games_played_previous: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Games played at previous school"
    )

    years_at_previous_school: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Number of years at previous school"
    )

    # Transfer destination
    new_team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="SET NULL"),
        doc="New team (if committed)"
    )

    commitment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date committed to new school"
    )

    enrollment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Expected enrollment date"
    )

    # Eligibility status
    transfer_status: Mapped[TransferStatus] = mapped_column(
        nullable=False,
        default=TransferStatus.IN_PORTAL,
        doc="Current transfer status"
    )

    immediate_eligibility: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether immediately eligible to play"
    )

    waiver_filed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether eligibility waiver was filed"
    )

    waiver_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Status of eligibility waiver"
    )

    sit_out_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether player must sit out a year"
    )

    # Academic standing
    academic_standing: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Academic standing status"
    )

    gpa: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Current GPA"
    )

    degree_progress: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Progress toward degree"
    )

    graduation_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Expected graduation date"
    )

    # Scholarship information
    scholarship_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Scholarship status at new school"
    )

    scholarship_type: Mapped[Optional[ScholarshipType]] = mapped_column(
        doc="Type of scholarship at new school"
    )

    # Transfer reasons and circumstances
    transfer_reason_detail: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Detailed reason for transfer"
    )

    coaching_change_factor: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether coaching change was a factor"
    )

    playing_time_factor: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether playing time was a factor"
    )

    academic_factor: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether academics were a factor"
    )

    family_factor: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether family reasons were a factor"
    )

    # Portal window information
    portal_window_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Type of portal window (regular, supplemental, etc.)"
    )

    deadline_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Deadline for portal entry"
    )

    # Recruiting as transfer
    receiving_interest_from: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON array of schools showing interest"
    )

    official_visits_scheduled: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of official visits scheduled"
    )

    offers_received: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of transfer offers received"
    )

    # Social media and contact
    social_media_announcement: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Social media announcement of portal entry"
    )

    twitter_handle: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Twitter handle"
    )

    # Portal outcome
    final_destination: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Final transfer destination"
    )

    portal_outcome: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Final outcome (transferred, returned, quit, etc.)"
    )

    portal_exit_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date exited portal"
    )

    # Additional notes
    transfer_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes about transfer"
    )

    # Relationships
    player: Mapped[Optional["FootballPlayer"]] = relationship(
        "FootballPlayer",
        lazy="selectin"
    )

    previous_team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        foreign_keys=[previous_team_id],
        lazy="selectin"
    )

    new_team: Mapped[Optional["FootballTeam"]] = relationship(
        "FootballTeam",
        foreign_keys=[new_team_id],
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_transfer_portal_player_id", "player_id"),
        Index("idx_football_transfer_portal_previous_team", "previous_team_id"),
        Index("idx_football_transfer_portal_new_team", "new_team_id"),
        Index("idx_football_transfer_portal_entry_date", "portal_entry_date"),
        Index("idx_football_transfer_portal_status", "transfer_status"),
        Index("idx_football_transfer_portal_position", "primary_position"),
        Index("idx_football_transfer_portal_grad", "is_graduate_transfer"),
        Index("idx_football_transfer_portal_eligibility", "immediate_eligibility"),
        Index("idx_football_transfer_portal_full_name", "full_name"),
    )

    def __repr__(self) -> str:
        return f"<FootballTransferPortalEntry(name='{self.full_name}', from='{self.previous_college_name}', date={self.portal_entry_date})>"

    @property
    def is_committed_to_new_school(self) -> bool:
        """Check if player has committed to new school"""
        return self.new_team_id is not None and self.commitment_date is not None

    @property
    def time_in_portal(self) -> Optional[int]:
        """Days spent in portal"""
        if self.portal_exit_date:
            return (self.portal_exit_date - self.portal_entry_date).days
        else:
            return (date.today() - self.portal_entry_date).days

    @property
    def transfer_status_display(self) -> str:
        """Display-friendly transfer status"""
        if self.is_committed_to_new_school:
            return f"Committed to {self.new_team.display_name if self.new_team else 'New School'}"
        else:
            return self.transfer_status.value.replace("_", " ").title()


# =============================================================================
# Coaching Staff Models
# =============================================================================

class FootballCoachingStaff(Base, UUIDMixin, TimestampMixin):
    """
    Football coaching staff with comprehensive personnel tracking
    """
    __tablename__ = "football_coaching_staff"

    # Team association
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football team"
    )

    # Academic context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Basic information
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Coach's first name"
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Coach's last name"
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Coach's full name"
    )

    # Position and role
    coaching_position: Mapped[CoachingPosition] = mapped_column(
        nullable=False,
        doc="Specific coaching position"
    )

    coaching_level: Mapped[CoachingLevel] = mapped_column(
        nullable=False,
        doc="Level of coaching position"
    )

    position_group_responsibility: Mapped[Optional[FootballPositionGroup]] = mapped_column(
        doc="Position group coached (if applicable)"
    )

    additional_responsibilities: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional coaching responsibilities"
    )

    # Employment details
    hire_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date hired"
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Start date of current position"
    )

    contract_end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Contract end date"
    )

    contract_status: Mapped[ContractStatus] = mapped_column(
        nullable=False,
        default=ContractStatus.ACTIVE,
        doc="Current contract status"
    )

    # Contract details
    annual_salary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        doc="Annual salary"
    )

    contract_length_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Length of contract in years"
    )

    buyout_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        doc="Contract buyout amount"
    )

    # Performance incentives
    performance_bonuses: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON of performance bonus structure"
    )

    recruiting_bonuses: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON of recruiting bonus structure"
    )

    # Previous experience
    previous_positions: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON array of previous coaching positions"
    )

    college_coaching_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Years of college coaching experience"
    )

    nfl_coaching_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Years of NFL coaching experience"
    )

    high_school_coaching_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Years of high school coaching experience"
    )

    # Educational background
    alma_mater: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="College/university attended"
    )

    degree: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Degree earned"
    )

    playing_background: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Playing background and experience"
    )

    # Recruiting responsibilities
    primary_recruiting_region: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Primary recruiting region/territory"
    )

    recruiting_states: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON array of recruiting states"
    )

    high_school_contacts: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Key high school coaching contacts"
    )

    recruiting_specialties: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Recruiting specialties or advantages"
    )

    # Performance metrics
    recruiting_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Recruiting effectiveness rating (1-10)"
    )

    coaching_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Coaching effectiveness rating (1-10)"
    )

    # Personal information
    birth_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of birth"
    )

    hometown: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Hometown"
    )

    family_info: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Family information"
    )

    # Social media and contact
    twitter_handle: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Twitter handle"
    )

    linkedin_profile: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="LinkedIn profile URL"
    )

    # Status tracking
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether coach is currently active"
    )

    termination_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of termination (if applicable)"
    )

    termination_reason: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Reason for termination"
    )

    # Notes and evaluations
    coaching_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notes about coaching performance"
    )

    strengths: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Coaching strengths"
    )

    areas_for_improvement: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Areas for improvement"
    )

    # Relationships
    team: Mapped["FootballTeam"] = relationship(
        "FootballTeam",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_coaching_staff_team_id", "team_id"),
        Index("idx_football_coaching_staff_academic_year_id", "academic_year_id"),
        Index("idx_football_coaching_staff_full_name", "full_name"),
        Index("idx_football_coaching_staff_position", "coaching_position"),
        Index("idx_football_coaching_staff_level", "coaching_level"),
        Index("idx_football_coaching_staff_active", "is_active"),
        Index("idx_football_coaching_staff_contract", "contract_status"),
        Index("idx_football_coaching_staff_team_year", "team_id", "academic_year_id"),
        UniqueConstraint("team_id", "coaching_position", "academic_year_id", name="uq_football_coaching_staff_team_position_year"),
    )

    def __repr__(self) -> str:
        return f"<FootballCoachingStaff(name='{self.full_name}', position='{self.coaching_position}', team='{self.team.display_name if self.team else None}')>"

    @property
    def total_coaching_experience(self) -> int:
        """Total years of coaching experience"""
        return (
            (self.college_coaching_years or 0) +
            (self.nfl_coaching_years or 0) +
            (self.high_school_coaching_years or 0)
        )

    @property
    def contract_years_remaining(self) -> Optional[int]:
        """Years remaining on contract"""
        if self.contract_end_date:
            today = date.today()
            if self.contract_end_date > today:
                return (self.contract_end_date - today).days // 365
        return None

    @property
    def is_head_coach(self) -> bool:
        """Check if this is the head coach"""
        return self.coaching_position == CoachingPosition.HEAD_COACH


# =============================================================================
# NIL Deal Models
# =============================================================================

class FootballNILDeal(Base, UUIDMixin, TimestampMixin):
    """
    Name, Image, Likeness (NIL) deal tracking for football players
    """
    __tablename__ = "football_nil_deals"

    # Player association
    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football player"
    )

    # Deal basics
    deal_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Name/title of the NIL deal"
    )

    deal_type: Mapped[NILDealType] = mapped_column(
        nullable=False,
        doc="Type of NIL deal"
    )

    nil_category: Mapped[NILCategory] = mapped_column(
        nullable=False,
        doc="Category of NIL activity"
    )

    # Partner/company information
    partner_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Company or individual partnering with player"
    )

    partner_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Type of partner (business, individual, collective, etc.)"
    )

    partner_location: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Location of partner organization"
    )

    # Financial details
    deal_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        doc="Total value of the deal"
    )

    payment_structure: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Payment structure (lump sum, installments, etc.)"
    )

    payment_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        doc="Payment amount per instance/period"
    )

    payment_frequency: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Payment frequency (one-time, monthly, per post, etc.)"
    )

    # Deal timeline
    deal_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date deal was signed/agreed"
    )

    effective_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date deal becomes effective"
    )

    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Deal expiration date"
    )

    deal_duration_months: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Duration of deal in months"
    )

    # Deal requirements and deliverables
    required_activities: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON array of required activities"
    )

    social_media_requirements: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Social media posting requirements"
    )

    appearance_requirements: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Required appearances or events"
    )

    content_creation_requirements: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Content creation requirements"
    )

    exclusivity_clauses: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Exclusivity requirements or restrictions"
    )

    # Performance metrics
    engagement_metrics: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="JSON of engagement metrics and targets"
    )

    performance_bonuses: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Performance bonus structure"
    )

    success_metrics: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Metrics for measuring deal success"
    )

    # Compliance and oversight
    compliance_status: Mapped[ComplianceStatus] = mapped_column(
        nullable=False,
        default=ComplianceStatus.PENDING_REVIEW,
        doc="NCAA compliance status"
    )

    school_approval_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether school approval is required"
    )

    school_approval_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of school approval"
    )

    ncaa_reporting_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether NCAA reporting is required"
    )

    reporting_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date reported to NCAA/school"
    )

    # Collective involvement
    nil_collective_involved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether NIL collective is involved"
    )

    collective_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Name of NIL collective (if involved)"
    )

    booster_involvement: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether boosters are involved"
    )

    # Deal status and outcome
    deal_status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
        doc="Current status of the deal"
    )

    completed_successfully: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        doc="Whether deal was completed successfully"
    )

    early_termination: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether deal was terminated early"
    )

    termination_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Reason for early termination"
    )

    # Additional details
    deal_description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Detailed description of the deal"
    )

    public_announcement: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether deal was publicly announced"
    )

    announcement_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of public announcement"
    )

    media_coverage: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Media coverage of the deal"
    )

    deal_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes about the deal"
    )

    # Relationships
    player: Mapped["FootballPlayer"] = relationship(
        "FootballPlayer",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_nil_deals_player_id", "player_id"),
        Index("idx_football_nil_deals_deal_date", "deal_date"),
        Index("idx_football_nil_deals_deal_type", "deal_type"),
        Index("idx_football_nil_deals_category", "nil_category"),
        Index("idx_football_nil_deals_partner", "partner_name"),
        Index("idx_football_nil_deals_value", "deal_value"),
        Index("idx_football_nil_deals_status", "deal_status"),
        Index("idx_football_nil_deals_compliance", "compliance_status"),
        Index("idx_football_nil_deals_collective", "nil_collective_involved"),
    )

    def __repr__(self) -> str:
        return f"<FootballNILDeal(player='{self.player.full_name if self.player else None}', partner='{self.partner_name}', value={self.deal_value})>"

    @property
    def estimated_annual_value(self) -> Optional[Decimal]:
        """Estimated annual value of the deal"""
        if self.deal_value and self.deal_duration_months:
            months_per_year = min(12, self.deal_duration_months)
            return (self.deal_value / Decimal(self.deal_duration_months)) * Decimal(months_per_year)
        return self.deal_value

    @property
    def is_active(self) -> bool:
        """Check if deal is currently active"""
        today = date.today()
        return (
            self.deal_status == "active" and
            self.effective_date <= today and
            (self.expiration_date is None or self.expiration_date >= today)
        )

    @property
    def days_remaining(self) -> Optional[int]:
        """Days remaining in deal"""
        if self.expiration_date:
            today = date.today()
            if self.expiration_date > today:
                return (self.expiration_date - today).days
        return None


# =============================================================================
# Eligibility Tracking Models
# =============================================================================

class FootballEligibilityTracking(Base, UUIDMixin, TimestampMixin):
    """
    Comprehensive academic and athletic eligibility tracking
    """
    __tablename__ = "football_eligibility_tracking"

    # Player association
    player_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("football_players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the football player"
    )

    # Academic context
    academic_year_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the academic year"
    )

    # Eligibility period
    eligibility_period: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Eligibility period (fall, spring, summer)"
    )

    eligibility_type: Mapped[EligibilityType] = mapped_column(
        nullable=False,
        doc="Type of eligibility being tracked"
    )

    # Academic eligibility
    overall_gpa: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Overall cumulative GPA"
    )

    semester_gpa: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Current semester GPA"
    )

    credit_hours_completed: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Total credit hours completed"
    )

    credit_hours_current_semester: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Credit hours in current semester"
    )

    degree_progress_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        doc="Percentage progress toward degree"
    )

    # Academic standing
    academic_standing: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Current academic standing"
    )

    academic_probation: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether on academic probation"
    )

    academic_suspension: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether on academic suspension"
    )

    # Athletic eligibility
    athletic_eligibility_status: Mapped[PlayerEligibilityStatus] = mapped_column(
        nullable=False,
        default=PlayerEligibilityStatus.ELIGIBLE,
        doc="Athletic eligibility status"
    )

    years_of_eligibility_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Years of eligibility used"
    )

    years_of_eligibility_remaining: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
        doc="Years of eligibility remaining"
    )

    # NCAA Progress-Toward-Degree requirements
    forty_percent_rule_met: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether 40% rule is met (sophomore year)"
    )

    sixty_percent_rule_met: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether 60% rule is met (junior year)"
    )

    eighty_percent_rule_met: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether 80% rule is met (senior year)"
    )

    # Transfer-specific eligibility
    transfer_eligibility_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Transfer-specific eligibility status"
    )

    transfer_waiver_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="Status of transfer eligibility waiver"
    )

    immediate_eligibility_granted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether immediate eligibility was granted"
    )

    # Disciplinary issues
    disciplinary_action: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether under disciplinary action"
    )

    suspension_status: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether currently suspended"
    )

    suspension_games_remaining: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Games remaining in suspension"
    )

    # Medical eligibility
    medical_clearance: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether medically cleared to play"
    )

    injury_status: Mapped[Optional[str]] = mapped_column(
        String(200),
        doc="Current injury status"
    )

    medical_redshirt_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether eligible for medical redshirt"
    )

    # Compliance tracking
    compliance_review_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of last compliance review"
    )

    compliance_officer_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notes from compliance officer"
    )

    ncaa_clearinghouse_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        doc="NCAA Clearinghouse status"
    )

    # Academic support
    academic_support_needed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether academic support is needed"
    )

    tutoring_hours_weekly: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Weekly tutoring hours"
    )

    study_hall_hours_weekly: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Weekly mandatory study hall hours"
    )

    # Status dates
    last_eligibility_check: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of last eligibility check"
    )

    next_eligibility_review: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of next scheduled review"
    )

    # Notes and alerts
    eligibility_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Notes about eligibility status"
    )

    academic_alerts: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Academic alerts or concerns"
    )

    compliance_alerts: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Compliance alerts or issues"
    )

    # Relationships
    player: Mapped["FootballPlayer"] = relationship(
        "FootballPlayer",
        lazy="selectin"
    )

    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_football_eligibility_player_id", "player_id"),
        Index("idx_football_eligibility_academic_year_id", "academic_year_id"),
        Index("idx_football_eligibility_period", "eligibility_period"),
        Index("idx_football_eligibility_type", "eligibility_type"),
        Index("idx_football_eligibility_athletic_status", "athletic_eligibility_status"),
        Index("idx_football_eligibility_academic_standing", "academic_standing"),
        Index("idx_football_eligibility_player_year", "player_id", "academic_year_id"),
        UniqueConstraint("player_id", "academic_year_id", "eligibility_period", "eligibility_type", name="uq_football_eligibility_player_year_period_type"),
    )

    def __repr__(self) -> str:
        return f"<FootballEligibilityTracking(player='{self.player.full_name if self.player else None}', year='{self.academic_year.name if self.academic_year else None}', status='{self.athletic_eligibility_status}')>"

    @property
    def is_academically_eligible(self) -> bool:
        """Check if player is academically eligible"""
        return (
            self.academic_standing not in ["suspension", "dismissed"] and
            not self.academic_suspension and
            (self.overall_gpa or 0) >= 2.0
        )

    @property
    def is_athletically_eligible(self) -> bool:
        """Check if player is athletically eligible"""
        return (
            self.athletic_eligibility_status == PlayerEligibilityStatus.ELIGIBLE and
            not self.suspension_status and
            self.medical_clearance and
            self.years_of_eligibility_remaining > 0
        )

    @property
    def is_fully_eligible(self) -> bool:
        """Check if player is fully eligible to compete"""
        return self.is_academically_eligible and self.is_athletically_eligible

    @property
    def eligibility_concerns(self) -> List[str]:
        """List of current eligibility concerns"""
        concerns = []

        if not self.is_academically_eligible:
            concerns.append("Academic eligibility")

        if not self.is_athletically_eligible:
            concerns.append("Athletic eligibility")

        if self.disciplinary_action:
            concerns.append("Disciplinary action")

        if not self.medical_clearance:
            concerns.append("Medical clearance")

        if self.academic_probation:
            concerns.append("Academic probation")

        return concerns