"""
User preferences and settings schemas
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.models.enums import ContentFrequency
from .common import BaseSchema, IDMixin, TimestampMixin


class UserSportPreference(BaseSchema, IDMixin, TimestampMixin):
    """User sport preference schema"""
    user_id: UUID
    sport_id: UUID
    rank: int = Field(ge=1, description="Priority ranking of this sport")
    is_active: bool = True

    # Sport info (if included)
    sport: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "sport_id": "550e8400-e29b-41d4-a716-446655440002",
                "rank": 1,
                "is_active": True,
                "created_at": "2025-01-17T10:00:00Z",
                "updated_at": "2025-01-17T10:00:00Z"
            }
        }


class UserTeamPreference(BaseSchema, IDMixin, TimestampMixin):
    """User team preference schema"""
    user_id: UUID
    team_id: UUID
    affinity_score: float = Field(ge=0.0, le=1.0, description="How much the user likes this team")
    is_active: bool = True

    # Team info (if included)
    team: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "team_id": "550e8400-e29b-41d4-a716-446655440004",
                "affinity_score": 0.9,
                "is_active": True,
                "created_at": "2025-01-17T10:00:00Z",
                "updated_at": "2025-01-17T10:00:00Z"
            }
        }


class UserNewsPreference(BaseSchema, IDMixin, TimestampMixin):
    """User news content preference schema"""
    user_id: UUID
    news_type: str = Field(description="Type of news content")
    enabled: bool = True
    priority: int = Field(ge=1, description="Priority level for this news type")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440005",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "news_type": "scores",
                "enabled": True,
                "priority": 1,
                "created_at": "2025-01-17T10:00:00Z",
                "updated_at": "2025-01-17T10:00:00Z"
            }
        }


class UserNotificationSettings(BaseSchema, IDMixin, TimestampMixin):
    """User notification settings schema"""
    user_id: UUID
    push_notifications: bool = False
    email_notifications: bool = False
    game_reminders: bool = False
    news_alerts: bool = False
    score_updates: bool = False

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440006",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "push_notifications": True,
                "email_notifications": False,
                "game_reminders": True,
                "news_alerts": False,
                "score_updates": True,
                "created_at": "2025-01-17T10:00:00Z",
                "updated_at": "2025-01-17T10:00:00Z"
            }
        }


class SportPreferenceUpdate(BaseModel):
    """Schema for updating a single sport preference"""
    sport_id: UUID
    rank: int = Field(ge=1, description="Priority ranking of this sport")
    is_active: bool = True

    class Config:
        schema_extra = {
            "example": {
                "sport_id": "550e8400-e29b-41d4-a716-446655440002",
                "rank": 1,
                "is_active": True
            }
        }


class TeamPreferenceUpdate(BaseModel):
    """Schema for updating a single team preference"""
    team_id: UUID
    affinity_score: float = Field(ge=0.0, le=1.0, description="How much the user likes this team")
    is_active: bool = True

    class Config:
        schema_extra = {
            "example": {
                "team_id": "550e8400-e29b-41d4-a716-446655440004",
                "affinity_score": 0.9,
                "is_active": True
            }
        }


class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating notification preferences"""
    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    game_reminders: Optional[bool] = None
    news_alerts: Optional[bool] = None
    score_updates: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "push_enabled": True,
                "email_enabled": False,
                "game_reminders": True,
                "news_alerts": False,
                "score_updates": True
            }
        }


class SportsPreferencesUpdate(BaseModel):
    """Schema for updating multiple sport preferences"""
    sports: List[SportPreferenceUpdate] = Field(description="List of sport preferences to update")

    class Config:
        schema_extra = {
            "example": {
                "sports": [
                    {
                        "sport_id": "550e8400-e29b-41d4-a716-446655440002",
                        "rank": 1,
                        "is_active": True
                    },
                    {
                        "sport_id": "550e8400-e29b-41d4-a716-446655440003",
                        "rank": 2,
                        "is_active": True
                    }
                ]
            }
        }


class TeamsPreferencesUpdate(BaseModel):
    """Schema for updating multiple team preferences"""
    teams: List[TeamPreferenceUpdate] = Field(description="List of team preferences to update")

    class Config:
        schema_extra = {
            "example": {
                "teams": [
                    {
                        "team_id": "550e8400-e29b-41d4-a716-446655440004",
                        "affinity_score": 0.9,
                        "is_active": True
                    },
                    {
                        "team_id": "550e8400-e29b-41d4-a716-446655440005",
                        "affinity_score": 0.7,
                        "is_active": True
                    }
                ]
            }
        }


class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences (bulk update)"""
    sports: Optional[List[SportPreferenceUpdate]] = None
    teams: Optional[List[TeamPreferenceUpdate]] = None
    notifications: Optional[NotificationPreferencesUpdate] = None
    content_frequency: Optional[ContentFrequency] = None

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "sports": [
                    {"sport_id": "550e8400-e29b-41d4-a716-446655440002", "rank": 1, "is_active": True}
                ],
                "teams": [
                    {"team_id": "550e8400-e29b-41d4-a716-446655440004", "affinity_score": 0.9, "is_active": True}
                ],
                "notifications": {
                    "push_enabled": True,
                    "email_enabled": False,
                    "game_reminders": True,
                    "news_alerts": False,
                    "score_updates": True
                },
                "content_frequency": "standard"
            }
        }