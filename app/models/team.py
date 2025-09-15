"""Team models and schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from .base import BaseSchema, TimestampedSchema


class Sport(str, Enum):
    """Supported sports enumeration."""
    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"
    MLS = "mls"
    COLLEGE_FOOTBALL = "college_football"
    COLLEGE_BASKETBALL = "college_basketball"


class League(str, Enum):
    """League enumeration."""
    NFL = "NFL"
    NBA = "NBA"
    MLB = "MLB"
    NHL = "NHL"
    MLS = "MLS"
    NCAA_FB = "NCAA_FB"
    NCAA_BB = "NCAA_BB"


class TeamStatus(str, Enum):
    """Team status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class TeamBase(BaseSchema):
    """Base team model with common fields."""

    name: str = Field(..., description="Team name")
    city: Optional[str] = Field(None, description="Team city")
    abbreviation: str = Field(..., description="Team abbreviation")
    sport: Sport = Field(..., description="Sport type")
    league: League = Field(..., description="League")
    logo_url: Optional[str] = Field(None, description="Team logo URL")
    primary_color: Optional[str] = Field(None, description="Primary team color")
    secondary_color: Optional[str] = Field(None, description="Secondary team color")
    conference: Optional[str] = Field(None, description="Conference")
    division: Optional[str] = Field(None, description="Division")
    status: TeamStatus = Field(default=TeamStatus.ACTIVE, description="Team status")


class TeamCreate(TeamBase):
    """Team creation model."""

    external_id: Optional[str] = Field(None, description="External API team ID")


class TeamUpdate(BaseSchema):
    """Team update model."""

    name: Optional[str] = None
    city: Optional[str] = None
    abbreviation: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    conference: Optional[str] = None
    division: Optional[str] = None
    status: Optional[TeamStatus] = None


class Team(TeamBase, TimestampedSchema):
    """Complete team model."""

    id: str = Field(..., description="Team ID")
    external_id: Optional[str] = Field(None, description="External API team ID")
    follower_count: int = Field(default=0, description="Number of followers")

    @validator('abbreviation')
    def validate_abbreviation(cls, v):
        if len(v) < 2 or len(v) > 5:
            raise ValueError('Abbreviation must be between 2 and 5 characters')
        return v.upper()


class TeamResponse(BaseSchema):
    """Team response model."""

    id: str
    name: str
    city: Optional[str]
    abbreviation: str
    sport: Sport
    league: League
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]
    conference: Optional[str]
    division: Optional[str]
    status: TeamStatus
    follower_count: int
    created_at: datetime
    updated_at: datetime


class TeamListResponse(BaseSchema):
    """Team list response model."""

    teams: List[TeamResponse]
    total: int
    page: int
    page_size: int


class TeamStats(BaseSchema):
    """Team statistics model."""

    wins: int = Field(default=0, description="Number of wins")
    losses: int = Field(default=0, description="Number of losses")
    ties: Optional[int] = Field(default=0, description="Number of ties")
    points_for: Optional[float] = Field(None, description="Points scored")
    points_against: Optional[float] = Field(None, description="Points allowed")
    win_percentage: Optional[float] = Field(None, description="Win percentage")
    season: str = Field(..., description="Season identifier")

    @validator('win_percentage', pre=True, always=True)
    def calculate_win_percentage(cls, v, values):
        if v is not None:
            return v
        wins = values.get('wins', 0)
        losses = values.get('losses', 0)
        ties = values.get('ties', 0)
        total_games = wins + losses + ties
        if total_games > 0:
            return (wins + ties * 0.5) / total_games
        return 0.0


class TeamStatsResponse(BaseSchema):
    """Team statistics response model."""

    team_id: str
    team_name: str
    team_abbreviation: str
    stats: TeamStats


class UserTeamFollow(BaseSchema):
    """User team follow relationship."""

    user_id: str = Field(..., description="User ID")
    team_id: str = Field(..., description="Team ID")
    followed_at: datetime = Field(default_factory=datetime.utcnow)
    notifications_enabled: bool = Field(default=True, description="Notifications enabled for this team")


class TeamSearchFilters(BaseSchema):
    """Team search filters."""

    sport: Optional[Sport] = None
    league: Optional[League] = None
    conference: Optional[str] = None
    division: Optional[str] = None
    status: Optional[TeamStatus] = None
    search_query: Optional[str] = Field(None, description="Search in team name or city")


class PopularTeam(BaseSchema):
    """Popular team model for rankings."""

    team: TeamResponse
    follower_count: int
    recent_followers: int = Field(..., description="New followers in last 7 days")
    rank: int = Field(..., description="Popularity rank")