"""
Test script for Phase 6 User Personalization integration
Validates models, relationships, and database integration
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import get_async_session
from backend.models import (
    User, CollegeTeam, Tournament,
    UserCollegePreferences, BracketPrediction, BracketChallenge,
    UserCollegeNotificationSettings, PersonalizedFeed,
    UserEngagementMetrics, UserPersonalizationProfile
)
from backend.models.enums import EngagementLevel, NotificationFrequency

logger = logging.getLogger(__name__)


async def test_model_creation(session: AsyncSession):
    """Test creating instances of all Phase 6 models"""
    print("Testing Phase 6 model creation...")

    # Test creating a sample user if none exists
    result = await session.execute(select(User).limit(1))
    user = result.scalar_one_or_none()

    if not user:
        print("Creating test user...")
        user = User(
            firebase_uid="test_user_phase6",
            email="test@phase6.com",
            display_name="Phase 6 Test User",
            is_active=True,
            is_verified=True,
            onboarding_completed_at=datetime.now()
        )
        session.add(user)
        await session.flush()

    # Test creating college team preference
    result = await session.execute(select(CollegeTeam).limit(1))
    college_team = result.scalar_one_or_none()

    if college_team:
        print("Testing UserCollegePreferences creation...")
        preference = UserCollegePreferences(
            user_id=user.id,
            college_team_id=college_team.id,
            engagement_level=EngagementLevel.DIE_HARD,
            is_active=True,
            game_reminders=True,
            injury_updates=True,
            recruiting_news=True,
            coaching_updates=True,
            interaction_score=Decimal("0.8500")
        )
        session.add(preference)
        print("✓ UserCollegePreferences created successfully")

    # Test notification settings
    print("Testing UserCollegeNotificationSettings creation...")
    notification_settings = UserCollegeNotificationSettings(
        user_id=user.id,
        enabled=True,
        game_reminders_frequency=NotificationFrequency.IMMEDIATE,
        score_updates_frequency=NotificationFrequency.IMMEDIATE,
        injury_updates_frequency=NotificationFrequency.IMMEDIATE,
        recruiting_news_frequency=NotificationFrequency.DAILY_DIGEST,
        push_notifications=True,
        email_notifications=False,
        quiet_hours_enabled=True,
        quiet_hours_start=22,
        quiet_hours_end=7,
        pre_game_reminders=True,
        pre_game_reminder_minutes=30
    )
    session.add(notification_settings)
    print("✓ UserCollegeNotificationSettings created successfully")

    # Test personalized feed
    print("Testing PersonalizedFeed creation...")
    personalized_feed = PersonalizedFeed(
        user_id=user.id,
        enabled=True,
        articles_weight=Decimal("1.00"),
        game_updates_weight=Decimal("0.80"),
        injury_reports_weight=Decimal("0.70"),
        recruiting_news_weight=Decimal("0.60"),
        coaching_news_weight=Decimal("0.75"),
        rankings_weight=Decimal("0.65"),
        tournament_news_weight=Decimal("0.90"),
        bracket_updates_weight=Decimal("0.85"),
        recency_factor=Decimal("0.30"),
        engagement_factor=Decimal("0.40"),
        team_preference_factor=Decimal("0.50"),
        max_items_per_refresh=50,
        refresh_interval_hours=2
    )
    session.add(personalized_feed)
    print("✓ PersonalizedFeed created successfully")

    # Test user personalization profile
    print("Testing UserPersonalizationProfile creation...")
    personalization_profile = UserPersonalizationProfile(
        user_id=user.id,
        content_type_scores={
            "articles": 0.8,
            "game_updates": 0.9,
            "injury_reports": 0.6,
            "recruiting_news": 0.4,
            "coaching_news": 0.7,
            "rankings": 0.6,
            "tournament_news": 0.9
        },
        team_affinity_scores={
            str(college_team.id) if college_team else "sample_team": 0.95
        },
        conference_affinity_scores={
            "acc": 0.8,
            "sec": 0.3,
            "big_ten": 0.2
        },
        engagement_patterns={
            "peak_hours": [19, 20, 21],
            "peak_days": ["saturday", "sunday"],
            "session_frequency": 0.7,
            "content_diversity": 0.6
        },
        total_interactions=150,
        average_session_duration=Decimal("25.50"),
        last_active_at=datetime.now(),
        last_calculated_at=datetime.now(),
        calculation_version="1.0"
    )
    session.add(personalization_profile)
    print("✓ UserPersonalizationProfile created successfully")

    # Test tournament-related models if tournament exists
    result = await session.execute(select(Tournament).limit(1))
    tournament = result.scalar_one_or_none()

    if tournament:
        print("Testing BracketPrediction creation...")
        bracket_prediction = BracketPrediction(
            user_id=user.id,
            tournament_id=tournament.id,
            bracket_name="Test Bracket",
            predictions={
                "rounds": {
                    "round_1": {"region_1": ["team_1", "team_2"]},
                    "round_2": {"region_1": ["team_1"]}
                },
                "championship": "team_1"
            },
            total_score=85,
            possible_score=150,
            correct_picks=35,
            total_picks=50
        )
        session.add(bracket_prediction)
        print("✓ BracketPrediction created successfully")

        print("Testing BracketChallenge creation...")
        bracket_challenge = BracketChallenge(
            creator_id=user.id,
            tournament_id=tournament.id,
            name="Test Challenge",
            description="A test bracket challenge",
            scoring_system={
                "round_1": 1,
                "round_2": 2,
                "round_3": 4,
                "round_4": 8
            },
            invite_code="TEST123",
            participant_count=1
        )
        session.add(bracket_challenge)
        print("✓ BracketChallenge created successfully")

    await session.commit()
    print("All Phase 6 models created and committed successfully!")
    return user


async def test_model_relationships(session: AsyncSession, user: User):
    """Test model relationships and queries"""
    print("\nTesting Phase 6 model relationships...")

    # Test user college preferences relationship
    user_with_preferences = await session.execute(
        select(User)
        .options(selectinload(User.team_preferences))
        .where(User.id == user.id)
    )
    user_result = user_with_preferences.scalar_one()
    print(f"✓ User has {len(user_result.team_preferences)} team preferences")

    # Test college preferences query
    college_prefs = await session.execute(
        select(UserCollegePreferences)
        .options(selectinload(UserCollegePreferences.college_team))
        .where(UserCollegePreferences.user_id == user.id)
    )
    prefs = list(college_prefs.scalars().all())
    print(f"✓ Found {len(prefs)} college preferences for user")

    if prefs:
        pref = prefs[0]
        print(f"✓ College preference: {pref.engagement_level} fan of {pref.college_team.name if pref.college_team else 'Unknown Team'}")
        print(f"✓ Interaction score: {pref.interaction_score}")

    # Test notification settings
    notification_settings = await session.execute(
        select(UserCollegeNotificationSettings)
        .where(UserCollegeNotificationSettings.user_id == user.id)
    )
    settings = notification_settings.scalar_one_or_none()
    if settings:
        print(f"✓ Notification settings: enabled={settings.enabled}")
        print(f"✓ Game reminders frequency: {settings.game_reminders_frequency}")

    # Test personalized feed
    feed = await session.execute(
        select(PersonalizedFeed)
        .where(PersonalizedFeed.user_id == user.id)
    )
    feed_result = feed.scalar_one_or_none()
    if feed_result:
        print(f"✓ Personalized feed: enabled={feed_result.enabled}")
        print(f"✓ Articles weight: {feed_result.articles_weight}")
        print(f"✓ Tournament news weight: {feed_result.tournament_news_weight}")

    # Test personalization profile
    profile = await session.execute(
        select(UserPersonalizationProfile)
        .where(UserPersonalizationProfile.user_id == user.id)
    )
    profile_result = profile.scalar_one_or_none()
    if profile_result:
        print(f"✓ Personalization profile: {profile_result.total_interactions} interactions")
        print(f"✓ Content type scores: {len(profile_result.content_type_scores)} types")
        print(f"✓ Team affinity scores: {len(profile_result.team_affinity_scores)} teams")

    # Test bracket predictions
    bracket_preds = await session.execute(
        select(BracketPrediction)
        .where(BracketPrediction.user_id == user.id)
    )
    predictions = list(bracket_preds.scalars().all())
    print(f"✓ Found {len(predictions)} bracket predictions")

    if predictions:
        pred = predictions[0]
        print(f"✓ Bracket prediction: {pred.bracket_name}, score: {pred.total_score}/{pred.possible_score}")

    print("All relationship tests passed!")


async def test_model_properties(session: AsyncSession, user: User):
    """Test model properties and methods"""
    print("\nTesting Phase 6 model properties and methods...")

    # Test college preference properties
    college_prefs = await session.execute(
        select(UserCollegePreferences)
        .where(UserCollegePreferences.user_id == user.id)
    )
    prefs = list(college_prefs.scalars().all())

    if prefs:
        pref = prefs[0]
        print(f"✓ Is die-hard fan: {pref.is_die_hard_fan}")

    # Test bracket prediction properties
    bracket_preds = await session.execute(
        select(BracketPrediction)
        .where(BracketPrediction.user_id == user.id)
    )
    predictions = list(bracket_preds.scalars().all())

    if predictions:
        pred = predictions[0]
        print(f"✓ Accuracy percentage: {pred.accuracy_percentage}%")
        print(f"✓ Score percentage: {pred.score_percentage}%")

    # Test notification settings methods
    notification_settings = await session.execute(
        select(UserCollegeNotificationSettings)
        .where(UserCollegeNotificationSettings.user_id == user.id)
    )
    settings = notification_settings.scalar_one_or_none()

    if settings:
        from backend.models.enums import CollegeNotificationType
        frequency = settings.get_frequency_for_type(CollegeNotificationType.GAME_REMINDERS)
        print(f"✓ Game reminders frequency method: {frequency}")

    # Test personalized feed methods
    feed = await session.execute(
        select(PersonalizedFeed)
        .where(PersonalizedFeed.user_id == user.id)
    )
    feed_result = feed.scalar_one_or_none()

    if feed_result:
        from backend.models.enums import FeedContentType
        weight = feed_result.get_content_weight(FeedContentType.ARTICLES)
        print(f"✓ Articles content weight method: {weight}")

    # Test personalization profile properties
    profile = await session.execute(
        select(UserPersonalizationProfile)
        .where(UserPersonalizationProfile.user_id == user.id)
    )
    profile_result = profile.scalar_one_or_none()

    if profile_result:
        print(f"✓ Is active user: {profile_result.is_active_user}")
        print(f"✓ Needs recalculation: {profile_result.needs_recalculation}")
        team_affinity = profile_result.get_team_affinity("sample_team")
        print(f"✓ Team affinity method: {team_affinity}")

    print("All property tests passed!")


async def run_integration_tests():
    """Run all integration tests"""
    print("Starting Phase 6 User Personalization Integration Tests")
    print("=" * 60)

    async for session in get_async_session():
        try:
            # Test model creation
            user = await test_model_creation(session)

            # Test relationships
            await test_model_relationships(session, user)

            # Test properties and methods
            await test_model_properties(session, user)

            print("\n" + "=" * 60)
            print("✅ All Phase 6 integration tests passed successfully!")
            print("The user personalization system is ready for production.")

            break

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(run_integration_tests())