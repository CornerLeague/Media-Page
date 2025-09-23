"""
Preference service for handling user preference operations
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from backend.models.users import User, UserSportPreference, UserTeamPreference, UserNotificationSettings
from backend.api.schemas.preferences import (
    SportPreferenceUpdate,
    TeamPreferenceUpdate,
    NotificationPreferencesUpdate,
    SportsPreferencesUpdate,
    TeamsPreferencesUpdate,
    PreferencesUpdate
)

logger = logging.getLogger(__name__)


class PreferenceService:
    """Service for user preference-related operations"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def update_sport_preferences(
        self,
        user: User,
        sports_update: List[SportPreferenceUpdate]
    ) -> List[UserSportPreference]:
        """
        Update user's sport preferences

        Args:
            user: User model
            sports_update: List of sport preference updates

        Returns:
            List of updated UserSportPreference models

        Raises:
            HTTPException: If validation or database operation fails
        """
        try:
            # Validate input
            if not sports_update:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one sport preference must be provided"
                )

            # Validate sports exist and ranks are unique
            existing_ranks = set()
            sport_ids_to_validate = set()

            for sport_update in sports_update:
                # Check for duplicate ranks
                if sport_update.rank in existing_ranks:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Duplicate rank {sport_update.rank} found in sport preferences"
                    )
                existing_ranks.add(sport_update.rank)
                sport_ids_to_validate.add(sport_update.sport_id)

            # Validate that all sports exist
            for sport_id in sport_ids_to_validate:
                if not await self.validate_sport_exists(sport_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Sport with ID {sport_id} does not exist"
                    )

            # Delete existing sport preferences
            await self.db.execute(
                delete(UserSportPreference).where(UserSportPreference.user_id == user.id)
            )

            # Create new sport preferences
            new_preferences = []
            for sport_update in sports_update:
                new_pref = UserSportPreference(
                    user_id=user.id,
                    sport_id=sport_update.sport_id,
                    rank=sport_update.rank,
                    is_active=sport_update.is_active
                )
                new_preferences.append(new_pref)
                self.db.add(new_pref)

            await self.db.commit()

            # Refresh to get related data
            for pref in new_preferences:
                await self.db.refresh(pref)

            return new_preferences

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating sport preferences for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update sport preferences"
            )

    async def update_team_preferences(
        self,
        user: User,
        teams_update: List[TeamPreferenceUpdate]
    ) -> List[UserTeamPreference]:
        """
        Update user's team preferences

        Args:
            user: User model
            teams_update: List of team preference updates

        Returns:
            List of updated UserTeamPreference models

        Raises:
            HTTPException: If validation or database operation fails
        """
        try:
            # Validate input
            if not teams_update:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one team preference must be provided"
                )

            # Validate teams exist and team IDs are unique
            team_ids = set()

            for team_update in teams_update:
                # Validate that team IDs are unique
                if team_update.team_id in team_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Duplicate team_id {team_update.team_id} found in team preferences"
                    )
                team_ids.add(team_update.team_id)

                # Validate affinity score range
                if not (0.0 <= team_update.affinity_score <= 1.0):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Affinity score {team_update.affinity_score} must be between 0.0 and 1.0"
                    )

            # Validate that all teams exist
            for team_id in team_ids:
                if not await self.validate_team_exists(team_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Team with ID {team_id} does not exist"
                    )

            # Delete existing team preferences
            await self.db.execute(
                delete(UserTeamPreference).where(UserTeamPreference.user_id == user.id)
            )

            # Create new team preferences
            new_preferences = []

            for team_update in teams_update:
                new_pref = UserTeamPreference(
                    user_id=user.id,
                    team_id=team_update.team_id,
                    affinity_score=Decimal(str(team_update.affinity_score)),
                    is_active=team_update.is_active
                )
                new_preferences.append(new_pref)
                self.db.add(new_pref)

            await self.db.commit()

            # Refresh to get related data
            for pref in new_preferences:
                await self.db.refresh(pref)

            return new_preferences

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating team preferences for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update team preferences"
            )

    async def update_notification_preferences(
        self,
        user: User,
        notifications_update: NotificationPreferencesUpdate
    ) -> UserNotificationSettings:
        """
        Update user's notification preferences

        Args:
            user: User model
            notifications_update: Notification preference updates

        Returns:
            Updated UserNotificationSettings model

        Raises:
            HTTPException: If validation or database operation fails
        """
        try:
            # Get or create notification settings
            result = await self.db.execute(
                select(UserNotificationSettings).where(
                    UserNotificationSettings.user_id == user.id
                )
            )
            notification_settings = result.scalar_one_or_none()

            if not notification_settings:
                notification_settings = UserNotificationSettings(user_id=user.id)
                self.db.add(notification_settings)

            # Update only provided fields
            if notifications_update.push_enabled is not None:
                notification_settings.push_enabled = notifications_update.push_enabled
            if notifications_update.email_enabled is not None:
                notification_settings.email_enabled = notifications_update.email_enabled
            if notifications_update.game_reminders is not None:
                notification_settings.game_reminders = notifications_update.game_reminders
            if notifications_update.news_alerts is not None:
                notification_settings.news_alerts = notifications_update.news_alerts
            if notifications_update.score_updates is not None:
                notification_settings.score_updates = notifications_update.score_updates

            await self.db.commit()
            await self.db.refresh(notification_settings)

            return notification_settings

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating notification preferences for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update notification preferences"
            )

    async def update_user_preferences(
        self,
        user: User,
        preferences_update: PreferencesUpdate
    ) -> Dict[str, Any]:
        """
        Update user's preferences in bulk

        Args:
            user: User model
            preferences_update: Bulk preference updates

        Returns:
            Dictionary with updated preferences

        Raises:
            HTTPException: If validation or database operation fails
        """
        try:
            result = {}

            # Update sport preferences if provided
            if preferences_update.sports is not None:
                sport_prefs = await self.update_sport_preferences(user, preferences_update.sports)
                result["sport_preferences"] = [
                    {
                        "id": str(pref.id),
                        "sport_id": str(pref.sport_id),
                        "sport_name": pref.sport.name if pref.sport else None,
                        "rank": pref.rank,
                        "is_active": pref.is_active
                    }
                    for pref in sport_prefs
                ]

            # Update team preferences if provided
            if preferences_update.teams is not None:
                team_prefs = await self.update_team_preferences(user, preferences_update.teams)
                result["team_preferences"] = [
                    {
                        "id": str(pref.id),
                        "team_id": str(pref.team_id),
                        "team_name": pref.team.name if pref.team else None,
                        "affinity_score": float(pref.affinity_score),
                        "is_active": pref.is_active
                    }
                    for pref in team_prefs
                ]

            # Update notification preferences if provided
            if preferences_update.notifications is not None:
                notification_settings = await self.update_notification_preferences(
                    user, preferences_update.notifications
                )
                result["notification_settings"] = {
                    "push_enabled": notification_settings.push_enabled,
                    "email_enabled": notification_settings.email_enabled,
                    "game_reminders": notification_settings.game_reminders,
                    "news_alerts": notification_settings.news_alerts,
                    "score_updates": notification_settings.score_updates
                }

            # Update content frequency if provided
            if preferences_update.content_frequency is not None:
                user.content_frequency = preferences_update.content_frequency
                await self.db.commit()
                await self.db.refresh(user)
                result["content_frequency"] = user.content_frequency

            return result

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user preferences for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences"
            )

    async def validate_sport_exists(self, sport_id: UUID) -> bool:
        """
        Validate that a sport exists

        Args:
            sport_id: Sport UUID to validate

        Returns:
            True if sport exists, False otherwise
        """
        try:
            from backend.models.sports import Sport
            result = await self.db.execute(
                select(Sport).where(Sport.id == sport_id)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error validating sport {sport_id}: {str(e)}")
            # Note: Session cleanup is handled by FastAPI dependency injection
            return False

    async def validate_team_exists(self, team_id: UUID) -> bool:
        """
        Validate that a team exists

        Args:
            team_id: Team UUID to validate

        Returns:
            True if team exists, False otherwise
        """
        try:
            from backend.models.sports import Team
            result = await self.db.execute(
                select(Team).where(Team.id == team_id)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error validating team {team_id}: {str(e)}")
            # Note: Session cleanup is handled by FastAPI dependency injection
            return False