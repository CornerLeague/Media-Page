"""
Phase 6: Performance Optimization for User Personalization
Database indexes, query optimization, and performance tuning for personalized features
"""

import asyncio
import logging
from typing import List, Dict, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

logger = logging.getLogger(__name__)


class Phase6PerformanceOptimizer:
    """
    Performance optimization for Phase 6 user personalization features
    """

    def __init__(self):
        self.optimizer_name = "Phase 6: Performance Optimization"
        self.version = "20250921_2300_phase6_performance"

    async def apply_optimizations(self, session: AsyncSession) -> None:
        """
        Apply performance optimizations for user personalization
        """
        logger.info(f"Starting {self.optimizer_name}...")

        try:
            # Create composite indexes for complex queries
            await self._create_composite_indexes(session)

            # Create partial indexes for filtered queries
            await self._create_partial_indexes(session)

            # Create functional indexes for JSON queries
            await self._create_functional_indexes(session)

            # Create materialized views for analytics
            await self._create_materialized_views(session)

            # Update table statistics
            await self._update_statistics(session)

            await session.commit()
            logger.info(f"{self.optimizer_name} completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during {self.optimizer_name}: {e}")
            raise

    async def _create_composite_indexes(self, session: AsyncSession) -> None:
        """Create composite indexes for common query patterns"""
        logger.info("Creating composite indexes for personalization queries...")

        composite_indexes = [
            # User college preferences - common filtering patterns
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_college_prefs_active_engagement
            ON user_college_preferences(user_id, is_active, engagement_level)
            WHERE is_active = true;
            """,

            # User college preferences - interaction scoring
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_college_prefs_interaction_score
            ON user_college_preferences(user_id, interaction_score DESC, last_interaction_at DESC)
            WHERE is_active = true;
            """,

            # Bracket predictions - leaderboard queries
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bracket_predictions_leaderboard
            ON bracket_predictions(tournament_id, total_score DESC, correct_picks DESC)
            WHERE status IN ('scoring', 'final');
            """,

            # Bracket challenges - discovery and participation
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bracket_challenges_discovery
            ON bracket_challenges(status, privacy_setting, participant_count)
            WHERE status IN ('open', 'closed');
            """,

            # User engagement metrics - analytics queries
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_engagement_metrics_analytics
            ON user_engagement_metrics(user_id, occurred_at DESC, metric_type, engagement_value DESC);
            """,

            # User engagement metrics - team-specific queries
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_engagement_metrics_team_analytics
            ON user_engagement_metrics(college_team_id, occurred_at DESC, metric_type)
            WHERE college_team_id IS NOT NULL;
            """,

            # Personalization profiles - calculation scheduling
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalization_profiles_calc_schedule
            ON user_personalization_profiles(last_calculated_at ASC, total_interactions DESC)
            WHERE total_interactions >= 10;
            """,
        ]

        for index_sql in composite_indexes:
            try:
                await session.execute(text(index_sql))
                logger.info("Created composite index")
            except Exception as e:
                logger.warning(f"Composite index creation skipped (might already exist): {e}")

    async def _create_partial_indexes(self, session: AsyncSession) -> None:
        """Create partial indexes for frequently filtered data"""
        logger.info("Creating partial indexes for filtered queries...")

        partial_indexes = [
            # Active college preferences only
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_college_prefs_active_only
            ON user_college_preferences(user_id, college_team_id, engagement_level)
            WHERE is_active = true;
            """,

            # Die-hard fans only (highest engagement)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_college_prefs_die_hard
            ON user_college_preferences(user_id, college_team_id, last_interaction_at DESC)
            WHERE is_active = true AND engagement_level = 'die_hard';
            """,

            # Active bracket predictions
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bracket_predictions_active
            ON bracket_predictions(user_id, tournament_id, total_score DESC)
            WHERE status IN ('submitted', 'locked', 'scoring', 'final');
            """,

            # Open challenges
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bracket_challenges_open
            ON bracket_challenges(created_at DESC, participant_count ASC)
            WHERE status = 'open' AND (max_participants IS NULL OR participant_count < max_participants);
            """,

            # Recent engagement metrics (last 30 days)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_engagement_metrics_recent
            ON user_engagement_metrics(user_id, metric_type, engagement_value DESC)
            WHERE occurred_at >= NOW() - INTERVAL '30 days';
            """,

            # High-value engagement metrics
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_engagement_metrics_high_value
            ON user_engagement_metrics(user_id, occurred_at DESC, entity_type, entity_id)
            WHERE engagement_value >= 0.7;
            """,

            # Enabled personalized feeds
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalized_feeds_enabled
            ON personalized_feeds(user_id, last_refreshed_at ASC)
            WHERE enabled = true;
            """,

            # Notification settings with push enabled
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notification_settings_push_enabled
            ON user_college_notification_settings(user_id)
            WHERE enabled = true AND push_notifications = true;
            """,
        ]

        for index_sql in partial_indexes:
            try:
                await session.execute(text(index_sql))
                logger.info("Created partial index")
            except Exception as e:
                logger.warning(f"Partial index creation skipped (might already exist): {e}")

    async def _create_functional_indexes(self, session: AsyncSession) -> None:
        """Create functional indexes for JSON and computed columns"""
        logger.info("Creating functional indexes for JSON queries...")

        functional_indexes = [
            # Content type scores in personalization profiles
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalization_content_scores
            ON user_personalization_profiles USING GIN (content_type_scores);
            """,

            # Team affinity scores in personalization profiles
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalization_team_scores
            ON user_personalization_profiles USING GIN (team_affinity_scores);
            """,

            # Conference affinity scores
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalization_conference_scores
            ON user_personalization_profiles USING GIN (conference_affinity_scores);
            """,

            # Engagement patterns for behavioral analysis
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalization_engagement_patterns
            ON user_personalization_profiles USING GIN (engagement_patterns);
            """,

            # Bracket predictions data
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bracket_predictions_data
            ON bracket_predictions USING GIN (predictions);
            """,

            # Challenge scoring systems
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bracket_challenges_scoring
            ON bracket_challenges USING GIN (scoring_system);
            """,

            # Engagement metadata
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_engagement_metrics_metadata
            ON user_engagement_metrics USING GIN (metadata);
            """,

            # Specific content type score extraction
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalization_articles_score
            ON user_personalization_profiles ((content_type_scores->>'articles'))
            WHERE content_type_scores ? 'articles';
            """,

            # Tournament news preference
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_personalization_tournament_score
            ON user_personalization_profiles ((content_type_scores->>'tournament_news'))
            WHERE content_type_scores ? 'tournament_news';
            """,
        ]

        for index_sql in functional_indexes:
            try:
                await session.execute(text(index_sql))
                logger.info("Created functional index")
            except Exception as e:
                logger.warning(f"Functional index creation skipped (might already exist): {e}")

    async def _create_materialized_views(self, session: AsyncSession) -> None:
        """Create materialized views for complex analytics"""
        logger.info("Creating materialized views for analytics...")

        materialized_views = [
            # User engagement summary
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS user_engagement_summary AS
            SELECT
                user_id,
                COUNT(*) as total_interactions,
                COUNT(DISTINCT DATE(occurred_at)) as active_days,
                COUNT(DISTINCT session_id) as total_sessions,
                AVG(engagement_value) as avg_engagement_value,
                MAX(occurred_at) as last_interaction,
                COUNT(DISTINCT metric_type) as interaction_types,
                COUNT(DISTINCT college_team_id) as teams_interacted
            FROM user_engagement_metrics
            WHERE occurred_at >= NOW() - INTERVAL '90 days'
            GROUP BY user_id;
            """,

            # Team popularity metrics
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS team_popularity_metrics AS
            SELECT
                college_team_id,
                COUNT(*) as total_followers,
                COUNT(CASE WHEN engagement_level = 'die_hard' THEN 1 END) as die_hard_fans,
                COUNT(CASE WHEN engagement_level = 'regular' THEN 1 END) as regular_fans,
                COUNT(CASE WHEN engagement_level = 'casual' THEN 1 END) as casual_fans,
                AVG(interaction_score) as avg_interaction_score,
                COUNT(CASE WHEN last_interaction_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_active_followers
            FROM user_college_preferences
            WHERE is_active = true
            GROUP BY college_team_id;
            """,

            # Challenge participation summary
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS challenge_participation_summary AS
            SELECT
                bc.id as challenge_id,
                bc.name as challenge_name,
                bc.tournament_id,
                bc.creator_id,
                bc.status,
                bc.participant_count,
                COUNT(bcp.id) as actual_participants,
                AVG(bcp.current_score) as avg_score,
                MAX(bcp.current_score) as top_score,
                COUNT(CASE WHEN bcp.current_rank = 1 THEN 1 END) as leaders
            FROM bracket_challenges bc
            LEFT JOIN bracket_challenge_participations bcp ON bc.id = bcp.challenge_id
            GROUP BY bc.id, bc.name, bc.tournament_id, bc.creator_id, bc.status, bc.participant_count;
            """,

            # Content engagement by type
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS content_engagement_by_type AS
            SELECT
                metric_type,
                entity_type,
                COUNT(*) as total_interactions,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(engagement_value) as avg_engagement_value,
                COUNT(CASE WHEN occurred_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_interactions
            FROM user_engagement_metrics
            WHERE occurred_at >= NOW() - INTERVAL '90 days'
            GROUP BY metric_type, entity_type;
            """,
        ]

        for view_sql in materialized_views:
            try:
                await session.execute(text(view_sql))
                logger.info("Created materialized view")
            except Exception as e:
                logger.warning(f"Materialized view creation skipped (might already exist): {e}")

        # Create indexes on materialized views
        materialized_view_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_engagement_summary_user ON user_engagement_summary(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_engagement_summary_interactions ON user_engagement_summary(total_interactions DESC);",
            "CREATE INDEX IF NOT EXISTS idx_team_popularity_metrics_team ON team_popularity_metrics(college_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_team_popularity_metrics_followers ON team_popularity_metrics(total_followers DESC);",
            "CREATE INDEX IF NOT EXISTS idx_challenge_participation_summary_challenge ON challenge_participation_summary(challenge_id);",
            "CREATE INDEX IF NOT EXISTS idx_challenge_participation_summary_tournament ON challenge_participation_summary(tournament_id);",
            "CREATE INDEX IF NOT EXISTS idx_content_engagement_by_type_metric ON content_engagement_by_type(metric_type);",
        ]

        for index_sql in materialized_view_indexes:
            try:
                await session.execute(text(index_sql))
                logger.info("Created materialized view index")
            except Exception as e:
                logger.warning(f"Materialized view index creation skipped: {e}")

    async def _update_statistics(self, session: AsyncSession) -> None:
        """Update table statistics for query optimization"""
        logger.info("Updating table statistics...")

        tables = [
            "user_college_preferences",
            "bracket_predictions",
            "bracket_challenges",
            "bracket_challenge_participations",
            "user_college_notification_settings",
            "personalized_feeds",
            "user_engagement_metrics",
            "user_personalization_profiles",
        ]

        for table in tables:
            try:
                await session.execute(text(f"ANALYZE {table};"))
                logger.info(f"Updated statistics for {table}")
            except Exception as e:
                logger.warning(f"Statistics update failed for {table}: {e}")

    async def create_performance_monitoring_queries(self) -> Dict[str, str]:
        """
        Return a set of performance monitoring queries for ongoing optimization
        """
        return {
            "slow_personalization_queries": """
                SELECT query, calls, total_time, mean_time, stddev_time
                FROM pg_stat_statements
                WHERE query LIKE '%user_college_preferences%'
                   OR query LIKE '%personalized_feeds%'
                   OR query LIKE '%user_engagement_metrics%'
                ORDER BY mean_time DESC
                LIMIT 10;
            """,

            "index_usage_stats": """
                SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE tablename IN (
                    'user_college_preferences',
                    'bracket_predictions',
                    'bracket_challenges',
                    'user_engagement_metrics',
                    'personalized_feeds'
                )
                ORDER BY idx_scan DESC;
            """,

            "table_size_stats": """
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables
                WHERE tablename IN (
                    'user_college_preferences',
                    'bracket_predictions',
                    'bracket_challenges',
                    'user_engagement_metrics',
                    'personalized_feeds',
                    'user_personalization_profiles'
                )
                ORDER BY size_bytes DESC;
            """,

            "materialized_view_freshness": """
                SELECT
                    schemaname,
                    matviewname,
                    ispopulated,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
                FROM pg_matviews
                WHERE matviewname IN (
                    'user_engagement_summary',
                    'team_popularity_metrics',
                    'challenge_participation_summary',
                    'content_engagement_by_type'
                );
            """,

            "active_user_distribution": """
                SELECT
                    engagement_level,
                    COUNT(*) as user_count,
                    AVG(interaction_score) as avg_interaction_score
                FROM user_college_preferences
                WHERE is_active = true
                GROUP BY engagement_level
                ORDER BY
                    CASE engagement_level
                        WHEN 'die_hard' THEN 1
                        WHEN 'regular' THEN 2
                        WHEN 'casual' THEN 3
                    END;
            """,
        }


