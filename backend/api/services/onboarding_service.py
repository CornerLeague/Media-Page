"""
OnboardingService - Business logic for user onboarding flow
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.users import User
from backend.models.sports import Sport, Team
from backend.api.schemas.onboarding import (
    OnboardingStatusResponse,
    OnboardingCompletionResponse,
    OnboardingSportResponse,
    OnboardingTeamResponse,
    OnboardingSportsListResponse,
    OnboardingTeamsListResponse
)

logger = logging.getLogger(__name__)


class OnboardingService:
    """Service for managing user onboarding process"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_onboarding_status(self, user: User) -> OnboardingStatusResponse:
        """Get current onboarding status for user"""
        return OnboardingStatusResponse(
            is_onboarded=user.is_onboarded,
            current_step=user.current_onboarding_step,
            onboarding_completed_at=user.onboarding_completed_at
        )

    async def update_onboarding_step(self, user: User, step: int) -> OnboardingStatusResponse:
        """Update user's current onboarding step"""
        try:
            # Validate step number
            if step < 1 or step > 5:
                raise ValueError("Step must be between 1 and 5")

            # Update the user's current step
            user.current_onboarding_step = step
            user.last_active_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Updated onboarding step for user {user.id} to step {step}")

            return OnboardingStatusResponse(
                is_onboarded=user.is_onboarded,
                current_step=user.current_onboarding_step,
                onboarding_completed_at=user.onboarding_completed_at
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating onboarding step for user {user.id}: {str(e)}")
            raise

    async def get_onboarding_sports(self) -> OnboardingSportsListResponse:
        """Get sports list for onboarding step 2"""
        try:
            # Query active sports ordered by popularity rank
            query = (
                select(Sport)
                .where(Sport.is_active == 1)  # Use 1 for SQLite boolean
                .order_by(Sport.popularity_rank.asc(), Sport.name.asc())
            )

            result = await self.db.execute(query)
            sports = result.scalars().all()

            # Convert to response objects
            sports_data = [
                OnboardingSportResponse(
                    id=sport.id,
                    name=sport.name,
                    slug=sport.slug,
                    icon=sport.icon,
                    icon_url=sport.icon_url,
                    description=sport.description,
                    popularity_rank=sport.popularity_rank,
                    is_active=sport.is_active
                )
                for sport in sports
            ]

            return OnboardingSportsListResponse(
                sports=sports_data,
                total=len(sports_data)
            )

        except Exception as e:
            logger.error(f"Error retrieving onboarding sports: {str(e)}")
            raise

    async def get_onboarding_teams(self, sport_ids: List[UUID]) -> OnboardingTeamsListResponse:
        """Get teams list for onboarding step 3, filtered by selected sports"""
        try:
            if not sport_ids:
                return OnboardingTeamsListResponse(
                    teams=[],
                    total=0,
                    sport_ids=[]
                )

            # For now, let's use a simpler approach without complex relationships
            # Use raw SQL for reliable results
            from sqlalchemy import text
            from uuid import UUID

            # Build query for all requested sport IDs
            sport_id_params = {}
            sport_id_conditions = []
            for i, sport_id in enumerate(sport_ids):
                param_name = f"sport_id_{i}"
                sport_id_params[param_name] = str(sport_id)
                sport_id_conditions.append(f"sport_id = :{param_name}")

            where_clause = " OR ".join(sport_id_conditions)

            raw_query = text(f"""
                SELECT id, name, market, slug, sport_id, logo_url, abbreviation,
                       primary_color, secondary_color
                FROM teams
                WHERE ({where_clause}) AND is_active = 1
                ORDER BY sport_id, market, name
            """)

            result = await self.db.execute(raw_query, sport_id_params)
            team_rows = result.fetchall()

            # Convert to response objects
            teams_data = []
            for row in team_rows:
                teams_data.append(
                    OnboardingTeamResponse(
                        id=UUID(row.id),
                        name=row.name,
                        market=row.market,
                        slug=row.slug,
                        sport_id=UUID(row.sport_id),
                        logo_url=row.logo_url,
                        abbreviation=row.abbreviation,
                        primary_color=row.primary_color,
                        secondary_color=row.secondary_color,
                        league_info=None  # Simplified for now - can add league lookup later
                    )
                )

            return OnboardingTeamsListResponse(
                teams=teams_data,
                total=len(teams_data),
                sport_ids=sport_ids
            )

        except Exception as e:
            logger.error(f"Error retrieving onboarding teams for sports {sport_ids}: {str(e)}")
            raise

    async def complete_onboarding(
        self,
        user: User,
        force_complete: bool = False
    ) -> OnboardingCompletionResponse:
        """Complete user onboarding process"""
        try:
            # Check if user has sufficient preferences (unless forced)
            if not force_complete:
                # Check if user has at least one sport preference
                if not user.sport_preferences:
                    raise ValueError("User must have at least one sport preference to complete onboarding")

                # Check if user has at least one team preference
                if not user.team_preferences:
                    raise ValueError("User must have at least one team preference to complete onboarding")

            # Mark onboarding as complete
            completion_time = datetime.utcnow()
            user.onboarding_completed_at = completion_time
            user.current_onboarding_step = None  # Clear step when completed
            user.last_active_at = completion_time

            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Completed onboarding for user {user.id}")

            return OnboardingCompletionResponse(
                success=True,
                user_id=user.id,
                onboarding_completed_at=completion_time,
                message="Onboarding completed successfully"
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error completing onboarding for user {user.id}: {str(e)}")

            return OnboardingCompletionResponse(
                success=False,
                user_id=user.id,
                onboarding_completed_at=datetime.utcnow(),
                message=f"Failed to complete onboarding: {str(e)}"
            )

    async def reset_onboarding(self, user: User) -> OnboardingStatusResponse:
        """Reset user onboarding (for testing/admin purposes)"""
        try:
            user.onboarding_completed_at = None
            user.current_onboarding_step = 1  # Reset to step 1
            user.last_active_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Reset onboarding for user {user.id}")

            return OnboardingStatusResponse(
                is_onboarded=user.is_onboarded,
                current_step=user.current_onboarding_step,
                onboarding_completed_at=user.onboarding_completed_at
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error resetting onboarding for user {user.id}: {str(e)}")
            raise

    async def get_onboarding_progress_stats(self) -> dict:
        """Get aggregated onboarding progress statistics (for analytics)"""
        try:
            # Total users
            total_query = select(func.count(User.id))
            total_result = await self.db.execute(total_query)
            total_users = total_result.scalar()

            # Completed onboarding
            completed_query = select(func.count(User.id)).where(User.onboarding_completed_at.is_not(None))
            completed_result = await self.db.execute(completed_query)
            completed_users = completed_result.scalar()

            # Users by current step
            step_stats = {}
            for step in range(1, 6):
                step_query = select(func.count(User.id)).where(User.current_onboarding_step == step)
                step_result = await self.db.execute(step_query)
                step_stats[f"step_{step}"] = step_result.scalar()

            return {
                "total_users": total_users,
                "completed_onboarding": completed_users,
                "completion_rate": (completed_users / total_users * 100) if total_users > 0 else 0,
                "step_distribution": step_stats
            }

        except Exception as e:
            logger.error(f"Error retrieving onboarding stats: {str(e)}")
            raise