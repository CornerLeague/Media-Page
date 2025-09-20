"""
Content Ingestion Pipeline Architecture

Implements the fetch → snapshot → parse → dedupe → store pattern with
<1% duplicate rates and robust error handling.
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

import aiohttp
import feedparser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_, or_

from backend.models import (
    FeedSource, FeedSnapshot, Article, ArticleSport, ArticleTeam,
    Sport, Team, User
)
from backend.models.enums import IngestionStatus, ContentCategory
from .deduplication import MinHashDeduplicator, URLHasher
from .content_classifier import ContentClassifier
from .article_parser import ArticleParser

logger = logging.getLogger(__name__)


@dataclass
class IngestionMetrics:
    """Metrics for monitoring ingestion pipeline performance"""
    fetched_items: int = 0
    processed_items: int = 0
    duplicates_found: int = 0
    errors: int = 0
    processing_time: float = 0.0

    @property
    def duplicate_rate(self) -> float:
        """Calculate duplicate rate percentage"""
        if self.processed_items == 0:
            return 0.0
        return (self.duplicates_found / self.processed_items) * 100

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.fetched_items == 0:
            return 0.0
        return ((self.processed_items - self.errors) / self.fetched_items) * 100


@dataclass
class ParsedContent:
    """Structured content after parsing"""
    title: str
    summary: Optional[str]
    content: Optional[str]
    author: Optional[str]
    published_at: datetime
    url: Optional[str]
    image_url: Optional[str]
    external_id: Optional[str]

    # Classification results
    category: ContentCategory
    sports: List[Tuple[UUID, float]]  # (sport_id, relevance_score)
    teams: List[Tuple[UUID, float, List[str]]]  # (team_id, relevance_score, mentioned_players)

    # Content analysis
    word_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    sentiment_score: Optional[float] = None


class IngestionError(Exception):
    """Base exception for ingestion pipeline errors"""
    pass


class FetchError(IngestionError):
    """Error during feed fetching"""
    pass


class ParseError(IngestionError):
    """Error during content parsing"""
    pass


class DeduplicationError(IngestionError):
    """Error during deduplication"""
    pass


class StorageError(IngestionError):
    """Error during database storage"""
    pass


class FeedFetcher:
    """Handles fetching RSS/Atom feeds with robust error handling"""

    def __init__(self, session: aiohttp.ClientSession, timeout: int = 30):
        self.session = session
        self.timeout = timeout

    async def fetch_feed(self, feed_source: FeedSource) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS/Atom feed

        Args:
            feed_source: FeedSource model instance

        Returns:
            List of raw feed items

        Raises:
            FetchError: If feed cannot be fetched or parsed
        """
        try:
            logger.info(f"Fetching feed: {feed_source.name} ({feed_source.url})")

            headers = {
                'User-Agent': 'Corner League Media Bot 1.0',
                'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml',
                'Accept-Encoding': 'gzip, deflate',
                'Cache-Control': 'no-cache',
            }

            # Add conditional headers if we have last fetch data
            if feed_source.last_fetched_at:
                headers['If-Modified-Since'] = feed_source.last_fetched_at.strftime(
                    '%a, %d %b %Y %H:%M:%S GMT'
                )

            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with self.session.get(
                feed_source.url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            ) as response:

                # Handle 304 Not Modified
                if response.status == 304:
                    logger.info(f"Feed not modified: {feed_source.name}")
                    return []

                if response.status != 200:
                    raise FetchError(
                        f"HTTP {response.status} fetching {feed_source.url}: {response.reason}"
                    )

                content = await response.text()

                # Parse RSS/Atom feed
                feed_data = feedparser.parse(content)

                if feed_data.bozo and feed_data.bozo_exception:
                    logger.warning(
                        f"Feed parsing warning for {feed_source.name}: {feed_data.bozo_exception}"
                    )

                items = []
                for entry in feed_data.entries:
                    # Convert feedparser entry to our format
                    item = {
                        'title': getattr(entry, 'title', ''),
                        'summary': getattr(entry, 'summary', ''),
                        'content': self._extract_content(entry),
                        'author': getattr(entry, 'author', ''),
                        'published': getattr(entry, 'published_parsed', None),
                        'updated': getattr(entry, 'updated_parsed', None),
                        'link': getattr(entry, 'link', ''),
                        'id': getattr(entry, 'id', ''),
                        'tags': [tag.term for tag in getattr(entry, 'tags', [])],
                        'raw_entry': entry,  # Keep original for debugging
                    }
                    items.append(item)

                logger.info(f"Fetched {len(items)} items from {feed_source.name}")
                return items

        except asyncio.TimeoutError:
            raise FetchError(f"Timeout fetching {feed_source.url}")
        except aiohttp.ClientError as e:
            raise FetchError(f"Network error fetching {feed_source.url}: {str(e)}")
        except Exception as e:
            raise FetchError(f"Unexpected error fetching {feed_source.url}: {str(e)}")

    def _extract_content(self, entry) -> str:
        """Extract full content from feed entry"""
        # Try different content fields in order of preference
        if hasattr(entry, 'content') and entry.content:
            return entry.content[0].value if isinstance(entry.content, list) else entry.content

        if hasattr(entry, 'description') and entry.description:
            return entry.description

        if hasattr(entry, 'summary') and entry.summary:
            return entry.summary

        return ""


