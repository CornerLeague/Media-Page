"""Article-related SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Enum, Integer, Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel, SearchableMixin
from .enums import ArticleStatus, ContentCategory


class Article(BaseModel, SearchableMixin):
    """Article model for sports content."""

    __tablename__ = "articles"

    # Content identification
    url_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
        doc="Primary deduplication key (hash of source URL)"
    )

    # Content metadata
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Article title"
    )

    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Full article content"
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Article summary or excerpt"
    )

    author: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Article author"
    )

    # Source information
    source_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Name of the content source"
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
        doc="Original article URL"
    )

    published_at: Mapped[Optional[datetime]] = mapped_column(
        Text,
        nullable=True,
        index=True,
        doc="Original publication timestamp"
    )

    # Content classification
    category: Mapped[Optional[ContentCategory]] = mapped_column(
        Enum(ContentCategory, name='content_category'),
        nullable=True,
        index=True,
        doc="Content category"
    )

    tags: Mapped[List[str]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        default=list,
        doc="Content tags"
    )

    sentiment_score: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=3, scale=2),
        nullable=True,
        doc="Sentiment score (-1.0 to 1.0)"
    )

    readability_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Readability score (0-100)"
    )

    # Team associations
    team_ids: Mapped[List[uuid.UUID]] = mapped_column(
        ARRAY(UUID()),
        nullable=True,
        default=list,
        doc="Related team IDs"
    )

    # AI-generated fields
    ai_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="AI-generated summary"
    )

    ai_tags: Mapped[List[str]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        default=list,
        doc="AI-generated tags"
    )

    ai_category: Mapped[Optional[ContentCategory]] = mapped_column(
        Enum(ContentCategory, name='content_category'),
        nullable=True,
        doc="AI-predicted category"
    )

    ai_confidence: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=3, scale=2),
        nullable=True,
        index=True,
        doc="AI prediction confidence (0.0 to 1.0)"
    )

    # Engagement metrics
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of views"
    )

    share_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of shares"
    )

    like_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of likes"
    )

    # Content state
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus, name='article_status'),
        default=ArticleStatus.PUBLISHED,
        nullable=False,
        index=True,
        doc="Article status"
    )

    # Full-text search
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True,
        doc="Full-text search vector (computed)"
    )

    @property
    def is_published(self) -> bool:
        """Check if article is published."""
        return self.status == ArticleStatus.PUBLISHED

    @property
    def engagement_score(self) -> float:
        """Calculate engagement score based on views, shares, and likes."""
        # Weighted engagement score
        return (
            self.view_count * 0.1 +
            self.share_count * 2.0 +
            self.like_count * 1.5
        )

    @property
    def has_ai_analysis(self) -> bool:
        """Check if article has AI analysis."""
        return bool(self.ai_summary or self.ai_category or self.ai_tags)

    def add_view(self) -> None:
        """Increment view count."""
        self.view_count += 1

    def add_share(self) -> None:
        """Increment share count."""
        self.share_count += 1

    def add_like(self) -> None:
        """Increment like count."""
        self.like_count += 1

    def get_related_teams(self) -> List[uuid.UUID]:
        """Get list of related team IDs."""
        return self.team_ids or []

    def add_team_association(self, team_id: uuid.UUID) -> None:
        """Add team association if not already present."""
        if self.team_ids is None:
            self.team_ids = []
        if team_id not in self.team_ids:
            self.team_ids.append(team_id)

    def remove_team_association(self, team_id: uuid.UUID) -> None:
        """Remove team association."""
        if self.team_ids and team_id in self.team_ids:
            self.team_ids.remove(team_id)

    def update_ai_analysis(self,
                          summary: Optional[str] = None,
                          category: Optional[ContentCategory] = None,
                          tags: Optional[List[str]] = None,
                          confidence: Optional[float] = None) -> None:
        """Update AI analysis fields."""
        if summary is not None:
            self.ai_summary = summary
        if category is not None:
            self.ai_category = category
        if tags is not None:
            self.ai_tags = tags
        if confidence is not None:
            self.ai_confidence = confidence

    @classmethod
    def search(cls, query: str, limit: int = 50, team_ids: Optional[List[uuid.UUID]] = None):
        """Search articles by content with optional team filtering."""
        from sqlalchemy import func, select, and_
        from ..database import get_session

        with get_session() as session:
            # Use full-text search with ranking
            search_query = func.plainto_tsquery('english', query)

            conditions = [
                cls.search_vector.op('@@')(search_query),
                cls.status == ArticleStatus.PUBLISHED
            ]

            # Add team filtering if specified
            if team_ids:
                conditions.append(
                    func.array_length(
                        func.array_intersection(cls.team_ids, team_ids), 1
                    ) > 0
                )

            return session.execute(
                select(cls)
                .where(and_(*conditions))
                .order_by(
                    func.ts_rank(cls.search_vector, search_query).desc(),
                    cls.published_at.desc()
                )
                .limit(limit)
            ).scalars().all()

    @classmethod
    def get_by_url_hash(cls, url_hash: str):
        """Get article by URL hash."""
        from ..database import get_session

        with get_session() as session:
            return session.execute(
                select(cls).where(cls.url_hash == url_hash)
            ).scalar_one_or_none()

    @classmethod
    def get_recent_by_teams(cls, team_ids: List[uuid.UUID], limit: int = 20):
        """Get recent articles for specific teams."""
        from sqlalchemy import func, select
        from ..database import get_session

        with get_session() as session:
            return session.execute(
                select(cls)
                .where(
                    and_(
                        cls.status == ArticleStatus.PUBLISHED,
                        func.array_length(
                            func.array_intersection(cls.team_ids, team_ids), 1
                        ) > 0
                    )
                )
                .order_by(cls.published_at.desc())
                .limit(limit)
            ).scalars().all()