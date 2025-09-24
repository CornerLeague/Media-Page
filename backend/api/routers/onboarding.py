"""
Onboarding API endpoints
"""

import logging
import re
import time
from typing import List, Dict, Any, Union
from uuid import UUID
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
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
from backend.api.middleware.logging import APIEndpointLogger

logger = APIEndpointLogger("onboarding")

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# UUID validation pattern
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


def validate_and_sanitize_sport_ids(sport_ids: Union[List[str], str]) -> List[str]:
    """
    Validate and sanitize sport IDs parameter input

    Args:
        sport_ids: Sport UUIDs as array or comma-separated string

    Returns:
        List of validated UUID strings

    Raises:
        HTTPException: If validation fails with detailed error message
    """
    try:
        # Convert sport_ids to list of strings, handling both array and comma-separated formats
        sport_id_strings = []

        if isinstance(sport_ids, str):
            # Single string parameter - may be comma-separated
            # First, URL decode the string to handle encoded commas (%2C)
            decoded_sport_ids = unquote(sport_ids).strip()

            # Basic input sanitization - remove any potentially harmful characters
            # Allow only UUID-valid characters, commas, and whitespace
            sanitized_input = re.sub(r'[^a-fA-F0-9\-,\s]', '', decoded_sport_ids)

            if sanitized_input != decoded_sport_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid characters detected in sport IDs. Only UUID format (hexadecimal digits, hyphens) and commas are allowed."
                )

            # Split on commas if present
            if ',' in sanitized_input:
                sport_id_strings = [id_str.strip() for id_str in sanitized_input.split(',') if id_str.strip()]
            else:
                sport_id_strings = [sanitized_input] if sanitized_input else []
        else:
            # List of strings - may contain comma-separated values in individual items
            for sport_id_str in sport_ids:
                if not isinstance(sport_id_str, str):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"All sport IDs must be strings, got: {type(sport_id_str).__name__}"
                    )

                # URL decode each item
                decoded_sport_id = unquote(sport_id_str).strip()

                # Basic input sanitization
                sanitized_input = re.sub(r'[^a-fA-F0-9\-,\s]', '', decoded_sport_id)

                if sanitized_input != decoded_sport_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid characters detected in sport IDs. Only UUID format (hexadecimal digits, hyphens) and commas are allowed."
                    )

                # Handle comma-separated values within individual list items
                if ',' in sanitized_input:
                    sport_id_strings.extend([id_str.strip() for id_str in sanitized_input.split(',') if id_str.strip()])
                else:
                    if sanitized_input:
                        sport_id_strings.append(sanitized_input)

        # Remove empty strings and duplicates while preserving order
        seen = set()
        validated_sport_ids = []
        for sport_id_str in sport_id_strings:
            if sport_id_str and sport_id_str not in seen:
                # Validate UUID format before adding
                if not UUID_PATTERN.match(sport_id_str):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid UUID format for sport ID: '{sport_id_str}'. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    )
                seen.add(sport_id_str)
                validated_sport_ids.append(sport_id_str)

        if not validated_sport_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one valid sport ID is required. Provide UUIDs in format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            )

        return validated_sport_ids

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during sport ID validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sport IDs parameter format. Expected UUID(s) in format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )


# Dependency to get OnboardingService
async def get_onboarding_service(db: AsyncSession = Depends(get_async_session)) -> OnboardingService:
    """Dependency to get OnboardingService instance"""
    return OnboardingService(db)


@router.get("/sports", response_model=OnboardingSportsListResponse)
async def get_onboarding_sports(
    request: Request,
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingSportsListResponse:
    """
    Get list of available sports for onboarding step 2

    Returns sports ordered by popularity rank with metadata for onboarding UI.
    This endpoint does not require authentication as it provides public sports data.
    """
    logger.log_endpoint_start(request)

    start_time = time.time()
    try:
        result = await onboarding_service.get_onboarding_sports()

        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_success(
            request,
            f"Retrieved {len(result.sports)} sports",
            duration_ms=duration_ms,
            sports_count=len(result.sports)
        )

        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_error(request, e, duration_ms=duration_ms)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sports data"
        )


@router.get("/teams", response_model=OnboardingTeamsListResponse)
async def get_onboarding_teams(
    request: Request,
    sport_ids: Union[List[str], str] = Query(..., description="Sport UUIDs as array or comma-separated string"),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingTeamsListResponse:
    """
    Get list of teams for onboarding step 3, filtered by selected sports

    Args:
        sport_ids: Sport UUIDs as array format (?sport_ids=uuid1&sport_ids=uuid2)
                  or comma-separated string (?sport_ids=uuid1,uuid2,uuid3)
                  Supports URL-encoded commas (?sport_ids=uuid1%2Cuuid2%2Cuuid3)

    Returns teams belonging to the specified sports with league information.
    This endpoint does not require authentication as it provides public team data.
    """
    logger.log_endpoint_start(request, sport_ids_raw=str(sport_ids))

    start_time = time.time()
    try:
        # Validate and sanitize sport IDs parameter input
        validated_sport_id_strings = validate_and_sanitize_sport_ids(sport_ids)
        logger.log_business_logic_event(
            request,
            "sport_ids_validated",
            {"original_input": str(sport_ids), "validated_count": len(validated_sport_id_strings)}
        )

        # Convert validated string UUIDs to UUID objects
        parsed_sport_ids = []
        for sport_id_str in validated_sport_id_strings:
            try:
                parsed_sport_ids.append(UUID(sport_id_str))
            except ValueError as ve:
                # This should not happen due to pre-validation, but keeping for safety
                logger.log_validation_error(
                    request,
                    f"UUID conversion failed for pre-validated ID '{sport_id_str}': {str(ve)}",
                    failed_id=sport_id_str
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid UUID format for sport ID: '{sport_id_str}'. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                )

        result = await onboarding_service.get_onboarding_teams(parsed_sport_ids)

        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_success(
            request,
            f"Retrieved teams for {len(parsed_sport_ids)} sports",
            duration_ms=duration_ms,
            sport_count=len(parsed_sport_ids),
            teams_returned=sum(len(league.teams) for league in result.leagues)
        )

        return result

    except HTTPException as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_validation_error(
            request,
            f"HTTP validation error: {e.detail}",
            status_code=e.status_code,
            duration_ms=duration_ms
        )
        raise
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_error(request, e, duration_ms=duration_ms)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve teams data"
        )


