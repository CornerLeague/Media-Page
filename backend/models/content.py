"""
Content management models for articles, feeds, and AI summaries
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean, DateTime, Integer, Numeric, String, Text, ForeignKey,
    CheckConstraint, Index, func, LargeBinary, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB, ARRAY, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import ContentCategory, IngestionStatus


class FeedSource(Base, UUIDMixin, TimestampMixin):
    """
    RSS feed sources for content ingestion
    """
    __tablename__ = "feed_sources"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Display name for the feed source"
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        unique=True,
        nullable=False,
        doc="RSS/feed URL"
    )

    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Main website URL"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Description of the feed source"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this feed is actively being processed"
    )

    fetch_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        doc="How often to fetch this feed (in minutes)"
    )

    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp of last fetch attempt"
    )

    last_success_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp of last successful fetch"
    )

    failure_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Consecutive failure count"
    )

    # Relationships
    mappings: Mapped[List["FeedSourceMapping"]] = relationship(
        "FeedSourceMapping",
        back_populates="feed_source",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    snapshots: Mapped[List["FeedSnapshot"]] = relationship(
        "FeedSnapshot",
        back_populates="feed_source",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FeedSource(id={self.id}, name='{self.name}', active={self.is_active})>"

    @property
    def is_healthy(self) -> bool:
        """Check if feed is healthy (low failure count)"""
        return self.failure_count < 5


class FeedSourceMapping(Base, UUIDMixin):
    """
    Mapping between feed sources and sports/teams
    """
    __tablename__ = "feed_source_mappings"

    feed_source_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("feed_sources.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the feed source"
    )

    sport_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        doc="Reference to the sport (if sport-specific)"
    )

    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        doc="Reference to the team (if team-specific)"
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
        doc="Priority level for this mapping"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "sport_id IS NOT NULL OR team_id IS NOT NULL",
            name="check_sport_or_team_required"
        ),
    )

    # Relationships
    feed_source: Mapped["FeedSource"] = relationship(
        "FeedSource",
        back_populates="mappings",
        lazy="select"
    )

    sport: Mapped[Optional["Sport"]] = relationship(
        "Sport",
        lazy="selectin"
    )

    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<FeedSourceMapping(feed_id={self.feed_source_id}, sport_id={self.sport_id}, team_id={self.team_id})>"


class FeedSnapshot(Base, UUIDMixin):
    """
    Raw feed snapshots for deduplication and processing
    """
    __tablename__ = "feed_snapshots"
    __table_args__ = (
        UniqueConstraint('feed_source_id', 'url_hash', name='uq_feed_url_hash'),
        Index('idx_feed_snapshots_content_hash', 'content_hash'),
        Index('idx_feed_snapshots_status', 'status'),
    )

    feed_source_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("feed_sources.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the feed source"
    )

    url_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="SHA-256 hash of the article URL for primary deduplication"
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="SHA-256 hash of content for duplicate detection"
    )

    minhash_signature: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary,
        doc="MinHash signature for near-duplicate detection"
    )

    raw_content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        doc="Raw RSS/feed item data"
    )

    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp when content was processed"
    )

    status: Mapped[IngestionStatus] = mapped_column(
        default=IngestionStatus.PENDING,
        nullable=False,
        doc="Processing status"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Error message if processing failed"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    feed_source: Mapped["FeedSource"] = relationship(
        "FeedSource",
        back_populates="snapshots",
        lazy="select"
    )

    article: Mapped[Optional["Article"]] = relationship(
        "Article",
        back_populates="feed_snapshot",
        uselist=False,
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<FeedSnapshot(id={self.id}, status={self.status}, url_hash='{self.url_hash}')>"

    @property
    def is_processed(self) -> bool:
        """Check if snapshot has been processed"""
        return self.status in [IngestionStatus.COMPLETED, IngestionStatus.DUPLICATE]


class Article(Base, UUIDMixin, TimestampMixin):
    """
    Processed articles from feed sources
    """
    __tablename__ = "articles"
    __table_args__ = (
        Index('idx_articles_published', 'published_at', postgresql_order_by='published_at DESC'),
        Index('idx_articles_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_articles_title_trgm', 'title', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}),
        CheckConstraint('word_count >= 0', name='check_valid_word_count'),
        CheckConstraint('reading_time_minutes >= 0', name='check_valid_reading_time'),
        CheckConstraint('sentiment_score >= -1 AND sentiment_score <= 1', name='check_valid_sentiment'),
    )

    feed_snapshot_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("feed_snapshots.id", ondelete="SET NULL"),
        doc="Reference to the feed snapshot this article came from"
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Article title"
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Article summary/excerpt"
    )

    content: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Full article content"
    )

    author: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="Article author"
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Source publication"
    )

    category: Mapped[ContentCategory] = mapped_column(
        default=ContentCategory.GENERAL,
        nullable=False,
        doc="Article category"
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
        doc="Article priority for display ordering"
    )

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Original publication timestamp"
    )

    url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        doc="Original article URL"
    )

    image_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        doc="Article featured image URL"
    )

    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="External identifier from source"
    )

    # Content analysis fields
    word_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Word count of the article"
    )

    reading_time_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Estimated reading time in minutes"
    )

    sentiment_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="Sentiment analysis score (-1 to 1)"
    )

    # Search vector for full-text search
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        doc="Full-text search vector"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this article is active/published"
    )

    # Relationships
    feed_snapshot: Mapped[Optional["FeedSnapshot"]] = relationship(
        "FeedSnapshot",
        back_populates="article",
        lazy="select"
    )

    sports: Mapped[List["ArticleSport"]] = relationship(
        "ArticleSport",
        back_populates="article",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    teams: Mapped[List["ArticleTeam"]] = relationship(
        "ArticleTeam",
        back_populates="article",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"

    @property
    def excerpt(self) -> str:
        """Get article excerpt"""
        if self.summary:
            return self.summary
        if self.content:
            return self.content[:200] + "..." if len(self.content) > 200 else self.content
        return ""


class ArticleSport(Base, UUIDMixin):
    """
    Relationship between articles and sports
    """
    __tablename__ = "article_sports"
    __table_args__ = (
        UniqueConstraint('article_id', 'sport_id', name='uq_article_sport'),
    )

    article_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the article"
    )

    sport_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the sport"
    )

    relevance_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.5"),
        doc="Relevance score of article to sport"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="sports",
        lazy="select"
    )

    sport: Mapped["Sport"] = relationship(
        "Sport",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ArticleSport(article_id={self.article_id}, sport_id={self.sport_id}, relevance={self.relevance_score})>"


class ArticleTeam(Base, UUIDMixin):
    """
    Relationship between articles and teams
    """
    __tablename__ = "article_teams"
    __table_args__ = (
        UniqueConstraint('article_id', 'team_id', name='uq_article_team'),
    )

    article_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the article"
    )

    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )

    relevance_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.5"),
        doc="Relevance score of article to team"
    )

    mentioned_players: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        default=list,
        doc="Array of player names mentioned in the article"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="teams",
        lazy="select"
    )

    team: Mapped["Team"] = relationship(
        "Team",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ArticleTeam(article_id={self.article_id}, team_id={self.team_id}, relevance={self.relevance_score})>"


class AISummary(Base, UUIDMixin):
    """
    AI-generated summaries for users, teams, or sports
    """
    __tablename__ = "ai_summaries"

    user_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        doc="Reference to user (for personalized summaries)"
    )

    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        doc="Reference to team (for team summaries)"
    )

    sport_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        doc="Reference to sport (for sport summaries)"
    )

    summary_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="The AI-generated summary text"
    )

    summary_type: Mapped[str] = mapped_column(
        String(50),
        default="daily",
        doc="Type of summary (daily, weekly, game, team)"
    )

    source_article_ids: Mapped[List[UUID]] = mapped_column(
        ARRAY(PostgreSQLUUID(as_uuid=True)),
        default=list,
        doc="Array of article IDs used to generate this summary"
    )

    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        doc="AI confidence score for the summary"
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when summary was generated"
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp when summary expires"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this summary is currently active"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="selectin"
    )

    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        lazy="selectin"
    )

    sport: Mapped[Optional["Sport"]] = relationship(
        "Sport",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AISummary(id={self.id}, type='{self.summary_type}', generated_at={self.generated_at})>"

    @property
    def is_expired(self) -> bool:
        """Check if summary has expired"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    @property
    def target_entity(self) -> str:
        """Get string representation of what this summary is for"""
        if self.user_id:
            return f"User:{self.user_id}"
        elif self.team_id:
            return f"Team:{self.team_id}"
        elif self.sport_id:
            return f"Sport:{self.sport_id}"
        else:
            return "General"