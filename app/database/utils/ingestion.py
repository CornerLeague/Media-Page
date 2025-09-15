"""Content ingestion pipeline for sports articles and data."""

import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import Article, FeedSource, IngestionLog, Team
from ..models.enums import ArticleStatus, ContentCategory, IngestionStatus
from ..database import get_session
from .deduplication import DuplicationChecker, URLHasher


@dataclass
class ContentItem:
    """Data class for content to be ingested."""
    url: str
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    source_name: str = ""
    published_at: Optional[datetime] = None
    category: Optional[ContentCategory] = None
    tags: List[str] = None
    team_names: List[str] = None  # Team names to be resolved to IDs

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.team_names is None:
            self.team_names = []


class TeamResolver:
    """Resolve team names to team IDs."""

    def __init__(self):
        self._team_cache = {}

    def resolve_team_names(self, session: Session, team_names: List[str]) -> List[uuid.UUID]:
        """Resolve team names to UUIDs."""
        if not team_names:
            return []

        team_ids = []
        for name in team_names:
            team_id = self._resolve_single_team(session, name)
            if team_id:
                team_ids.append(team_id)

        return team_ids

    def _resolve_single_team(self, session: Session, team_name: str) -> Optional[uuid.UUID]:
        """Resolve a single team name to UUID."""
        # Check cache first
        cache_key = team_name.lower().strip()
        if cache_key in self._team_cache:
            return self._team_cache[cache_key]

        # Search database
        team = session.execute(
            select(Team.id)
            .where(
                Team.name.ilike(f"%{team_name}%")
                | Team.city.ilike(f"%{team_name}%")
                | Team.abbreviation.ilike(f"%{team_name}%")
            )
            .limit(1)
        ).scalar_one_or_none()

        # Cache result
        self._team_cache[cache_key] = team
        return team


class ContentIngester:
    """Handles ingestion of individual content items."""

    def __init__(self):
        self.duplication_checker = DuplicationChecker()
        self.team_resolver = TeamResolver()

    def ingest_content(self, session: Session, content: ContentItem,
                      source_id: Optional[uuid.UUID] = None) -> Tuple[bool, str, Optional[uuid.UUID]]:
        """
        Ingest a single content item.

        Returns:
            (success, message, article_id)
        """
        try:
            # Generate URL hash
            url_hash = URLHasher.hash_url(content.url)

            # Check for duplicates
            is_duplicate, duplicate_id, similarity = self.duplication_checker.check_for_duplicates(
                session, content.url, content.title, content.content
            )

            if is_duplicate:
                # Log duplicate
                IngestionLog.log_duplicate(
                    source_id=source_id,
                    url_hash=url_hash,
                    source_url=content.url,
                    duplicate_of=uuid.UUID(duplicate_id),
                    similarity_score=similarity
                )
                return False, f"Duplicate content detected (similarity: {similarity:.2f})", None

            # Resolve team associations
            team_ids = self.team_resolver.resolve_team_names(session, content.team_names)

            # Create article
            article = Article(
                url_hash=url_hash,
                title=content.title,
                content=content.content,
                summary=content.summary,
                author=content.author,
                source_name=content.source_name,
                source_url=content.url,
                published_at=content.published_at,
                category=content.category,
                tags=content.tags,
                team_ids=team_ids,
                status=ArticleStatus.PUBLISHED
            )

            session.add(article)
            session.flush()  # Get the ID

            # Log successful ingestion
            IngestionLog.log_success(
                source_id=source_id,
                url_hash=url_hash,
                source_url=content.url
            )

            return True, "Content ingested successfully", article.id

        except Exception as e:
            # Log error
            IngestionLog.log_error(
                source_id=source_id,
                url_hash=URLHasher.hash_url(content.url),
                source_url=content.url,
                error_message=str(e)
            )
            return False, f"Ingestion error: {str(e)}", None


