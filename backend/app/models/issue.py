"""NAGARPAALAN AI — Issue ORM Model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Issue(Base):
    """A physical defect or damage event on an asset (e.g., pothole, broken luminaire)."""

    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    issue_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    asset_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # Pothole, Surface Crack, Streetlight Failure, etc.
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(32), default="Medium")  # Low, Medium, High, Critical
    status: Mapped[str] = mapped_column(String(32), default="Open")  # Open, In Review, Assigned, Under Repair, Repaired, Recurring
    
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # City Memory Recurrence Tracking
    recurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    is_recurrence: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    first_reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="issues")
    complaints = relationship("Complaint", back_populates="issue")
    observations = relationship("Observation", back_populates="issue")
    repairs = relationship("Repair", back_populates="issue")
