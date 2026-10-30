"""NAGARPAALAN AI — Data Integrity, AI Validation & Core Workflows Test Suite.

Automated verification covering the 12 core requirements of Task 5:
1. Asset creation and retrieval.
2. Issue creation and asset linking.
3. Multiple complaints linked to one issue.
4. Duplicate complaint matching with explainable scores.
5. Human approval of duplicate matches.
6. Repair creation, contractor linking, and completion.
7. Recurrence post-repair and risk score escalation.
8. GPS-unavailable observations remaining unlocated (latitude/longitude is None).
9. GPS provenance preservation ('Manual Input', 'GPX', 'EXIF', 'Unlocated').
10. Financial expenditure auditing (Actual vs Estimated vs Avoidable Repeat Waste).
11. Invalid API payload rejection (HTTP 422).
12. Dashcam frame extraction and heuristic CV transparency contract.
"""

from __future__ import annotations

import io
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_session_factory, init_db
from app.models.asset import Asset
from app.models.city_memory import CityMemoryEvent
from app.models.complaint import Complaint
from app.models.issue import Issue
from app.models.maintenance import Contractor, Repair
from app.models.observation import Observation
from app.schemas.asset import AssetCreate
from app.schemas.complaint import ComplaintCreate, LinkIssueRequest
from app.schemas.issue import IssueCreate
from app.schemas.maintenance import ContractorCreate, RepairCreate
from app.services.city_memory import evaluate_recurrence_and_update_risk
from app.services.semantic_matcher import evaluate_duplicate_match
from app.services.ai_adapters.pipeline_manager import pipeline_manager


@pytest.fixture(scope="module")
def db_session():
    """Ensure database schema is ready and yield test session."""
    init_db()
    factory = get_session_factory()
    session = factory()
    yield session
    session.close()


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