# Protected endpoints - require authentication

@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    request: Request,
    current_user: User = Depends(get_current_db_user),
    onboarding_service: OnboardingService = Depends(get_onboarding_service)
) -> OnboardingStatusResponse:
    """
    Get current user's onboarding progress status

    Requires: Valid Firebase JWT token
    Returns: Current onboarding step and completion status
    """
    logger.log_endpoint_start(request, user_id=str(current_user.id))

    start_time = time.time()
    try:
        result = await onboarding_service.get_onboarding_status(current_user)

        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_success(
            request,
            f"Retrieved onboarding status for user {current_user.id}",
            duration_ms=duration_ms,
            current_step=result.current_step,
            is_completed=result.is_completed
        )

        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_error(
            request,
            e,
            duration_ms=duration_ms,
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding status"
        )


@router.put("/step", response_model=OnboardingStatusResponse)
async def update_onboarding_step(
    request: Request,
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
    logger.log_endpoint_start(
        request,
        user_id=str(current_user.id),
        new_step=step_update.step,
        current_step=current_user.current_onboarding_step
    )

    start_time = time.time()
    try:
        result = await onboarding_service.update_onboarding_step(current_user, step_update.step)

        duration_ms = (time.time() - start_time) * 1000
        logger.log_business_logic_event(
            request,
            "onboarding_step_updated",
            {
                "user_id": str(current_user.id),
                "previous_step": current_user.current_onboarding_step,
                "new_step": step_update.step,
                "duration_ms": duration_ms
            }
        )

        logger.log_endpoint_success(
            request,
            f"Updated onboarding step to {step_update.step}",
            duration_ms=duration_ms,
            new_step=step_update.step
        )

        return result
    except ValueError as ve:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_validation_error(
            request,
            f"Invalid step value: {str(ve)}",
            requested_step=step_update.step,
            duration_ms=duration_ms
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_error(
            request,
            e,
            duration_ms=duration_ms,
            user_id=str(current_user.id),
            requested_step=step_update.step
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update onboarding step"
        )


@router.post("/complete", response_model=OnboardingCompletionResponse)
async def complete_onboarding(
    request: Request,
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
    logger.log_endpoint_start(
        request,
        user_id=str(current_user.id),
        force_complete=completion_request.force_complete,
        current_step=current_user.current_onboarding_step
    )

    start_time = time.time()
    try:
        response = await onboarding_service.complete_onboarding(
            current_user,
            force_complete=completion_request.force_complete
        )

        if not response.success:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_business_logic_event(
                request,
                "onboarding_completion_failed",
                {
                    "user_id": str(current_user.id),
                    "reason": response.message,
                    "force_complete": completion_request.force_complete,
                    "duration_ms": duration_ms
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )

        duration_ms = (time.time() - start_time) * 1000
        logger.log_business_logic_event(
            request,
            "onboarding_completed",
            {
                "user_id": str(current_user.id),
                "completion_timestamp": response.completed_at,
                "force_complete": completion_request.force_complete,
                "duration_ms": duration_ms
            }
        )

        logger.log_endpoint_success(
            request,
            f"Onboarding completed for user {current_user.id}",
            duration_ms=duration_ms,
            completed_at=response.completed_at
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_error(
            request,
            e,
            duration_ms=duration_ms,
            user_id=str(current_user.id),
            force_complete=completion_request.force_complete
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete onboarding"
        )


@router.post("/reset", response_model=OnboardingStatusResponse)
async def reset_onboarding(
    request: Request,
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
    logger.log_endpoint_start(request, user_id=str(current_user.id))

    start_time = time.time()
    try:
        result = await onboarding_service.reset_onboarding(current_user)

        duration_ms = (time.time() - start_time) * 1000
        logger.log_business_logic_event(
            request,
            "onboarding_reset",
            {"user_id": str(current_user.id), "duration_ms": duration_ms}
        )

        logger.log_endpoint_success(request, f"Reset onboarding for user {current_user.id}", duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_error(request, e, duration_ms=duration_ms, user_id=str(current_user.id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset onboarding"
        )


@router.get("/stats")
async def get_onboarding_stats(
    request: Request,
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
    logger.log_endpoint_start(request, user_id=str(current_user.id))

    start_time = time.time()
    try:
        result = await onboarding_service.get_onboarding_progress_stats()

        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_success(
            request,
            "Retrieved onboarding statistics",
            duration_ms=duration_ms,
            stats_retrieved=True
        )

        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_endpoint_error(request, e, duration_ms=duration_ms)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding statistics"
        )