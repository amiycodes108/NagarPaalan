"""NAGARPAALAN AI — Analytics, Hotspots, and Audited Financial Schemas."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class AnalyticsOverviewResponse(BaseModel):
    total_assets: int
    total_issues: int
    active_issues: int
    recurring_issues: int
    recurrence_rate_percentage: float
    total_complaints: int
    ai_observations_count: int
    unlocated_observations_count: int
    total_repairs_count: int
    total_actual_expenditure: float
    total_estimated_expenditure: float
    total_civic_expenditure: float
    avoidable_repeat_expenditure: float
    avoidable_waste_percentage: float
    city_average_health: float
    critical_risk_assets_count: int


class HotspotCluster(BaseModel):
    cluster_id: str
    ward: str
    zone: str
    latitude: float
    longitude: float
    radius_meters: float
    defect_count: int
    primary_category: str
    recurrence_index: float  # 0.0 to 10.0
    risk_level: str  # Critical, High, Medium
    top_assets: list[str]


class FinancialExplanationItem(BaseModel):
    metric: str
    amount: float
    classification: str  # "Actual Disbursed" or "Estimated Commitment"
    methodology: str


class FinancialOverviewResponse(BaseModel):
    total_budget_allocated: float
    total_actual_expenditure: float
    total_estimated_commitment: float
    total_spent: float
    remaining_budget: float
    spend_by_category: list[dict[str, Any]]
    spend_by_ward: list[dict[str, Any]]
    avoidable_repeat_expenditure: float
    avoidable_waste_percentage: float
    contractor_spending: list[dict[str, Any]]
    metric_explanations: list[FinancialExplanationItem]


class AIModelInfo(BaseModel):
    id: str
    name: str
    task: str
    architecture: str
    source_candidate: str
    version: str
    status: str
    classes_detected: list[str]
    license: str
