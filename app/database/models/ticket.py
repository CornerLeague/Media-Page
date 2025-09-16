"""Ticket deals model."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import SeatQuality


class TicketDeal(BaseModel):
    """Ticket deals and pricing model."""

    __tablename__ = "ticket_deal"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    game_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    row: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seat_numbers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=8, scale=2), nullable=False)
    fees_est: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=8, scale=2), nullable=True)
    total_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=8, scale=2), nullable=True)
    seat_quality: Mapped[Optional[SeatQuality]] = mapped_column(nullable=True)
    availability: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deal_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=3, scale=2), nullable=True)
    provider_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="ticket_deals")

    def __repr__(self) -> str:
        return f"<TicketDeal(game_id={self.game_id}, provider={self.provider}, price={self.price})>"