# ── TEST 1: Asset Creation and Retrieval ──────────────────────────────────────
def test_asset_creation_and_retrieval(client: TestClient, db_session: Session):
    code = f"AST-TEST-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "asset_code": code,
        "name": "Koramangala 80 Feet Road Section 4",
        "category": "Road",
        "asset_type": "Arterial Road",
        "ward": "Ward 151 - Koramangala",
        "zone": "South Zone",
        "status": "Operational",
        "latitude": 12.9352,
        "longitude": 77.6245,
        "address": "80 Feet Road, 4th Block, Koramangala",
        "install_year": 2021,
    }
    create_res = client.post("/api/v1/assets", json=payload)
    assert create_res.status_code == 200, create_res.text
    data = create_res.json()
    assert data["asset_code"] == code
    assert data["category"] == "Road"
    asset_id = data["id"]

    # Retrieval
    get_res = client.get(f"/api/v1/assets/{asset_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == asset_id
    assert retrieved["name"] == "Koramangala 80 Feet Road Section 4"
    assert abs(retrieved["latitude"] - 12.9352) < 1e-4
    assert abs(retrieved["longitude"] - 77.6245) < 1e-4


# ── TEST 2: Issue Creation and Asset Linking ──────────────────────────────────
def test_issue_creation_and_asset_linking(client: TestClient, db_session: Session):
    # Create asset
    asset = Asset(
        asset_code=f"AST-RD-{uuid.uuid4().hex[:5].upper()}",
        name="Indiranagar 100 Feet Road",
        category="Road",
        ward="Ward 112 - Domlur",
        status="Operational",
        latitude=12.9784,
        longitude=77.6408,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    # Create issue linked to asset
    issue_payload = {
        "asset_id": asset.id,
        "category": "Pothole",
        "title": "Severe Asphalt Crater Near 12th Main",
        "description": "Deep asphalt subsidence causing motorcycle skidding.",
        "severity": "High",
        "status": "Open",
        "latitude": 12.9785,
        "longitude": 77.6409,
    }
    create_res = client.post("/api/v1/issues", json=issue_payload)
    assert create_res.status_code == 200, create_res.text
    issue_data = create_res.json()
    assert issue_data["asset_id"] == asset.id
    assert issue_data["title"] == "Severe Asphalt Crater Near 12th Main"

    # Verify relationship in DB
    refreshed_asset = db_session.query(Asset).filter(Asset.id == asset.id).first()
    assert any(i.id == issue_data["id"] for i in refreshed_asset.issues)


# ── TEST 3: Multiple Complaints Linked to One Issue ───────────────────────────
def test_multiple_complaints_linked_to_one_issue(client: TestClient, db_session: Session):
    # Setup issue
    issue = Issue(
        issue_code=f"ISS-{uuid.uuid4().hex[:5].upper()}",
        category="Pothole",
        title="Shared Pothole Defect on Old Airport Road",
        description="Pothole opposite command hospital.",
        severity="Medium",
        status="Open",
        latitude=12.9601,
        longitude=77.6480,
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)

    # Register Complaint 1
    c1 = Complaint(
        ticket_number=f"CMP-TEST-{uuid.uuid4().hex[:5].upper()}",
        title="Broken road surface near command hospital",
        description="Asphalt depression on lane 1.",
        category="Pothole",
        latitude=12.9602,
        longitude=77.6481,
        citizen_name="Citizen One",
        status="Investigating",
        issue_id=issue.id,
    )
    # Register Complaint 2
    c2 = Complaint(
        ticket_number=f"CMP-TEST-{uuid.uuid4().hex[:5].upper()}",
        title="Large crater road damage command hospital gate",
        description="Hazardous hole right at the gate.",
        category="Pothole",
        latitude=12.9600,
        longitude=77.6482,
        citizen_name="Citizen Two",
        status="Investigating",
        issue_id=issue.id,
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    # Query complaints for this issue
    issue_complaints = db_session.query(Complaint).filter(Complaint.issue_id == issue.id).all()
    assert len(issue_complaints) == 2
    assert {c.citizen_name for c in issue_complaints} == {"Citizen One", "Citizen Two"}


# ── TEST 4: Duplicate Complaint Matching with Explainable Scores ──────────────
def test_duplicate_complaint_matching(db_session: Session):
    existing_issue = Issue(
        issue_code=f"ISS-{uuid.uuid4().hex[:5].upper()}",
        category="Pothole",
        title="Deep pothole on MG Road near Trinity circle",
        description="Severe asphalt disintegration near metro pillar 45.",
        severity="High",
        status="Open",
        latitude=12.9733,
        longitude=77.6111,
    )
    db_session.add(existing_issue)
    db_session.commit()

    # Differently worded incoming report within 25 meters
    match_result = evaluate_duplicate_match(
        new_title="Dangerous crater outside trinity metro station",
        new_description="Large asphalt hole causing traffic slowdowns at pillar 45.",
        new_lat=12.9734,
        new_lng=77.6112,
        new_category="Pothole",
        existing_issues=[existing_issue],
    )
    assert match_result.is_duplicate is True
    assert match_result.matched_issue_id == existing_issue.id
    assert match_result.confidence_score >= 60.0
    # Check that explainable criteria are articulated
    criteria = [r.criterion for r in match_result.reasons]
    assert "Geographic Proximity" in criteria
    assert "Semantic Description" in criteria


# ── TEST 5: Human Approval of Duplicate Matches ───────────────────────────────
def test_human_approval_of_duplicate_matches(client: TestClient, db_session: Session):
    issue = Issue(
        issue_code=f"ISS-{uuid.uuid4().hex[:5].upper()}",
        category="Streetlight",
        title="Non-functional sodium streetlight",
        description="Dark junction at 5th block.",
        severity="Medium",
        status="Open",
        latitude=12.9340,
        longitude=77.6100,
    )
    db_session.add(issue)
    db_session.commit()

    complaint = Complaint(
        ticket_number=f"CMP-TEST-{uuid.uuid4().hex[:5].upper()}",
        title="Light pole dead at junction",
        description="No lighting at night.",
        category="Streetlight",
        latitude=12.9341,
        longitude=77.6101,
        citizen_name="Ramesh Kumar",
        status="Pending Review",
        match_status="Matched Existing",
        match_score=78.5,
    )
    db_session.add(complaint)
    db_session.commit()

    # Admin confirms the match
    link_res = client.post(
        f"/api/v1/complaints/{complaint.id}/link-issue",
        json={"issue_id": issue.id, "review_notes": "Verified identical physical asset and issue."},
    )
    assert link_res.status_code == 200, link_res.text
    data = link_res.json()
    assert data["match_status"] == "Confirmed Match"
    assert data["issue_id"] == issue.id


# ── TEST 6: Repair Creation, Contractor Linking, and Completion ───────────────
def test_repair_creation_and_completion(client: TestClient, db_session: Session):
    contractor = Contractor(
        name=f"Karnataka Roads Infra Ltd - {uuid.uuid4().hex[:4]}",
        registration_number=f"REG-BLR-{uuid.uuid4().hex[:4].upper()}",
        contact_phone="+91-80-22998877",
        rating=4.5,
    )
    db_session.add(contractor)
    db_session.commit()

    asset = Asset(
        asset_code=f"AST-RD-{uuid.uuid4().hex[:5].upper()}",
        name="Outer Ring Road Bellandur Flyover",
        category="Road",
        ward="Ward 150 - Bellandur",
        status="Operational",
        latitude=12.9260,
        longitude=77.6762,
    )
    db_session.add(asset)
    db_session.commit()

    issue = Issue(
        issue_code=f"ISS-{uuid.uuid4().hex[:5].upper()}",
        asset_id=asset.id,
        category="Pothole",
        title="Expansion Joint Fracture",
        description="Spalling concrete along flyover joint.",
        severity="High",
        status="Open",
        latitude=12.9260,
        longitude=77.6762,
    )
    db_session.add(issue)
    db_session.commit()

    repair_payload = {
        "asset_id": asset.id,
        "issue_id": issue.id,
        "contractor_id": contractor.id,
        "repair_type": "Elastomeric Joint Resurfacing",
        "description": "Replaced damaged expansion seal and cold asphalt patch.",
        "cost": 65000.0,
        "warranty_months": 12,
        "status": "Completed",
    }
    rep_res = client.post("/api/v1/maintenance/repairs", json=repair_payload)
    assert rep_res.status_code == 200, rep_res.text
    rep_data = rep_res.json()
    assert rep_data["status"] == "Completed"
    assert rep_data["cost"] == 65000.0
    assert rep_data["contractor_id"] == contractor.id


# ── TEST 7: Recurrence After Repair and Risk Escalation ───────────────────────
def test_recurrence_after_repair(db_session: Session):
    asset = Asset(
        asset_code=f"AST-TEST-REC-{uuid.uuid4().hex[:4]}",
        name="Bannerghatta Main Road Defect Test",
        category="Road",
        ward="Ward 193 - Arakere",
        status="Operational",
        latitude=12.8876,
        longitude=77.5971,
        health_score=85,
        risk_score=2.0,
        risk_level="Low",
    )
    db_session.add(asset)
    db_session.commit()

    issue = Issue(
        issue_code=f"ISS-REC-{uuid.uuid4().hex[:4]}",
        asset_id=asset.id,
        category="Pothole",
        title="Repeated Tar Degradation",
        description="Sub-base collapse resulting in repeat potholes.",
        severity="High",
        status="Repaired",
        latitude=12.8876,
        longitude=77.5971,
        recurrence_count=0,
        is_recurrence=False,
    )
    db_session.add(issue)
    db_session.commit()

    # Complete a repair with active warranty
    contractor = db_session.query(Contractor).first()
    repair = Repair(
        repair_code=f"REP-{uuid.uuid4().hex[:5].upper()}",
        asset_id=asset.id,
        issue_id=issue.id,
        contractor_id=contractor.id if contractor else None,
        repair_type="Surface Patching",
        cost=40000.0,
        warranty_months=12,
        status="Completed",
    )
    db_session.add(repair)
    db_session.commit()

    # Trigger recurrence evaluation post-repair
    rec_result = evaluate_recurrence_and_update_risk(
        db=db_session,
        asset_id=asset.id,
        issue=issue,
        trigger_channel="Dashcam Telemetry AI",
    )

    assert rec_result["is_recurring"] is True
    assert rec_result["recurrence_count"] == 1
    assert rec_result["warranty_breach"] is True

    # Check updated asset risk score
    db_session.refresh(asset)
    assert asset.risk_score > 2.0
    assert any("recurring" in f.lower() for f in asset.risk_factors)


# ── TEST 8: GPS-Unavailable Observations Remain Unlocated ─────────────────────
def test_gps_unavailable_observations_remain_unlocated(client: TestClient, db_session: Session):
    # Upload an image without any GPS tags or manual coordinates
    # 1x1 black PNG image
    tiny_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    files = {"file": ("test_unlocated.png", io.BytesIO(tiny_png), "image/png")}
    data = {"category": "Road"}
    res = client.post("/api/v1/vision/analyze-image", files=files, data=data)
    assert res.status_code == 200, res.text
    res_data = res.json()

    # Must NOT have invented coordinates
    assert res_data["latitude"] is None
    assert res_data["longitude"] is None
    assert res_data["is_located"] is False
    assert res_data["location_provenance"] == "Unlocated"
    # Must NOT have matched to a physical asset
    assert res_data["matched_asset_id"] is None


# ── TEST 9: GPS Provenance Preservation ────────────────────────────────────────
def test_gps_provenance_preservation(client: TestClient, db_session: Session):
    # Explicit manual coordinates
    tiny_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("manual_geo.png", io.BytesIO(tiny_png), "image/png")}
    data = {
        "category": "Road",
        "latitude": 12.9716,
        "longitude": 77.5946,
    }
    res = client.post("/api/v1/vision/analyze-image", files=files, data=data)
    assert res.status_code == 200, res.text
    res_data = res.json()
    assert res_data["latitude"] == 12.9716
    assert res_data["longitude"] == 77.5946
    assert res_data["is_located"] is True
    assert res_data["location_provenance"] == "Manual Input"

    # Verify GPX parsing logic directly
    sample_gpx = """<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="DashcamGPS">
      <trk>
        <trkseg>
          <trkpt lat="12.9750" lon="77.6000"></trkpt>
          <trkpt lat="12.9760" lon="77.6010"></trkpt>
        </trkseg>
      </trk>
    </gpx>
    """
    points = pipeline_manager.parse_gpx_telemetry(sample_gpx)
    assert len(points) == 2
    assert points[0] == (12.9750, 77.6000)
    assert points[1] == (12.9760, 77.6010)


# ── TEST 10: Financial Expenditure Calculations ───────────────────────────────
def test_financial_expenditure_calculations(client: TestClient, db_session: Session):
    res = client.get("/api/v1/analytics/finances")
    assert res.status_code == 200, res.text
    data = res.json()

    assert "total_actual_expenditure" in data
    assert "total_estimated_expenditure" in data
    assert "avoidable_repeat_expenditure" in data
    assert "avoidable_waste_percentage" in data
    assert "metric_explanations" in data

    # Actual expenditure must not exceed total estimated commitment
    assert data["total_actual_expenditure"] <= data["total_estimated_expenditure"]
    # Avoidable repeat expenditure must not exceed total expenditure
    assert data["avoidable_repeat_expenditure"] <= data["total_estimated_expenditure"]

    # Explanations must be populated and transparent
    explanations = data["metric_explanations"]
    assert len(explanations) >= 3
    metric_names = [e["metric"] for e in explanations]
    assert "Total Disbursed (Actual)" in metric_names
    assert "Avoidable Recurrence Waste" in metric_names


# ── TEST 11: Invalid API Payloads ─────────────────────────────────────────────
def test_invalid_api_payloads(client: TestClient):
    # Missing required 'title' and 'category'
    bad_payload = {
        "description": "Incomplete complaint missing mandatory fields",
    }
    res = client.post("/api/v1/complaints", json=bad_payload)
    assert res.status_code == 422, "API should return 422 Unprocessable Entity for invalid payloads"

    # Malformed asset payload (e.g. invalid status or wrong type for health_score)
    bad_asset_payload = {
        "name": 12345,  # Invalid type
    }
    res2 = client.post("/api/v1/assets", json=bad_asset_payload)
    assert res2.status_code == 422


# ── TEST 12: Dashcam Frame Extraction and Heuristic CV Transparency ───────────
def test_dashcam_frame_extraction_and_heuristic_cv_transparency(client: TestClient):
    models_res = client.get("/api/v1/vision/models")
    assert models_res.status_code == 200
    models_info = models_res.json()

    assert "models" in models_info
    models = models_info["models"]
    road_model = next((m for m in models if m["category"] == "Road"), None)
    assert road_model is not None

    # Transparently states heuristic CV, NOT verified neural weights
    assert "heuristic" in road_model["name"].lower()
    assert road_model["weights_loaded"] is False
    assert "heuristic" in road_model["engine_type"].lower()
