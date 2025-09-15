"""User models and schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum

from .base import BaseSchema, TimestampedSchema


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


class UserPreferences(BaseSchema):
    """User preferences model."""

    # Theme preferences
    theme: str = Field(default="light", description="UI theme preference")
    language: str = Field(default="en", description="Language preference")
    timezone: str = Field(default="UTC", description="Timezone preference")

    # Notification preferences
    email_notifications: bool = Field(default=True, description="Email notifications enabled")
    push_notifications: bool = Field(default=True, description="Push notifications enabled")

    # Sports preferences
    favorite_teams: List[str] = Field(default_factory=list, description="List of favorite team IDs")
    favorite_sports: List[str] = Field(default_factory=list, description="List of favorite sports")

    # Content preferences
    content_categories: List[str] = Field(default_factory=list, description="Preferred content categories")
    ai_summary_enabled: bool = Field(default=True, description="AI summary feature enabled")


class UserBase(BaseSchema):
    """Base user model with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    image_url: Optional[str] = Field(None, description="Profile image URL")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")


class UserCreate(UserBase):
    """User creation model."""

    clerk_user_id: str = Field(..., description="Clerk user ID")
    preferences: Optional[UserPreferences] = Field(default_factory=UserPreferences)


class UserUpdate(BaseSchema):
    """User update model."""

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    status: Optional[UserStatus] = None


class User(UserBase, TimestampedSchema):
    """Complete user model."""

    id: str = Field(..., description="User ID")
    clerk_user_id: str = Field(..., description="Clerk user ID")
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    @validator('username')
    def validate_username(cls, v):
        if v and len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v


class UserResponse(BaseSchema):
    """User response model."""

    id: str
    email: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    image_url: Optional[str]
    role: UserRole
    status: UserStatus
    preferences: UserPreferences
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]


class UserListResponse(BaseSchema):
    """User list response model."""

    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class UserPreferencesUpdate(BaseSchema):
    """User preferences update model."""

    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    favorite_teams: Optional[List[str]] = None
    favorite_sports: Optional[List[str]] = None
    content_categories: Optional[List[str]] = None
    ai_summary_enabled: Optional[bool] = None


class CurrentUser(BaseSchema):
    """Current authenticated user model."""

    user_id: str = Field(..., description="Current user ID")
    email: str = Field(..., description="Current user email")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    image_url: Optional[str] = None
    role: UserRole = UserRole.USER
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    @classmethod
    def from_jwt_payload(cls, payload: Dict[str, Any]) -> "CurrentUser":
        """Create CurrentUser from JWT payload."""
        return cls(
            user_id=payload.get("sub", ""),
            email=payload.get("email", ""),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            username=payload.get("username"),
            image_url=payload.get("image_url")
        )