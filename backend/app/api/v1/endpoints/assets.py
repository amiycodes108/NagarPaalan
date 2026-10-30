"""NAGARPAALAN AI — Asset Registry Endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.city_memory import CityMemoryEvent
from app.models.issue import Issue
from app.models.maintenance import Repair
from app.schemas.asset import (
    AssetCreate,
    AssetDetailResponse,
    AssetResponse,
    AssetUpdate,
    CityMemoryEventResponse,
)
from app.services.city_memory import record_memory_event

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetResponse], summary="List infrastructure assets")
def list_assets(
    category: str | None = Query(None, description="Filter by category (Road, Streetlight, etc.)"),
    ward: str | None = Query(None, description="Filter by municipal ward"),
    zone: str | None = Query(None, description="Filter by administrative zone"),
    status: str | None = Query(None, description="Filter by status (Operational, Degraded, Critical)"),
    risk_level: str | None = Query(None, description="Filter by risk level (Low, Medium, High, Critical)"),
    search: str | None = Query(None, description="Search by name, asset code, or address"),
    db: Session = Depends(get_db),
) -> list[AssetResponse]:
    """Retrieve all physical civic infrastructure assets with optional filtering."""
    query = db.query(Asset)

    if category:
        query = query.filter(Asset.category.ilike(f"%{category}%"))
    if ward:
        query = query.filter(Asset.ward.ilike(f"%{ward}%"))
    if zone:
        query = query.filter(Asset.zone.ilike(f"%{zone}%"))
    if status:
        query = query.filter(Asset.status == status)
    if risk_level:
        query = query.filter(Asset.risk_level == risk_level)
    if search:
        search_filter = (
            Asset.name.ilike(f"%{search}%")
            | Asset.asset_code.ilike(f"%{search}%")
            | Asset.address.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    return query.order_by(Asset.risk_score.desc(), Asset.id.asc()).all()


@router.post("", response_model=AssetResponse, summary="Register new physical asset")
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)) -> AssetResponse:
    """Register a new physical infrastructure asset into the city registry."""
    code = payload.asset_code or f"AST-{payload.category[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"

    asset = Asset(
        asset_code=code,
        name=payload.name,
        category=payload.category,
        asset_type=payload.asset_type,
        ward=payload.ward,
        zone=payload.zone,
        status=payload.status,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address=payload.address,
        install_year=payload.install_year,
        health_score=90,
        risk_score=1.2,
        risk_level="Low",
        risk_factors=["Asset commissioned into City Registry"],
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    # Initial City Memory registration
    record_memory_event(
        db=db,
        asset_id=asset.id,
        event_type="ASSET_COMMISSIONED",
        severity="Info",
        summary=f"Asset {asset.asset_code} ({asset.name}) registered in Ward {asset.ward}.",
        details={"category": asset.category, "lat": asset.latitude, "lon": asset.longitude},
        actor="Registry Officer",
    )

    return asset


@router.get("/{asset_id}", response_model=AssetDetailResponse, summary="Get asset detail and City Memory")
def get_asset(asset_id: int, db: Session = Depends(get_db)) -> AssetDetailResponse:
    """Retrieve full asset profile with issues count, repairs, and chronological City Memory events."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    issues = db.query(Issue).filter(Issue.asset_id == asset_id).all()
    active_issues = [i for i in issues if i.status not in ["Repaired", "Resolved"]]
    recurring_issues = [i for i in issues if i.is_recurrence or i.recurrence_count > 0]
    repairs = db.query(Repair).filter(Repair.asset_id == asset_id).all()
    total_repair_cost = sum(r.cost for r in repairs)

    events = (
        db.query(CityMemoryEvent)
        .filter(CityMemoryEvent.asset_id == asset_id)
        .order_by(CityMemoryEvent.timestamp.desc())
        .all()
    )

    return AssetDetailResponse(
        id=asset.id,
        asset_code=asset.asset_code,
        name=asset.name,
        category=asset.category,
        asset_type=asset.asset_type,
        ward=asset.ward,
        zone=asset.zone,
        status=asset.status,
        latitude=asset.latitude,
        longitude=asset.longitude,
        address=asset.address,
        health_score=asset.health_score,
        risk_score=asset.risk_score,
        risk_level=asset.risk_level,
        risk_factors=asset.risk_factors or [],
        install_year=asset.install_year,
        last_inspected_at=asset.last_inspected_at,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        issues_count=len(issues),
        active_issues_count=len(active_issues),
        recurring_issues_count=len(recurring_issues),
        repairs_count=len(repairs),
        total_repair_cost=total_repair_cost,
        memory_events=[CityMemoryEventResponse.model_validate(e) for e in events],
    )


@router.get("/{asset_id}/timeline", response_model=list[CityMemoryEventResponse], summary="Get asset memory timeline")
def get_asset_timeline(asset_id: int, db: Session = Depends(get_db)) -> list[CityMemoryEventResponse]:
    """Get the full chronological City Memory ledger for an asset."""
    events = (
        db.query(CityMemoryEvent)
        .filter(CityMemoryEvent.asset_id == asset_id)
        .order_by(CityMemoryEvent.timestamp.desc())
        .all()
    )
    return events
