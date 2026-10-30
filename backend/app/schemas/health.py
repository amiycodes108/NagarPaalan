"""NAGARPAALAN AI — Health-check Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    """Health status of a single infrastructure component."""

    status: str = Field(..., description="Component status: 'healthy' or 'unhealthy'")
    latency_ms: float | None = Field(
        None, description="Round-trip latency in milliseconds"
    )
    detail: str | None = Field(None, description="Additional detail (e.g. version)")


class HealthResponse(BaseModel):
    """Aggregated application health response."""

    status: str = Field(..., description="Overall status: 'healthy' or 'unhealthy'")
    version: str = Field(..., description="Application version")
    app_name: str = Field(..., description="Application name")
    components: dict[str, ComponentHealth] = Field(
        default_factory=dict,
        description="Per-component health details",
    )
