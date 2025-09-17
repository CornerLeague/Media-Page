"""
Authentication and user management schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from backend.models.enums import ContentFrequency
from .common import BaseSchema, IDMixin, TimestampMixin
from .preferences import UserSportPreference, UserTeamPreference, UserNewsPreference, UserNotificationSettings


class ClerkUser(BaseModel):
    """Clerk user data from authentication"""
    id: str
    email_address: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    created_at: int  # Unix timestamp
    updated_at: int  # Unix timestamp

    class Config:
        # Handle Clerk's field naming
        alias_generator = lambda field_name: field_name  # Keep original names


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    clerk_user_id: str = Field(..., description="Clerk authentication user ID")
    display_name: Optional[str] = Field(None, max_length=100, description="User's display name")
    email: Optional[EmailStr] = Field(None, description="User's email address")

    # Onboarding data
    sports: List[dict] = Field(default_factory=list, description="User's sport preferences")
    teams: List[dict] = Field(default_factory=list, description="User's team preferences")
    preferences: dict = Field(default_factory=dict, description="User's content preferences")

    class Config:
        schema_extra = {
            "example": {
                "clerk_user_id": "user_2abc123def456",
                "display_name": "John Doe",
                "email": "john@example.com",
                "sports": [
                    {
                        "sport_id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Basketball",
                        "rank": 1,
                        "has_teams": True
                    }
                ],
                "teams": [
                    {
                        "team_id": "550e8400-e29b-41d4-a716-446655440001",
                        "name": "Lakers",
                        "sport_id": "550e8400-e29b-41d4-a716-446655440000",
                        "league": "NBA",
                        "affinity_score": 0.9
                    }
                ],
                "preferences": {
                    "news_types": [
                        {"type": "general", "enabled": True, "priority": 1},
                        {"type": "scores", "enabled": True, "priority": 2}
                    ],
                    "notifications": {
                        "push": False,
                        "email": False,
                        "game_reminders": False,
                        "news_alerts": False,
                        "score_updates": False
                    },
                    "content_frequency": "standard"
                }
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    display_name: Optional[str] = Field(None, max_length=100)
    content_frequency: Optional[ContentFrequency] = None
    avatar_url: Optional[str] = Field(None, max_length=500)

    class Config:
        use_enum_values = True


class UserProfile(BaseSchema, IDMixin, TimestampMixin):
    """Complete user profile response"""
    clerk_user_id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    content_frequency: ContentFrequency
    is_active: bool
    onboarding_completed_at: Optional[datetime] = None
    last_active_at: datetime

    # Relationships
    sport_preferences: List[UserSportPreference] = Field(default_factory=list)
    team_preferences: List[UserTeamPreference] = Field(default_factory=list)
    news_preferences: List[UserNewsPreference] = Field(default_factory=list)
    notification_settings: Optional[UserNotificationSettings] = None

    @property
    def is_onboarded(self) -> bool:
        """Check if user has completed onboarding"""
        return self.onboarding_completed_at is not None

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "clerk_user_id": "user_2abc123def456",
                "email": "john@example.com",
                "display_name": "John Doe",
                "avatar_url": "https://images.clerk.dev/avatar.jpg",
                "content_frequency": "standard",
                "is_active": True,
                "onboarding_completed_at": "2025-01-17T12:00:00Z",
                "last_active_at": "2025-01-17T12:00:00Z",
                "created_at": "2025-01-17T10:00:00Z",
                "updated_at": "2025-01-17T12:00:00Z",
                "sport_preferences": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "sport_id": "550e8400-e29b-41d4-a716-446655440002",
                        "rank": 1,
                        "is_active": True,
                        "sport": {
                            "id": "550e8400-e29b-41d4-a716-446655440002",
                            "name": "Basketball",
                            "slug": "basketball",
                            "has_teams": True
                        }
                    }
                ],
                "team_preferences": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "team_id": "550e8400-e29b-41d4-a716-446655440004",
                        "affinity_score": 0.9,
                        "is_active": True,
                        "team": {
                            "id": "550e8400-e29b-41d4-a716-446655440004",
                            "name": "Lakers",
                            "market": "Los Angeles",
                            "league": "NBA"
                        }
                    }
                ]
            }
        }