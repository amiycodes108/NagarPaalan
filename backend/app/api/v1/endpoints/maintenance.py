"""NAGARPAALAN AI — Maintenance, Repairs, and Contractor Endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.issue import Issue
from app.models.maintenance import Contractor, Inspection, Repair
from app.schemas.maintenance import (
    ContractorCreate,
    ContractorResponse,
    InspectionCreate,
    InspectionResponse,
    RepairCreate,
    RepairResponse,
    RepairUpdate,
)
from app.services.city_memory import evaluate_recurrence_and_update_risk, record_memory_event

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


# ── Repairs & Work Orders ──────────────────────────────────────────────

@router.get("/repairs", response_model=list[RepairResponse], summary="List repairs and work orders")
def list_repairs(
    asset_id: int | None = None,
    status: str | None = None,
    contractor_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[RepairResponse]:
    """Retrieve all civic maintenance work orders."""
    query = db.query(Repair)
    if asset_id:
        query = query.filter(Repair.asset_id == asset_id)
    if status:
        query = query.filter(Repair.status == status)
    if contractor_id:
        query = query.filter(Repair.contractor_id == contractor_id)

    repairs = query.order_by(Repair.created_at.desc()).all()

    results: list[RepairResponse] = []
    for r in repairs:
        asset_name = r.asset.name if r.asset else None
        contractor_name = r.contractor.name if r.contractor else None
        results.append(
            RepairResponse(
                id=r.id,
                work_order_no=r.work_order_no,
                asset_id=r.asset_id,
                issue_id=r.issue_id,
                contractor_id=r.contractor_id,
                repair_type=r.repair_type,
                materials=r.materials,
                cost=r.cost,
                budget_code=r.budget_code,
                warranty_months=r.warranty_months,
                status=r.status,
                notes=r.notes,
                scheduled_date=r.scheduled_date,
                completed_at=r.completed_at,
                recurred_during_warranty=r.recurred_during_warranty,
                completion_photo_url=r.completion_photo_url,
                created_at=r.created_at,
                asset_name=asset_name,
                contractor_name=contractor_name,
            )
        )
    return results


@router.post("/repairs", response_model=RepairResponse, summary="Issue repair work order")
def create_repair(payload: RepairCreate, db: Session = Depends(get_db)) -> RepairResponse:
    """Issue a new maintenance repair work order, link contractor, and log in City Memory."""
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    wo_no = payload.work_order_no or f"WO-{datetime.utcnow().year}-{uuid.uuid4().hex[:5].upper()}"

    repair = Repair(
        work_order_no=wo_no,
        asset_id=payload.asset_id,
        issue_id=payload.issue_id,
        contractor_id=payload.contractor_id,
        repair_type=payload.repair_type,
        materials=payload.materials,
        cost=payload.cost,
        budget_code=payload.budget_code,
        warranty_months=payload.warranty_months,
        status=payload.status,
        notes=payload.notes,
        scheduled_date=payload.scheduled_date or datetime.utcnow(),
        completed_at=payload.completed_at or (datetime.utcnow() if payload.status == "Completed" else None),
        completion_photo_url=payload.completion_photo_url,
    )
    db.add(repair)

    # If linked to an issue and status is completed, resolve issue
    if payload.issue_id and payload.status == "Completed":
        issue = db.query(Issue).filter(Issue.id == payload.issue_id).first()
        if issue:
            issue.status = "Repaired"
            issue.resolved_at = datetime.utcnow()

    # Update contractor total spend if contractor assigned
    if payload.contractor_id:
        contractor = db.query(Contractor).filter(Contractor.id == payload.contractor_id).first()
        if contractor:
            contractor.total_spend += payload.cost

    db.commit()
    db.refresh(repair)

    record_memory_event(
        db=db,
        asset_id=repair.asset_id,
        issue_id=repair.issue_id,
        event_type="WORK_ORDER_ISSUED" if repair.status != "Completed" else "REPAIR_COMPLETED",
        severity="Info",
        summary=f"Work Order {repair.work_order_no}: {repair.repair_type} (Cost: ₹{repair.cost:,.0f}).",
        details={
            "work_order_no": repair.work_order_no,
            "contractor_id": repair.contractor_id,
            "cost": repair.cost,
            "warranty_months": repair.warranty_months,
        },
        actor="Maintenance Engineer",
    )

    evaluate_recurrence_and_update_risk(db, repair.asset_id, trigger_channel="Maintenance Registry")

    asset_name = asset.name
    contractor_name = repair.contractor.name if repair.contractor else None

    return RepairResponse(
        id=repair.id,
        work_order_no=repair.work_order_no,
        asset_id=repair.asset_id,
        issue_id=repair.issue_id,
        contractor_id=repair.contractor_id,
        repair_type=repair.repair_type,
        materials=repair.materials,
        cost=repair.cost,
        budget_code=repair.budget_code,
        warranty_months=repair.warranty_months,
        status=repair.status,
        notes=repair.notes,
        scheduled_date=repair.scheduled_date,
        completed_at=repair.completed_at,
        recurred_during_warranty=repair.recurred_during_warranty,
        completion_photo_url=repair.completion_photo_url,
        created_at=repair.created_at,
        asset_name=asset_name,
        contractor_name=contractor_name,
    )


# ── Contractors ────────────────────────────────────────────────────────

@router.get("/contractors", response_model=list[ContractorResponse], summary="List contractors")
def list_contractors(db: Session = Depends(get_db)) -> list[ContractorResponse]:
    """Retrieve contractor registry with performance and recurrence metrics."""
    contractors = db.query(Contractor).order_by(Contractor.performance_rating.desc()).all()
    return [ContractorResponse.model_validate(c) for c in contractors]


@router.post("/contractors", response_model=ContractorResponse, summary="Register contractor")
def create_contractor(payload: ContractorCreate, db: Session = Depends(get_db)) -> ContractorResponse:
    """Register a new infrastructure maintenance contractor."""
    code = payload.contractor_code or f"CON-{uuid.uuid4().hex[:6].upper()}"

    contractor = Contractor(
        contractor_code=code,
        name=payload.name,
        category=payload.category,
        contact_person=payload.contact_person,
        email=payload.email,
        phone=payload.phone,
        performance_rating=payload.performance_rating,
        warranty_adherence_rate=payload.warranty_adherence_rate,
        recurrence_rate=payload.recurrence_rate,
        active_contracts=payload.active_contracts,
        total_spend=0.0,
    )
    db.add(contractor)
    db.commit()
    db.refresh(contractor)
    return ContractorResponse.model_validate(contractor)


# ── Inspections ────────────────────────────────────────────────────────

@router.get("/inspections", response_model=list[InspectionResponse], summary="List inspections")
def list_inspections(asset_id: int | None = None, db: Session = Depends(get_db)) -> list[InspectionResponse]:
    """List field quality inspection reports."""
    query = db.query(Inspection)
    if asset_id:
        query = query.filter(Inspection.asset_id == asset_id)
    inspections = query.order_by(Inspection.inspected_at.desc()).all()
    return [InspectionResponse.model_validate(i) for i in inspections]


@router.post("/inspections", response_model=InspectionResponse, summary="Record field inspection")
def create_inspection(payload: InspectionCreate, db: Session = Depends(get_db)) -> InspectionResponse:
    """Record a field engineering inspection and update asset inspection timestamp."""
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    code = f"INSP-{datetime.utcnow().year}-{uuid.uuid4().hex[:5].upper()}"
    inspection = Inspection(
        inspection_code=code,
        asset_id=payload.asset_id,
        inspector_name=payload.inspector_name,
        inspector_role=payload.inspector_role,
        finding=payload.finding,
        notes=payload.notes,
        photo_url=payload.photo_url,
        inspected_at=datetime.utcnow(),
    )
    db.add(inspection)

    asset.last_inspected_at = datetime.utcnow()
    db.commit()
    db.refresh(inspection)

    record_memory_event(
        db=db,
        asset_id=payload.asset_id,
        event_type="INSPECTION_CONDUCTED",
        severity="Warning" if payload.finding in ["Severe Defect", "Immediate Action Required"] else "Info",
        summary=f"Field Inspection by {payload.inspector_name}: Finding is '{payload.finding}'.",
        details={"finding": payload.finding, "notes": payload.notes},
        actor=payload.inspector_name,
    )

    return InspectionResponse.model_validate(inspection)
