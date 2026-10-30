"""NAGARPAALAN AI — Complaint Registration & Duplicate Intelligence Endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.complaint import Complaint
from app.models.issue import Issue
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    CreateIssueFromComplaintRequest,
    DuplicateMatchCandidate,
    LinkIssueRequest,
)
from app.services.city_memory import record_memory_event
from app.services.geo_similarity import find_nearest_asset
from app.services.semantic_matcher import evaluate_duplicate_match

router = APIRouter(prefix="/complaints", tags=["complaints"])


def _find_matches_for_complaint(complaint: Complaint, db: Session) -> list[DuplicateMatchCandidate]:
    """Scan existing issues and complaints within geographic proximity and compute match scores."""
    candidates: list[DuplicateMatchCandidate] = []

    # 1. Compare against existing open or recent issues
    issues = db.query(Issue).all()
    for iss in issues:
        same_asset = (complaint.asset_id is not None) and (iss.asset_id == complaint.asset_id)
        cand = evaluate_duplicate_match(
            new_text=f"{complaint.title} {complaint.description}",
            new_category=complaint.category,
            new_lat=complaint.latitude,
            new_lon=complaint.longitude,
            candidate_id=iss.id,
            candidate_code=iss.issue_code,
            candidate_title=iss.title,
            candidate_desc=iss.description or "",
            candidate_category=iss.category,
            candidate_status=iss.status,
            candidate_lat=iss.latitude,
            candidate_lon=iss.longitude,
            same_asset=same_asset,
            target_type="issue",
        )
        if cand.overall_match_score >= 35.0:
            candidates.append(cand)

    # 2. Compare against existing complaints (excluding self)
    prior_complaints = db.query(Complaint).filter(Complaint.id != complaint.id).all()
    for pc in prior_complaints:
        cand = evaluate_duplicate_match(
            new_text=f"{complaint.title} {complaint.description}",
            new_category=complaint.category,
            new_lat=complaint.latitude,
            new_lon=complaint.longitude,
            candidate_id=pc.id,
            candidate_code=pc.ticket_number,
            candidate_title=pc.title,
            candidate_desc=pc.description,
            candidate_category=pc.category,
            candidate_status=pc.status,
            candidate_lat=pc.latitude,
            candidate_lon=pc.longitude,
            same_asset=False,
            target_type="complaint",
        )
        if cand.overall_match_score >= 45.0:
            candidates.append(cand)

    candidates.sort(key=lambda c: c.overall_match_score, reverse=True)
    return candidates[:5]


@router.get("", response_model=list[ComplaintResponse], summary="List citizen complaints")
def list_complaints(
    status: str | None = Query(None, description="Filter by complaint status"),
    category: str | None = Query(None, description="Filter by category"),
    match_status: str | None = Query(None, description="Filter by duplicate match status"),
    channel: str | None = Query(None, description="Filter by intake channel"),
    db: Session = Depends(get_db),
) -> list[ComplaintResponse]:
    """Retrieve all submitted complaints with duplicate triage status."""
    query = db.query(Complaint)

    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category.ilike(f"%{category}%"))
    if match_status:
        query = query.filter(Complaint.match_status == match_status)
    if channel:
        query = query.filter(Complaint.channel == channel)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    results: list[ComplaintResponse] = []
    for c in complaints:
        resp = ComplaintResponse.model_validate(c)
        results.append(resp)

    return results


@router.post("", response_model=ComplaintResponse, summary="Submit citizen/administrative complaint")
def register_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)) -> ComplaintResponse:
    """Register a new complaint, associate to nearest physical asset, and run duplicate detection."""
    # Find nearest physical infrastructure asset
    assets = db.query(Asset).all()
    nearest = find_nearest_asset(payload.latitude, payload.longitude, assets, max_distance_m=180.0)
    matched_asset_id = nearest[0].id if nearest else None

    ticket = f"CMP-{datetime.utcnow().year}-{uuid.uuid4().hex[:5].upper()}"

    complaint = Complaint(
        ticket_number=ticket,
        asset_id=matched_asset_id,
        citizen_name=payload.citizen_name,
        citizen_phone=payload.citizen_phone,
        citizen_email=payload.citizen_email,
        channel=payload.channel,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address_landmark=payload.address_landmark,
        photo_url=payload.photo_url,
        status="Submitted",
        match_status="New",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Run Explainable Duplicate Evaluation
    matches = _find_matches_for_complaint(complaint, db)
    if matches and matches[0].overall_match_score >= 50.0:
        top_match = matches[0]
        complaint.match_status = "Matched Existing"
        complaint.match_score = top_match.overall_match_score
        complaint.match_reasons = [r.model_dump() for r in top_match.reasons]
        if top_match.target_type == "complaint":
            complaint.potential_duplicate_of_id = top_match.target_id
        db.commit()
        db.refresh(complaint)

    # Record in City Memory if asset matched
    if matched_asset_id:
        record_memory_event(
            db=db,
            asset_id=matched_asset_id,
            event_type="COMPLAINT_FILED",
            severity="Info",
            summary=f"Citizen report #{complaint.ticket_number}: '{complaint.title}'.",
            details={
                "ticket_number": complaint.ticket_number,
                "category": complaint.category,
                "channel": complaint.channel,
                "match_status": complaint.match_status,
                "match_score": complaint.match_score,
            },
            actor=complaint.citizen_name or "Citizen",
        )

    resp = ComplaintResponse.model_validate(complaint)
    resp.matched_candidates = matches
    return resp


@router.get("/{complaint_id}", response_model=ComplaintResponse, summary="Get complaint detail and matches")
def get_complaint(complaint_id: int, db: Session = Depends(get_db)) -> ComplaintResponse:
    """Retrieve complaint with dynamic duplicate matching analysis."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    matches = _find_matches_for_complaint(complaint, db)
    resp = ComplaintResponse.model_validate(complaint)
    resp.matched_candidates = matches
    return resp


