"""Database models derived from privacy-policy.md data schema (F-07)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class CLScore(Base):
    """Cognitive load scores time series."""

    __tablename__ = "cl_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    band: Mapped[str] = mapped_column(String(20), nullable=False)
    burnout_risk: Mapped[float] = mapped_column(Numeric(4, 3), nullable=True)
    flow_state: Mapped[bool] = mapped_column(Boolean, default=False)
    component_scores: Mapped[dict] = mapped_column(JSONB, nullable=True)
    risk_factors: Mapped[list] = mapped_column(JSONB, nullable=True)
    recommended_interventions: Mapped[list] = mapped_column(JSONB, nullable=True)
    data_mode: Mapped[str] = mapped_column(String(10), default="live")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Intervention(Base):
    """Intervention log — audit trail of all interventions (live and dry-run)."""

    __tablename__ = "interventions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    int_type: Mapped[str] = mapped_column(String(10), nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(10), nullable=False)
    triggered_by: Mapped[list] = mapped_column(JSONB, nullable=True)
    cl_score_before: Mapped[int] = mapped_column(Integer, nullable=True)
    cl_score_after: Mapped[int] = mapped_column(Integer, nullable=True)
    action_taken: Mapped[str] = mapped_column(Text, nullable=True)
    outcome: Mapped[str] = mapped_column(String(20), nullable=True)
    miro_card_id: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SignalSnapshot(Base):
    """Signal snapshots — derived signals only, never raw content."""

    __tablename__ = "signal_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    signal_id: Mapped[str] = mapped_column(String(10), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(10, 3), nullable=True)
    source_mode: Mapped[str] = mapped_column(String(10), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserConsent(Base):
    """User consent records — consent must be granted before data collection."""

    __tablename__ = "user_consent"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    consent_level: Mapped[str] = mapped_column(String(10), nullable=False)  # BASIC | STANDARD | FULL
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UserToken(Base):
    """OAuth tokens for authenticated users."""

    __tablename__ = "user_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    google_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    google_refresh_token: Mapped[str] = mapped_column(Text, nullable=True)
    token_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
