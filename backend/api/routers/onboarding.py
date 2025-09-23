"""
Onboarding API endpoints
"""

import logging
from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session
from backend.api.services.user_service import get_current_db_user
from backend.api.services.onboarding_service import OnboardingService
from backend.models.users import User
from backend.api.schemas.onboarding import (
    OnboardingStepUpdate,
    OnboardingStatusResponse,
    OnboardingCompletionRequest,
    OnboardingCompletionResponse,
    OnboardingSportsListResponse,
    OnboardingTeamsListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# Dependency to get OnboardingService
async def get_onboarding_service(db: AsyncSession = Depends(get_async_session)) -> OnboardingService:
    """Dependency to get OnboardingService instance"""
    return OnboardingService(db)


@router.get("/sports", response_model=OnboardingSportsListResponse)
async def get_onboarding_sports(
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingSportsListResponse:
    """
    Get list of available sports for onboarding step 2

    Returns sports ordered by popularity rank with metadata for onboarding UI.
    This endpoint does not require authentication as it provides public sports data.
    """
    try:
        return await onboarding_service.get_onboarding_sports()
    except Exception as e:
        logger.error(f"Error retrieving onboarding sports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sports data"
        )


@router.get("/teams", response_model=OnboardingTeamsListResponse)
async def get_onboarding_teams(
    sport_ids: List[str] = Query(..., description="Comma-separated list of sport UUIDs"),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingTeamsListResponse:
    """
    Get list of teams for onboarding step 3, filtered by selected sports

    Args:
        sport_ids: List of sport UUIDs to filter teams by

    Returns teams belonging to the specified sports with league information.
    This endpoint does not require authentication as it provides public team data.
    """
    try:
        # Convert string UUIDs to UUID objects
        parsed_sport_ids = []
        for sport_id_str in sport_ids:
            try:
                # Handle comma-separated values in single parameter
                if ',' in sport_id_str:
                    for id_part in sport_id_str.split(','):
                        parsed_sport_ids.append(UUID(id_part.strip()))
                else:
                    parsed_sport_ids.append(UUID(sport_id_str))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid sport ID format: {sport_id_str}"
                )

        if not parsed_sport_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one sport ID is required"
            )

        return await onboarding_service.get_onboarding_teams(parsed_sport_ids)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving onboarding teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve teams data"
        )


# Protected endpoints - require authentication

@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_db_user),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingStatusResponse:
    """
    Get current user's onboarding progress status

    Requires: Valid Firebase JWT token
    Returns: Current onboarding step and completion status
    """
    try:
        return await onboarding_service.get_onboarding_status(current_user)
    except Exception as e:
        logger.error(f"Error retrieving onboarding status for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding status"
        )


@router.get("/status/new-user", response_model=OnboardingStatusResponse)
async def get_new_user_onboarding_status() -> OnboardingStatusResponse:
    """
    Get default onboarding status for new/unauthenticated users

    This endpoint provides a fallback for when authentication is not yet configured
    or for new users who haven't completed Firebase setup.

    Returns: Default onboarding status indicating the user should start onboarding
    """
    # Return default status for new users - onboarding not complete
    return OnboardingStatusResponse(
        is_onboarded=False,
        current_step=1,
        onboarding_completed_at=None
    )


@router.put("/step", response_model=OnboardingStatusResponse)
async def update_onboarding_step(
    step_update: OnboardingStepUpdate,
    current_user: User = Depends(get_current_db_user),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingStatusResponse:
    """
    Update current user's onboarding step

    Requires: Valid Firebase JWT token
    Args:
        step_update: New step number (1-5)
    Returns: Updated onboarding status
    """
    try:
        return await onboarding_service.update_onboarding_step(current_user, step_update.step)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error updating onboarding step for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update onboarding step"
        )


@router.post("/complete", response_model=OnboardingCompletionResponse)
async def complete_onboarding(
    completion_request: OnboardingCompletionRequest,
    current_user: User = Depends(get_current_db_user),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingCompletionResponse:
    """
    Mark user's onboarding as complete

    Requires: Valid Firebase JWT token
    Args:
        completion_request: Completion parameters
    Returns: Completion status and timestamp

    This endpoint validates that the user has completed the necessary
    preference selections before marking onboarding as complete.
    """
    try:
        response = await onboarding_service.complete_onboarding(
            current_user,
            force_complete=completion_request.force_complete
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing onboarding for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete onboarding"
        )


@router.post("/reset", response_model=OnboardingStatusResponse)
async def reset_onboarding(
    current_user: User = Depends(get_current_db_user),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingStatusResponse:
    """
    Reset user's onboarding status (for testing/admin purposes)

    Requires: Valid Firebase JWT token
    Returns: Reset onboarding status

    WARNING: This will reset the user's onboarding completion status
    and set them back to step 1. Use with caution.
    """
    try:
        return await onboarding_service.reset_onboarding(current_user)
    except Exception as e:
        logger.error(f"Error resetting onboarding for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset onboarding"
        )


@router.get("/stats")
async def get_onboarding_stats(
    current_user: User = Depends(get_current_db_user),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """
    Get aggregated onboarding statistics (admin/analytics endpoint)

    Requires: Valid Firebase JWT token
    Returns: Onboarding completion rates and step distribution

    Note: In production, this endpoint should have additional
    authorization checks for admin users only.
    """
    try:
        return await onboarding_service.get_onboarding_progress_stats()
    except Exception as e:
        logger.error(f"Error retrieving onboarding stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding statistics"
        )