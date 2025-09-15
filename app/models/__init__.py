"""Models package for the application."""

from .base import BaseSchema, TimestampedSchema, BaseResponse, ErrorResponse, PaginatedResponse
from .user import (
    User, UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserPreferences, UserPreferencesUpdate, CurrentUser, UserRole, UserStatus
)
from .team import (
    Team, TeamCreate, TeamUpdate, TeamResponse, TeamListResponse,
    TeamStats, TeamStatsResponse, UserTeamFollow, TeamSearchFilters,
    PopularTeam, Sport, League, TeamStatus
)

__all__ = [
    # Base models
    "BaseSchema", "TimestampedSchema", "BaseResponse", "ErrorResponse", "PaginatedResponse",

    # User models
    "User", "UserCreate", "UserUpdate", "UserResponse", "UserListResponse",
    "UserPreferences", "UserPreferencesUpdate", "CurrentUser", "UserRole", "UserStatus",

    # Team models
    "Team", "TeamCreate", "TeamUpdate", "TeamResponse", "TeamListResponse",
    "TeamStats", "TeamStatsResponse", "UserTeamFollow", "TeamSearchFilters",
    "PopularTeam", "Sport", "League", "TeamStatus"
]