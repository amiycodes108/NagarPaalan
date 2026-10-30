"""NAGARPAALAN AI — Maintenance, Repairs, and Contractor Schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ContractorBase(BaseModel):
    name: str = Field(..., example="Apex Urban Infra Ltd")
    category: str = Field(..., example="Road Works")
    contact_person: str | None = Field(default=None, example="Vikram Patel")
    email: str | None = Field(default=None, example="projects@apexinfra.in")
    phone: str | None = Field(default=None, example="+91 98765 43210")


class ContractorCreate(ContractorBase):
    contractor_code: str | None = None
    performance_rating: float = 4.2
    warranty_adherence_rate: float = 90.0
    recurrence_rate: float = 8.5
    active_contracts: int = 2


class ContractorResponse(ContractorBase):
    id: int
    contractor_code: str
    performance_rating: float
    warranty_adherence_rate: float
    recurrence_rate: float
    active_contracts: int
    total_spend: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepairBase(BaseModel):
    asset_id: int
    issue_id: int | None = None
    contractor_id: int | None = None
    repair_type: str = Field(..., example="Cold Mix Bitumen Asphalt Patch")
    materials: str | None = Field(default="VG-30 Bitumen + Aggregate 12mm", example="VG-30 Bitumen + Aggregate")
    cost: float = Field(default=25000.0, example=35000.0)
    budget_code: str = Field(default="CIVIC-CAPEX-2026")
    warranty_months: int = Field(default=12)
    status: str = Field(default="Completed")
    notes: str | None = None


class RepairCreate(RepairBase):
    work_order_no: str | None = None
    scheduled_date: datetime | None = None
    completed_at: datetime | None = None
    completion_photo_url: str | None = None


class RepairUpdate(BaseModel):
    status: str | None = None
    completed_at: datetime | None = None
    recurred_during_warranty: bool | None = None
    notes: str | None = None


class RepairResponse(RepairBase):
    id: int
    work_order_no: str
    status: str
    scheduled_date: datetime | None = None
    completed_at: datetime | None = None
    recurred_during_warranty: bool = False
    completion_photo_url: str | None = None
    created_at: datetime
    asset_name: str | None = None
    contractor_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InspectionCreate(BaseModel):
    asset_id: int
    inspector_name: str = Field(..., example="Er. Ramesh Deshmukh")
    inspector_role: str = Field(default="Senior Quality Inspector")
    finding: str = Field(..., example="Satisfactory")  # Satisfactory, Minor Defect, Severe Defect
    notes: str | None = None
    photo_url: str | None = None


class InspectionResponse(BaseModel):
    id: int
    inspection_code: str
    asset_id: int
    inspector_name: str
    inspector_role: str
    finding: str
    notes: str | None = None
    photo_url: str | None = None
    inspected_at: datetime

    model_config = ConfigDict(from_attributes=True)
