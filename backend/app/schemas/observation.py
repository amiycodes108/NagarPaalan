"""NAGARPAALAN AI — Normalized AI Observation Schemas (Section 5 Standard with GPS Integrity)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class NormalizedDetection(BaseModel):
    """Universal normalized detection output returned by every AI Adapter."""

    category: str = Field(..., json_schema_extra={"example": "pothole"})
    confidence: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.88})
    bounding_box: BoundingBox | None = None
    frame_reference: str | None = Field(default=None, json_schema_extra={"example": "frame_00042.jpg"})
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # GPS Data Integrity
    latitude: float | None = None
    longitude: float | None = None
    location_provenance: str = Field(default="Unlocated", json_schema_extra={"example": "Manual Input"})
    is_located: bool = False

    # AI Inference Transparency
    model_name: str = Field(..., json_schema_extra={"example": "iwatchroad-v2-heuristic"})
    model_version: str = Field(default="1.0.0", json_schema_extra={"example": "2.1.0"})
    inference_engine_type: str = Field(default="Heuristic Rule-Based", json_schema_extra={"example": "Heuristic Rule-Based"})

    # Defect classification distinction
    is_defect: bool = Field(default=True, description="Distinguishes detected object from verified defect")
    defect_label: str | None = Field(default=None, json_schema_extra={"example": "Severe Pothole"})
    severity: str = Field(default="Medium", json_schema_extra={"example": "High"})


class ObservationCreate(NormalizedDetection):
    asset_id: int | None = None
    issue_id: int | None = None
    source_channel: str = "Dashcam"
    image_url: str | None = None


class ObservationResponse(BaseModel):
    id: int
    observation_code: str
    asset_id: int | None = None
    issue_id: int | None = None
    source_channel: str
    category: str
    confidence: float
    bounding_box: dict[str, Any] | None = None
    frame_reference: str | None = None
    timestamp: datetime

    # GPS Integrity Fields
    latitude: float | None = None
    longitude: float | None = None
    location_provenance: str = "Unlocated"
    is_located: bool = False

    # AI Inference Transparency
    model_name: str
    model_version: str
    inference_engine_type: str = "Heuristic Rule-Based"
    image_url: str | None = None
    defect_confirmed: bool
    defect_classification: str | None = None
    notes: str | None = None
    created_at: datetime
    asset_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class VideoProcessingResponse(BaseModel):
    video_id: str
    filename: str
    total_frames_extracted: int
    detections_found: int
    matched_assets_count: int
    unlocated_detections_count: int
    recurrence_alerts: list[dict[str, Any]]
    observations: list[ObservationResponse]
