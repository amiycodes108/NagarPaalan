"""NAGARPAALAN AI — Issue Management Endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.complaint import Complaint
from app.models.issue import Issue
from app.models.observation import Observation
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate
from app.services.city_memory import evaluate_recurrence_and_update_risk, record_memory_event
from app.services.geo_similarity import find_nearest_asset

router = APIRouter(prefix="/issues", tags=["issues"])


@router.get("", response_model=list[IssueResponse], summary="List physical defects/issues")
def list_issues(
    asset_id: int | None = Query(None, description="Filter by physical asset ID"),
    category: str | None = Query(None, description="Filter by category (Pothole, etc.)"),
    severity: str | None = Query(None, description="Filter by severity (Low, Medium, High, Critical)"),
    status: str | None = Query(None, description="Filter by status (Open, Assigned, Repaired, Recurring)"),
    is_recurrence: bool | None = Query(None, description="Filter only recurring defects"),
    db: Session = Depends(get_db),
) -> list[IssueResponse]:
    """Retrieve all physical issues across city infrastructure."""
    query = db.query(Issue)

    if asset_id:
        query = query.filter(Issue.asset_id == asset_id)
    if category:
        query = query.filter(Issue.category.ilike(f"%{category}%"))
    if severity:
        query = query.filter(Issue.severity == severity)
    if status:
        query = query.filter(Issue.status == status)
    if is_recurrence is not None:
        query = query.filter(Issue.is_recurrence == is_recurrence)

    issues = query.order_by(Issue.is_recurrence.desc(), Issue.created_at.desc()).all()

    results: list[IssueResponse] = []
    for iss in issues:
        asset_name = iss.asset.name if iss.asset else None
        c_count = db.query(Complaint).filter(Complaint.issue_id == iss.id).count()
        o_count = db.query(Observation).filter(Observation.issue_id == iss.id).count()

        resp = IssueResponse(
            id=iss.id,
            issue_code=iss.issue_code,
            asset_id=iss.asset_id,
            category=iss.category,
            title=iss.title,
            description=iss.description,
            severity=iss.severity,
            status=iss.status,
            latitude=iss.latitude,
            longitude=iss.longitude,
            recurrence_count=iss.recurrence_count,
            is_recurrence=iss.is_recurrence,
            recurrence_notes=iss.recurrence_notes,
            first_reported_at=iss.first_reported_at,
            last_reported_at=iss.last_reported_at,
            resolved_at=iss.resolved_at,
            created_at=iss.created_at,
            updated_at=iss.updated_at,
            asset_name=asset_name,
            complaints_count=c_count,
            observations_count=o_count,
        )
        results.append(resp)

    return results


@router.post("", response_model=IssueResponse, summary="Create new physical issue")
def create_issue(payload: IssueCreate, db: Session = Depends(get_db)) -> IssueResponse:
    """Create a new physical issue and link to nearest asset if not specified."""
    asset_id = payload.asset_id
    if not asset_id:
        assets = db.query(Asset).all()
        nearest = find_nearest_asset(payload.latitude, payload.longitude, assets, max_distance_m=150.0)
        if nearest:
            asset_id = nearest[0].id

    code = payload.issue_code or f"ISS-{datetime.utcnow().year}-{uuid.uuid4().hex[:5].upper()}"

    issue = Issue(
        issue_code=code,
        asset_id=asset_id,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        status=payload.status,
        latitude=payload.latitude,
        longitude=payload.longitude,
        recurrence_count=payload.recurrence_count,
        is_recurrence=payload.is_recurrence,
        recurrence_notes=payload.recurrence_notes,
        first_reported_at=datetime.utcnow(),
        last_reported_at=datetime.utcnow(),
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    if asset_id:
        record_memory_event(
            db=db,
            asset_id=asset_id,
            issue_id=issue.id,
            event_type="ISSUE_LOGGED",
            severity="Warning" if issue.severity in ["High", "Critical"] else "Info",
            summary=f"Defect '{issue.title}' ({issue.category}) identified on asset.",
            details={"issue_code": issue.issue_code, "severity": issue.severity},
            actor="Municipal Inspector",
        )
        evaluate_recurrence_and_update_risk(db, asset_id, issue, trigger_channel="Field Inspection")

    asset_name = issue.asset.name if issue.asset else None
    return IssueResponse(
        id=issue.id,
        issue_code=issue.issue_code,
        asset_id=issue.asset_id,
        category=issue.category,
        title=issue.title,
        description=issue.description,
        severity=issue.severity,
        status=issue.status,
        latitude=issue.latitude,
        longitude=issue.longitude,
        recurrence_count=issue.recurrence_count,
        is_recurrence=issue.is_recurrence,
        recurrence_notes=issue.recurrence_notes,
        first_reported_at=issue.first_reported_at,
        last_reported_at=issue.last_reported_at,
        resolved_at=issue.resolved_at,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
        asset_name=asset_name,
        complaints_count=0,
        observations_count=0,
    )


@router.patch("/{issue_id}", response_model=IssueResponse, summary="Update issue status / recurrence")
def update_issue(issue_id: int, payload: IssueUpdate, db: Session = Depends(get_db)) -> IssueResponse:
    """Update issue status (e.g. mark Repaired or Recurring) and update City Memory."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if payload.status is not None:
        issue.status = payload.status
        if payload.status in ["Repaired", "Resolved"]:
            issue.resolved_at = datetime.utcnow()
    if payload.severity is not None:
        issue.severity = payload.severity
    if payload.recurrence_count is not None:
        issue.recurrence_count = payload.recurrence_count
    if payload.is_recurrence is not None:
        issue.is_recurrence = payload.is_recurrence
    if payload.recurrence_notes is not None:
        issue.recurrence_notes = payload.recurrence_notes

    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)

    if issue.asset_id:
        evaluate_recurrence_and_update_risk(db, issue.asset_id, issue, trigger_channel="Status Update")

    asset_name = issue.asset.name if issue.asset else None
    c_count = db.query(Complaint).filter(Complaint.issue_id == issue.id).count()
    o_count = db.query(Observation).filter(Observation.issue_id == issue.id).count()

    return IssueResponse(
        id=issue.id,
        issue_code=issue.issue_code,
        asset_id=issue.asset_id,
        category=issue.category,
        title=issue.title,
        description=issue.description,
        severity=issue.severity,
        status=issue.status,
        latitude=issue.latitude,
        longitude=issue.longitude,
        recurrence_count=issue.recurrence_count,
        is_recurrence=issue.is_recurrence,
        recurrence_notes=issue.recurrence_notes,
        first_reported_at=issue.first_reported_at,
        last_reported_at=issue.last_reported_at,
        resolved_at=issue.resolved_at,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
        asset_name=asset_name,
        complaints_count=c_count,
        observations_count=o_count,
    )
