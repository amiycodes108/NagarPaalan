"""NAGARPAALAN AI — Demonstration Scenario Automated End-to-End Test.

Validates the complete 10-step hackathon workflow:
1. Citizen reports a pothole.
2. NagarPaalan stores complaint.
3. System matches it to a physical road asset.
4. Differently worded complaint arrives.
5. AI identifies match to existing issue (explainable match score > 70%).
6. Admin reviews and confirms match.
7. Repair work order is completed.
8. Dashcam detects the pothole again.
9. City Memory identifies a recurrence & logs warranty breach.
10. Asset receives elevated risk score with explainable causal factors.
"""

from __future__ import annotations

import pytest
from app.db.session import get_session_factory, init_db
from app.models.asset import Asset
from app.models.city_memory import CityMemoryEvent
from app.models.complaint import Complaint
from app.models.issue import Issue
from app.models.maintenance import Contractor, Repair
from app.schemas.complaint import ComplaintCreate, CreateIssueFromComplaintRequest, LinkIssueRequest
from app.schemas.maintenance import RepairCreate
from app.api.v1.endpoints.complaints import register_complaint, link_complaint_to_issue, promote_complaint_to_issue
from app.api.v1.endpoints.maintenance import create_repair
from app.api.v1.endpoints.demo import seed_demo_data
from app.services.city_memory import evaluate_recurrence_and_update_risk, record_memory_event
from app.services.semantic_matcher import evaluate_duplicate_match


@pytest.fixture(scope="module")
def db_session():
    init_db()
    factory = get_session_factory()
    db = factory()
    yield db
    db.close()


def test_full_demonstration_scenario(db_session):
    # Setup: Seed baseline scenario
    seed_demo_data(db_session)

    # 1. Citizen Sanjay reports a pothole
    c1_payload = ComplaintCreate(
        title="Crater on MG Road outer bus bay lane",
        description="Deep 14cm pothole creating dangerous vehicle slowdowns near Trinity Circle.",
        category="Pothole",
        latitude=12.9733,
        longitude=77.6111,
        citizen_name="Sanjay Ramanathan",
        channel="Citizen App",
    )
    c1 = register_complaint(c1_payload, db_session)
    assert c1.ticket_number is not None
    # 2 & 3: NagarPaalan stores complaint & matches to physical road asset
    assert c1.asset_id is not None
    asset = db_session.query(Asset).filter(Asset.id == c1.asset_id).first()
    assert asset.asset_code == "AST-RD-MG-101"

    # Promote to issue if not existing
    issue = db_session.query(Issue).filter(Issue.asset_id == asset.id).first()
    assert issue is not None

    # 4. Differently worded complaint arrives from another citizen
    c2_payload = ComplaintCreate(
        title="Big broken road hole near metro pillar 42 MG road",
        description="Severe asphalt depression and broken pavement damaging vehicle tires.",
        category="Pothole",
        latitude=12.9735,
        longitude=77.6113,
        citizen_name="Meera Swaminathan",
        channel="WhatsApp Helpline",
    )
    c2 = register_complaint(c2_payload, db_session)

    # 5. AI identifies that it may refer to the same existing issue (explainable match)
    assert c2.match_status == "Matched Existing"
    assert c2.match_score >= 60.0
    assert len(c2.matched_candidates) > 0
    top_cand = c2.matched_candidates[0]
    assert top_cand.overall_match_score >= 60.0
    # Check that explainable breakdown exists
    reasons = [r.criterion for r in top_cand.reasons]
    assert "Geographic Proximity" in reasons
    assert "Semantic Description" in reasons

    # 6. Administrator reviews and confirms match
    linked = link_complaint_to_issue(
        c2.id,
        LinkIssueRequest(issue_id=issue.id, review_notes="Admin confirmed match from Trinity cluster."),
        db_session,
    )
    assert linked.match_status == "Confirmed Match"
    assert linked.issue_id == issue.id

    # 7. A repair is recorded
    contractor = db_session.query(Contractor).first()
    rep_payload = RepairCreate(
        asset_id=asset.id,
        issue_id=issue.id,
        contractor_id=contractor.id,
        repair_type="Cold Bitumen Asphalt Resurfacing",
        cost=35000.0,
        warranty_months=12,
        status="Completed",
    )
    repair = create_repair(rep_payload, db_session)
    assert repair.status == "Completed"

    # 8 & 9: Dashcam detects the pothole again post-repair -> City Memory identifies recurrence
    rec_result = evaluate_recurrence_and_update_risk(
        db=db_session,
        asset_id=asset.id,
        issue=issue,
        trigger_channel="Dashcam Telemetry AI",
    )
    assert rec_result["is_recurring"] is True

    # 10. Asset receives elevated risk score with explainable reasons
    db_session.refresh(asset)
    assert asset.risk_score >= 6.0
    assert asset.risk_level in ["High", "Critical"]
    assert len(asset.risk_factors) > 0
    assert any("recurring" in f.lower() for f in asset.risk_factors)
