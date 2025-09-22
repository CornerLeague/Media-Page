"""
Phase 5: Content Integration Performance Optimization

This script provides database performance optimization for Phase 5 content models,
including custom indexing strategies, query optimization, and maintenance procedures.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

logger = logging.getLogger(__name__)


class Phase5PerformanceOptimizer:
    """
    Performance optimization tools for Phase 5 content integration.

    Provides:
    - Advanced indexing strategies
    - Query performance analysis
    - Content search optimization
    - Database maintenance procedures
    - Performance monitoring
    """

    def __init__(self):
        self.optimization_name = "Phase 5: Content Performance Optimization"

    async def optimize_all(self, session: AsyncSession) -> None:
        """Run all performance optimizations"""
        logger.info(f"Starting {self.optimization_name}...")

        try:
            # Create advanced indexes
            await self._create_advanced_indexes(session)

            # Optimize search functionality
            await self._optimize_search_performance(session)

            # Create composite indexes for common query patterns
            await self._create_composite_indexes(session)

            # Set up database maintenance procedures
            await self._setup_maintenance_procedures(session)

            # Analyze and optimize existing queries
            await self._analyze_query_performance(session)

            await session.commit()
            logger.info(f"{self.optimization_name} completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.optimization_name}: {str(e)}")
            raise

    async def _create_advanced_indexes(self, session: AsyncSession) -> None:
        """Create advanced indexes for complex query patterns"""
        logger.info("Creating advanced indexes...")

        # Partial indexes for active content
        advanced_indexes = [
            # Partial index for active college content by publication date
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_active_published
            ON college_content (published_at DESC, relevance_score DESC)
            WHERE is_active = true
            """,

            # Partial index for featured content
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_featured_active
            ON college_content (published_at DESC, content_type)
            WHERE is_featured = true AND is_active = true
            """,

            # Composite index for team-specific content queries
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_team_type_date
            ON college_content (primary_team_id, content_type, published_at DESC)
            WHERE is_active = true
            """,

            # Index for multi-team content (games, etc.)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_multi_team
            ON college_content (primary_team_id, secondary_team_id, published_at DESC)
            WHERE secondary_team_id IS NOT NULL AND is_active = true
            """,

            # Injury reports by severity and status
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_injury_reports_severity_active
            ON injury_reports (severity, current_status, injury_date DESC)
            WHERE is_active = true
            """,

            # Recent injury reports by team
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_injury_reports_team_recent
            ON injury_reports (team_id, injury_date DESC)
            WHERE is_active = true AND injury_date >= CURRENT_DATE - INTERVAL '30 days'
            """,

            # Recruiting news by class and event type
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recruiting_news_class_event
            ON recruiting_news (recruiting_class, event_type, event_date DESC)
            WHERE verified = true
            """,

            # Transfer portal activity
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recruiting_news_transfers
            ON recruiting_news (event_type, event_date DESC, team_id)
            WHERE is_transfer = true
            """,

            # High-rated recruits
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recruiting_news_rating
            ON recruiting_news (rating DESC, national_ranking ASC, event_date DESC)
            WHERE rating >= 4.0 AND verified = true
            """,

            # Recent coaching changes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_coaching_news_recent_changes
            ON coaching_news (change_type, effective_date DESC, team_id)
            WHERE verified = true AND effective_date >= CURRENT_DATE - INTERVAL '1 year'
            """,

            # Content team associations by relevance
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_team_assoc_relevance_desc
            ON content_team_associations (team_id, relevance_score DESC, created_at DESC)
            """,

            # Content classifications by confidence
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_class_confidence_type
            ON content_classifications (classification_type, confidence_score DESC, created_at DESC)
            """
        ]

        for index_sql in advanced_indexes:
            try:
                await session.execute(text(index_sql))
                logger.info(f"Created advanced index: {index_sql.split()[5]}")
            except Exception as e:
                logger.warning(f"Index creation skipped or failed: {str(e)}")

    async def _optimize_search_performance(self, session: AsyncSession) -> None:
        """Optimize full-text search performance"""
        logger.info("Optimizing search performance...")

        # Enable pg_trgm extension if not already enabled
        try:
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        except Exception as e:
            logger.warning(f"pg_trgm extension setup skipped: {str(e)}")

        # Create specialized search indexes
        search_optimizations = [
            # Trigram index for fuzzy title search
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_title_trgm_ops
            ON college_content USING gin (title gin_trgm_ops)
            """,

            # Trigram index for author search
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_author_trgm
            ON college_content USING gin (author gin_trgm_ops)
            WHERE author IS NOT NULL
            """,

            # Array index for tags
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_tags_gin
            ON college_content USING gin (tags)
            """,

            # Array index for mentioned players
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_players_gin
            ON college_content USING gin (mentioned_players)
            """,

            # Array index for mentioned coaches
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_college_content_coaches_gin
            ON college_content USING gin (mentioned_coaches)
            """,

            # Recruit name trigram search
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recruiting_news_recruit_trgm
            ON recruiting_news USING gin (recruit_name gin_trgm_ops)
            """,

            # Coach name trigram search
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_coaching_news_coach_trgm
            ON coaching_news USING gin (coach_name gin_trgm_ops)
            """
        ]

        for search_sql in search_optimizations:
            try:
                await session.execute(text(search_sql))
                logger.info(f"Created search index: {search_sql.split()[5]}")
            except Exception as e:
                logger.warning(f"Search index creation skipped: {str(e)}")

    async def _create_composite_indexes(self, session: AsyncSession) -> None:
        """Create composite indexes for common query patterns"""
        logger.info("Creating composite indexes for common query patterns...")

        composite_indexes = [
            # Team content feed query optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_team_content_feed
            ON college_content (primary_team_id, is_active, published_at DESC, relevance_score DESC)
            """,

            # Player-related content optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_player_content_lookup
            ON college_content (primary_player_id, content_type, published_at DESC)
            WHERE primary_player_id IS NOT NULL
            """,

            # Content type timeline optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_type_timeline
            ON college_content (content_type, published_at DESC, is_active)
            """,

            # Team injury tracking optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_team_injury_tracking
            ON injury_reports (team_id, current_status, injury_date DESC, severity)
            """,

            # Player injury history optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_player_injury_history
            ON injury_reports (player_id, injury_date DESC, severity)
            """,

            # Team recruiting activity optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_team_recruiting_activity
            ON recruiting_news (team_id, event_type, event_date DESC, verified)
            """,

            # Recruiting class analysis optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recruiting_class_analysis
            ON recruiting_news (recruiting_class, rating DESC, national_ranking ASC, event_type)
            """,

            # Team coaching stability optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_team_coaching_stability
            ON coaching_news (team_id, change_type, effective_date DESC, verified)
            """,

            # Content engagement optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_engagement
            ON college_content (engagement_score DESC, published_at DESC, is_active)
            WHERE engagement_score IS NOT NULL
            """,

            # Multi-team content analysis
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_multi_team_content
            ON content_team_associations (team_id, relevance_score DESC, association_type)
            """
        ]

        for index_sql in composite_indexes:
            try:
                await session.execute(text(index_sql))
                logger.info(f"Created composite index: {index_sql.split()[5]}")
            except Exception as e:
                logger.warning(f"Composite index creation skipped: {str(e)}")

    async def _setup_maintenance_procedures(self, session: AsyncSession) -> None:
        """Set up database maintenance procedures for content tables"""
        logger.info("Setting up maintenance procedures...")

        # Create function for cleaning old content
        cleanup_function = """
        CREATE OR REPLACE FUNCTION cleanup_old_content()
        RETURNS void AS $$
        BEGIN
            -- Archive old inactive content (older than 2 years)
            UPDATE college_content
            SET is_active = false
            WHERE published_at < NOW() - INTERVAL '2 years'
              AND is_active = true
              AND is_featured = false;

            -- Clean up old injury reports (resolved and older than 1 year)
            UPDATE injury_reports
            SET is_active = false
            WHERE actual_return_date IS NOT NULL
              AND actual_return_date < NOW() - INTERVAL '1 year'
              AND is_active = true;

            -- Archive old recruiting news (older than 3 years)
            DELETE FROM recruiting_news
            WHERE event_date < NOW() - INTERVAL '3 years';

            -- Clean up old content classifications
            DELETE FROM content_classifications
            WHERE created_at < NOW() - INTERVAL '1 year'
              AND content_id NOT IN (
                  SELECT id FROM college_content WHERE is_active = true
              );

            RAISE NOTICE 'Content cleanup completed at %', NOW();
        END;
        $$ LANGUAGE plpgsql;
        """

        # Create function for updating search vectors
        search_update_function = """
        CREATE OR REPLACE FUNCTION update_all_search_vectors()
        RETURNS void AS $$
        BEGIN
            UPDATE college_content
            SET search_vector =
                setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(content, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(author, '')), 'D') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(mentioned_players, ' '), '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(mentioned_coaches, ' '), '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(tags, ' '), '')), 'C')
            WHERE search_vector IS NULL
               OR updated_at > NOW() - INTERVAL '1 hour';

            RAISE NOTICE 'Search vectors updated at %', NOW();
        END;
        $$ LANGUAGE plpgsql;
        """

        # Create function for content statistics
        stats_function = """
        CREATE OR REPLACE FUNCTION get_content_statistics()
        RETURNS TABLE (
            total_content bigint,
            active_content bigint,
            featured_content bigint,
            recent_content bigint,
            injury_reports bigint,
            recruiting_news bigint,
            coaching_news bigint
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                (SELECT COUNT(*) FROM college_content),
                (SELECT COUNT(*) FROM college_content WHERE is_active = true),
                (SELECT COUNT(*) FROM college_content WHERE is_featured = true),
                (SELECT COUNT(*) FROM college_content WHERE published_at >= NOW() - INTERVAL '7 days'),
                (SELECT COUNT(*) FROM injury_reports WHERE is_active = true),
                (SELECT COUNT(*) FROM recruiting_news WHERE event_date >= NOW() - INTERVAL '30 days'),
                (SELECT COUNT(*) FROM coaching_news WHERE effective_date >= NOW() - INTERVAL '30 days');
        END;
        $$ LANGUAGE plpgsql;
        """

        maintenance_functions = [cleanup_function, search_update_function, stats_function]

        for func_sql in maintenance_functions:
            try:
                await session.execute(text(func_sql))
                logger.info("Created maintenance function")
            except Exception as e:
                logger.warning(f"Maintenance function creation skipped: {str(e)}")

    async def _analyze_query_performance(self, session: AsyncSession) -> None:
        """Analyze common query performance patterns"""
        logger.info("Analyzing query performance...")

        # Sample queries to analyze
        performance_queries = [
            {
                "name": "Recent team content",
                "query": """
                SELECT title, published_at, content_type
                FROM college_content
                WHERE primary_team_id = $1 AND is_active = true
                ORDER BY published_at DESC
                LIMIT 10
                """
            },
            {
                "name": "Featured content feed",
                "query": """
                SELECT title, published_at, relevance_score
                FROM college_content
                WHERE is_featured = true AND is_active = true
                ORDER BY published_at DESC
                LIMIT 20
                """
            },
            {
                "name": "Active injury reports",
                "query": """
                SELECT ir.injury_description, ir.severity, p.full_name, ct.name
                FROM injury_reports ir
                JOIN players p ON ir.player_id = p.id
                JOIN college_teams ct ON ir.team_id = ct.id
                WHERE ir.is_active = true
                ORDER BY ir.injury_date DESC
                """
            },
            {
                "name": "Recent recruiting commits",
                "query": """
                SELECT recruit_name, rating, ct.name as team
                FROM recruiting_news rn
                LEFT JOIN college_teams ct ON rn.team_id = ct.id
                WHERE event_type = 'commit' AND verified = true
                ORDER BY event_date DESC
                LIMIT 20
                """
            },
            {
                "name": "Content search by tags",
                "query": """
                SELECT title, tags, published_at
                FROM college_content
                WHERE tags && ARRAY['recruiting'] AND is_active = true
                ORDER BY published_at DESC
                LIMIT 15
                """
            }
        ]

        for query_info in performance_queries:
            try:
                # Use EXPLAIN to analyze query performance
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS) {query_info['query']}"
                result = await session.execute(text(explain_query))

                logger.info(f"Query analysis for '{query_info['name']}':")
                for row in result:
                    logger.info(f"  {row[0]}")

            except Exception as e:
                logger.warning(f"Query analysis failed for '{query_info['name']}': {str(e)}")

    async def generate_performance_report(self, session: AsyncSession) -> Dict:
        """Generate a comprehensive performance report"""
        logger.info("Generating performance report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "table_sizes": {},
            "index_usage": {},
            "content_statistics": {}
        }

        try:
            # Get table sizes
            size_query = """
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables
            WHERE tablename IN (
                'college_content', 'injury_reports', 'recruiting_news',
                'coaching_news', 'content_team_associations', 'content_classifications'
            )
            ORDER BY size_bytes DESC
            """

            result = await session.execute(text(size_query))
            for row in result:
                report["table_sizes"][row.tablename] = {
                    "size": row.size,
                    "size_bytes": row.size_bytes
                }

            # Get content statistics
            stats_result = await session.execute(text("SELECT * FROM get_content_statistics()"))
            stats = stats_result.fetchone()
            if stats:
                report["content_statistics"] = {
                    "total_content": stats[0],
                    "active_content": stats[1],
                    "featured_content": stats[2],
                    "recent_content": stats[3],
                    "injury_reports": stats[4],
                    "recruiting_news": stats[5],
                    "coaching_news": stats[6]
                }

            # Get index usage statistics
            index_query = """
            SELECT
                indexrelname as index_name,
                idx_tup_read,
                idx_tup_fetch,
                idx_scan
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
              AND indexrelname LIKE '%college_content%'
               OR indexrelname LIKE '%injury_reports%'
               OR indexrelname LIKE '%recruiting_news%'
               OR indexrelname LIKE '%coaching_news%'
            ORDER BY idx_scan DESC
            """

            result = await session.execute(text(index_query))
            for row in result:
                report["index_usage"][row.index_name] = {
                    "tuples_read": row.idx_tup_read,
                    "tuples_fetched": row.idx_tup_fetch,
                    "scans": row.idx_scan
                }

        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            report["error"] = str(e)

        return report

    async def cleanup_old_data(self, session: AsyncSession) -> None:
        """Run data cleanup maintenance"""
        logger.info("Running data cleanup...")

        try:
            await session.execute(text("SELECT cleanup_old_content()"))
            await session.commit()
            logger.info("Data cleanup completed successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Data cleanup failed: {str(e)}")
            raise

    async def refresh_search_vectors(self, session: AsyncSession) -> None:
        """Refresh all search vectors"""
        logger.info("Refreshing search vectors...")

        try:
            await session.execute(text("SELECT update_all_search_vectors()"))
            await session.commit()
            logger.info("Search vector refresh completed successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Search vector refresh failed: {str(e)}")
            raise


