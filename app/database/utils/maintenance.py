"""Database maintenance utilities for Corner League Media."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy import text, func, select, and_
from sqlalchemy.orm import Session

from ..database import get_session, get_database_info
from ..models import Article, IngestionLog, SearchAnalytics, Team, User


class DatabaseMaintenance:
    """Database maintenance and optimization utilities."""

    @staticmethod
    def vacuum_analyze(table_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform VACUUM ANALYZE on specified tables or all tables."""
        results = {}

        with get_session() as session:
            if table_names is None:
                # Get all table names
                table_result = session.execute(
                    text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """)
                ).fetchall()
                table_names = [row[0] for row in table_result]

            for table_name in table_names:
                try:
                    # Run VACUUM ANALYZE
                    session.execute(text(f"VACUUM ANALYZE {table_name}"))
                    session.commit()
                    results[table_name] = "success"
                except Exception as e:
                    results[table_name] = f"error: {str(e)}"

        return results

    @staticmethod
    def update_table_statistics() -> Dict[str, Any]:
        """Update table statistics for query optimization."""
        with get_session() as session:
            try:
                session.execute(text("ANALYZE"))
                session.commit()
                return {"status": "success", "message": "Table statistics updated"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    @staticmethod
    def cleanup_old_data(days: int = 90) -> Dict[str, int]:
        """Clean up old data from various tables."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        results = {}

        with get_session() as session:
            # Clean up old ingestion logs
            ingestion_deleted = session.execute(
                IngestionLog.__table__.delete()
                .where(IngestionLog.created_at < cutoff_date)
            ).rowcount

            # Clean up old search analytics (keep more recent data)
            search_cutoff = datetime.utcnow() - timedelta(days=days * 2)
            search_deleted = session.execute(
                SearchAnalytics.__table__.delete()
                .where(SearchAnalytics.created_at < search_cutoff)
            ).rowcount

            # Clean up archived articles (older than specified days)
            archived_deleted = session.execute(
                Article.__table__.delete()
                .where(
                    and_(
                        Article.status == 'archived',
                        Article.created_at < cutoff_date
                    )
                )
            ).rowcount

            session.commit()

            results = {
                'ingestion_logs_deleted': ingestion_deleted,
                'search_analytics_deleted': search_deleted,
                'archived_articles_deleted': archived_deleted
            }

        return results

    @staticmethod
    def reindex_search_vectors() -> Dict[str, int]:
        """Rebuild search vectors for all content."""
        with get_session() as session:
            # Update article search vectors
            articles_updated = session.execute(
                text("""
                UPDATE articles
                SET search_vector = (
                    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(content, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
                    setweight(to_tsvector('english', array_to_string(COALESCE(tags, '{}'), ' ')), 'C')
                )
                """)
            ).rowcount

            # Update team search vectors
            teams_updated = session.execute(
                text("""
                UPDATE teams
                SET search_vector = (
                    setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(city, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(abbreviation, '')), 'A')
                )
                """)
            ).rowcount

            session.commit()

            return {
                'articles_updated': articles_updated,
                'teams_updated': teams_updated
            }

    @staticmethod
    def check_index_usage() -> List[Dict[str, Any]]:
        """Check index usage statistics."""
        with get_session() as session:
            index_stats = session.execute(
                text("""
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch,
                    idx_scan,
                    CASE
                        WHEN idx_scan = 0 THEN 'UNUSED'
                        WHEN idx_scan < 10 THEN 'LOW_USAGE'
                        ELSE 'NORMAL'
                    END as usage_status
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
                """)
            ).fetchall()

            return [
                {
                    'schema': row[0],
                    'table': row[1],
                    'index': row[2],
                    'tuples_read': row[3],
                    'tuples_fetched': row[4],
                    'scans': row[5],
                    'usage_status': row[6]
                }
                for row in index_stats
            ]

    @staticmethod
    def get_table_sizes() -> List[Dict[str, Any]]:
        """Get table sizes and row counts."""
        with get_session() as session:
            table_sizes = session.execute(
                text("""
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """)
            ).fetchall()

            return [
                {
                    'schema': row[0],
                    'table': row[1],
                    'size': row[2],
                    'size_bytes': row[3],
                    'inserts': row[4],
                    'updates': row[5],
                    'deletes': row[6],
                    'live_tuples': row[7],
                    'dead_tuples': row[8]
                }
                for row in table_sizes
            ]

    @staticmethod
    def optimize_queries() -> List[str]:
        """Get query optimization recommendations."""
        recommendations = []

        with get_session() as session:
            # Check for tables with high dead tuple ratios
            dead_tuple_stats = session.execute(
                text("""
                SELECT
                    tablename,
                    n_dead_tup,
                    n_live_tup,
                    CASE
                        WHEN n_live_tup > 0
                        THEN round((n_dead_tup::float / n_live_tup::float) * 100, 2)
                        ELSE 0
                    END as dead_tuple_ratio
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                AND n_live_tup > 0
                ORDER BY dead_tuple_ratio DESC
                """)
            ).fetchall()

            for table, dead, live, ratio in dead_tuple_stats:
                if ratio > 20:  # More than 20% dead tuples
                    recommendations.append(
                        f"Table '{table}' has {ratio}% dead tuples. Consider running VACUUM."
                    )

            # Check for unused indexes
            unused_indexes = session.execute(
                text("""
                SELECT indexname, tablename
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                AND idx_scan = 0
                AND indexname NOT LIKE '%_pkey'
                """)
            ).fetchall()

            for index, table in unused_indexes:
                recommendations.append(
                    f"Index '{index}' on table '{table}' is unused and may be dropped."
                )

            # Check for tables without recent ANALYZE
            analyze_stats = session.execute(
                text("""
                SELECT
                    tablename,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                AND (
                    last_analyze IS NULL
                    OR last_analyze < NOW() - INTERVAL '7 days'
                )
                AND (
                    last_autoanalyze IS NULL
                    OR last_autoanalyze < NOW() - INTERVAL '7 days'
                )
                """)
            ).fetchall()

            for table, last_analyze, last_autoanalyze in analyze_stats:
                recommendations.append(
                    f"Table '{table}' statistics are outdated. Consider running ANALYZE."
                )

        return recommendations

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Comprehensive database health check."""
        health_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'database_info': get_database_info(),
            'connection_status': 'healthy',
            'issues': [],
            'warnings': []
        }

        try:
            with get_session() as session:
                # Check connection
                session.execute(text("SELECT 1"))

                # Check table counts
                table_counts = {}
                tables = ['users', 'teams', 'articles', 'games', 'feed_sources']

                for table in tables:
                    try:
                        count = session.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        ).scalar()
                        table_counts[table] = count
                    except Exception as e:
                        health_data['issues'].append(f"Cannot access table '{table}': {str(e)}")

                health_data['table_counts'] = table_counts

                # Check for critical issues
                recommendations = DatabaseMaintenance.optimize_queries()
                if recommendations:
                    health_data['warnings'].extend(recommendations[:5])  # Limit to top 5

                # Check disk space (PostgreSQL specific)
                try:
                    disk_usage = session.execute(
                        text("""
                        SELECT
                            pg_size_pretty(pg_database_size(current_database())) as db_size,
                            pg_database_size(current_database()) as db_size_bytes
                        """)
                    ).fetchone()

                    if disk_usage:
                        health_data['database_size'] = disk_usage[0]
                        health_data['database_size_bytes'] = disk_usage[1]

                except Exception as e:
                    health_data['warnings'].append(f"Cannot check database size: {str(e)}")

                # Check for long-running queries
                try:
                    long_queries = session.execute(
                        text("""
                        SELECT
                            pid,
                            now() - pg_stat_activity.query_start AS duration,
                            query
                        FROM pg_stat_activity
                        WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
                        AND state = 'active'
                        """)
                    ).fetchall()

                    if long_queries:
                        health_data['warnings'].append(
                            f"Found {len(long_queries)} long-running queries"
                        )

                except Exception:
                    # This is non-critical
                    pass

                # Overall health status
                if health_data['issues']:
                    health_data['status'] = 'unhealthy'
                elif health_data['warnings']:
                    health_data['status'] = 'warning'
                else:
                    health_data['status'] = 'healthy'

        except Exception as e:
            health_data['connection_status'] = 'failed'
            health_data['status'] = 'unhealthy'
            health_data['issues'].append(f"Database connection failed: {str(e)}")

        return health_data

    @staticmethod
    def backup_recommendations() -> Dict[str, Any]:
        """Get backup and recovery recommendations."""
        with get_session() as session:
            # Get database size
            db_size = session.execute(
                text("SELECT pg_database_size(current_database())")
            ).scalar()

            # Get growth rate (approximate)
            recent_articles = session.execute(
                select(func.count(Article.id))
                .where(Article.created_at >= func.now() - text("INTERVAL '7 days'"))
            ).scalar() or 0

            total_articles = session.execute(
                select(func.count(Article.id))
            ).scalar() or 0

            growth_rate = (recent_articles / 7) if recent_articles > 0 else 0  # Articles per day

            # Calculate recommended backup frequency
            if db_size < 1024 * 1024 * 1024:  # < 1GB
                backup_frequency = "daily"
            elif db_size < 10 * 1024 * 1024 * 1024:  # < 10GB
                backup_frequency = "every 12 hours"
            else:
                backup_frequency = "every 6 hours"

            return {
                'database_size_bytes': db_size,
                'database_size_readable': f"{db_size / (1024**3):.2f} GB",
                'total_articles': total_articles,
                'recent_articles_7_days': recent_articles,
                'growth_rate_articles_per_day': round(growth_rate, 1),
                'recommended_backup_frequency': backup_frequency,
                'recommendations': [
                    "Enable point-in-time recovery (PITR) for Supabase",
                    "Set up automated backups with retention policy",
                    "Test backup restoration procedures regularly",
                    "Monitor backup success/failure notifications"
                ]
            }