"""Article classification and entity extraction models."""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import ArticleClassificationCategory


class ArticleClassification(BaseModel):
    """Article AI classification model."""

    __tablename__ = "article_classification"
    __table_args__ = (
        UniqueConstraint("article_id", "category", name="uq_article_category"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    article_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[ArticleClassificationCategory] = mapped_column(nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(precision=3, scale=2), nullable=False)
    rationale_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="classifications")

    def __repr__(self) -> str:
        return f"<ArticleClassification(article_id={self.article_id}, category={self.category}, confidence={self.confidence})>"


class ArticleEntity(BaseModel):
    """Article named entity extraction model."""

    __tablename__ = "article_entities"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    article_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=3, scale=2), nullable=True)
    start_pos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_pos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="entities")

    def __repr__(self) -> str:
        return f"<ArticleEntity(article_id={self.article_id}, type={self.entity_type}, value={self.value})>"