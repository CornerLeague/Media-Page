"""
Phase 6: College Basketball User Personalization Migration
Creates user preferences, bracket predictions, challenges, and engagement tracking

This migration implements the final user personalization layer for the college
basketball platform, integrating with existing user authentication and preference systems.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

logger = logging.getLogger(__name__)


class Phase6UserPersonalizationMigration:
    """
    Phase 6 migration implementing user personalization features.

    Creates:
    - User college team preferences with engagement levels
    - Bracket prediction system for March Madness
    - Bracket challenge group competitions
    - Enhanced notification settings for college basketball
    - Personalized content feed configuration
    - User engagement metrics tracking
    - Aggregated personalization profiles
    """

    def __init__(self):
        self.migration_name = "Phase 6: User Personalization"
        self.version = "20250921_2100_phase6_user_personalization"

    async def upgrade(self, session: AsyncSession) -> None:
        """
        Apply Phase 6 user personalization schema changes
        """
        logger.info(f"Starting {self.migration_name} upgrade...")

        try:
            # Create enum types first
            await self._create_enum_types(session)

            # Create core personalization tables
            await self._create_personalization_tables(session)

            # Create indexes for performance
            await self._create_indexes(session)

            # Add constraints and relationships
            await self._create_constraints(session)

            await session.commit()
            logger.info(f"{self.migration_name} upgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during {self.migration_name} upgrade: {e}")
            raise

    async def downgrade(self, session: AsyncSession) -> None:
        """
        Rollback Phase 6 user personalization schema changes
        """
        logger.info(f"Starting {self.migration_name} downgrade...")

        try:
            # Drop tables in reverse dependency order
            await self._drop_personalization_tables(session)

            # Drop enum types
            await self._drop_enum_types(session)

            await session.commit()
            logger.info(f"{self.migration_name} downgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during {self.migration_name} downgrade: {e}")
            raise

    async def _create_enum_types(self, session: AsyncSession) -> None:
        """Create enum types for Phase 6"""
        logger.info("Creating Phase 6 enum types...")

        enum_definitions = [
            # Engagement Level
            """
            CREATE TYPE engagement_level AS ENUM (
                'casual', 'regular', 'die_hard'
            );
            """,

            # Bracket Prediction Status
            """
            CREATE TYPE bracket_prediction_status AS ENUM (
                'draft', 'submitted', 'locked', 'scoring', 'final'
            );
            """,

            # Bracket Challenge Status
            """
            CREATE TYPE bracket_challenge_status AS ENUM (
                'open', 'closed', 'locked', 'in_progress', 'completed'
            );
            """,

            # Challenge Privacy
            """
            CREATE TYPE challenge_privacy AS ENUM (
                'public', 'friends_only', 'invite_only', 'private'
            );
            """,

            # Notification Frequency
            """
            CREATE TYPE notification_frequency AS ENUM (
                'never', 'immediate', 'daily_digest', 'weekly_digest', 'game_day_only'
            );
            """,

            # College Notification Type
            """
            CREATE TYPE college_notification_type AS ENUM (
                'game_reminders', 'score_updates', 'injury_updates',
                'recruiting_news', 'coaching_changes', 'ranking_changes',
                'tournament_updates', 'bracket_challenge', 'transfer_portal',
                'suspension_news'
            );
            """,

            # Feed Content Type
            """
            CREATE TYPE feed_content_type AS ENUM (
                'articles', 'game_updates', 'injury_reports', 'recruiting_news',
                'coaching_news', 'rankings', 'tournament_news', 'bracket_updates',
                'social_updates'
            );
            """,

            # Engagement Metric Type
            """
            CREATE TYPE engagement_metric_type AS ENUM (
                'article_view', 'article_share', 'article_like', 'team_page_view',
                'game_detail_view', 'bracket_created', 'bracket_updated',
                'challenge_joined', 'comment_posted', 'search_performed',
                'notification_clicked', 'feed_scroll', 'team_followed',
                'team_unfollowed', 'settings_updated'
            );
            """,

            # Personalization Score
            """
            CREATE TYPE personalization_score AS ENUM (
                'very_low', 'low', 'medium', 'high', 'very_high'
            );
            """,
        ]

        for enum_def in enum_definitions:
            await session.execute(text(enum_def))

    async def _create_personalization_tables(self, session: AsyncSession) -> None:
        """Create Phase 6 personalization tables"""
        logger.info("Creating Phase 6 personalization tables...")

        # 1. User College Preferences
        await session.execute(text("""
            CREATE TABLE user_college_preferences (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                college_team_id UUID NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                engagement_level engagement_level NOT NULL DEFAULT 'regular',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                followed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                -- Team-specific notification preferences
                game_reminders BOOLEAN NOT NULL DEFAULT TRUE,
                injury_updates BOOLEAN NOT NULL DEFAULT TRUE,
                recruiting_news BOOLEAN NOT NULL DEFAULT FALSE,
                coaching_updates BOOLEAN NOT NULL DEFAULT TRUE,

                -- Calculated engagement metrics
                interaction_score NUMERIC(5,4) NOT NULL DEFAULT 0.5000,
                last_interaction_at TIMESTAMPTZ,

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                CONSTRAINT uq_user_college_team UNIQUE (user_id, college_team_id)
            );
        """))

        # 2. Bracket Predictions
        await session.execute(text("""
            CREATE TABLE bracket_predictions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
                bracket_name VARCHAR(100),
                status bracket_prediction_status NOT NULL DEFAULT 'draft',

                -- Bracket data
                predictions JSONB NOT NULL DEFAULT '{}',

                -- Scoring information
                total_score INTEGER NOT NULL DEFAULT 0,
                possible_score INTEGER NOT NULL DEFAULT 0,
                correct_picks INTEGER NOT NULL DEFAULT 0,
                total_picks INTEGER NOT NULL DEFAULT 0,

                -- Timing information
                submitted_at TIMESTAMPTZ,
                locked_at TIMESTAMPTZ,
                last_scored_at TIMESTAMPTZ,

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                CONSTRAINT uq_user_tournament_bracket UNIQUE (user_id, tournament_id)
            );
        """))

        # 3. Bracket Challenges
        await session.execute(text("""
            CREATE TABLE bracket_challenges (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                status bracket_challenge_status NOT NULL DEFAULT 'open',
                privacy_setting challenge_privacy NOT NULL DEFAULT 'friends_only',

                -- Entry settings
                entry_fee NUMERIC(10,2),
                max_participants INTEGER,
                registration_deadline TIMESTAMPTZ,

                -- Scoring and prizes
                scoring_system JSONB NOT NULL DEFAULT '{}',
                prize_structure JSONB,

                -- Challenge code
                invite_code VARCHAR(20) UNIQUE,

                -- Statistics
                participant_count INTEGER NOT NULL DEFAULT 0,

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))

        # 4. Bracket Challenge Participations
        await session.execute(text("""
            CREATE TABLE bracket_challenge_participations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                challenge_id UUID NOT NULL REFERENCES bracket_challenges(id) ON DELETE CASCADE,
                bracket_prediction_id UUID NOT NULL REFERENCES bracket_predictions(id) ON DELETE CASCADE,

                -- Participation details
                joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                -- Challenge-specific scoring
                current_score INTEGER NOT NULL DEFAULT 0,
                current_rank INTEGER,

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                CONSTRAINT uq_challenge_bracket UNIQUE (challenge_id, bracket_prediction_id)
            );
        """))

        # 5. User College Notification Settings
        await session.execute(text("""
            CREATE TABLE user_college_notification_settings (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,

                -- Global settings
                enabled BOOLEAN NOT NULL DEFAULT TRUE,

                -- Frequency preferences
                game_reminders_frequency notification_frequency NOT NULL DEFAULT 'game_day_only',
                score_updates_frequency notification_frequency NOT NULL DEFAULT 'immediate',
                injury_updates_frequency notification_frequency NOT NULL DEFAULT 'immediate',
                recruiting_news_frequency notification_frequency NOT NULL DEFAULT 'daily_digest',
                coaching_changes_frequency notification_frequency NOT NULL DEFAULT 'immediate',
                ranking_changes_frequency notification_frequency NOT NULL DEFAULT 'weekly_digest',
                tournament_updates_frequency notification_frequency NOT NULL DEFAULT 'immediate',
                bracket_challenge_frequency notification_frequency NOT NULL DEFAULT 'immediate',
                transfer_portal_frequency notification_frequency NOT NULL DEFAULT 'daily_digest',

                -- Delivery methods
                push_notifications BOOLEAN NOT NULL DEFAULT TRUE,
                email_notifications BOOLEAN NOT NULL DEFAULT FALSE,

                -- Time preferences
                quiet_hours_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                quiet_hours_start INTEGER CHECK (quiet_hours_start >= 0 AND quiet_hours_start <= 23),
                quiet_hours_end INTEGER CHECK (quiet_hours_end >= 0 AND quiet_hours_end <= 23),

                -- Game day settings
                pre_game_reminders BOOLEAN NOT NULL DEFAULT TRUE,
                pre_game_reminder_minutes INTEGER NOT NULL DEFAULT 30,
                halftime_updates BOOLEAN NOT NULL DEFAULT FALSE,
                final_score_notifications BOOLEAN NOT NULL DEFAULT TRUE,

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))

        # 6. Personalized Feeds
        await session.execute(text("""
            CREATE TABLE personalized_feeds (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,

                -- Feed configuration
                enabled BOOLEAN NOT NULL DEFAULT TRUE,

                -- Content type weights (0.0 - 1.0)
                articles_weight NUMERIC(3,2) NOT NULL DEFAULT 1.00,
                game_updates_weight NUMERIC(3,2) NOT NULL DEFAULT 0.80,
                injury_reports_weight NUMERIC(3,2) NOT NULL DEFAULT 0.70,
                recruiting_news_weight NUMERIC(3,2) NOT NULL DEFAULT 0.60,
                coaching_news_weight NUMERIC(3,2) NOT NULL DEFAULT 0.75,
                rankings_weight NUMERIC(3,2) NOT NULL DEFAULT 0.65,
                tournament_news_weight NUMERIC(3,2) NOT NULL DEFAULT 0.90,
                bracket_updates_weight NUMERIC(3,2) NOT NULL DEFAULT 0.85,

                -- Algorithm preferences
                recency_factor NUMERIC(3,2) NOT NULL DEFAULT 0.30,
                engagement_factor NUMERIC(3,2) NOT NULL DEFAULT 0.40,
                team_preference_factor NUMERIC(3,2) NOT NULL DEFAULT 0.50,

                -- Feed settings
                max_items_per_refresh INTEGER NOT NULL DEFAULT 50,
                refresh_interval_hours INTEGER NOT NULL DEFAULT 2,

                -- Refresh tracking
                last_refreshed_at TIMESTAMPTZ,

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))

        # 7. User Engagement Metrics
        await session.execute(text("""
            CREATE TABLE user_engagement_metrics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                metric_type engagement_metric_type NOT NULL,

                -- Entity information
                entity_type VARCHAR(50) NOT NULL,
                entity_id UUID,

                -- Interaction details
                occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                metadata JSONB,

                -- Engagement scoring
                engagement_value NUMERIC(5,4) NOT NULL DEFAULT 0.0000,

                -- Session information
                session_id VARCHAR(100),

                -- College basketball context
                college_team_id UUID REFERENCES college_teams(id) ON DELETE SET NULL,

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))

        # 8. User Personalization Profiles
        await session.execute(text("""
            CREATE TABLE user_personalization_profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,

                -- Calculated preference scores
                content_type_scores JSONB NOT NULL DEFAULT '{}',
                team_affinity_scores JSONB NOT NULL DEFAULT '{}',
                conference_affinity_scores JSONB NOT NULL DEFAULT '{}',
                engagement_patterns JSONB NOT NULL DEFAULT '{}',

                -- Engagement metrics
                total_interactions INTEGER NOT NULL DEFAULT 0,
                average_session_duration NUMERIC(8,2),
                last_active_at TIMESTAMPTZ,

                -- Profile metadata
                last_calculated_at TIMESTAMPTZ,
                calculation_version VARCHAR(20) NOT NULL DEFAULT '1.0',

                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))

    async def _create_indexes(self, session: AsyncSession) -> None:
        """Create performance indexes for Phase 6 tables"""
        logger.info("Creating Phase 6 performance indexes...")

        indexes = [
            # User College Preferences indexes
            "CREATE INDEX idx_user_college_engagement ON user_college_preferences(user_id, engagement_level);",
            "CREATE INDEX idx_user_college_active ON user_college_preferences(user_id, is_active);",
            "CREATE INDEX idx_college_preferences_team ON user_college_preferences(college_team_id);",

            # Bracket Predictions indexes
            "CREATE INDEX idx_bracket_status ON bracket_predictions(status);",
            "CREATE INDEX idx_bracket_score ON bracket_predictions(total_score, status);",
            "CREATE INDEX idx_bracket_tournament ON bracket_predictions(tournament_id);",

            # Bracket Challenges indexes
            "CREATE INDEX idx_challenge_status ON bracket_challenges(status);",
            "CREATE INDEX idx_challenge_privacy ON bracket_challenges(privacy_setting);",
            "CREATE INDEX idx_challenge_creator ON bracket_challenges(creator_id);",
            "CREATE INDEX idx_challenge_tournament ON bracket_challenges(tournament_id);",

            # Bracket Challenge Participations indexes
            "CREATE INDEX idx_participation_challenge ON bracket_challenge_participations(challenge_id);",
            "CREATE INDEX idx_participation_score ON bracket_challenge_participations(challenge_id, current_score);",

            # User Engagement Metrics indexes
            "CREATE INDEX idx_engagement_user_type ON user_engagement_metrics(user_id, metric_type);",
            "CREATE INDEX idx_engagement_entity ON user_engagement_metrics(entity_type, entity_id);",
            "CREATE INDEX idx_engagement_timestamp ON user_engagement_metrics(occurred_at);",
            "CREATE INDEX idx_engagement_team ON user_engagement_metrics(college_team_id);",
            "CREATE INDEX idx_engagement_session ON user_engagement_metrics(user_id, session_id);",

            # Personalization performance indexes
            "CREATE INDEX idx_personalization_active ON user_personalization_profiles(last_active_at);",
            "CREATE INDEX idx_personalization_calculation ON user_personalization_profiles(last_calculated_at);",
        ]

        for index_sql in indexes:
            await session.execute(text(index_sql))

    async def _create_constraints(self, session: AsyncSession) -> None:
        """Create additional constraints for data integrity"""
        logger.info("Creating Phase 6 data integrity constraints...")

        constraints = [
            # Ensure engagement scores are within valid range
            "ALTER TABLE user_college_preferences ADD CONSTRAINT chk_interaction_score CHECK (interaction_score >= 0.0 AND interaction_score <= 1.0);",

            # Ensure bracket scores are non-negative
            "ALTER TABLE bracket_predictions ADD CONSTRAINT chk_total_score CHECK (total_score >= 0);",
            "ALTER TABLE bracket_predictions ADD CONSTRAINT chk_possible_score CHECK (possible_score >= 0);",
            "ALTER TABLE bracket_predictions ADD CONSTRAINT chk_correct_picks CHECK (correct_picks >= 0);",
            "ALTER TABLE bracket_predictions ADD CONSTRAINT chk_total_picks CHECK (total_picks >= 0);",

            # Ensure challenge participant count is non-negative
            "ALTER TABLE bracket_challenges ADD CONSTRAINT chk_participant_count CHECK (participant_count >= 0);",

            # Ensure challenge scores are non-negative
            "ALTER TABLE bracket_challenge_participations ADD CONSTRAINT chk_current_score CHECK (current_score >= 0);",

            # Ensure feed weights are within valid range
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_articles_weight CHECK (articles_weight >= 0.0 AND articles_weight <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_game_updates_weight CHECK (game_updates_weight >= 0.0 AND game_updates_weight <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_injury_reports_weight CHECK (injury_reports_weight >= 0.0 AND injury_reports_weight <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_recruiting_news_weight CHECK (recruiting_news_weight >= 0.0 AND recruiting_news_weight <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_coaching_news_weight CHECK (coaching_news_weight >= 0.0 AND coaching_news_weight <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_rankings_weight CHECK (rankings_weight >= 0.0 AND rankings_weight <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_tournament_news_weight CHECK (tournament_news_weight >= 0.0 AND tournament_news_weight <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_bracket_updates_weight CHECK (bracket_updates_weight >= 0.0 AND bracket_updates_weight <= 1.0);",

            # Ensure algorithm factors are within valid range
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_recency_factor CHECK (recency_factor >= 0.0 AND recency_factor <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_engagement_factor CHECK (engagement_factor >= 0.0 AND engagement_factor <= 1.0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_team_preference_factor CHECK (team_preference_factor >= 0.0 AND team_preference_factor <= 1.0);",

            # Ensure feed settings are reasonable
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_max_items CHECK (max_items_per_refresh > 0);",
            "ALTER TABLE personalized_feeds ADD CONSTRAINT chk_refresh_interval CHECK (refresh_interval_hours > 0);",

            # Ensure engagement values are within valid range
            "ALTER TABLE user_engagement_metrics ADD CONSTRAINT chk_engagement_value CHECK (engagement_value >= 0.0 AND engagement_value <= 1.0);",

            # Ensure profile metrics are non-negative
            "ALTER TABLE user_personalization_profiles ADD CONSTRAINT chk_total_interactions CHECK (total_interactions >= 0);",
            "ALTER TABLE user_personalization_profiles ADD CONSTRAINT chk_session_duration CHECK (average_session_duration IS NULL OR average_session_duration >= 0);",
        ]

        for constraint_sql in constraints:
            await session.execute(text(constraint_sql))

    async def _drop_personalization_tables(self, session: AsyncSession) -> None:
        """Drop Phase 6 personalization tables"""
        logger.info("Dropping Phase 6 personalization tables...")

        tables = [
            "user_personalization_profiles",
            "user_engagement_metrics",
            "personalized_feeds",
            "user_college_notification_settings",
            "bracket_challenge_participations",
            "bracket_challenges",
            "bracket_predictions",
            "user_college_preferences",
        ]

        for table in tables:
            await session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

    async def _drop_enum_types(self, session: AsyncSession) -> None:
        """Drop Phase 6 enum types"""
        logger.info("Dropping Phase 6 enum types...")

        enums = [
            "personalization_score",
            "engagement_metric_type",
            "feed_content_type",
            "college_notification_type",
            "notification_frequency",
            "challenge_privacy",
            "bracket_challenge_status",
            "bracket_prediction_status",
            "engagement_level",
        ]

        for enum_type in enums:
            await session.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE;"))


async def run_migration():
    """
    Run the Phase 6 migration
    """
    migration = Phase6UserPersonalizationMigration()

    session_generator = get_async_session()
    session = await session_generator.__anext__()
    try:
        await migration.upgrade(session)
        print(f"Successfully applied {migration.migration_name}")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        try:
            await session_generator.__anext__()
        except StopAsyncIteration:
            pass


async def rollback_migration():
    """
    Rollback the Phase 6 migration
    """
    migration = Phase6UserPersonalizationMigration()

    session_generator = get_async_session()
    session = await session_generator.__anext__()
    try:
        await migration.downgrade(session)
        print(f"Successfully rolled back {migration.migration_name}")
    except Exception as e:
        print(f"Rollback failed: {e}")
        raise
    finally:
        try:
            await session_generator.__anext__()
        except StopAsyncIteration:
            pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_migration())
    else:
        asyncio.run(run_migration())