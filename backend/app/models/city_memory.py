"""NAGARPAALAN AI — City Memory Timeline Event Model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CityMemoryEvent(Base):
    """Immutable memory timeline event recorded for an infrastructure asset."""

    __tablename__ = "city_memory_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    issue_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("issues.id", ondelete="SET NULL"), nullable=True)

    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    # COMPLAINT_FILED, AI_OBSERVATION, INSPECTION_CONDUCTED, WORK_ORDER_ISSUED,
    # REPAIR_COMPLETED, RECURRENCE_DETECTED, WARRANTY_BREACH, RISK_ESCALATION

    severity: Mapped[str] = mapped_column(String(32), default="Info")  # Info, Warning, Critical
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    actor: Mapped[str] = mapped_column(String(128), default="System")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="memory_events")