@router.post("/{complaint_id}/link-issue", response_model=ComplaintResponse, summary="Admin links complaint to issue")
def link_complaint_to_issue(
    complaint_id: int,
    payload: LinkIssueRequest,
    db: Session = Depends(get_db),
) -> ComplaintResponse:
    """Administrator confirms duplicate match and links complaint to existing issue."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    issue = db.query(Issue).filter(Issue.id == payload.issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Target issue not found")

    complaint.issue_id = issue.id
    complaint.status = "Linked to Issue"
    complaint.match_status = "Confirmed Match"
    db.commit()
    db.refresh(complaint)

    # Record in City Memory
    if issue.asset_id:
        record_memory_event(
            db=db,
            asset_id=issue.asset_id,
            issue_id=issue.id,
            event_type="COMPLAINT_LINKED",
            severity="Info",
            summary=f"Admin confirmed Complaint #{complaint.ticket_number} matches Issue {issue.issue_code}.",
            details={
                "ticket_number": complaint.ticket_number,
                "issue_code": issue.issue_code,
                "notes": payload.review_notes,
            },
            actor="Municipal Admin",
        )

    resp = ComplaintResponse.model_validate(complaint)
    resp.matched_candidates = _find_matches_for_complaint(complaint, db)
    return resp


@router.post("/{complaint_id}/create-issue", response_model=ComplaintResponse, summary="Promote complaint to new issue")
def promote_complaint_to_issue(
    complaint_id: int,
    payload: CreateIssueFromComplaintRequest,
    db: Session = Depends(get_db),
) -> ComplaintResponse:
    """Administrator creates a new distinct physical defect issue from this complaint."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    asset_id = payload.asset_id or complaint.asset_id
    code = f"ISS-{datetime.utcnow().year}-{uuid.uuid4().hex[:5].upper()}"

    issue = Issue(
        issue_code=code,
        asset_id=asset_id,
        category=complaint.category,
        title=payload.title or complaint.title,
        description=complaint.description,
        severity=payload.severity,
        status="Open",
        latitude=complaint.latitude,
        longitude=complaint.longitude,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    complaint.issue_id = issue.id
    complaint.status = "In Progress"
    complaint.match_status = "New Issue Created"
    db.commit()
    db.refresh(complaint)

    if asset_id:
        record_memory_event(
            db=db,
            asset_id=asset_id,
            issue_id=issue.id,
            event_type="ISSUE_PROMOTED",
            severity="Warning",
            summary=f"Complaint #{complaint.ticket_number} promoted to physical issue {issue.issue_code}.",
            details={"issue_code": issue.issue_code, "severity": issue.severity},
            actor="Municipal Admin",
        )

    resp = ComplaintResponse.model_validate(complaint)
    resp.matched_candidates = []
    return resp
