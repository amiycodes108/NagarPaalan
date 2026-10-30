"""NAGARPAALAN AI — Complaint and Duplicate Detection Schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ComplaintBase(BaseModel):
    category: str = Field(..., example="Road Damage")
    title: str = Field(..., example="Huge crater near Metro pillar 42")
    description: str = Field(..., example="Water collected in large road depression, two wheelers skidding.")
    latitude: float = Field(..., example=12.9718)
    longitude: float = Field(..., example=77.5947)
    address_landmark: str | None = Field(default=None, example="Opposite Trinity Metro Gate 2")
    citizen_name: str = Field(default="Concerned Resident")
    citizen_phone: str | None = Field(default=None)
    citizen_email: str | None = Field(default=None)
    channel: str = Field(default="Citizen App")  # Citizen App, Web Portal, WhatsApp, Call Center
    photo_url: str | None = None


class ComplaintCreate(ComplaintBase):
    pass


class MatchReasonItem(BaseModel):
    criterion: str  # e.g., "Geographic Proximity", "Semantic Intent", "Asset Alignment"
    score: float  # 0 to 100
    weight: float  # e.g., 0.4
    explanation: str  # e.g. "Located 18 meters from reported Issue ISS-2026-001 (Threshold: 50m)"


class DuplicateMatchCandidate(BaseModel):
    target_type: str  # "issue" or "complaint"
    target_id: int
    target_code: str
    target_title: str
    target_status: str
    distance_meters: float
    semantic_similarity: float  # 0.0 to 1.0
    overall_match_score: float  # 0.0 to 100.0%
    reasons: list[MatchReasonItem]
    recommended_action: str  # "LINK_TO_EXISTING_ISSUE", "FLAG_FOR_REVIEW", "CREATE_NEW_ISSUE"


class ComplaintResponse(ComplaintBase):
    id: int
    ticket_number: str
    issue_id: int | None = None
    asset_id: int | None = None
    status: str
    match_status: str
    match_score: float | None = None
    match_reasons: list[Any] = []
    potential_duplicate_of_id: int | None = None
    created_at: datetime
    updated_at: datetime
    matched_candidates: list[DuplicateMatchCandidate] = []

    model_config = ConfigDict(from_attributes=True)


class LinkIssueRequest(BaseModel):
    issue_id: int
    review_notes: str | None = None
    confirm_recurrence: bool = False


class CreateIssueFromComplaintRequest(BaseModel):
    asset_id: int | None = None
    severity: str = "High"
    title: str | None = None
