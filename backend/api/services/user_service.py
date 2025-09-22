"""
User service for handling authenticated user operations and context extraction
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status

from backend.models.users import User
from backend.api.schemas.auth import FirebaseUser, UserProfile
from backend.api.middleware.auth import firebase_auth_required, firebase_auth_optional
from backend.database import get_async_session

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations with Firebase authentication"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """
        Get user by Firebase UID

        Args:
            firebase_uid: Firebase authentication UID

        Returns:
            User model if found, None otherwise
        """
        try:
            result = await self.db.execute(
                select(User).where(User.firebase_uid == firebase_uid)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user by Firebase UID {firebase_uid}: {str(e)}")
            return None

    async def get_user_profile(self, firebase_uid: str) -> Optional[UserProfile]:
        """
        Get complete user profile with preferences

        Args:
            firebase_uid: Firebase authentication UID

        Returns:
            UserProfile if user exists, None otherwise
        """
        user = await self.get_user_by_firebase_uid(firebase_uid)
        if not user:
            return None

        # Convert to UserProfile schema (relationships are already loaded via selectin)
        return UserProfile.from_orm(user)

    async def create_or_update_user_from_firebase(
        self,
        firebase_user: FirebaseUser,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Create or update user from Firebase authentication data

        Args:
            firebase_user: Firebase user information
            additional_data: Additional user data to update

        Returns:
            Created or updated User model
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_firebase_uid(firebase_user.uid)

            if existing_user:
                # Update existing user with fresh Firebase data
                existing_user.email = firebase_user.email
                existing_user.display_name = firebase_user.display_name
                existing_user.avatar_url = firebase_user.photo_url

                # Update email verification status
                if firebase_user.email_verified and not existing_user.email_verified_at:
                    from datetime import datetime, timezone
                    existing_user.email_verified_at = datetime.now(timezone.utc)
                    existing_user.is_verified = True

                # Update with additional data if provided
                if additional_data:
                    for key, value in additional_data.items():
                        if hasattr(existing_user, key):
                            setattr(existing_user, key, value)

                await self.db.commit()
                await self.db.refresh(existing_user)
                return existing_user

            else:
                # Create new user
                from datetime import datetime, timezone

                new_user_data = {
                    "firebase_uid": firebase_user.uid,
                    "email": firebase_user.email,
                    "display_name": firebase_user.display_name,
                    "avatar_url": firebase_user.photo_url,
                    "is_verified": firebase_user.email_verified,
                    "last_active_at": datetime.now(timezone.utc)
                }

                if firebase_user.email_verified:
                    new_user_data["email_verified_at"] = datetime.now(timezone.utc)

                # Add additional data if provided
                if additional_data:
                    new_user_data.update(additional_data)

                new_user = User(**new_user_data)
                self.db.add(new_user)
                await self.db.commit()
                await self.db.refresh(new_user)
                return new_user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating/updating user from Firebase: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or update user"
            )

    async def update_last_active(self, firebase_uid: str) -> None:
        """
        Update user's last active timestamp

        Args:
            firebase_uid: Firebase authentication UID
        """
        try:
            user = await self.get_user_by_firebase_uid(firebase_uid)
            if user:
                from datetime import datetime, timezone
                user.last_active_at = datetime.now(timezone.utc)
                await self.db.commit()
        except Exception as e:
            logger.error(f"Error updating last active for user {firebase_uid}: {str(e)}")


class AuthenticatedUserContext:
    """Context class for authenticated user operations"""

    def __init__(
        self,
        firebase_user: FirebaseUser,
        db_user: Optional[User] = None,
        user_service: Optional[UserService] = None
    ):
        self.firebase_user = firebase_user
        self.db_user = db_user
        self.user_service = user_service

    @property
    def firebase_uid(self) -> str:
        """Get Firebase UID"""
        return self.firebase_user.uid

    @property
    def email(self) -> Optional[str]:
        """Get user email"""
        return self.firebase_user.email

    @property
    def display_name(self) -> Optional[str]:
        """Get user display name"""
        return self.firebase_user.display_name

    @property
    def is_verified(self) -> bool:
        """Check if user email is verified"""
        return self.firebase_user.email_verified

    async def get_or_create_db_user(self) -> User:
        """
        Get or create database user record

        Returns:
            User model from database
        """
        if self.db_user:
            return self.db_user

        if not self.user_service:
            raise RuntimeError("UserService not available in context")

        # Create or update user from Firebase data
        self.db_user = await self.user_service.create_or_update_user_from_firebase(
            self.firebase_user
        )
        return self.db_user

    async def get_user_profile(self) -> Optional[UserProfile]:
        """
        Get complete user profile

        Returns:
            UserProfile if user exists
        """
        if not self.user_service:
            raise RuntimeError("UserService not available in context")

        return await self.user_service.get_user_profile(self.firebase_uid)


# Dependency functions for FastAPI

async def get_user_service(db: AsyncSession = Depends(get_async_session)) -> UserService:
    """Dependency to get UserService instance"""
    return UserService(db)


async def get_current_user_context(
    firebase_user: FirebaseUser = Depends(firebase_auth_required),
    user_service: UserService = Depends(get_user_service)
) -> AuthenticatedUserContext:
    """
    Dependency to get authenticated user context with database integration

    Args:
        firebase_user: Authenticated Firebase user
        user_service: User service instance

    Returns:
        AuthenticatedUserContext with Firebase and database user data
    """
    # Get database user
    db_user = await user_service.get_user_by_firebase_uid(firebase_user.uid)

    # Update last active timestamp
    await user_service.update_last_active(firebase_user.uid)

    return AuthenticatedUserContext(
        firebase_user=firebase_user,
        db_user=db_user,
        user_service=user_service
    )


async def get_current_user_context_optional(
    firebase_user: Optional[FirebaseUser] = Depends(firebase_auth_optional),
    user_service: UserService = Depends(get_user_service)
) -> Optional[AuthenticatedUserContext]:
    """
    Dependency to get optional authenticated user context

    Args:
        firebase_user: Optional authenticated Firebase user
        user_service: User service instance

    Returns:
        AuthenticatedUserContext if authenticated, None otherwise
    """
    if not firebase_user:
        return None

    # Get database user
    db_user = await user_service.get_user_by_firebase_uid(firebase_user.uid)

    # Update last active timestamp
    await user_service.update_last_active(firebase_user.uid)

    return AuthenticatedUserContext(
        firebase_user=firebase_user,
        db_user=db_user,
        user_service=user_service
    )


async def get_current_db_user(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> User:
    """
    Dependency to get current authenticated database user

    Args:
        user_context: Authenticated user context

    Returns:
        User model from database

    Raises:
        HTTPException: If user doesn't exist in database
    """
    db_user = await user_context.get_or_create_db_user()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


async def require_onboarded_user(
    db_user: User = Depends(get_current_db_user)
) -> User:
    """
    Dependency that requires user to have completed onboarding

    Args:
        db_user: Current authenticated database user

    Returns:
        User model if onboarding is complete

    Raises:
        HTTPException: If user hasn't completed onboarding
    """
    if not db_user.is_onboarded:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Onboarding required",
            headers={"X-Error-Code": "ONBOARDING_REQUIRED"}
        )
    return db_user


async def require_onboarding_in_progress(
    db_user: User = Depends(get_current_db_user)
) -> User:
    """
    Dependency that requires user to be in onboarding process

    Args:
        db_user: Current authenticated database user

    Returns:
        User model if onboarding is in progress

    Raises:
        HTTPException: If user has already completed onboarding
    """
    if db_user.is_onboarded:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding already completed",
            headers={"X-Error-Code": "ONBOARDING_COMPLETED"}
        )
    return db_user


async def require_onboarding_step(
    required_step: int,
    db_user: User = Depends(get_current_db_user)
) -> User:
    """
    Dependency factory that requires user to be on a specific onboarding step

    Args:
        required_step: The required onboarding step (1-5)
        db_user: Current authenticated database user

    Returns:
        User model if on the required step

    Raises:
        HTTPException: If user is not on the required step
    """
    if db_user.is_onboarded:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding already completed",
            headers={"X-Error-Code": "ONBOARDING_COMPLETED"}
        )

    if db_user.current_onboarding_step != required_step:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected onboarding step {required_step}, but user is on step {db_user.current_onboarding_step}",
            headers={"X-Error-Code": "INVALID_ONBOARDING_STEP"}
        )

    return db_user