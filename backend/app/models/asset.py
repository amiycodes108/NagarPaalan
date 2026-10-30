"""NAGARPAALAN AI — Asset ORM Model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Asset(Base):
    """Permanent physical infrastructure identity (road, streetlight, bridge, drain)."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # Road, Streetlight, Drainage, Bridge, Waste Point
    asset_type: Mapped[str] = mapped_column(String(64), nullable=True)  # Asphalt Highway, LED High-Mast, etc.
    ward: Mapped[str] = mapped_column(String(64), nullable=False)
    zone: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="Operational")  # Operational, Degraded, Under Repair, Critical
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Health & Risk Composite
    health_score: Mapped[int] = mapped_column(Integer, default=90)  # 0 to 100
    risk_score: Mapped[float] = mapped_column(Float, default=1.5)  # 0.0 to 10.0
    risk_level: Mapped[str] = mapped_column(String(32), default="Low")  # Low, Medium, High, Critical
    risk_factors: Mapped[list[Any]] = mapped_column(JSON, default=list)

    install_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_inspected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issues = relationship("Issue", back_populates="asset", cascade="all, delete-orphan")
    observations = relationship("Observation", back_populates="asset")
    repairs = relationship("Repair", back_populates="asset")
    inspections = relationship("Inspection", back_populates="asset", cascade="all, delete-orphan")
    memory_events = relationship("CityMemoryEvent", back_populates="asset", cascade="all, delete-orphan")
