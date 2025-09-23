"""
Pydantic schemas for API requests and responses
"""

from .auth import FirebaseUser, UserCreate, UserUpdate, UserProfile
from .sports import Sport, League, Team, SportResponse, LeagueResponse, TeamResponse
from .content import (
    Article, ArticleResponse, ArticleCreate, ArticleUpdate,
    FeedSource, FeedSourceResponse, FeedSourceCreate,
    AISummary, AISummaryResponse
)
from .games import Game, GameResponse, GameEvent, GameEventResponse
from .players import Player, PlayerResponse, DepthChartEntry, DepthChartResponse
from .tickets import TicketDeal, TicketDealResponse, TicketProvider
from .experiences import FanExperience, FanExperienceResponse, UserExperienceRegistration
from .preferences import (
    UserSportPreference, UserTeamPreference, UserNewsPreference,
    UserNotificationSettings, PreferencesUpdate
)
from .analytics import UserInteraction, ContentPerformance
from .dashboard import TeamDashboard, HomeData, PersonalizedFeed
from .common import PaginatedResponse, APIResponse, ErrorResponse

__all__ = [
    # Auth
    "FirebaseUser",
    "UserCreate",
    "UserUpdate",
    "UserProfile",
    # Sports
    "Sport",
    "League",
    "Team",
    "SportResponse",
    "LeagueResponse",
    "TeamResponse",
    # Content
    "Article",
    "ArticleResponse",
    "ArticleCreate",
    "ArticleUpdate",
    "FeedSource",
    "FeedSourceResponse",
    "FeedSourceCreate",
    "AISummary",
    "AISummaryResponse",
    # Games
    "Game",
    "GameResponse",
    "GameEvent",
    "GameEventResponse",
    # Players
    "Player",
    "PlayerResponse",
    "DepthChartEntry",
    "DepthChartResponse",
    # Tickets
    "TicketDeal",
    "TicketDealResponse",
    "TicketProvider",
    # Experiences
    "FanExperience",
    "FanExperienceResponse",
    "UserExperienceRegistration",
    # Preferences
    "UserSportPreference",
    "UserTeamPreference",
    "UserNewsPreference",
    "UserNotificationSettings",
    "PreferencesUpdate",
    # Analytics
    "UserInteraction",
    "ContentPerformance",
    # Dashboard
    "TeamDashboard",
    "HomeData",
    "PersonalizedFeed",
    # Common
    "PaginatedResponse",
    "APIResponse",
    "ErrorResponse",
]