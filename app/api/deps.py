"""API dependencies for authentication and services."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from ..core.security import security, verify_clerk_token
from ..models.user import CurrentUser
from ..services.auth_service import get_auth_service, AuthService
from ..services.user_service import get_user_service, UserService
from ..services.redis_service import get_redis_service, RedisService


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user.

    This dependency:
    1. Extracts the JWT token from the Authorization header
    2. Validates the token with Clerk
    3. Returns the current user information
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Authenticate user with token
        current_user = await auth_service.authenticate_user(credentials.credentials)
        return current_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> CurrentUser:
    """
    Dependency to get the current active user.

    This dependency ensures the user has an active session.
    """
    # Check if user is active
    is_active = await auth_service.is_user_active(current_user.user_id)

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User session is not active"
        )

    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[CurrentUser]:
    """
    Dependency to optionally get the current user.

    Returns None if no valid token is provided, otherwise returns the user.
    Used for endpoints that can work with or without authentication.
    """
    if not credentials:
        return None

    try:
        current_user = await auth_service.authenticate_user(credentials.credentials)
        return current_user
    except:
        return None


# Service dependencies
async def get_redis() -> RedisService:
    """Get Redis service dependency."""
    return await get_redis_service()


async def get_auth() -> AuthService:
    """Get auth service dependency."""
    return await get_auth_service()


async def get_user() -> UserService:
    """Get user service dependency."""
    return await get_user_service()


# Admin user dependency
async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> CurrentUser:
    """
    Dependency to get the current admin user.

    Ensures the user has admin privileges.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return current_user


# Rate limiting dependency (placeholder for future implementation)
async def rate_limit_dependency():
    """
    Placeholder for rate limiting dependency.

    In production, this would implement rate limiting logic.
    """
    # TODO: Implement actual rate limiting
    pass