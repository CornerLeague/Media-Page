"""User service for user management operations."""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from ..models.user import (
    User, UserCreate, UserUpdate, UserResponse,
    UserPreferences, UserPreferencesUpdate, CurrentUser
)
from .redis_service import RedisService

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations."""

    def __init__(self, redis_service: RedisService):
        self.redis = redis_service

    # Mock database operations (replace with actual database in production)
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            # Check cache first
            cached_user = await self.redis.get_user_data(user_id)
            if cached_user:
                return UserResponse(**cached_user)

            # Mock user data (replace with database query)
            mock_user_data = {
                "id": user_id,
                "email": "user@example.com",
                "username": "user123",
                "first_name": "John",
                "last_name": "Doe",
                "image_url": "https://example.com/avatar.jpg",
                "role": "user",
                "status": "active",
                "preferences": {
                    "theme": "light",
                    "language": "en",
                    "timezone": "UTC",
                    "email_notifications": True,
                    "push_notifications": True,
                    "favorite_teams": [],
                    "favorite_sports": [],
                    "content_categories": [],
                    "ai_summary_enabled": True
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }

            # Cache user data
            await self.redis.cache_user_data(user_id, mock_user_data)

            return UserResponse(**mock_user_data)

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[UserResponse]:
        """Get user by Clerk user ID."""
        try:
            # Mock implementation - in production, query database
            # For now, assume clerk_user_id maps to user_id
            return await self.get_user_by_id(clerk_user_id)
        except Exception as e:
            logger.error(f"Error getting user by Clerk ID {clerk_user_id}: {str(e)}")
            return None

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            # Mock user creation (replace with database insert)
            new_user_data = {
                "id": user_data.clerk_user_id,  # Use Clerk ID as user ID
                "email": user_data.email,
                "username": user_data.username,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "image_url": user_data.image_url,
                "role": user_data.role.value,
                "status": user_data.status.value,
                "preferences": user_data.preferences.dict() if user_data.preferences else UserPreferences().dict(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None
            }

            # Cache new user
            await self.redis.cache_user_data(new_user_data["id"], new_user_data)

            return UserResponse(**new_user_data)

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserResponse]:
        """Update user information."""
        try:
            # Get existing user
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                return None

            # Update fields
            update_data = user_update.dict(exclude_unset=True)
            user_data = existing_user.dict()
            user_data.update(update_data)
            user_data["updated_at"] = datetime.utcnow().isoformat()

            # Cache updated user
            await self.redis.cache_user_data(user_id, user_data)

            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return None

    async def update_user_preferences(
        self,
        user_id: str,
        preferences_update: UserPreferencesUpdate
    ) -> Optional[UserResponse]:
        """Update user preferences."""
        try:
            # Get existing user
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                return None

            # Update preferences
            current_preferences = existing_user.preferences.dict()
            update_data = preferences_update.dict(exclude_unset=True)
            current_preferences.update(update_data)

            # Update user
            user_data = existing_user.dict()
            user_data["preferences"] = current_preferences
            user_data["updated_at"] = datetime.utcnow().isoformat()

            # Cache updated user
            await self.redis.cache_user_data(user_id, user_data)

            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error updating user preferences {user_id}: {str(e)}")
            return None

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        try:
            # Get existing user
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                return False

            # Update last login
            user_data = existing_user.dict()
            user_data["last_login"] = datetime.utcnow().isoformat()
            user_data["updated_at"] = datetime.utcnow().isoformat()

            # Cache updated user
            await self.redis.cache_user_data(user_id, user_data)
            return True

        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            return False

    async def get_user_favorite_teams(self, user_id: str) -> List[str]:
        """Get user's favorite team IDs."""
        try:
            user = await self.get_user_by_id(user_id)
            if user and user.preferences:
                return user.preferences.favorite_teams
            return []
        except Exception as e:
            logger.error(f"Error getting favorite teams for user {user_id}: {str(e)}")
            return []

    async def add_favorite_team(self, user_id: str, team_id: str) -> bool:
        """Add team to user's favorites."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False

            favorite_teams = user.preferences.favorite_teams
            if team_id not in favorite_teams:
                favorite_teams.append(team_id)

                # Update preferences
                preferences_update = UserPreferencesUpdate(favorite_teams=favorite_teams)
                updated_user = await self.update_user_preferences(user_id, preferences_update)
                return updated_user is not None

            return True  # Already in favorites

        except Exception as e:
            logger.error(f"Error adding favorite team {team_id} for user {user_id}: {str(e)}")
            return False

    async def remove_favorite_team(self, user_id: str, team_id: str) -> bool:
        """Remove team from user's favorites."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False

            favorite_teams = user.preferences.favorite_teams
            if team_id in favorite_teams:
                favorite_teams.remove(team_id)

                # Update preferences
                preferences_update = UserPreferencesUpdate(favorite_teams=favorite_teams)
                updated_user = await self.update_user_preferences(user_id, preferences_update)
                return updated_user is not None

            return True  # Not in favorites

        except Exception as e:
            logger.error(f"Error removing favorite team {team_id} for user {user_id}: {str(e)}")
            return False

    async def delete_user_cache(self, user_id: str) -> bool:
        """Delete user cache."""
        try:
            return await self.redis.invalidate_user_cache(user_id)
        except Exception as e:
            logger.error(f"Error deleting user cache for {user_id}: {str(e)}")
            return False


# Global user service instance
_user_service: Optional[UserService] = None


async def get_user_service() -> UserService:
    """Get user service instance."""
    global _user_service

    if _user_service is None:
        from .redis_service import get_redis_service
        redis_service = await get_redis_service()
        _user_service = UserService(redis_service)

    return _user_service