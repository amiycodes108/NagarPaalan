"""NAGARPAALAN AI — Complaint ORM Model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Complaint(Base):
    """An administrative report submitted by a citizen or official concerning an issue."""

    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_number: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    issue_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("issues.id", ondelete="SET NULL"), nullable=True)
    asset_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)

    citizen_name: Mapped[str] = mapped_column(String(128), default="Citizen Reporter")
    citizen_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    citizen_email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    channel: Mapped[str] = mapped_column(String(64), default="Citizen App")  # Citizen App, Web Portal, WhatsApp, Call Center
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address_landmark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="Submitted")  # Submitted, Triaged, Linked to Issue, In Progress, Resolved, Rejected

    # Duplicate & Similarity Engine Scoring
    match_status: Mapped[str] = mapped_column(String(32), default="New")  # New, Matched Existing, Confirmed Match, Rejected Match
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # Explainable match percentage (0-100%)
    match_reasons: Mapped[list[Any]] = mapped_column(JSON, default=list)  # Detail reasons for match
    potential_duplicate_of_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("complaints.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issue = relationship("Issue", back_populates="complaints")
