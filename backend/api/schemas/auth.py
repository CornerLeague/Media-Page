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


class FirebaseUser(BaseModel):
    """Firebase user data from authentication"""
    uid: str = Field(..., description="Firebase user UID")
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: bool = False
    provider_data: Optional[dict] = Field(default_factory=dict)
    custom_claims: Optional[dict] = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "uid": "firebase_user_123abc456def",
                "email": "user@example.com",
                "display_name": "John Doe",
                "photo_url": "https://example.com/avatar.jpg",
                "email_verified": True,
                "provider_data": [],
                "custom_claims": {}
            }
        }


class OnboardingStatus(BaseModel):
    """Onboarding status response schema"""
    hasCompletedOnboarding: bool = Field(..., description="Whether user has completed onboarding")
    currentStep: Optional[int] = Field(None, description="Current onboarding step (1-5), null if completed")

    class Config:
        schema_extra = {
            "example": {
                "hasCompletedOnboarding": False,
                "currentStep": 2
            }
        }


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    firebase_uid: str = Field(..., description="Firebase authentication user ID")
    display_name: Optional[str] = Field(None, max_length=100, description="User's display name")
    email: Optional[EmailStr] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=50, description="User's last name")
    bio: Optional[str] = Field(None, description="User's biographical information")
    location: Optional[str] = Field(None, max_length=100, description="User's location")
    timezone: Optional[str] = Field("UTC", max_length=50, description="User's timezone")

    # Onboarding data
    sports: List[dict] = Field(default_factory=list, description="User's sport preferences")
    teams: List[dict] = Field(default_factory=list, description="User's team preferences")
    preferences: dict = Field(default_factory=dict, description="User's content preferences")

    class Config:
        schema_extra = {
            "example": {
                "firebase_uid": "firebase_user_123abc456def",
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
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None)
    location: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    content_frequency: Optional[ContentFrequency] = None
    avatar_url: Optional[str] = Field(None, max_length=500)

    class Config:
        use_enum_values = True


class UserProfile(BaseSchema, IDMixin, TimestampMixin):
    """Complete user profile response"""
    firebase_uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = "UTC"
    content_frequency: ContentFrequency
    is_active: bool
    is_verified: bool
    onboarding_completed_at: Optional[datetime] = None
    last_active_at: datetime
    email_verified_at: Optional[datetime] = None

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
                "firebase_uid": "firebase_user_123abc456def",
                "email": "john@example.com",
                "display_name": "John Doe",
                "first_name": "John",
                "last_name": "Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Sports enthusiast and Lakers fan from Los Angeles",
                "location": "Los Angeles, CA",
                "timezone": "America/Los_Angeles",
                "content_frequency": "standard",
                "is_active": True,
                "is_verified": True,
                "onboarding_completed_at": "2025-01-17T12:00:00Z",
                "last_active_at": "2025-01-17T12:00:00Z",
                "email_verified_at": "2025-01-17T10:30:00Z",
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