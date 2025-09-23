"""
Sports-related schemas for team selection endpoints
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from .common import BaseSchema, IDMixin, TimestampMixin, PaginatedResponse


class SportBase(BaseModel):
    """Base sport schema"""
    name: str = Field(..., description="Display name of the sport")
    slug: str = Field(..., description="URL-friendly slug for the sport")
    has_teams: bool = Field(default=True, description="Whether this sport has team-based competition")
    icon: Optional[str] = Field(None, description="Icon identifier or URL for the sport")
    is_active: bool = Field(default=True, description="Whether this sport is currently active")
    display_order: int = Field(default=0, description="Order for displaying sports in UI")


class Sport(SportBase, IDMixin, TimestampMixin):
    """Complete sport schema with ID and timestamps"""
    pass


class SportResponse(SportBase, IDMixin):
    """Sport response schema without timestamps"""
    leagues_count: Optional[int] = Field(None, description="Number of leagues in this sport")


class SportWithLeagues(SportResponse):
    """Sport response with included leagues"""
    leagues: List["LeagueResponse"] = Field(default_factory=list, description="List of leagues in this sport")


class LeagueBase(BaseModel):
    """Base league schema"""
    sport_id: UUID = Field(..., description="Reference to the sport this league belongs to")
    name: str = Field(..., description="Display name of the league")
    slug: str = Field(..., description="URL-friendly slug for the league")
    abbreviation: Optional[str] = Field(None, description="Short abbreviation for the league")
    is_active: bool = Field(default=True, description="Whether this league is currently active")
    season_start_month: Optional[int] = Field(None, ge=1, le=12, description="Month when season starts (1-12)")
    season_end_month: Optional[int] = Field(None, ge=1, le=12, description="Month when season ends (1-12)")
    # Enhanced metadata from Phase 2
    country_code: Optional[str] = Field(None, description="ISO country code for the league")
    league_level: int = Field(default=1, description="League tier level (1 = top tier)")
    competition_type: str = Field(default="league", description="Type of competition (league, cup, international)")


class League(LeagueBase, IDMixin, TimestampMixin):
    """Complete league schema with ID and timestamps"""
    pass


class LeagueResponse(LeagueBase, IDMixin):
    """League response schema without timestamps"""
    sport_name: Optional[str] = Field(None, description="Name of the sport this league belongs to")
    teams_count: Optional[int] = Field(None, description="Number of teams in this league")


class LeagueWithTeams(LeagueResponse):
    """League response with included teams"""
    teams: List["TeamResponse"] = Field(default_factory=list, description="List of teams in this league")


class TeamBase(BaseModel):
    """Base team schema"""
    sport_id: UUID = Field(..., description="Reference to the sport this team plays")
    league_id: Optional[UUID] = Field(None, description="Reference to the primary league this team belongs to (determined from memberships)")
    name: str = Field(..., description="Team name (e.g., 'Patriots', 'Lakers')")
    market: str = Field(..., description="City or region the team represents")
    slug: str = Field(..., description="URL-friendly slug for the team")
    abbreviation: Optional[str] = Field(None, description="Short team abbreviation")
    logo_url: Optional[str] = Field(None, description="URL to the team's logo image")
    primary_color: Optional[str] = Field(None, description="Primary team color in hex format")
    secondary_color: Optional[str] = Field(None, description="Secondary team color in hex format")
    is_active: bool = Field(default=True, description="Whether this team is currently active")
    external_id: Optional[str] = Field(None, description="External API identifier for this team")
    # Enhanced metadata from Phase 2
    official_name: Optional[str] = Field(None, description="Official full name of the team")
    short_name: Optional[str] = Field(None, description="Short name of the team")
    country_code: Optional[str] = Field(None, description="ISO country code for the team")
    founding_year: Optional[int] = Field(None, description="Year the team was founded")


class Team(TeamBase, IDMixin, TimestampMixin):
    """Complete team schema with ID and timestamps"""
    pass


class LeagueInfo(BaseModel):
    """League information for team responses"""
    id: UUID = Field(..., description="League ID")
    name: str = Field(..., description="League name")
    slug: str = Field(..., description="League slug")
    country_code: Optional[str] = Field(None, description="League country code")
    league_level: Optional[int] = Field(None, description="League tier level")
    competition_type: Optional[str] = Field(None, description="Competition type")
    is_primary: bool = Field(default=False, description="Whether this is the team's primary league")
    season_start_year: Optional[int] = Field(None, description="Season start year for this membership")
    position_last_season: Optional[int] = Field(None, description="Last season position")


class TeamResponse(TeamBase, IDMixin):
    """Team response schema without timestamps"""
    sport_name: Optional[str] = Field(None, description="Name of the sport this team plays")
    league_name: Optional[str] = Field(None, description="Name of the primary league this team belongs to")
    display_name: Optional[str] = Field(None, description="Full display name (market + name)")
    computed_short_name: Optional[str] = Field(None, description="Computed short name (short_name or abbreviation or name)")
    computed_official_name: Optional[str] = Field(None, description="Computed official name")
    leagues: List[LeagueInfo] = Field(default_factory=list, description="All leagues this team participates in")


class TeamSearchParams(BaseModel):
    """Team search parameters"""
    query: Optional[str] = Field(None, description="Search query for team name or market")
    sport_id: Optional[UUID] = Field(None, description="Filter by sport ID")
    league_id: Optional[UUID] = Field(None, description="Filter by league ID")
    market: Optional[str] = Field(None, description="Filter by market/city")
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")


class UserTeamPreferenceBase(BaseModel):
    """Base user team preference schema"""
    team_id: UUID = Field(..., description="Reference to the team")
    affinity_score: float = Field(..., ge=0.0, le=1.0, description="User's affinity score for this team (0.0-1.0)")
    is_active: bool = Field(default=True, description="Whether this preference is active")


class UserTeamPreferenceCreate(UserTeamPreferenceBase):
    """Schema for creating user team preferences"""
    pass


class UserTeamPreferenceUpdate(UserTeamPreferenceBase):
    """Schema for updating user team preferences"""
    affinity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="User's affinity score for this team")
    is_active: Optional[bool] = Field(None, description="Whether this preference is active")


class UserTeamPreferenceResponse(UserTeamPreferenceBase, IDMixin, TimestampMixin):
    """User team preference response schema"""
    team_name: Optional[str] = Field(None, description="Team name")
    team_market: Optional[str] = Field(None, description="Team market/city")
    team_display_name: Optional[str] = Field(None, description="Full team display name")
    team_logo_url: Optional[str] = Field(None, description="Team logo URL")
    sport_name: Optional[str] = Field(None, description="Sport name")
    league_name: Optional[str] = Field(None, description="League name")


class UserTeamPreferencesUpdate(BaseModel):
    """Schema for bulk updating user team preferences"""
    preferences: List[UserTeamPreferenceCreate] = Field(..., description="List of team preferences to set")


class UserTeamPreferencesResponse(BaseModel):
    """Response schema for user team preferences"""
    preferences: List[UserTeamPreferenceResponse] = Field(default_factory=list, description="User's team preferences")
    total_count: int = Field(0, description="Total number of team preferences")


# Pagination response types
SportsPaginatedResponse = PaginatedResponse[SportResponse]
LeaguesPaginatedResponse = PaginatedResponse[LeagueResponse]
TeamsPaginatedResponse = PaginatedResponse[TeamResponse]

class TeamLeagueMembershipBase(BaseModel):
    """Base team-league membership schema"""
    team_id: UUID = Field(..., description="Reference to the team")
    league_id: UUID = Field(..., description="Reference to the league")
    season_start_year: int = Field(..., description="Year when team joined this league")
    season_end_year: Optional[int] = Field(None, description="Year when team left this league (NULL for ongoing)")
    is_active: bool = Field(default=True, description="Whether this membership is currently active")
    position_last_season: Optional[int] = Field(None, description="Final league position if applicable")


class TeamLeagueMembershipResponse(TeamLeagueMembershipBase, IDMixin, TimestampMixin):
    """Team-league membership response schema"""
    team_name: Optional[str] = Field(None, description="Team name")
    team_display_name: Optional[str] = Field(None, description="Team display name")
    league_name: Optional[str] = Field(None, description="League name")
    league_country_code: Optional[str] = Field(None, description="League country code")
    is_current: bool = Field(default=False, description="Whether this is a current membership")


class MultiLeagueTeamResponse(BaseModel):
    """Enhanced team response with multi-league support"""
    id: UUID = Field(..., description="Team ID")
    name: str = Field(..., description="Team name")
    market: str = Field(..., description="Team market/city")
    slug: str = Field(..., description="Team slug")
    display_name: str = Field(..., description="Full display name")
    official_name: Optional[str] = Field(None, description="Official team name")
    short_name: Optional[str] = Field(None, description="Short team name")
    computed_short_name: str = Field(..., description="Computed short name")
    country_code: Optional[str] = Field(None, description="Team country code")
    founding_year: Optional[int] = Field(None, description="Founding year")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    primary_color: Optional[str] = Field(None, description="Primary color")
    secondary_color: Optional[str] = Field(None, description="Secondary color")
    sport_name: str = Field(..., description="Sport name")
    primary_league: LeagueInfo = Field(..., description="Primary league information")
    all_leagues: List[LeagueInfo] = Field(default_factory=list, description="All leagues this team participates in")
    is_multi_league: bool = Field(default=False, description="Whether team participates in multiple leagues")


class SoccerTeamFilters(BaseModel):
    """Soccer-specific team filters"""
    league_ids: Optional[List[UUID]] = Field(None, description="Filter by specific league IDs")
    country_codes: Optional[List[str]] = Field(None, description="Filter by country codes")
    competition_types: Optional[List[str]] = Field(None, description="Filter by competition types (domestic, international, cup)")
    league_levels: Optional[List[int]] = Field(None, description="Filter by league levels")
    multi_league_only: bool = Field(default=False, description="Show only teams in multiple leagues")
    founding_year_min: Optional[int] = Field(None, description="Minimum founding year")
    founding_year_max: Optional[int] = Field(None, description="Maximum founding year")
    query: Optional[str] = Field(None, description="Search query for team names")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")


# Pagination response types for new schemas
MultiLeagueTeamsPaginatedResponse = PaginatedResponse[MultiLeagueTeamResponse]
TeamLeagueMembershipsPaginatedResponse = PaginatedResponse[TeamLeagueMembershipResponse]

# Enhanced search schemas for Phase 2A

class SearchMatchInfo(BaseModel):
    """Information about what matched in the search"""
    field: str = Field(..., description="Field that matched (name, market, abbreviation, etc.)")
    value: str = Field(..., description="The matched value")
    highlighted: str = Field(..., description="The value with search term highlighted")


class SearchMetadata(BaseModel):
    """Metadata about the search operation"""
    query: Optional[str] = Field(None, description="Original search query")
    total_matches: int = Field(..., description="Total number of matches found")
    response_time_ms: float = Field(..., description="Search response time in milliseconds")
    filters_applied: dict = Field(default_factory=dict, description="Applied filters")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Search timestamp")


class EnhancedTeamResponse(TeamResponse):
    """Enhanced team response with search highlighting and metadata"""
    search_matches: List[SearchMatchInfo] = Field(default_factory=list, description="Fields that matched the search")
    relevance_score: Optional[float] = Field(None, description="Relevance score for search ranking")


class EnhancedTeamsPaginatedResponse(BaseModel):
    """Enhanced paginated response with search metadata"""
    items: List[EnhancedTeamResponse] = Field(default_factory=list, description="List of teams")
    total: int = Field(0, description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of items per page")
    has_next: bool = Field(False, description="Whether there are more pages")
    has_previous: bool = Field(False, description="Whether there are previous pages")
    search_metadata: SearchMetadata = Field(..., description="Search operation metadata")


class TeamSearchSuggestion(BaseModel):
    """Team search suggestion/autocomplete"""
    suggestion: str = Field(..., description="Suggested search term")
    type: str = Field(..., description="Type of suggestion (team_name, market, abbreviation)")
    team_count: int = Field(..., description="Number of teams matching this suggestion")
    preview_teams: List[str] = Field(default_factory=list, description="Preview team names")


class SearchSuggestionsResponse(BaseModel):
    """Response for search suggestions/autocomplete"""
    query: str = Field(..., description="Original query")
    suggestions: List[TeamSearchSuggestion] = Field(default_factory=list, description="List of suggestions")
    response_time_ms: float = Field(..., description="Response time in milliseconds")


# Update forward references
SportWithLeagues.model_rebuild()
LeagueWithTeams.model_rebuild()