"""User management routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from ..deps import get_current_active_user, get_user, get_current_admin_user
from ...models.user import (
    CurrentUser, UserResponse, UserUpdate, UserPreferencesUpdate,
    UserPreferences
)
from ...models.base import BaseResponse
from ...services.user_service import UserService

router = APIRouter()


class UserUpdateResponse(BaseResponse):
    """User update response model."""

    user: UserResponse


class UserPreferencesResponse(BaseResponse):
    """User preferences response model."""

    preferences: UserPreferences


class FavoriteTeamsResponse(BaseResponse):
    """Favorite teams response model."""

    teams: List[str]


class TeamActionRequest(BaseModel):
    """Team action request model."""

    team_id: str


@router.get(
    "/me",
    response_model=UserUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the current authenticated user's full profile information"
)
async def get_my_profile(
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Get current user's profile.

    Returns complete user profile including preferences and settings.
    """
    try:
        user_profile = await user_service.get_user_by_id(current_user.user_id)

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        return UserUpdateResponse(
            success=True,
            message="User profile retrieved successfully",
            user=user_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )


@router.put(
    "/me",
    response_model=UserUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update the current authenticated user's profile information"
)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Update current user's profile.

    Allows updating:
    - Username
    - First and last name
    - Image URL
    - Other profile fields
    """
    try:
        updated_user = await user_service.update_user(
            current_user.user_id,
            user_update
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserUpdateResponse(
            success=True,
            message="User profile updated successfully",
            user=updated_user
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )


@router.get(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user preferences",
    description="Get the current user's preferences and settings"
)
async def get_my_preferences(
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Get current user's preferences.

    Returns user preferences including:
    - Theme settings
    - Notification preferences
    - Favorite teams and sports
    - Content preferences
    """
    try:
        user_profile = await user_service.get_user_by_id(current_user.user_id)

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserPreferencesResponse(
            success=True,
            message="User preferences retrieved successfully",
            preferences=user_profile.preferences
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user preferences: {str(e)}"
        )


@router.put(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user preferences",
    description="Update the current user's preferences and settings"
)
async def update_my_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Update current user's preferences.

    Allows updating any user preference including:
    - Theme and language settings
    - Notification preferences
    - Favorite teams and sports
    - Content preferences
    """
    try:
        updated_user = await user_service.update_user_preferences(
            current_user.user_id,
            preferences_update
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserPreferencesResponse(
            success=True,
            message="User preferences updated successfully",
            preferences=updated_user.preferences
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preferences: {str(e)}"
        )


@router.get(
    "/me/teams",
    response_model=FavoriteTeamsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get favorite teams",
    description="Get the current user's favorite teams"
)
async def get_my_favorite_teams(
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Get current user's favorite teams.

    Returns a list of team IDs that the user follows.
    """
    try:
        favorite_teams = await user_service.get_user_favorite_teams(current_user.user_id)

        return FavoriteTeamsResponse(
            success=True,
            message="Favorite teams retrieved successfully",
            teams=favorite_teams
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve favorite teams: {str(e)}"
        )


@router.post(
    "/me/teams",
    response_model=FavoriteTeamsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add favorite team",
    description="Add a team to the current user's favorites"
)
async def add_favorite_team(
    request: TeamActionRequest,
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Add team to favorites.

    Adds a team to the user's favorite teams list.
    """
    try:
        success = await user_service.add_favorite_team(
            current_user.user_id,
            request.team_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add team to favorites"
            )

        # Get updated favorite teams
        favorite_teams = await user_service.get_user_favorite_teams(current_user.user_id)

        return FavoriteTeamsResponse(
            success=True,
            message="Team added to favorites successfully",
            teams=favorite_teams
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add favorite team: {str(e)}"
        )


@router.delete(
    "/me/teams/{team_id}",
    response_model=FavoriteTeamsResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove favorite team",
    description="Remove a team from the current user's favorites"
)
async def remove_favorite_team(
    team_id: str,
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Remove team from favorites.

    Removes a team from the user's favorite teams list.
    """
    try:
        success = await user_service.remove_favorite_team(
            current_user.user_id,
            team_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to remove team from favorites"
            )

        # Get updated favorite teams
        favorite_teams = await user_service.get_user_favorite_teams(current_user.user_id)

        return FavoriteTeamsResponse(
            success=True,
            message="Team removed from favorites successfully",
            teams=favorite_teams
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove favorite team: {str(e)}"
        )


@router.delete(
    "/me/cache",
    status_code=status.HTTP_200_OK,
    summary="Clear user cache",
    description="Clear the current user's cached data"
)
async def clear_my_cache(
    current_user: CurrentUser = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user)
):
    """
    Clear user cache.

    Clears all cached data for the current user.
    """
    try:
        success = await user_service.delete_user_cache(current_user.user_id)

        return {
            "success": success,
            "message": "User cache cleared successfully" if success else "Failed to clear cache"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear user cache: {str(e)}"
        )


# Admin-only routes
@router.get(
    "/{user_id}",
    response_model=UserUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID (Admin)",
    description="Get any user's profile by ID (Admin only)"
)
async def get_user_by_id(
    user_id: str,
    admin_user: CurrentUser = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user)
):
    """
    Get user by ID (Admin only).

    Allows administrators to view any user's profile.
    """
    try:
        user_profile = await user_service.get_user_by_id(user_id)

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserUpdateResponse(
            success=True,
            message="User profile retrieved successfully",
            user=user_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )