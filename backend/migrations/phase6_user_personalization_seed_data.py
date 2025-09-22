"""
Phase 6: User Personalization Seed Data
Populates user preferences, bracket predictions, challenges, and engagement data
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session
from backend.models import (
    User, CollegeTeam, Tournament,
    UserCollegePreferences, BracketPrediction, BracketChallenge,
    BracketChallengeParticipation, UserCollegeNotificationSettings,
    PersonalizedFeed, UserEngagementMetrics, UserPersonalizationProfile
)
from backend.models.enums import (
    EngagementLevel, BracketPredictionStatus, BracketChallengeStatus,
    ChallengePrivacy, NotificationFrequency, EngagementMetricType
)

logger = logging.getLogger(__name__)


class Phase6SeedDataGenerator:
    """
    Generate comprehensive seed data for Phase 6 user personalization features
    """

    def __init__(self):
        self.seed_name = "Phase 6: User Personalization Seed Data"
        self.version = "20250921_2200_phase6_seed_data"

    async def generate_seed_data(self, session: AsyncSession) -> None:
        """
        Generate comprehensive seed data for user personalization
        """
        logger.info(f"Starting {self.seed_name} generation...")

        try:
            # Get existing data
            users = await self._get_existing_users(session)
            college_teams = await self._get_existing_college_teams(session)
            tournaments = await self._get_existing_tournaments(session)

            if not users:
                logger.warning("No users found. Creating sample users...")
                users = await self._create_sample_users(session)

            if not college_teams:
                logger.warning("No college teams found. Skipping team-dependent data.")
                return

            # Generate user college preferences
            await self._generate_user_college_preferences(session, users, college_teams)

            # Generate notification settings
            await self._generate_notification_settings(session, users)

            # Generate personalized feeds
            await self._generate_personalized_feeds(session, users)

            # Generate engagement metrics
            await self._generate_engagement_metrics(session, users, college_teams)

            # Generate bracket predictions (if tournaments exist)
            if tournaments:
                await self._generate_bracket_predictions(session, users, tournaments)
                await self._generate_bracket_challenges(session, users, tournaments)

            # Generate personalization profiles
            await self._generate_personalization_profiles(session, users)

            await session.commit()
            logger.info(f"{self.seed_name} generation completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during {self.seed_name} generation: {e}")
            raise

    async def _get_existing_users(self, session: AsyncSession) -> List[User]:
        """Get existing users from the database"""
        result = await session.execute(
            select(User).where(User.is_active == True).limit(50)
        )
        return list(result.scalars().all())

    async def _get_existing_college_teams(self, session: AsyncSession) -> List[CollegeTeam]:
        """Get existing college teams from the database"""
        result = await session.execute(
            select(CollegeTeam).limit(100)
        )
        return list(result.scalars().all())

    async def _get_existing_tournaments(self, session: AsyncSession) -> List[Tournament]:
        """Get existing tournaments from the database"""
        result = await session.execute(
            select(Tournament).limit(10)
        )
        return list(result.scalars().all())

    async def _create_sample_users(self, session: AsyncSession) -> List[User]:
        """Create sample users for testing"""
        logger.info("Creating sample users...")

        sample_users = [
            {
                "firebase_uid": f"sample_user_{i}",
                "email": f"user{i}@example.com",
                "display_name": f"Test User {i}",
                "first_name": f"Test",
                "last_name": f"User{i}",
                "is_active": True,
                "is_verified": True,
                "onboarding_completed_at": datetime.now() - timedelta(days=random.randint(1, 90))
            }
            for i in range(1, 21)  # Create 20 sample users
        ]

        users = []
        for user_data in sample_users:
            user = User(**user_data)
            session.add(user)
            users.append(user)

        await session.flush()  # Get IDs
        return users

    async def _generate_user_college_preferences(
        self, session: AsyncSession, users: List[User], college_teams: List[CollegeTeam]
    ) -> None:
        """Generate user college team preferences"""
        logger.info("Generating user college preferences...")

        preferences = []
        for user in users:
            # Each user follows 1-5 teams with different engagement levels
            num_teams = random.randint(1, 5)
            user_teams = random.sample(college_teams, min(num_teams, len(college_teams)))

            for i, team in enumerate(user_teams):
                # Primary team gets highest engagement
                if i == 0:
                    engagement = EngagementLevel.DIE_HARD
                elif i == 1:
                    engagement = EngagementLevel.REGULAR
                else:
                    engagement = random.choice([EngagementLevel.CASUAL, EngagementLevel.REGULAR])

                preference = UserCollegePreferences(
                    user_id=user.id,
                    college_team_id=team.id,
                    engagement_level=engagement,
                    is_active=True,
                    followed_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                    game_reminders=random.choice([True, False]),
                    injury_updates=engagement != EngagementLevel.CASUAL,
                    recruiting_news=engagement == EngagementLevel.DIE_HARD,
                    coaching_updates=random.choice([True, False]),
                    interaction_score=Decimal(str(random.uniform(0.2, 1.0))),
                    last_interaction_at=datetime.now() - timedelta(hours=random.randint(1, 168))
                )
                preferences.append(preference)

        # Batch insert
        session.add_all(preferences)
        await session.flush()
        logger.info(f"Created {len(preferences)} user college preferences")

    async def _generate_notification_settings(
        self, session: AsyncSession, users: List[User]
    ) -> None:
        """Generate user notification settings"""
        logger.info("Generating user notification settings...")

        settings = []
        for user in users:
            # Randomize notification preferences
            setting = UserCollegeNotificationSettings(
                user_id=user.id,
                enabled=random.choice([True, True, True, False]),  # 75% enabled
                game_reminders_frequency=random.choice(list(NotificationFrequency)),
                score_updates_frequency=random.choice([
                    NotificationFrequency.IMMEDIATE,
                    NotificationFrequency.GAME_DAY_ONLY,
                    NotificationFrequency.NEVER
                ]),
                injury_updates_frequency=random.choice([
                    NotificationFrequency.IMMEDIATE,
                    NotificationFrequency.DAILY_DIGEST
                ]),
                recruiting_news_frequency=random.choice([
                    NotificationFrequency.DAILY_DIGEST,
                    NotificationFrequency.WEEKLY_DIGEST,
                    NotificationFrequency.NEVER
                ]),
                coaching_changes_frequency=random.choice([
                    NotificationFrequency.IMMEDIATE,
                    NotificationFrequency.DAILY_DIGEST
                ]),
                ranking_changes_frequency=random.choice([
                    NotificationFrequency.WEEKLY_DIGEST,
                    NotificationFrequency.DAILY_DIGEST
                ]),
                tournament_updates_frequency=NotificationFrequency.IMMEDIATE,
                bracket_challenge_frequency=random.choice([
                    NotificationFrequency.IMMEDIATE,
                    NotificationFrequency.NEVER
                ]),
                transfer_portal_frequency=random.choice([
                    NotificationFrequency.DAILY_DIGEST,
                    NotificationFrequency.WEEKLY_DIGEST
                ]),
                push_notifications=random.choice([True, True, False]),  # 67% enabled
                email_notifications=random.choice([True, False, False]),  # 33% enabled
                quiet_hours_enabled=random.choice([True, True, False]),  # 67% enabled
                quiet_hours_start=random.randint(22, 23) if random.choice([True, False]) else None,
                quiet_hours_end=random.randint(6, 8) if random.choice([True, False]) else None,
                pre_game_reminders=random.choice([True, True, False]),
                pre_game_reminder_minutes=random.choice([15, 30, 60, 120]),
                halftime_updates=random.choice([True, False, False]),  # 33% enabled
                final_score_notifications=random.choice([True, True, True, False])  # 75% enabled
            )
            settings.append(setting)

        session.add_all(settings)
        await session.flush()
        logger.info(f"Created {len(settings)} user notification settings")

    async def _generate_personalized_feeds(
        self, session: AsyncSession, users: List[User]
    ) -> None:
        """Generate personalized feed configurations"""
        logger.info("Generating personalized feed configurations...")

        feeds = []
        for user in users:
            # Randomize content weights based on user preferences
            feed = PersonalizedFeed(
                user_id=user.id,
                enabled=random.choice([True, True, True, False]),  # 75% enabled
                articles_weight=Decimal(str(random.uniform(0.5, 1.0))),
                game_updates_weight=Decimal(str(random.uniform(0.3, 1.0))),
                injury_reports_weight=Decimal(str(random.uniform(0.2, 0.9))),
                recruiting_news_weight=Decimal(str(random.uniform(0.1, 0.8))),
                coaching_news_weight=Decimal(str(random.uniform(0.3, 0.9))),
                rankings_weight=Decimal(str(random.uniform(0.4, 0.8))),
                tournament_news_weight=Decimal(str(random.uniform(0.7, 1.0))),
                bracket_updates_weight=Decimal(str(random.uniform(0.5, 1.0))),
                recency_factor=Decimal(str(random.uniform(0.1, 0.5))),
                engagement_factor=Decimal(str(random.uniform(0.2, 0.6))),
                team_preference_factor=Decimal(str(random.uniform(0.3, 0.7))),
                max_items_per_refresh=random.choice([25, 50, 75, 100]),
                refresh_interval_hours=random.choice([1, 2, 4, 6]),
                last_refreshed_at=datetime.now() - timedelta(hours=random.randint(1, 24))
            )
            feeds.append(feed)

        session.add_all(feeds)
        await session.flush()
        logger.info(f"Created {len(feeds)} personalized feed configurations")

    async def _generate_engagement_metrics(
        self, session: AsyncSession, users: List[User], college_teams: List[CollegeTeam]
    ) -> None:
        """Generate user engagement metrics"""
        logger.info("Generating user engagement metrics...")

        metrics = []
        for user in users:
            # Generate 10-50 engagement events per user over the last 30 days
            num_events = random.randint(10, 50)

            for _ in range(num_events):
                # Choose random metric type
                metric_type = random.choice(list(EngagementMetricType))

                # Choose random entity type based on metric
                entity_types = {
                    EngagementMetricType.ARTICLE_VIEW: "article",
                    EngagementMetricType.ARTICLE_SHARE: "article",
                    EngagementMetricType.ARTICLE_LIKE: "article",
                    EngagementMetricType.TEAM_PAGE_VIEW: "team",
                    EngagementMetricType.GAME_DETAIL_VIEW: "game",
                    EngagementMetricType.BRACKET_CREATED: "bracket",
                    EngagementMetricType.BRACKET_UPDATED: "bracket",
                    EngagementMetricType.CHALLENGE_JOINED: "challenge",
                    EngagementMetricType.COMMENT_POSTED: "comment",
                    EngagementMetricType.SEARCH_PERFORMED: "search",
                    EngagementMetricType.NOTIFICATION_CLICKED: "notification",
                    EngagementMetricType.FEED_SCROLL: "feed",
                    EngagementMetricType.TEAM_FOLLOWED: "team",
                    EngagementMetricType.TEAM_UNFOLLOWED: "team",
                    EngagementMetricType.SETTINGS_UPDATED: "settings",
                }

                entity_type = entity_types.get(metric_type, "unknown")

                # Engagement values based on metric type
                engagement_values = {
                    EngagementMetricType.ARTICLE_VIEW: random.uniform(0.1, 0.3),
                    EngagementMetricType.ARTICLE_SHARE: random.uniform(0.6, 0.9),
                    EngagementMetricType.ARTICLE_LIKE: random.uniform(0.4, 0.7),
                    EngagementMetricType.TEAM_PAGE_VIEW: random.uniform(0.2, 0.5),
                    EngagementMetricType.GAME_DETAIL_VIEW: random.uniform(0.3, 0.6),
                    EngagementMetricType.BRACKET_CREATED: random.uniform(0.8, 1.0),
                    EngagementMetricType.BRACKET_UPDATED: random.uniform(0.5, 0.8),
                    EngagementMetricType.CHALLENGE_JOINED: random.uniform(0.7, 0.9),
                    EngagementMetricType.TEAM_FOLLOWED: random.uniform(0.8, 1.0),
                    EngagementMetricType.TEAM_UNFOLLOWED: random.uniform(0.3, 0.5),
                }

                engagement_value = Decimal(str(engagement_values.get(metric_type, 0.3)))

                metric = UserEngagementMetrics(
                    user_id=user.id,
                    metric_type=metric_type,
                    entity_type=entity_type,
                    entity_id=uuid4(),  # Random entity ID
                    occurred_at=datetime.now() - timedelta(
                        days=random.randint(0, 30),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    ),
                    engagement_value=engagement_value,
                    session_id=f"session_{user.id}_{random.randint(1, 100)}",
                    college_team_id=random.choice(college_teams).id if college_teams and random.choice([True, False]) else None,
                    metadata={
                        "device": random.choice(["mobile", "desktop", "tablet"]),
                        "source": random.choice(["organic", "notification", "direct"]),
                        "duration_seconds": random.randint(5, 300)
                    }
                )
                metrics.append(metric)

        session.add_all(metrics)
        await session.flush()
        logger.info(f"Created {len(metrics)} engagement metrics")

    async def _generate_bracket_predictions(
        self, session: AsyncSession, users: List[User], tournaments: List[Tournament]
    ) -> None:
        """Generate bracket predictions"""
        logger.info("Generating bracket predictions...")

        predictions = []
        for user in users:
            # 60% of users create bracket predictions
            if random.random() < 0.6:
                for tournament in random.sample(tournaments, min(2, len(tournaments))):
                    # Generate realistic bracket data
                    bracket_data = self._generate_mock_bracket_data()

                    prediction = BracketPrediction(
                        user_id=user.id,
                        tournament_id=tournament.id,
                        bracket_name=f"{user.display_name}'s {tournament.name} Bracket",
                        status=random.choice([
                            BracketPredictionStatus.SUBMITTED,
                            BracketPredictionStatus.LOCKED,
                            BracketPredictionStatus.SCORING,
                            BracketPredictionStatus.FINAL
                        ]),
                        predictions=bracket_data,
                        total_score=random.randint(0, 100),
                        possible_score=random.randint(100, 150),
                        correct_picks=random.randint(0, 40),
                        total_picks=random.randint(40, 63),
                        submitted_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                        locked_at=datetime.now() - timedelta(days=random.randint(0, 25)),
                        last_scored_at=datetime.now() - timedelta(hours=random.randint(1, 24))
                    )
                    predictions.append(prediction)

        session.add_all(predictions)
        await session.flush()
        logger.info(f"Created {len(predictions)} bracket predictions")
        return predictions

    async def _generate_bracket_challenges(
        self, session: AsyncSession, users: List[User], tournaments: List[Tournament]
    ) -> None:
        """Generate bracket challenges"""
        logger.info("Generating bracket challenges...")

        challenges = []
        for i, user in enumerate(users[:5]):  # Only first 5 users create challenges
            for tournament in random.sample(tournaments, min(1, len(tournaments))):
                challenge = BracketChallenge(
                    creator_id=user.id,
                    tournament_id=tournament.id,
                    name=f"{user.display_name}'s {tournament.name} Challenge",
                    description=f"Join {user.display_name}'s bracket challenge for {tournament.name}!",
                    status=random.choice([
                        BracketChallengeStatus.OPEN,
                        BracketChallengeStatus.CLOSED,
                        BracketChallengeStatus.IN_PROGRESS
                    ]),
                    privacy_setting=random.choice([
                        ChallengePrivacy.PUBLIC,
                        ChallengePrivacy.FRIENDS_ONLY,
                        ChallengePrivacy.INVITE_ONLY
                    ]),
                    entry_fee=Decimal(str(random.choice([0, 5, 10, 25]))) if random.choice([True, False]) else None,
                    max_participants=random.choice([10, 20, 50, 100]) if random.choice([True, False]) else None,
                    registration_deadline=datetime.now() + timedelta(days=random.randint(1, 7)),
                    scoring_system={
                        "round_1": 1,
                        "round_2": 2,
                        "round_3": 4,
                        "round_4": 8,
                        "round_5": 16,
                        "round_6": 32
                    },
                    prize_structure={
                        "1st": "50%",
                        "2nd": "30%",
                        "3rd": "20%"
                    } if random.choice([True, False]) else None,
                    invite_code=f"CHAL{random.randint(1000, 9999)}",
                    participant_count=random.randint(1, 15)
                )
                challenges.append(challenge)

        session.add_all(challenges)
        await session.flush()
        logger.info(f"Created {len(challenges)} bracket challenges")

    def _generate_mock_bracket_data(self) -> Dict[str, Any]:
        """Generate mock bracket prediction data"""
        return {
            "rounds": {
                "round_1": {
                    "region_1": [f"team_{i}" for i in range(1, 17)],
                    "region_2": [f"team_{i}" for i in range(17, 33)],
                    "region_3": [f"team_{i}" for i in range(33, 49)],
                    "region_4": [f"team_{i}" for i in range(49, 65)]
                },
                "round_2": {
                    "region_1": [f"team_{random.randint(1, 16)}" for _ in range(8)],
                    "region_2": [f"team_{random.randint(17, 32)}" for _ in range(8)],
                    "region_3": [f"team_{random.randint(33, 48)}" for _ in range(8)],
                    "region_4": [f"team_{random.randint(49, 64)}" for _ in range(8)]
                }
            },
            "championship": f"team_{random.randint(1, 64)}",
            "confidence_points": random.randint(50, 100)
        }

    async def _generate_personalization_profiles(
        self, session: AsyncSession, users: List[User]
    ) -> None:
        """Generate user personalization profiles"""
        logger.info("Generating user personalization profiles...")

        profiles = []
        for user in users:
            profile = UserPersonalizationProfile(
                user_id=user.id,
                content_type_scores={
                    "articles": random.uniform(0.3, 1.0),
                    "game_updates": random.uniform(0.2, 0.9),
                    "injury_reports": random.uniform(0.1, 0.8),
                    "recruiting_news": random.uniform(0.0, 0.7),
                    "coaching_news": random.uniform(0.2, 0.9),
                    "rankings": random.uniform(0.3, 0.8),
                    "tournament_news": random.uniform(0.5, 1.0)
                },
                team_affinity_scores={
                    f"team_{i}": random.uniform(0.0, 1.0) for i in range(1, 21)
                },
                conference_affinity_scores={
                    f"conference_{i}": random.uniform(0.0, 1.0) for i in range(1, 11)
                },
                engagement_patterns={
                    "peak_hours": random.sample(range(0, 24), 3),
                    "peak_days": random.sample(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], 2),
                    "session_frequency": random.uniform(0.1, 1.0),
                    "content_diversity": random.uniform(0.2, 0.9)
                },
                total_interactions=random.randint(50, 500),
                average_session_duration=Decimal(str(random.uniform(5.0, 45.0))),
                last_active_at=datetime.now() - timedelta(hours=random.randint(1, 48)),
                last_calculated_at=datetime.now() - timedelta(hours=random.randint(1, 24)),
                calculation_version="1.0"
            )
            profiles.append(profile)

        session.add_all(profiles)
        await session.flush()
        logger.info(f"Created {len(profiles)} personalization profiles")


async def run_seed_data():
    """
    Run the Phase 6 seed data generation
    """
    generator = Phase6SeedDataGenerator()

    async for session in get_async_session():
        try:
            await generator.generate_seed_data(session)
            print(f"Successfully generated {generator.seed_name}")
            break
        except Exception as e:
            print(f"Seed data generation failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_seed_data())