class SnapshotProcessor:
    """Handles creating and managing feed snapshots for deduplication"""

    def __init__(self, session: AsyncSession, deduplicator: MinHashDeduplicator):
        self.session = session
        self.deduplicator = deduplicator
        self.url_hasher = URLHasher()

    async def create_snapshots(
        self,
        feed_source: FeedSource,
        items: List[Dict[str, Any]]
    ) -> List[FeedSnapshot]:
        """
        Create feed snapshots with deduplication

        Args:
            feed_source: Source of the feed
            items: Raw feed items

        Returns:
            List of FeedSnapshot instances (only new/unique items)
        """
        snapshots = []

        for item in items:
            try:
                # Generate URL hash for primary deduplication
                url = item.get('link', '') or item.get('id', '')
                if not url:
                    logger.warning(f"No URL found for item: {item.get('title', 'Unknown')}")
                    continue

                url_hash = self.url_hasher.hash_url(url)

                # Check if we already have this URL
                existing = await self.session.execute(
                    select(FeedSnapshot).where(
                        and_(
                            FeedSnapshot.feed_source_id == feed_source.id,
                            FeedSnapshot.url_hash == url_hash
                        )
                    )
                )

                if existing.scalar_one_or_none():
                    logger.debug(f"Duplicate URL found: {url}")
                    continue

                # Generate content hash
                content_text = f"{item.get('title', '')}\n{item.get('content', '')}\n{item.get('summary', '')}"
                content_hash = hashlib.sha256(content_text.encode()).hexdigest()

                # Generate MinHash signature for near-duplicate detection
                minhash_signature = self.deduplicator.generate_signature(content_text)

                # Create snapshot
                snapshot = FeedSnapshot(
                    feed_source_id=feed_source.id,
                    url_hash=url_hash,
                    content_hash=content_hash,
                    minhash_signature=minhash_signature.serialize(),
                    raw_content=item,
                    status=IngestionStatus.PENDING
                )

                snapshots.append(snapshot)

            except Exception as e:
                logger.error(f"Error creating snapshot for item {item.get('title', 'Unknown')}: {str(e)}")
                continue

        # Bulk insert snapshots
        if snapshots:
            self.session.add_all(snapshots)
            await self.session.flush()
            logger.info(f"Created {len(snapshots)} new snapshots from {feed_source.name}")

        return snapshots


