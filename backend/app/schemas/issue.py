"""NAGARPAALAN AI — Issue Pydantic Schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class IssueBase(BaseModel):
    category: str = Field(..., example="Pothole")
    title: str = Field(..., example="Deep pothole in outer lane")
    description: str | None = Field(default=None, example="Estimated 12cm depth creating severe vehicle slowdowns")
    severity: str = Field(default="Medium", example="High")  # Low, Medium, High, Critical
    status: str = Field(default="Open", example="Open")  # Open, In Review, Assigned, Under Repair, Repaired, Recurring
    latitude: float = Field(..., example=12.9719)
    longitude: float = Field(..., example=77.5948)
    asset_id: int | None = None


class IssueCreate(IssueBase):
    issue_code: str | None = None
    recurrence_count: int = 0
    is_recurrence: bool = False
    recurrence_notes: str | None = None


class IssueUpdate(BaseModel):
    category: str | None = None
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    asset_id: int | None = None
    recurrence_count: int | None = None
    is_recurrence: bool | None = None
    recurrence_notes: str | None = None
    resolved_at: datetime | None = None


class IssueResponse(IssueBase):
    id: int
    issue_code: str
    asset_id: int | None = None
    recurrence_count: int = 0
    is_recurrence: bool = False
    recurrence_notes: str | None = None
    first_reported_at: datetime
    last_reported_at: datetime
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    asset_name: str | None = None
    complaints_count: int = 0
    observations_count: int = 0

    model_config = ConfigDict(from_attributes=True)
