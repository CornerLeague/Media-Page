"""Authentication service for user management."""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging

from ..core.security import verify_clerk_token, extract_user_metadata
from ..models.user import CurrentUser
from .redis_service import RedisService

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for handling user authentication and sessions."""

    def __init__(self, redis_service: RedisService):
        self.redis = redis_service

    async def authenticate_user(self, token: str) -> CurrentUser:
        """Authenticate user with JWT token."""
        try:
            # Verify token and get payload
            payload = await verify_clerk_token(token)

            # Extract user metadata
            user_metadata = extract_user_metadata(payload)

            # Create current user object
            current_user = CurrentUser.from_jwt_payload(payload)

            # Cache user session
            await self._cache_user_session(current_user.user_id, user_metadata)

            return current_user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )

    async def get_current_user_from_cache(
        self, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get current user data from cache."""
        try:
            cache_key = f"user_session:{user_id}"
            cached_data = await self.redis.get_json(cache_key)
            return cached_data
        except Exception as e:
            logger.error(f"Error getting user from cache: {str(e)}")
            return None

    async def _cache_user_session(
        self,
        user_id: str,
        user_metadata: Dict[str, Any],
        expire: int = 3600
    ) -> bool:
        """Cache user session data."""
        try:
            cache_key = f"user_session:{user_id}"
            session_data = {
                **user_metadata,
                "cached_at": str(int(time.time()))
            }
            return await self.redis.set_json(cache_key, session_data, expire)
        except Exception as e:
            logger.error(f"Error caching user session: {str(e)}")
            return False

    async def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session cache."""
        try:
            cache_key = f"user_session:{user_id}"
            return await self.redis.delete(cache_key)
        except Exception as e:
            logger.error(f"Error invalidating user session: {str(e)}")
            return False

    async def refresh_user_session(
        self,
        user_id: str,
        user_metadata: Dict[str, Any]
    ) -> bool:
        """Refresh user session in cache."""
        return await self._cache_user_session(user_id, user_metadata)

    async def is_user_active(self, user_id: str) -> bool:
        """Check if user has an active session."""
        try:
            cache_key = f"user_session:{user_id}"
            return await self.redis.exists(cache_key)
        except Exception as e:
            logger.error(f"Error checking user active status: {str(e)}")
            return False

    async def get_active_users_count(self) -> int:
        """Get count of active users."""
        try:
            # This is a simplified implementation
            # In production, you might want to use Redis SCAN
            # to count keys matching pattern "user_session:*"
            return 0  # Placeholder
        except Exception as e:
            logger.error(f"Error getting active users count: {str(e)}")
            return 0

    async def logout_user(self, user_id: str) -> bool:
        """Logout user by invalidating session."""
        return await self.invalidate_user_session(user_id)

    async def validate_user_permissions(
        self,
        user_id: str,
        required_permissions: list = None
    ) -> bool:
        """Validate user permissions (placeholder for future implementation)."""
        # This is a placeholder for future permission system
        # Currently, all authenticated users have basic permissions
        return True


# Global auth service instance
_auth_service: Optional[AuthService] = None


async def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    global _auth_service

    if _auth_service is None:
        from .redis_service import get_redis_service
        redis_service = await get_redis_service()
        _auth_service = AuthService(redis_service)

    return _auth_service


import time