class ContentProcessor:
    """Processes feed snapshots into structured articles"""

    def __init__(
        self,
        session: AsyncSession,
        parser: ArticleParser,
        classifier: ContentClassifier,
        deduplicator: MinHashDeduplicator
    ):
        self.session = session
        self.parser = parser
        self.classifier = classifier
        self.deduplicator = deduplicator

    async def process_snapshots(
        self,
        snapshots: List[FeedSnapshot]
    ) -> Tuple[List[Article], int]:
        """
        Process snapshots into articles with deduplication

        Args:
            snapshots: List of FeedSnapshot instances to process

        Returns:
            Tuple of (created_articles, duplicate_count)
        """
        articles = []
        duplicate_count = 0

        for snapshot in snapshots:
            try:
                # Parse raw content
                parsed = await self._parse_snapshot(snapshot)
                if not parsed:
                    await self._mark_snapshot_failed(snapshot, "Failed to parse content")
                    continue

                # Check for near-duplicates using MinHash
                if await self._is_near_duplicate(parsed, snapshot):
                    await self._mark_snapshot_duplicate(snapshot)
                    duplicate_count += 1
                    continue

                # Create article
                article = await self._create_article(snapshot, parsed)
                if article:
                    articles.append(article)
                    await self._mark_snapshot_completed(snapshot)
                else:
                    await self._mark_snapshot_failed(snapshot, "Failed to create article")

            except Exception as e:
                logger.error(f"Error processing snapshot {snapshot.id}: {str(e)}")
                await self._mark_snapshot_failed(snapshot, str(e))

        return articles, duplicate_count

    async def _parse_snapshot(self, snapshot: FeedSnapshot) -> Optional[ParsedContent]:
        """Parse snapshot into structured content"""
        try:
            item = snapshot.raw_content

            # Parse basic content
            parsed_basic = self.parser.parse_item(item)
            if not parsed_basic:
                return None

            # Classify content
            classification = await self.classifier.classify_article(
                title=parsed_basic.title,
                content=parsed_basic.content or parsed_basic.summary or "",
                source=snapshot.feed_source.name if snapshot.feed_source else "unknown"
            )

            return ParsedContent(
                title=parsed_basic.title,
                summary=parsed_basic.summary,
                content=parsed_basic.content,
                author=parsed_basic.author,
                published_at=parsed_basic.published_at,
                url=parsed_basic.url,
                image_url=parsed_basic.image_url,
                external_id=parsed_basic.external_id,
                category=classification.category,
                sports=classification.sports,
                teams=classification.teams,
                word_count=parsed_basic.word_count,
                reading_time_minutes=parsed_basic.reading_time_minutes,
                sentiment_score=classification.sentiment_score
            )

        except Exception as e:
            logger.error(f"Error parsing snapshot {snapshot.id}: {str(e)}")
            return None

    async def _is_near_duplicate(self, parsed: ParsedContent, snapshot: FeedSnapshot) -> bool:
        """Check for near-duplicate content using MinHash"""
        try:
            content_text = f"{parsed.title}\n{parsed.content or ''}\n{parsed.summary or ''}"
            current_signature = self.deduplicator.generate_signature(content_text)

            # Get recent content hashes for comparison (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)

            result = await self.session.execute(
                select(FeedSnapshot.content_hash, FeedSnapshot.minhash_signature)
                .where(
                    and_(
                        FeedSnapshot.created_at >= cutoff_date,
                        FeedSnapshot.status == IngestionStatus.COMPLETED,
                        FeedSnapshot.id != snapshot.id
                    )
                )
            )

            existing_items = result.fetchall()

            for content_hash, minhash_bytes in existing_items:
                # Skip exact duplicates (already handled by content_hash)
                if content_hash == hashlib.sha256(content_text.encode()).hexdigest():
                    continue

                if minhash_bytes:
                    existing_signature = self.deduplicator.deserialize_signature(minhash_bytes)
                    similarity = self.deduplicator.calculate_similarity(current_signature, existing_signature)

                    # Consider similar if >85% similar
                    if similarity > 0.85:
                        logger.info(f"Near-duplicate found: {similarity:.2%} similar")
                        return True

            return False

        except Exception as e:
            logger.error(f"Error checking near-duplicates for snapshot {snapshot.id}: {str(e)}")
            return False

    async def _create_article(self, snapshot: FeedSnapshot, parsed: ParsedContent) -> Optional[Article]:
        """Create article from parsed content"""
        try:
            # Create article
            article = Article(
                feed_snapshot_id=snapshot.id,
                title=parsed.title,
                summary=parsed.summary,
                content=parsed.content,
                author=parsed.author,
                source=snapshot.feed_source.name if snapshot.feed_source else "unknown",
                category=parsed.category,
                published_at=parsed.published_at,
                url=parsed.url,
                image_url=parsed.image_url,
                external_id=parsed.external_id,
                word_count=parsed.word_count,
                reading_time_minutes=parsed.reading_time_minutes,
                sentiment_score=parsed.sentiment_score,
                is_active=True
            )

            self.session.add(article)
            await self.session.flush()  # Get article ID

            # Create sport relationships
            for sport_id, relevance_score in parsed.sports:
                article_sport = ArticleSport(
                    article_id=article.id,
                    sport_id=sport_id,
                    relevance_score=relevance_score
                )
                self.session.add(article_sport)

            # Create team relationships
            for team_id, relevance_score, mentioned_players in parsed.teams:
                article_team = ArticleTeam(
                    article_id=article.id,
                    team_id=team_id,
                    relevance_score=relevance_score,
                    mentioned_players=mentioned_players
                )
                self.session.add(article_team)

            await self.session.flush()
            return article

        except Exception as e:
            logger.error(f"Error creating article from snapshot {snapshot.id}: {str(e)}")
            raise StorageError(f"Failed to create article: {str(e)}")

    async def _mark_snapshot_completed(self, snapshot: FeedSnapshot):
        """Mark snapshot as successfully processed"""
        snapshot.status = IngestionStatus.COMPLETED
        snapshot.processed_at = datetime.now()
        snapshot.error_message = None

    async def _mark_snapshot_failed(self, snapshot: FeedSnapshot, error_message: str):
        """Mark snapshot as failed with error message"""
        snapshot.status = IngestionStatus.FAILED
        snapshot.processed_at = datetime.now()
        snapshot.error_message = error_message

    async def _mark_snapshot_duplicate(self, snapshot: FeedSnapshot):
        """Mark snapshot as duplicate"""
        snapshot.status = IngestionStatus.DUPLICATE
        snapshot.processed_at = datetime.now()


