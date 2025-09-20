"""
Ticket deals and provider models
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class TicketProvider(Base, UUIDMixin, TimestampMixin):
    """
    Ticket providers/platforms
    """
    __tablename__ = "ticket_providers"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        doc="Name of the ticket provider"
    )

    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Provider's website URL"
    )

    api_endpoint: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="API endpoint for this provider"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this provider is currently active"
    )

    # Relationships
    ticket_deals: Mapped[list["TicketDeal"]] = relationship(
        "TicketDeal",
        back_populates="provider",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<TicketProvider(id={self.id}, name='{self.name}', active={self.is_active})>"


class TicketDeal(Base, UUIDMixin, TimestampMixin):
    """
    Ticket deals and pricing information
    """
    __tablename__ = "ticket_deals"
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_valid_price'),
        CheckConstraint('quantity > 0', name='check_valid_quantity'),
        CheckConstraint('deal_score >= 0 AND deal_score <= 1', name='check_valid_deal_score'),
    )

    provider_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ticket_providers.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the ticket provider"
    )

    game_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        doc="Reference to the specific game (if applicable)"
    )

    team_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        doc="Reference to the team (for general team tickets)"
    )

    section: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Stadium section for the tickets"
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        doc="Ticket price in USD"
    )

    quantity: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of tickets available"
    )

    deal_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.5"),
        nullable=False,
        doc="Deal quality score (0.0 to 1.0, higher is better)"
    )

    external_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        doc="URL to purchase tickets on provider's site"
    )

    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="External identifier from the provider"
    )

    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When this deal expires"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this deal is currently active"
    )

    # Relationships
    provider: Mapped["TicketProvider"] = relationship(
        "TicketProvider",
        back_populates="ticket_deals",
        lazy="selectin"
    )

    game: Mapped[Optional["Game"]] = relationship(
        "Game",
        lazy="selectin"
    )

    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<TicketDeal(id={self.id}, provider='{self.provider.name if self.provider else None}', section='{self.section}', price=${self.price})>"

    @property
    def is_great_deal(self) -> bool:
        """Check if this is considered a great deal"""
        return self.deal_score >= Decimal("0.8")

    @property
    def is_good_deal(self) -> bool:
        """Check if this is considered a good deal"""
        return self.deal_score >= Decimal("0.6")

    @property
    def deal_quality(self) -> str:
        """Get deal quality description"""
        if self.deal_score >= Decimal("0.8"):
            return "Great Deal"
        elif self.deal_score >= Decimal("0.6"):
            return "Good Deal"
        elif self.deal_score >= Decimal("0.4"):
            return "Fair Deal"
        else:
            return "Poor Deal"

    @property
    def is_expired(self) -> bool:
        """Check if the deal has expired"""
        if not self.valid_until:
            return False
        return datetime.now() > self.valid_until