async def run_performance_optimization():
    """Run Phase 5 performance optimization"""
    optimizer = Phase5PerformanceOptimizer()

    async with get_async_session() as session:
        await optimizer.optimize_all(session)
        print("Phase 5 performance optimization completed successfully!")


async def run_performance_report():
    """Generate and display performance report"""
    optimizer = Phase5PerformanceOptimizer()

    async with get_async_session() as session:
        report = await optimizer.generate_performance_report(session)

        print("\n" + "="*60)
        print("PHASE 5 PERFORMANCE REPORT")
        print("="*60)

        print("\nTable Sizes:")
        for table, info in report.get("table_sizes", {}).items():
            print(f"  {table}: {info['size']}")

        print("\nContent Statistics:")
        stats = report.get("content_statistics", {})
        if stats:
            print(f"  Total Content: {stats.get('total_content', 0)}")
            print(f"  Active Content: {stats.get('active_content', 0)}")
            print(f"  Featured Content: {stats.get('featured_content', 0)}")
            print(f"  Recent Content (7 days): {stats.get('recent_content', 0)}")
            print(f"  Active Injury Reports: {stats.get('injury_reports', 0)}")
            print(f"  Recent Recruiting News: {stats.get('recruiting_news', 0)}")
            print(f"  Recent Coaching News: {stats.get('coaching_news', 0)}")

        print("\nTop Index Usage:")
        for index, info in list(report.get("index_usage", {}).items())[:10]:
            print(f"  {index}: {info['scans']} scans")


async def run_maintenance():
    """Run database maintenance tasks"""
    optimizer = Phase5PerformanceOptimizer()

    async with get_async_session() as session:
        print("Running database maintenance...")
        await optimizer.cleanup_old_data(session)
        await optimizer.refresh_search_vectors(session)
        print("Database maintenance completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "report":
            asyncio.run(run_performance_report())
        elif sys.argv[1] == "maintenance":
            asyncio.run(run_maintenance())
        else:
            print("Usage: python phase5_performance_optimization.py [report|maintenance]")
    else:
        asyncio.run(run_performance_optimization())