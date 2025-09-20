"""
Analytics and metrics models
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID

from sqlalchemy import Date, DateTime, Numeric, String, func, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin
from .enums import InteractionType, EntityType


class UserInteraction(Base, UUIDMixin):
    """
    User interactions for analytics and personalization
    """
    __tablename__ = "user_interactions"

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the user"
    )

    interaction_type: Mapped[InteractionType] = mapped_column(
        nullable=False,
        doc="Type of interaction performed"
    )

    entity_type: Mapped[EntityType] = mapped_column(
        nullable=False,
        doc="Type of entity being interacted with"
    )

    entity_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
        doc="ID of the entity being interacted with"
    )

    interaction_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        doc="Additional metadata about the interaction"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the interaction occurred"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<UserInteraction(user_id={self.user_id}, type={self.interaction_type}, entity={self.entity_type}:{self.entity_id})>"

    @property
    def is_engagement(self) -> bool:
        """Check if this is an engagement interaction"""
        engagement_types = {
            InteractionType.ARTICLE_VIEW,
            InteractionType.ARTICLE_SHARE,
            InteractionType.GAME_VIEW,
            InteractionType.EXPERIENCE_REGISTER,
            InteractionType.TICKET_VIEW,
        }
        return self.interaction_type in engagement_types

    @property
    def is_preference_signal(self) -> bool:
        """Check if this indicates user preference"""
        preference_types = {
            InteractionType.TEAM_FOLLOW,
            InteractionType.TEAM_UNFOLLOW,
            InteractionType.ARTICLE_SHARE,
            InteractionType.EXPERIENCE_REGISTER,
        }
        return self.interaction_type in preference_types


class ContentPerformance(Base, UUIDMixin):
    """
    Content performance metrics aggregated by date
    """
    __tablename__ = "content_performance"
    __table_args__ = (
        UniqueConstraint('content_type', 'content_id', 'metric_name', 'date_recorded', name='uq_content_metric_date'),
    )

    content_type: Mapped[EntityType] = mapped_column(
        nullable=False,
        doc="Type of content being measured"
    )

    content_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
        doc="ID of the content being measured"
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Name of the metric being recorded"
    )

    metric_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 4),
        nullable=False,
        doc="Value of the metric"
    )

    date_recorded: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
        nullable=False,
        doc="Date when the metric was recorded"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created"
    )

    def __repr__(self) -> str:
        return f"<ContentPerformance({self.content_type}:{self.content_id}, {self.metric_name}={self.metric_value}, {self.date_recorded})>"

    @property
    def content_reference(self) -> str:
        """Get string reference to the content"""
        return f"{self.content_type.value}:{self.content_id}"