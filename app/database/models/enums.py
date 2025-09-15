"""Database enums for Corner League Media."""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TeamStatus(str, Enum):
    """Team status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


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


class ArticleStatus(str, Enum):
    """Article status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ContentCategory(str, Enum):
    """Content category enumeration."""
    NEWS = "news"
    ANALYSIS = "analysis"
    OPINION = "opinion"
    RUMORS = "rumors"
    INJURY_REPORT = "injury_report"
    TRADE = "trade"
    DRAFT = "draft"
    GAME_RECAP = "game_recap"


class GameStatus(str, Enum):
    """Game status enumeration."""
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class IngestionStatus(str, Enum):
    """Content ingestion status enumeration."""
    SUCCESS = "success"
    DUPLICATE = "duplicate"
    ERROR = "error"
    SKIP = "skip"