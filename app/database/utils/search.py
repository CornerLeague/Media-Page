"""Full-text search utilities for PostgreSQL and Supabase."""

from typing import List, Dict, Any, Optional, Tuple
import uuid

from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import Session

from ..models import Article, Team, SearchAnalytics
from ..models.enums import ArticleStatus, TeamStatus
from ..database import get_session


class FullTextSearchManager:
    """Manage full-text search operations."""

    @staticmethod
    def search_articles(query: str, limit: int = 50, offset: int = 0,
                       user_id: Optional[uuid.UUID] = None,
                       team_ids: Optional[List[uuid.UUID]] = None,
                       category: Optional[str] = None) -> Dict[str, Any]:
        """
        Search articles using PostgreSQL full-text search.

        Returns:
            Dictionary with results, pagination info, and metadata
        """
        with get_session() as session:
            # Build search query
            search_conditions = [
                Article.status == ArticleStatus.PUBLISHED
            ]

            # Add full-text search condition
            if query.strip():
                search_vector_query = func.plainto_tsquery('english', query)
                search_conditions.append(
                    Article.search_vector.op('@@')(search_vector_query)
                )

            # Add team filter
            if team_ids:
                search_conditions.append(
                    func.array_length(
                        func.array_intersection(Article.team_ids, team_ids), 1
                    ) > 0
                )

            # Add category filter
            if category:
                search_conditions.append(Article.category == category)

            # Build base query
            base_query = select(Article).where(and_(*search_conditions))

            # Add ranking for search queries
            if query.strip():
                search_vector_query = func.plainto_tsquery('english', query)
                rank_expression = func.ts_rank(Article.search_vector, search_vector_query)

                # Order by relevance then by recency
                base_query = base_query.order_by(
                    rank_expression.desc(),
                    Article.published_at.desc()
                )
            else:
                # No search query, order by recency
                base_query = base_query.order_by(Article.published_at.desc())

            # Get total count
            count_query = select(func.count()).select_from(
                base_query.subquery()
            )
            total_count = session.execute(count_query).scalar() or 0

            # Apply pagination
            paginated_query = base_query.offset(offset).limit(limit)
            articles = session.execute(paginated_query).scalars().all()

            # Log search analytics
            if query.strip():
                SearchAnalytics.log_search(
                    query=query,
                    results_count=total_count,
                    user_id=user_id
                )

            return {
                'articles': [article.to_dict() for article in articles],
                'total_count': total_count,
                'page_size': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count,
                'query': query,
                'filters': {
                    'team_ids': team_ids,
                    'category': category
                }
            }

    @staticmethod
    def search_teams(query: str, limit: int = 20, sport: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search teams using full-text search."""
        with get_session() as session:
            search_conditions = [
                Team.status == TeamStatus.ACTIVE
            ]

            # Add full-text search
            if query.strip():
                search_vector_query = func.plainto_tsquery('english', query)
                search_conditions.append(
                    Team.search_vector.op('@@')(search_vector_query)
                )

            # Add sport filter
            if sport:
                search_conditions.append(Team.sport == sport)

            # Build query with ranking
            if query.strip():
                search_vector_query = func.plainto_tsquery('english', query)
                rank_expression = func.ts_rank(Team.search_vector, search_vector_query)

                teams_query = select(Team).where(and_(*search_conditions)).order_by(
                    rank_expression.desc(),
                    Team.follower_count.desc()
                ).limit(limit)
            else:
                teams_query = select(Team).where(and_(*search_conditions)).order_by(
                    Team.follower_count.desc()
                ).limit(limit)

            teams = session.execute(teams_query).scalars().all()

            return [team.to_dict() for team in teams]

    @staticmethod
    def search_suggestions(query: str, limit: int = 10) -> Dict[str, List[str]]:
        """Get search suggestions based on query."""
        with get_session() as session:
            suggestions = {
                'teams': [],
                'queries': [],
                'categories': []
            }

            if not query.strip():
                return suggestions

            # Team suggestions
            team_suggestions = session.execute(
                select(Team.name, Team.city)
                .where(
                    and_(
                        Team.status == TeamStatus.ACTIVE,
                        or_(
                            Team.name.ilike(f"%{query}%"),
                            Team.city.ilike(f"%{query}%"),
                            Team.abbreviation.ilike(f"%{query}%")
                        )
                    )
                )
                .limit(limit)
            ).fetchall()

            for name, city in team_suggestions:
                team_display = f"{city} {name}" if city else name
                suggestions['teams'].append(team_display)

            # Popular query suggestions
            popular_queries = session.execute(
                select(SearchAnalytics.query, func.count(SearchAnalytics.id).label('frequency'))
                .where(SearchAnalytics.query.ilike(f"%{query}%"))
                .group_by(SearchAnalytics.query)
                .order_by(func.count(SearchAnalytics.id).desc())
                .limit(limit)
            ).fetchall()

            suggestions['queries'] = [q[0] for q in popular_queries]

            # Category suggestions (if query matches)
            from ..models.enums import ContentCategory
            category_matches = [
                cat.value for cat in ContentCategory
                if query.lower() in cat.value.lower()
            ]
            suggestions['categories'] = category_matches[:limit]

            return suggestions

    @staticmethod
    def get_trending_searches(days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending search queries."""
        with get_session() as session:
            from datetime import timedelta

            cutoff_date = func.now() - timedelta(days=days)

            trending = session.execute(
                select(
                    SearchAnalytics.query,
                    func.count(SearchAnalytics.id).label('search_count'),
                    func.avg(SearchAnalytics.results_count).label('avg_results'),
                    func.sum(
                        func.case(
                            (func.array_length(SearchAnalytics.clicked_results, 1) > 0, 1),
                            else_=0
                        )
                    ).label('searches_with_clicks')
                )
                .where(SearchAnalytics.created_at >= cutoff_date)
                .group_by(SearchAnalytics.query)
                .having(func.count(SearchAnalytics.id) >= 2)  # Minimum threshold
                .order_by(func.count(SearchAnalytics.id).desc())
                .limit(limit)
            ).fetchall()

            return [
                {
                    'query': row[0],
                    'search_count': row[1],
                    'avg_results': float(row[2]) if row[2] else 0,
                    'click_through_rate': (row[3] / row[1]) if row[1] > 0 else 0
                }
                for row in trending
            ]

    @staticmethod
    def improve_search_relevance(article_id: uuid.UUID, query: str, user_id: Optional[uuid.UUID] = None) -> None:
        """Record that a user clicked on a search result to improve relevance."""
        with get_session() as session:
            # Find recent search analytics for this user/query
            recent_search = session.execute(
                select(SearchAnalytics)
                .where(
                    and_(
                        SearchAnalytics.query == query,
                        SearchAnalytics.user_id == user_id if user_id else SearchAnalytics.user_id.is_(None),
                        SearchAnalytics.created_at >= func.now() - text("INTERVAL '1 hour'")
                    )
                )
                .order_by(SearchAnalytics.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if recent_search:
                recent_search.add_click(article_id)
                session.commit()

    @staticmethod
    def get_personalized_content(user_id: uuid.UUID, limit: int = 20) -> List[Dict[str, Any]]:
        """Get personalized content based on user preferences and search history."""
        with get_session() as session:
            # Get user's team preferences (this would require joining with user_teams)
            # For now, return recent popular articles
            articles = session.execute(
                select(Article)
                .where(Article.status == ArticleStatus.PUBLISHED)
                .order_by(
                    Article.view_count.desc(),
                    Article.published_at.desc()
                )
                .limit(limit)
            ).scalars().all()

            return [article.to_dict() for article in articles]

    @staticmethod
    def update_search_vectors() -> int:
        """Update search vectors for all articles and teams (maintenance operation)."""
        with get_session() as session:
            # For PostgreSQL, the search vectors are computed automatically
            # This function would be used for maintenance or after bulk imports

            # Update article search vectors
            article_count = session.execute(
                text("""
                UPDATE articles
                SET search_vector = (
                    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(content, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
                    setweight(to_tsvector('english', array_to_string(COALESCE(tags, '{}'), ' ')), 'C')
                )
                WHERE search_vector IS NULL
                """)
            ).rowcount

            # Update team search vectors
            team_count = session.execute(
                text("""
                UPDATE teams
                SET search_vector = (
                    setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(city, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(abbreviation, '')), 'A')
                )
                WHERE search_vector IS NULL
                """)
            ).rowcount

            session.commit()
            return article_count + team_count

    @staticmethod
    def search_analytics_summary(days: int = 30) -> Dict[str, Any]:
        """Get search analytics summary."""
        with get_session() as session:
            from datetime import timedelta

            cutoff_date = func.now() - timedelta(days=days)

            # Total searches
            total_searches = session.execute(
                select(func.count(SearchAnalytics.id))
                .where(SearchAnalytics.created_at >= cutoff_date)
            ).scalar() or 0

            # Unique users
            unique_users = session.execute(
                select(func.count(func.distinct(SearchAnalytics.user_id)))
                .where(
                    and_(
                        SearchAnalytics.created_at >= cutoff_date,
                        SearchAnalytics.user_id.is_not(None)
                    )
                )
            ).scalar() or 0

            # Average results per search
            avg_results = session.execute(
                select(func.avg(SearchAnalytics.results_count))
                .where(SearchAnalytics.created_at >= cutoff_date)
            ).scalar() or 0

            # Zero result queries
            zero_results = session.execute(
                select(func.count(SearchAnalytics.id))
                .where(
                    and_(
                        SearchAnalytics.created_at >= cutoff_date,
                        SearchAnalytics.results_count == 0
                    )
                )
            ).scalar() or 0

            # Click through rate
            searches_with_clicks = session.execute(
                select(func.count(SearchAnalytics.id))
                .where(
                    and_(
                        SearchAnalytics.created_at >= cutoff_date,
                        func.array_length(SearchAnalytics.clicked_results, 1) > 0
                    )
                )
            ).scalar() or 0

            click_through_rate = searches_with_clicks / total_searches if total_searches > 0 else 0

            return {
                'period_days': days,
                'total_searches': total_searches,
                'unique_users': unique_users,
                'avg_results_per_search': round(float(avg_results), 2),
                'zero_result_rate': round(zero_results / total_searches, 3) if total_searches > 0 else 0,
                'click_through_rate': round(click_through_rate, 3)
            }