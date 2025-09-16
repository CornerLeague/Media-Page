"""Pipeline and job management models."""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import AgentType, RunStatus, JobType


class AgentRun(BaseModel):
    """Pipeline execution tracking model."""

    __tablename__ = "agent_run"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    agent_type: Mapped[AgentType] = mapped_column(nullable=False)
    subject_key: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RunStatus] = mapped_column(nullable=False, default=RunStatus.PENDING)
    started_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    meta_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    items_processed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    items_created: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    items_updated: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    items_failed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    scrape_jobs: Mapped[list["ScrapeJob"]] = relationship(
        "ScrapeJob", back_populates="last_run", foreign_keys="ScrapeJob.last_run_id"
    )

    def __repr__(self) -> str:
        return f"<AgentRun(id={self.id}, type={self.agent_type}, status={self.status})>"


class ScrapeJob(BaseModel):
    """Scheduled scraping jobs model."""

    __tablename__ = "scrape_job"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    subject_type: Mapped[str] = mapped_column(Text, nullable=False)
    subject_id: Mapped[Optional[UUID]] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    job_type: Mapped[JobType] = mapped_column(nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    scheduled_for: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    status: Mapped[RunStatus] = mapped_column(nullable=False, default=RunStatus.PENDING)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_run_id: Mapped[Optional[UUID]] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("agent_run.id", ondelete="SET NULL"), nullable=True
    )
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    config_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    last_run: Mapped[Optional["AgentRun"]] = relationship(
        "AgentRun", back_populates="scrape_jobs", foreign_keys=[last_run_id]
    )

    def __repr__(self) -> str:
        return f"<ScrapeJob(id={self.id}, type={self.job_type}, status={self.status})>"