class IngestionPipeline:
    """
    Main ingestion pipeline orchestrator

    Implements the complete fetch → snapshot → parse → dedupe → store pipeline
    with monitoring and error handling.
    """

    def __init__(
        self,
        session: AsyncSession,
        fetcher: FeedFetcher,
        snapshot_processor: SnapshotProcessor,
        content_processor: ContentProcessor
    ):
        self.session = session
        self.fetcher = fetcher
        self.snapshot_processor = snapshot_processor
        self.content_processor = content_processor

    async def run_ingestion_cycle(
        self,
        feed_sources: Optional[List[FeedSource]] = None,
        force_fetch: bool = False
    ) -> IngestionMetrics:
        """
        Run complete ingestion cycle

        Args:
            feed_sources: Specific feed sources to process (if None, processes all active)
            force_fetch: Whether to force fetch even if recently fetched

        Returns:
            IngestionMetrics with pipeline performance data
        """
        start_time = datetime.now()
        metrics = IngestionMetrics()

        try:
            # Get feed sources to process
            if feed_sources is None:
                feed_sources = await self._get_active_feed_sources(force_fetch)

            logger.info(f"Starting ingestion cycle for {len(feed_sources)} feed sources")

            for feed_source in feed_sources:
                try:
                    await self._process_feed_source(feed_source, metrics)
                except Exception as e:
                    logger.error(f"Error processing feed source {feed_source.name}: {str(e)}")
                    metrics.errors += 1

                    # Update feed source failure count
                    feed_source.failure_count += 1
                    await self.session.commit()

            # Calculate final metrics
            metrics.processing_time = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"Ingestion cycle completed: "
                f"{metrics.processed_items} processed, "
                f"{metrics.duplicates_found} duplicates ({metrics.duplicate_rate:.1f}%), "
                f"{metrics.errors} errors, "
                f"{metrics.processing_time:.1f}s"
            )

            return metrics

        except Exception as e:
            logger.error(f"Critical error in ingestion cycle: {str(e)}")
            await self.session.rollback()
            raise IngestionError(f"Ingestion cycle failed: {str(e)}")

    async def _get_active_feed_sources(self, force_fetch: bool = False) -> List[FeedSource]:
        """Get feed sources that need to be fetched"""
        query = select(FeedSource).where(FeedSource.is_active == True)

        if not force_fetch:
            # Only fetch feeds that haven't been fetched recently
            cutoff_time = datetime.now() - timedelta(minutes=15)  # Minimum 15 minutes between fetches
            query = query.where(
                or_(
                    FeedSource.last_fetched_at.is_(None),
                    FeedSource.last_fetched_at < cutoff_time
                )
            )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _process_feed_source(self, feed_source: FeedSource, metrics: IngestionMetrics):
        """Process a single feed source through the complete pipeline"""
        try:
            # Update last fetched timestamp
            feed_source.last_fetched_at = datetime.now()

            # 1. Fetch feed
            items = await self.fetcher.fetch_feed(feed_source)
            metrics.fetched_items += len(items)

            if not items:
                logger.info(f"No new items for {feed_source.name}")
                return

            # 2. Create snapshots with deduplication
            snapshots = await self.snapshot_processor.create_snapshots(feed_source, items)

            if not snapshots:
                logger.info(f"No new content for {feed_source.name} (all duplicates)")
                metrics.duplicates_found += len(items)
                return

            # 3. Process snapshots into articles
            articles, duplicate_count = await self.content_processor.process_snapshots(snapshots)

            metrics.processed_items += len(snapshots)
            metrics.duplicates_found += duplicate_count

            # Update feed source success info
            feed_source.last_success_at = datetime.now()
            feed_source.failure_count = 0

            await self.session.commit()

            logger.info(
                f"Processed {feed_source.name}: "
                f"{len(articles)} articles created, "
                f"{duplicate_count} duplicates found"
            )

        except Exception as e:
            await self.session.rollback()
            raise e


