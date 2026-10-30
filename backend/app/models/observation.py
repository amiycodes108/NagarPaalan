"""NAGARPAALAN AI — AI Observation ORM Model (with GPS Provenance & Verification)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Observation(Base):
    """Normalized AI detection record from dashcam, civic vision, or citizen uploads."""

    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    observation_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    asset_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    issue_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("issues.id", ondelete="SET NULL"), nullable=True)

    source_channel: Mapped[str] = mapped_column(String(64), default="Dashcam")  # Dashcam, Civic Vision, Citizen Photo
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    bounding_box: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    frame_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # GPS Data Integrity & Provenance
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_provenance: Mapped[str] = mapped_column(String(64), default="Unlocated")  # Manual Input, EXIF, GPX, Embedded Telemetry, Unlocated
    is_located: Mapped[bool] = mapped_column(Boolean, default=False)

    # Model & Inference Transparency
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    inference_engine_type: Mapped[str] = mapped_column(String(64), default="Heuristic Rule-Based")
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    defect_confirmed: Mapped[bool] = mapped_column(Boolean, default=True)
    defect_classification: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="observations")
    issue = relationship("Issue", back_populates="observations")
