"""
SQLAlchemy Models for Corner League Media
"""

from .base import Base, TimestampMixin
from .sports import Sport, League, Team
from .users import (
    User,
    UserSportPreference,
    UserTeamPreference,
    UserNewsPreference,
    UserNotificationSettings,
)
from .games import Game, GameEvent
from .content import (
    FeedSource,
    FeedSourceMapping,
    FeedSnapshot,
    Article,
    ArticleSport,
    ArticleTeam,
    AISummary,
)
from .players import Player, DepthChartEntry
from .tickets import TicketProvider, TicketDeal
from .experiences import FanExperience, UserExperienceRegistration
from .analytics import UserInteraction, ContentPerformance

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    # Sports
    "Sport",
    "League",
    "Team",
    # Users
    "User",
    "UserSportPreference",
    "UserTeamPreference",
    "UserNewsPreference",
    "UserNotificationSettings",
    # Games
    "Game",
    "GameEvent",
    # Content
    "FeedSource",
    "FeedSourceMapping",
    "FeedSnapshot",
    "Article",
    "ArticleSport",
    "ArticleTeam",
    "AISummary",
    # Players
    "Player",
    "DepthChartEntry",
    # Tickets
    "TicketProvider",
    "TicketDeal",
    # Experiences
    "FanExperience",
    "UserExperienceRegistration",
    # Analytics
    "UserInteraction",
    "ContentPerformance",
]