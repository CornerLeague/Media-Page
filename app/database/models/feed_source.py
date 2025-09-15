"""Feed source and ingestion-related SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import Dict, Optional, Any

from sqlalchemy import (
    Boolean, Enum, ForeignKey, Integer, Numeric, String, Text, DateTime
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .enums import IngestionStatus


class FeedSource(BaseModel):
    """Feed source configuration for content ingestion."""

    __tablename__ = "feed_sources"

    # Source identification
    name: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        doc="Unique feed source name"
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Feed URL"
    )

    feed_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Feed type (rss, json, api, etc.)"
    )

    # Source state
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Whether source is actively being processed"
    )

    # Fetch tracking
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Last fetch attempt timestamp"
    )

    last_successful_fetch_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last successful fetch timestamp"
    )

    fetch_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        doc="Fetch interval in minutes"
    )

    # Configuration
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        doc="Feed-specific configuration"
    )

    # Relationships
    ingestion_logs: Mapped[list["IngestionLog"]] = relationship(
        "IngestionLog",
        back_populates="source",
        doc="Ingestion attempts for this source"
    )

    @property
    def is_due_for_fetch(self) -> bool:
        """Check if source is due for fetching."""
        if not self.is_active:
            return False

        if self.last_fetched_at is None:
            return True

        from datetime import timedelta
        interval = timedelta(minutes=self.fetch_interval_minutes)
        return (datetime.utcnow() - self.last_fetched_at) >= interval

    @property
    def fetch_success_rate(self) -> float:
        """Calculate recent fetch success rate."""
        if not self.ingestion_logs:
            return 0.0

        # Look at last 20 attempts
        recent_logs = sorted(self.ingestion_logs, key=lambda x: x.created_at, reverse=True)[:20]
        if not recent_logs:
            return 0.0

        success_count = sum(1 for log in recent_logs if log.ingestion_status == IngestionStatus.SUCCESS)
        return success_count / len(recent_logs)

    def update_fetch_time(self, successful: bool = True) -> None:
        """Update fetch timestamps."""
        now = datetime.utcnow()
        self.last_fetched_at = now

        if successful:
            self.last_successful_fetch_at = now

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default) if self.config else default

    def set_config_value(self, key: str, value: Any) -> None:
        """Set configuration value."""
        if self.config is None:
            self.config = {}
        self.config[key] = value

    @classmethod
    def get_active_sources(cls):
        """Get all active feed sources."""
        from sqlalchemy import select
        from ..database import get_session

        with get_session() as session:
            return session.execute(
                select(cls).where(cls.is_active == True)
            ).scalars().all()

    @classmethod
    def get_sources_due_for_fetch(cls):
        """Get sources that are due for fetching."""
        from sqlalchemy import select, func
        from datetime import timedelta
        from ..database import get_session

        with get_session() as session:
            now = func.now()
            return session.execute(
                select(cls)
                .where(
                    cls.is_active == True,
                    func.coalesce(
                        cls.last_fetched_at + func.make_interval(0, 0, 0, 0, 0, cls.fetch_interval_minutes),
                        now
                    ) <= now
                )
            ).scalars().all()


class IngestionLog(BaseModel):
    """Log entry for content ingestion attempts."""

    __tablename__ = "ingestion_logs"

    # Source relationship
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feed_sources.id"),
        nullable=True,
        index=True,
        doc="Source feed ID"
    )

    # Content identification
    url_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
        doc="URL hash for deduplication"
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Original content URL"
    )

    # Ingestion result
    ingestion_status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus, name='ingestion_status'),
        nullable=False,
        index=True,
        doc="Ingestion attempt result"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Error message if ingestion failed"
    )

    # Duplicate detection
    duplicate_of: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id"),
        nullable=True,
        doc="Original article if this is a duplicate"
    )

    similarity_score: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=3, scale=2),
        nullable=True,
        doc="Similarity score for near-duplicate detection"
    )

    # Relationships
    source: Mapped[Optional["FeedSource"]] = relationship(
        "FeedSource",
        back_populates="ingestion_logs",
        doc="Source feed"
    )

    @property
    def is_success(self) -> bool:
        """Check if ingestion was successful."""
        return self.ingestion_status == IngestionStatus.SUCCESS

    @property
    def is_duplicate(self) -> bool:
        """Check if content was detected as duplicate."""
        return self.ingestion_status == IngestionStatus.DUPLICATE

    @property
    def is_error(self) -> bool:
        """Check if ingestion failed with error."""
        return self.ingestion_status == IngestionStatus.ERROR

    @classmethod
    def log_success(cls, source_id: Optional[uuid.UUID], url_hash: str, source_url: str):
        """Log successful ingestion."""
        from ..database import get_session

        log = cls(
            source_id=source_id,
            url_hash=url_hash,
            source_url=source_url,
            ingestion_status=IngestionStatus.SUCCESS
        )

        with get_session() as session:
            session.add(log)
            session.commit()
            return log

    @classmethod
    def log_duplicate(cls,
                     source_id: Optional[uuid.UUID],
                     url_hash: str,
                     source_url: str,
                     duplicate_of: uuid.UUID,
                     similarity_score: Optional[float] = None):
        """Log duplicate detection."""
        from ..database import get_session

        log = cls(
            source_id=source_id,
            url_hash=url_hash,
            source_url=source_url,
            ingestion_status=IngestionStatus.DUPLICATE,
            duplicate_of=duplicate_of,
            similarity_score=similarity_score
        )

        with get_session() as session:
            session.add(log)
            session.commit()
            return log

    @classmethod
    def log_error(cls,
                 source_id: Optional[uuid.UUID],
                 url_hash: str,
                 source_url: str,
                 error_message: str):
        """Log ingestion error."""
        from ..database import get_session

        log = cls(
            source_id=source_id,
            url_hash=url_hash,
            source_url=source_url,
            ingestion_status=IngestionStatus.ERROR,
            error_message=error_message
        )

        with get_session() as session:
            session.add(log)
            session.commit()
            return log

    @classmethod
    def get_duplicate_rate(cls, source_id: Optional[uuid.UUID] = None, days: int = 7) -> float:
        """Calculate duplicate rate for source or overall."""
        from sqlalchemy import select, func, and_
        from datetime import timedelta
        from ..database import get_session

        with get_session() as session:
            conditions = [
                cls.created_at >= func.now() - timedelta(days=days)
            ]

            if source_id:
                conditions.append(cls.source_id == source_id)

            # Get total attempts
            total_query = select(func.count(cls.id)).where(and_(*conditions))
            total = session.execute(total_query).scalar() or 0

            if total == 0:
                return 0.0

            # Get duplicates
            duplicate_conditions = conditions + [cls.ingestion_status == IngestionStatus.DUPLICATE]
            duplicate_query = select(func.count(cls.id)).where(and_(*duplicate_conditions))
            duplicates = session.execute(duplicate_query).scalar() or 0

            return duplicates / total

    @classmethod
    def get_recent_logs(cls, source_id: Optional[uuid.UUID] = None, limit: int = 100):
        """Get recent ingestion logs."""
        from sqlalchemy import select
        from ..database import get_session

        with get_session() as session:
            query = select(cls)

            if source_id:
                query = query.where(cls.source_id == source_id)

            return session.execute(
                query.order_by(cls.created_at.desc()).limit(limit)
            ).scalars().all()