"""NAGARPAALAN AI — Maintenance, Repairs, and Contractor Models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Contractor(Base):
    """Civic maintenance and construction contractor profile."""

    __tablename__ = "contractors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contractor_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # Road Works, Electrical, Drainage, Sanitation
    contact_person: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Performance Intelligence
    performance_rating: Mapped[float] = mapped_column(Float, default=4.2)  # 0.0 - 5.0
    warranty_adherence_rate: Mapped[float] = mapped_column(Float, default=92.0)  # %
    recurrence_rate: Mapped[float] = mapped_column(Float, default=8.0)  # %
    active_contracts: Mapped[int] = mapped_column(Integer, default=2)
    total_spend: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    repairs = relationship("Repair", back_populates="contractor")


class Repair(Base):
    """Repair work order executed on an issue/asset with cost and warranty tracking."""

    __tablename__ = "repairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    work_order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    issue_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("issues.id", ondelete="SET NULL"), nullable=True)
    contractor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("contractors.id", ondelete="SET NULL"), nullable=True)

    repair_type: Mapped[str] = mapped_column(String(128), nullable=False)  # Cold Asphalt Patch, Full Resurfacing, Luminaire Swap
    materials: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    budget_code: Mapped[str] = mapped_column(String(64), default="CIVIC-CAPEX-2026")
    status: Mapped[str] = mapped_column(String(32), default="Scheduled")  # Scheduled, In Progress, Completed, Under Warranty

    warranty_months: Mapped[int] = mapped_column(Integer, default=12)
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    recurred_during_warranty: Mapped[bool] = mapped_column(Boolean, default=False)

    completion_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="repairs")
    issue = relationship("Issue", back_populates="repairs")
    contractor = relationship("Contractor", back_populates="repairs")


class Inspection(Base):
    """Field engineer inspection report."""

    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inspection_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    inspector_name: Mapped[str] = mapped_column(String(128), nullable=False)
    inspector_role: Mapped[str] = mapped_column(String(64), default="Municipal Quality Inspector")
    finding: Mapped[str] = mapped_column(String(64), nullable=False)  # Satisfactory, Minor Defect, Severe Defect
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    inspected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="inspections")