# Factory function for creating configured pipeline
async def create_ingestion_pipeline(session: AsyncSession) -> IngestionPipeline:
    """Create a fully configured ingestion pipeline"""

    # Initialize components
    http_session = aiohttp.ClientSession()
    deduplicator = MinHashDeduplicator(num_perm=128)
    classifier = ContentClassifier()
    parser = ArticleParser()

    # Create pipeline components
    fetcher = FeedFetcher(http_session)
    snapshot_processor = SnapshotProcessor(session, deduplicator)
    content_processor = ContentProcessor(session, parser, classifier, deduplicator)

    # Create pipeline
    pipeline = IngestionPipeline(
        session=session,
        fetcher=fetcher,
        snapshot_processor=snapshot_processor,
        content_processor=content_processor
    )

    return pipeline


# CLI entry point for running ingestion
async def run_ingestion_cli():
    """CLI entry point for running ingestion pipeline"""
    import argparse
    from backend.database import get_async_session

    parser = argparse.ArgumentParser(description="Run content ingestion pipeline")
    parser.add_argument("--force", action="store_true", help="Force fetch all feeds")
    parser.add_argument("--source", help="Process specific feed source by name")
    args = parser.parse_args()

    async with get_async_session() as session:
        pipeline = await create_ingestion_pipeline(session)

        feed_sources = None
        if args.source:
            result = await session.execute(
                select(FeedSource).where(FeedSource.name == args.source)
            )
            feed_source = result.scalar_one_or_none()
            if not feed_source:
                print(f"Feed source '{args.source}' not found")
                return
            feed_sources = [feed_source]

        metrics = await pipeline.run_ingestion_cycle(
            feed_sources=feed_sources,
            force_fetch=args.force
        )

        print(f"Ingestion completed:")
        print(f"  Items processed: {metrics.processed_items}")
        print(f"  Duplicates found: {metrics.duplicates_found} ({metrics.duplicate_rate:.1f}%)")
        print(f"  Errors: {metrics.errors}")
        print(f"  Success rate: {metrics.success_rate:.1f}%")
        print(f"  Processing time: {metrics.processing_time:.1f}s")


if __name__ == "__main__":
    asyncio.run(run_ingestion_cli())