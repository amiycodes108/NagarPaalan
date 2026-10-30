"""NAGARPAALAN AI — Asset Pydantic Schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class AssetBase(BaseModel):
    name: str = Field(..., example="MG Road Flyover North Segment")
    category: str = Field(..., example="Road")  # Road, Streetlight, Drainage, Bridge, Waste Point
    asset_type: str | None = Field(default=None, example="Asphalt Arterial")
    ward: str = Field(..., example="Ward 14 - Central")
    zone: str = Field(..., example="North Zone")
    status: str = Field(default="Operational", example="Operational")
    latitude: float = Field(..., example=12.9716)
    longitude: float = Field(..., example=77.5946)
    address: str | None = Field(default=None, example="Near Trinity Metro, MG Road")
    install_year: int | None = Field(default=2021)


class AssetCreate(AssetBase):
    asset_code: str | None = None


class AssetUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    asset_type: str | None = None
    ward: str | None = None
    zone: str | None = None
    status: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    health_score: int | None = None
    risk_score: float | None = None
    risk_level: str | None = None
    risk_factors: list[Any] | None = None


class AssetResponse(AssetBase):
    id: int
    asset_code: str
    health_score: int
    risk_score: float
    risk_level: str
    risk_factors: list[Any]
    last_inspected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CityMemoryEventResponse(BaseModel):
    id: int
    asset_id: int
    issue_id: int | None = None
    event_type: str
    severity: str
    summary: str
    details: dict[str, Any]
    actor: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetDetailResponse(AssetResponse):
    issues_count: int = 0
    active_issues_count: int = 0
    recurring_issues_count: int = 0
    repairs_count: int = 0
    total_repair_cost: float = 0.0
    memory_events: list[CityMemoryEventResponse] = []