class IngestionPipeline:
    """Main ingestion pipeline coordinator."""

    def __init__(self):
        self.content_ingester = ContentIngester()

    def process_content_batch(self, content_items: List[ContentItem],
                            source_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Process a batch of content items."""
        results = {
            'total': len(content_items),
            'successful': 0,
            'duplicates': 0,
            'errors': 0,
            'error_details': [],
            'duplicate_rate': 0.0
        }

        with get_session() as session:
            for content in content_items:
                success, message, article_id = self.content_ingester.ingest_content(
                    session, content, source_id
                )

                if success:
                    results['successful'] += 1
                elif 'duplicate' in message.lower():
                    results['duplicates'] += 1
                else:
                    results['errors'] += 1
                    results['error_details'].append({
                        'url': content.url,
                        'error': message
                    })

            # Calculate duplicate rate
            if results['total'] > 0:
                results['duplicate_rate'] = results['duplicates'] / results['total']

        return results

    def process_feed_source(self, source_id: uuid.UUID) -> Dict[str, Any]:
        """Process content from a specific feed source."""
        with get_session() as session:
            # Get feed source
            source = session.execute(
                select(FeedSource).where(FeedSource.id == source_id)
            ).scalar_one_or_none()

            if not source:
                return {'error': 'Feed source not found'}

            if not source.is_active:
                return {'error': 'Feed source is not active'}

            # Check if source is due for fetching
            if not source.is_due_for_fetch:
                return {'message': 'Source not due for fetching', 'skipped': True}

            try:
                # Fetch content from source (this would be implemented based on feed type)
                content_items = self._fetch_content_from_source(source)

                # Update fetch timestamp
                source.update_fetch_time(successful=True)
                session.commit()

                # Process content
                results = self.process_content_batch(content_items, source_id)
                results['source_name'] = source.name
                results['source_type'] = source.feed_type

                return results

            except Exception as e:
                # Update fetch timestamp as failed
                source.update_fetch_time(successful=False)
                session.commit()

                return {
                    'error': f'Failed to process feed source: {str(e)}',
                    'source_name': source.name
                }

    def _fetch_content_from_source(self, source: FeedSource) -> List[ContentItem]:
        """Fetch content from a feed source."""
        # This is a placeholder - implementation would depend on feed type
        # RSS feeds, JSON APIs, web scraping, etc.

        if source.feed_type == 'rss':
            return self._fetch_rss_content(source)
        elif source.feed_type == 'json':
            return self._fetch_json_content(source)
        elif source.feed_type == 'api':
            return self._fetch_api_content(source)
        else:
            raise ValueError(f"Unsupported feed type: {source.feed_type}")

    def _fetch_rss_content(self, source: FeedSource) -> List[ContentItem]:
        """Fetch content from RSS feed."""
        # Placeholder implementation
        return []

    def _fetch_json_content(self, source: FeedSource) -> List[ContentItem]:
        """Fetch content from JSON feed."""
        # Placeholder implementation
        return []

    def _fetch_api_content(self, source: FeedSource) -> List[ContentItem]:
        """Fetch content from API endpoint."""
        # Placeholder implementation
        return []

    def get_ingestion_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get ingestion statistics for the last N days."""
        with get_session() as session:
            from sqlalchemy import func
            from datetime import timedelta

            cutoff_date = func.now() - timedelta(days=days)

            # Total ingestion attempts
            total_attempts = session.execute(
                select(func.count(IngestionLog.id))
                .where(IngestionLog.created_at >= cutoff_date)
            ).scalar() or 0

            # Successful ingestions
            successful = session.execute(
                select(func.count(IngestionLog.id))
                .where(
                    IngestionLog.created_at >= cutoff_date,
                    IngestionLog.ingestion_status == IngestionStatus.SUCCESS
                )
            ).scalar() or 0

            # Duplicates
            duplicates = session.execute(
                select(func.count(IngestionLog.id))
                .where(
                    IngestionLog.created_at >= cutoff_date,
                    IngestionLog.ingestion_status == IngestionStatus.DUPLICATE
                )
            ).scalar() or 0

            # Errors
            errors = session.execute(
                select(func.count(IngestionLog.id))
                .where(
                    IngestionLog.created_at >= cutoff_date,
                    IngestionLog.ingestion_status == IngestionStatus.ERROR
                )
            ).scalar() or 0

            # Calculate rates
            duplicate_rate = duplicates / total_attempts if total_attempts > 0 else 0
            success_rate = successful / total_attempts if total_attempts > 0 else 0
            error_rate = errors / total_attempts if total_attempts > 0 else 0

            return {
                'period_days': days,
                'total_attempts': total_attempts,
                'successful': successful,
                'duplicates': duplicates,
                'errors': errors,
                'duplicate_rate': round(duplicate_rate, 3),
                'success_rate': round(success_rate, 3),
                'error_rate': round(error_rate, 3)
            }

    def cleanup_old_logs(self, days: int = 30) -> int:
        """Clean up old ingestion logs."""
        with get_session() as session:
            from datetime import timedelta
            from sqlalchemy import func

            cutoff_date = func.now() - timedelta(days=days)

            # Delete old logs
            result = session.execute(
                IngestionLog.__table__.delete()
                .where(IngestionLog.created_at < cutoff_date)
            )

            deleted_count = result.rowcount
            session.commit()

            return deleted_count


class FeedSourceManager:
    """Manage feed sources and their configurations."""

    @staticmethod
    def create_feed_source(name: str, url: str, feed_type: str,
                          config: Optional[Dict[str, Any]] = None,
                          fetch_interval_minutes: int = 30) -> uuid.UUID:
        """Create a new feed source."""
        with get_session() as session:
            source = FeedSource(
                name=name,
                url=url,
                feed_type=feed_type,
                config=config or {},
                fetch_interval_minutes=fetch_interval_minutes,
                is_active=True
            )

            session.add(source)
            session.commit()
            return source.id

    @staticmethod
    def get_sources_due_for_fetch() -> List[FeedSource]:
        """Get all sources that are due for fetching."""
        return FeedSource.get_sources_due_for_fetch()

    @staticmethod
    def update_source_config(source_id: uuid.UUID, config: Dict[str, Any]) -> bool:
        """Update feed source configuration."""
        with get_session() as session:
            source = session.execute(
                select(FeedSource).where(FeedSource.id == source_id)
            ).scalar_one_or_none()

            if not source:
                return False

            source.config.update(config)
            session.commit()
            return True

    @staticmethod
    def toggle_source_status(source_id: uuid.UUID, is_active: bool) -> bool:
        """Enable or disable a feed source."""
        with get_session() as session:
            source = session.execute(
                select(FeedSource).where(FeedSource.id == source_id)
            ).scalar_one_or_none()

            if not source:
                return False

            source.is_active = is_active
            session.commit()
            return True