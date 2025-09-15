"""Authentication routes."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..deps import get_current_user, get_current_active_user, get_auth, get_user
from ...models.user import CurrentUser, UserResponse
from ...models.base import BaseResponse
from ...services.auth_service import AuthService
from ...services.user_service import UserService

router = APIRouter()


class LoginResponse(BaseResponse):
    """Login response model."""

    user: UserResponse
    session_token: Optional[str] = None


class LogoutResponse(BaseResponse):
    """Logout response model."""

    message: str = "Successfully logged out"


class SessionResponse(BaseResponse):
    """Session response model."""

    user: CurrentUser
    is_active: bool
    last_seen: datetime


@router.get(
    "/me",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get the current authenticated user's information"
)
async def get_current_user_info(
    current_user: CurrentUser = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth)
):
    """
    Get current authenticated user information.

    Returns:
    - User profile data
    - Session status
    - Last seen timestamp
    """
    is_active = await auth_service.is_user_active(current_user.user_id)

    return SessionResponse(
        success=True,
        message="User information retrieved successfully",
        user=current_user,
        is_active=is_active,
        last_seen=datetime.utcnow()
    )


@router.post(
    "/refresh",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh user session",
    description="Refresh the current user session and update last seen"
)
async def refresh_session(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth),
    user_service: UserService = Depends(get_user)
):
    """
    Refresh user session.

    This endpoint:
    1. Validates the current token
    2. Updates the user's last login time
    3. Refreshes the session cache
    4. Returns updated user information
    """
    try:
        # Update last login
        await user_service.update_last_login(current_user.user_id)

        # Refresh session in cache
        user_metadata = {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "username": current_user.username,
            "image_url": current_user.image_url,
            "role": current_user.role.value
        }
        await auth_service.refresh_user_session(current_user.user_id, user_metadata)

        is_active = await auth_service.is_user_active(current_user.user_id)

        return SessionResponse(
            success=True,
            message="Session refreshed successfully",
            user=current_user,
            is_active=is_active,
            last_seen=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh session: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout the current user and invalidate their session"
)
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth)
):
    """
    Logout current user.

    This endpoint:
    1. Invalidates the user's session cache
    2. Clears any temporary user data
    3. Returns logout confirmation
    """
    try:
        # Logout user (invalidate session)
        success = await auth_service.logout_user(current_user.user_id)

        if success:
            return LogoutResponse(
                success=True,
                message="Successfully logged out"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout user"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get(
    "/session/status",
    status_code=status.HTTP_200_OK,
    summary="Check session status",
    description="Check if the current session is valid and active"
)
async def check_session_status(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth)
):
    """
    Check session status.

    Returns information about the current session:
    - Whether the session is active
    - Session validity
    - User ID
    """
    try:
        is_active = await auth_service.is_user_active(current_user.user_id)

        return {
            "valid": True,
            "active": is_active,
            "user_id": current_user.user_id,
            "checked_at": datetime.utcnow()
        }

    except Exception as e:
        return {
            "valid": False,
            "active": False,
            "user_id": None,
            "error": str(e),
            "checked_at": datetime.utcnow()
        }


@router.get(
    "/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate token",
    description="Validate the provided JWT token and return user info"
)
async def validate_token(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Validate JWT token.

    This endpoint can be used by other services to validate
    tokens and get basic user information.
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.user_id,
            "email": current_user.email,
            "role": current_user.role.value
        },
        "validated_at": datetime.utcnow()
    }