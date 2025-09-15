"""Analytics-related SQLAlchemy models."""

import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class SearchAnalytics(BaseModel):
    """Search analytics for tracking user search behavior."""

    __tablename__ = "search_analytics"

    # User relationship (optional for anonymous searches)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="User who performed the search (null for anonymous)"
    )

    # Search data
    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Search query text"
    )

    results_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Number of results returned"
    )

    clicked_results: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        ARRAY(UUID()),
        nullable=True,
        doc="Article IDs that were clicked from results"
    )

    # Full-text search on queries
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True,
        doc="Full-text search vector for query analysis (computed)"
    )

    # Relationship
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="search_analytics",
        doc="User who performed the search"
    )

    @property
    def click_through_rate(self) -> float:
        """Calculate click-through rate."""
        if self.results_count == 0:
            return 0.0

        clicked_count = len(self.clicked_results) if self.clicked_results else 0
        return clicked_count / self.results_count

    @property
    def has_clicks(self) -> bool:
        """Check if search resulted in clicks."""
        return bool(self.clicked_results)

    def add_click(self, article_id: uuid.UUID) -> None:
        """Add article click to search analytics."""
        if self.clicked_results is None:
            self.clicked_results = []

        if article_id not in self.clicked_results:
            self.clicked_results.append(article_id)

    @classmethod
    def log_search(cls,
                  query: str,
                  results_count: int,
                  user_id: Optional[uuid.UUID] = None) -> "SearchAnalytics":
        """Log a search query."""
        from ..database import get_session

        analytics = cls(
            user_id=user_id,
            query=query,
            results_count=results_count
        )

        with get_session() as session:
            session.add(analytics)
            session.commit()
            return analytics

    @classmethod
    def get_popular_queries(cls, limit: int = 20, days: int = 7):
        """Get most popular search queries."""
        from sqlalchemy import select, func, and_
        from datetime import timedelta
        from ..database import get_session

        with get_session() as session:
            cutoff_date = func.now() - timedelta(days=days)

            return session.execute(
                select(
                    cls.query,
                    func.count(cls.id).label('search_count'),
                    func.avg(cls.results_count).label('avg_results'),
                    func.avg(
                        func.coalesce(func.array_length(cls.clicked_results, 1), 0)
                    ).label('avg_clicks')
                )
                .where(cls.created_at >= cutoff_date)
                .group_by(cls.query)
                .order_by(func.count(cls.id).desc())
                .limit(limit)
            ).all()

    @classmethod
    def get_user_search_history(cls, user_id: uuid.UUID, limit: int = 50):
        """Get search history for a specific user."""
        from sqlalchemy import select
        from ..database import get_session

        with get_session() as session:
            return session.execute(
                select(cls)
                .where(cls.user_id == user_id)
                .order_by(cls.created_at.desc())
                .limit(limit)
            ).scalars().all()

    @classmethod
    def get_zero_result_queries(cls, limit: int = 20, days: int = 7):
        """Get queries that returned no results."""
        from sqlalchemy import select, func
        from datetime import timedelta
        from ..database import get_session

        with get_session() as session:
            cutoff_date = func.now() - timedelta(days=days)

            return session.execute(
                select(
                    cls.query,
                    func.count(cls.id).label('frequency')
                )
                .where(
                    and_(
                        cls.created_at >= cutoff_date,
                        cls.results_count == 0
                    )
                )
                .group_by(cls.query)
                .order_by(func.count(cls.id).desc())
                .limit(limit)
            ).all()

    @classmethod
    def get_search_trends(cls, days: int = 30):
        """Get search volume trends over time."""
        from sqlalchemy import select, func
        from datetime import timedelta
        from ..database import get_session

        with get_session() as session:
            cutoff_date = func.now() - timedelta(days=days)

            return session.execute(
                select(
                    func.date_trunc('day', cls.created_at).label('search_date'),
                    func.count(cls.id).label('search_count'),
                    func.count(func.distinct(cls.user_id)).label('unique_users'),
                    func.avg(cls.results_count).label('avg_results'),
                    func.sum(
                        func.case(
                            (func.array_length(cls.clicked_results, 1) > 0, 1),
                            else_=0
                        )
                    ).label('searches_with_clicks')
                )
                .where(cls.created_at >= cutoff_date)
                .group_by(func.date_trunc('day', cls.created_at))
                .order_by(func.date_trunc('day', cls.created_at))
            ).all()