async def run_performance_optimization():
    """
    Run the Phase 6 performance optimization
    """
    optimizer = Phase6PerformanceOptimizer()

    async with get_async_session() as session:
        try:
            await optimizer.apply_optimizations(session)
            print(f"Successfully applied {optimizer.optimizer_name}")

            # Show performance monitoring queries
            monitoring_queries = await optimizer.create_performance_monitoring_queries()
            print("\nPerformance Monitoring Queries:")
            print("=" * 50)
            for name, query in monitoring_queries.items():
                print(f"\n{name.upper()}:")
                print(f"-- {query}")

        except Exception as e:
            print(f"Performance optimization failed: {e}")
            raise


async def refresh_materialized_views():
    """
    Refresh materialized views for updated analytics
    """
    print("Refreshing materialized views...")

    views = [
        "user_engagement_summary",
        "team_popularity_metrics",
        "challenge_participation_summary",
        "content_engagement_by_type",
    ]

    async with get_async_session() as session:
        try:
            for view in views:
                await session.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view};"))
                print(f"✓ Refreshed {view}")

            await session.commit()
            print("All materialized views refreshed successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Materialized view refresh failed: {e}")
            raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "refresh":
        asyncio.run(refresh_materialized_views())
    else:
        asyncio.run(run_performance_optimization())