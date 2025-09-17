"""
Enums for Corner League Media database models
"""

import enum


class ContentFrequency(str, enum.Enum):
    """User content frequency preferences"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class NewsType(str, enum.Enum):
    """Types of news content"""
    INJURIES = "injuries"
    TRADES = "trades"
    ROSTER = "roster"
    GENERAL = "general"
    SCORES = "scores"
    ANALYSIS = "analysis"


class GameStatus(str, enum.Enum):
    """Game status options"""
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINAL = "FINAL"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"


class GameResult(str, enum.Enum):
    """Game result options"""
    WIN = "W"
    LOSS = "L"
    TIE = "T"


class ExperienceType(str, enum.Enum):
    """Fan experience types"""
    WATCH_PARTY = "watch_party"
    TAILGATE = "tailgate"
    VIEWING = "viewing"
    MEETUP = "meetup"


class ContentCategory(str, enum.Enum):
    """Content category options"""
    INJURIES = "injuries"
    TRADES = "trades"
    ROSTER = "roster"
    GENERAL = "general"
    SCORES = "scores"
    ANALYSIS = "analysis"


class IngestionStatus(str, enum.Enum):
    """Feed ingestion status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


class InteractionType(str, enum.Enum):
    """User interaction types for analytics"""
    ARTICLE_VIEW = "article_view"
    ARTICLE_SHARE = "article_share"
    TEAM_FOLLOW = "team_follow"
    TEAM_UNFOLLOW = "team_unfollow"
    GAME_VIEW = "game_view"
    EXPERIENCE_REGISTER = "experience_register"
    TICKET_VIEW = "ticket_view"
    SEARCH = "search"
    FEED_SCROLL = "feed_scroll"


class EntityType(str, enum.Enum):
    """Entity types for analytics and references"""
    ARTICLE = "article"
    TEAM = "team"
    GAME = "game"
    PLAYER = "player"
    EXPERIENCE = "experience"
    TICKET_DEAL = "ticket_deal"
    AI_SUMMARY = "ai_summary"