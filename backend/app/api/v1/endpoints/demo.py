"""NAGARPAALAN AI — Demonstration Scenario Seeder (Section 9 Specification).

Sets up the end-to-end hackathon demo workflow:
1. Citizen reports a pothole.
2. NagarPaalan stores complaint & matches to physical road asset.
3. Differently worded complaint arrives -> AI identifies potential match (explainable match score).
4. Administrator reviews & confirms match.
5. Repair work order is completed.
6. Dashcam detects the pothole again -> Recurrence event recorded in City Memory!
7. Asset risk score escalates to Critical with explainable causal factors.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.city_memory import CityMemoryEvent
from app.models.complaint import Complaint
from app.models.issue import Issue
from app.models.maintenance import Contractor, Inspection, Repair
from app.models.observation import Observation
from app.services.city_memory import evaluate_recurrence_and_update_risk, record_memory_event

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", summary="Seed demonstration scenario dataset")
def seed_demo_data(db: Session = Depends(get_db)) -> dict[str, str]:
    """Seed comprehensive realistic civic data and the demonstration scenario."""
    # Reset existing records
    db.query(CityMemoryEvent).delete()
    db.query(Observation).delete()
    db.query(Complaint).delete()
    db.query(Repair).delete()
    db.query(Inspection).delete()
    db.query(Issue).delete()
    db.query(Asset).delete()
    db.query(Contractor).delete()
    db.commit()

    # 1. Contractors
    c1 = Contractor(
        contractor_code="CON-APEX-01",
        name="Apex InfraWorks Ltd",
        category="Road Works",
        contact_person="Er. Vikram Patel",
        email="projects@apexinfra.in",
        phone="+91 98450 11223",
        performance_rating=3.8,
        warranty_adherence_rate=78.0,
        recurrence_rate=24.5,
        active_contracts=3,
        total_spend=420000.0,
    )
    c2 = Contractor(
        contractor_code="CON-LUMI-02",
        name="LumiTech Urban Lighting",
        category="Electrical & Lighting",
        contact_person="Ananya Rao",
        email="support@lumitech.in",
        phone="+91 98451 44556",
        performance_rating=4.7,
        warranty_adherence_rate=95.0,
        recurrence_rate=4.2,
        active_contracts=2,
        total_spend=185000.0,
    )
    c3 = Contractor(
        contractor_code="CON-ECO-03",
        name="EcoDrain Urban Sanitation",
        category="Drainage Works",
        contact_person="K. Sundaram",
        email="ops@ecodrain.in",
        phone="+91 98452 77889",
        performance_rating=4.1,
        warranty_adherence_rate=88.0,
        recurrence_rate=12.0,
        active_contracts=1,
        total_spend=290000.0,
    )
    db.add_all([c1, c2, c3])
    db.commit()

    # 2. Physical Infrastructure Assets
    a1 = Asset(
        asset_code="AST-RD-MG-101",
        name="Mahatma Gandhi Road - Section B (Trinity to Mayo Hall)",
        category="Road",
        asset_type="Bituminous Arterial Road",
        ward="Ward 14 - Central Business District",
        zone="Central Zone",
        status="Degraded",
        latitude=12.9733,
        longitude=77.6111,
        address="MG Road, near Trinity Circle",
        health_score=48,
        risk_score=6.8,
        risk_level="High",
        risk_factors=[
            "2 chronic pothole recurrence cycles within 6 months",
            "Contractor warranty breach on Work Order WO-2026-440",
            "High heavy bus transit axle-load corridor",
        ],
        install_year=2021,
        last_inspected_at=datetime.utcnow() - timedelta(days=12),
    )
    a2 = Asset(
        asset_code="AST-SL-BR-204",
        name="Brigade Road Commercial Luminaire Corridor",
        category="Streetlight",
        asset_type="LED Smart High-Mast",
        ward="Ward 14 - Central Business District",
        zone="Central Zone",
        status="Operational",
        latitude=12.9716,
        longitude=77.6074,
        address="Brigade Road Pedestrian Walkway",
        health_score=92,
        risk_score=1.4,
        risk_level="Low",
        risk_factors=["Standard operational life cycle"],
        install_year=2023,
        last_inspected_at=datetime.utcnow() - timedelta(days=5),
    )
    a3 = Asset(
        asset_code="AST-DR-IN-305",
        name="Indiranagar 100ft Road Stormwater Trunk Drain",
        category="Drainage",
        asset_type="RCC Covered Storm Drain",
        ward="Ward 08 - Indiranagar",
        zone="East Zone",
        status="Operational",
        latitude=12.9784,
        longitude=77.6408,
        address="100ft Road, 12th Main Junction",
        health_score=78,
        risk_score=3.2,
        risk_level="Medium",
        risk_factors=["Monsoon silt accumulation risk"],
        install_year=2019,
        last_inspected_at=datetime.utcnow() - timedelta(days=18),
    )
    a4 = Asset(
        asset_code="AST-RD-OR-402",
        name="Outer Ring Road - Bellandur Flyover Ramp",
        category="Road",
        asset_type="Elevated Asphalt Expressway",
        ward="Ward 150 - Bellandur",
        zone="South-East Zone",
        status="Critical",
        latitude=12.9304,
        longitude=77.6784,
        address="ORR, near Ecospace Tech Park",
        health_score=35,
        risk_score=8.5,
        risk_level="Critical",
        risk_factors=[
            "Severe alligator surface cracking across both lanes",
            "Frequent heavy monsoon waterlogging",
            "Multiple unmerged citizen grievances",
        ],
        install_year=2018,
        last_inspected_at=datetime.utcnow() - timedelta(days=2),
    )
    a5 = Asset(
        asset_code="AST-WP-KR-501",
        name="KR Market Civic Solid Waste Transfer Station",
        category="Waste Point",
        asset_type="Secondary Waste Compactor Facility",
        ward="Ward 22 - Chickpet",
        zone="West Zone",
        status="Degraded",
        latitude=12.9634,
        longitude=77.5755,
        address="Near KR Market Flower Complex",
        health_score=52,
        risk_score=5.8,
        risk_level="High",
        risk_factors=["Persistent overflow beyond compactor capacity"],
        install_year=2020,
        last_inspected_at=datetime.utcnow() - timedelta(days=8),
    )
    db.add_all([a1, a2, a3, a4, a5])
    db.commit()

    # 3. Demonstration Scenario Issue on MG Road (Asset 1)
    iss1 = Issue(
        issue_code="ISS-2026-089",
        asset_id=a1.id,
        category="Pothole",
        title="Deep Crater on MG Road outer bus bay lane",
        description="Dangerous 14cm road pothole creating severe vehicle deceleration near Trinity Circle.",
        severity="Critical",
        status="Recurring",
        latitude=12.9735,
        longitude=77.6114,
        recurrence_count=2,
        is_recurrence=True,
        recurrence_notes="Repaired on 2026-09-14 under WO-2026-440 by Apex InfraWorks. Recurred within 45 days during October rains.",
        first_reported_at=datetime.utcnow() - timedelta(days=60),
        last_reported_at=datetime.utcnow() - timedelta(hours=3),
    )
    # Secondary issue on ORR
    iss2 = Issue(
        issue_code="ISS-2026-112",
        asset_id=a4.id,
        category="Surface Crack",
        title="Extensive Alligator Cracking on Flyover Ascent",
        description="Bitumen fatigue fractures spreading over 35 meters.",
        severity="High",
        status="Open",
        latitude=12.9306,
        longitude=77.6787,
        recurrence_count=0,
        is_recurrence=False,
        first_reported_at=datetime.utcnow() - timedelta(days=10),
        last_reported_at=datetime.utcnow() - timedelta(days=2),
    )
    db.add_all([iss1, iss2])
    db.commit()

    # 4. Maintenance / Historical Repair
    rep1 = Repair(
        work_order_no="WO-2026-440",
        asset_id=a1.id,
        issue_id=iss1.id,
        contractor_id=c1.id,
        repair_type="Cold Mix Asphalt Patching",
        materials="VG-30 Bitumen Emulsion + 12mm Graded Aggregate",
        cost=35000.0,
        budget_code="CIVIC-CAPEX-WARD14",
        warranty_months=12,
        status="Completed",
        scheduled_date=datetime.utcnow() - timedelta(days=50),
        completed_at=datetime.utcnow() - timedelta(days=45),
        recurred_during_warranty=True,
        notes="Surface patched under emergency monsoon grant. Premature degradation noted 45 days post-completion.",
    )
    db.add(rep1)
    db.commit()

    # 5. Complaints (The Demonstration Scenario)
    # Complaint 1: The original citizen grievance
    c_orig = Complaint(
        ticket_number="CMP-2026-101",
        issue_id=iss1.id,
        asset_id=a1.id,
        citizen_name="Sanjay Ramanathan",
        citizen_phone="+91 98801 22334",
        channel="Citizen App",
        category="Road Damage",
        title="Huge crater on MG Road outer lane near Trinity",
        description="Massive road crater right in front of Trinity Metro gate 2. Water collected inside, two-wheelers violently swerving.",
        latitude=12.9734,
        longitude=77.6112,
        address_landmark="Opposite Trinity Metro Gate 2, MG Road",
        status="Linked to Issue",
        match_status="Confirmed Match",
        created_at=datetime.utcnow() - timedelta(days=4),
    )

    # Complaint 2: Differently worded report for Demonstration step 4-6
    c_new = Complaint(
        ticket_number="CMP-2026-104",
        asset_id=a1.id,
        citizen_name="Meera Swaminathan",
        citizen_phone="+91 99160 55443",
        channel="WhatsApp Helpline",
        category="Pothole",
        title="Dangerous broken depression near pillar 42 MG road",
        description="Car suspension hit very hard on deep broken road hole close to metro pillar 42. Please fix immediately.",
        latitude=12.9736,
        longitude=77.6115,
        address_landmark="Near Metro Pillar 42, Trinity MG Road",
        status="Submitted",
        match_status="Matched Existing",
        match_score=84.5,
        match_reasons=[
            {"criterion": "Geographic Proximity", "score": 94.0, "weight": 0.35, "explanation": "Coordinates are 18.2m away from reported Issue ISS-2026-089."},
            {"criterion": "Semantic Description", "score": 82.0, "weight": 0.35, "explanation": "High semantic intent match: 'broken hole / depression' matches 'crater / pothole'."},
            {"criterion": "Asset Context", "score": 100.0, "weight": 0.15, "explanation": "Both incidents align to Mahatma Gandhi Road - Section B."},
            {"criterion": "Category Alignment", "score": 100.0, "weight": 0.15, "explanation": "Complaint category 'Pothole' matches issue category 'Pothole'."},
        ],
        created_at=datetime.utcnow() - timedelta(hours=5),
    )
    db.add_all([c_orig, c_new])
    db.commit()

    # 6. AI Observations (Dashcam Ingestion)
    obs1 = Observation(
        observation_code="OBS-2026-042",
        asset_id=a1.id,
        issue_id=iss1.id,
        source_channel="Dashcam",
        category="pothole",
        confidence=0.94,
        bounding_box={"x1": 210, "y1": 340, "x2": 490, "y2": 520},
        frame_reference="dashcam_mg_road_seq04_f12.jpg",
        timestamp=datetime.utcnow() - timedelta(hours=2),
        latitude=12.9735,
        longitude=77.6114,
        model_name="iwatchroad-v2-yolo",
        model_version="2.1.0",
        defect_confirmed=True,
        defect_classification="Severe Road Crater (Recurrence Cycle #2)",
        notes="Automated dashcam detection matched to physical asset AST-RD-MG-101. Recurrence confirmed.",
    )
    db.add(obs1)
    db.commit()

    # 7. City Memory Chronicle
    record_memory_event(
        db=db,
        asset_id=a1.id,
        event_type="ASSET_COMMISSIONED",
        severity="Info",
        summary="Asset AST-RD-MG-101 registered in City Infrastructure Memory.",
        details={"category": "Road", "ward": "Ward 14"},
        actor="Registry Officer",
    )
    record_memory_event(
        db=db,
        asset_id=a1.id,
        issue_id=iss1.id,
        event_type="COMPLAINT_FILED",
        severity="Info",
        summary="Citizen Sanjay filed Complaint #CMP-2026-101: 'Huge crater on MG Road'.",
        details={"channel": "Citizen App", "ticket": "CMP-2026-101"},
        actor="Citizen Sanjay",
    )
    record_memory_event(
        db=db,
        asset_id=a1.id,
        issue_id=iss1.id,
        event_type="REPAIR_COMPLETED",
        severity="Info",
        summary="Repair completed under WO-2026-440 by Apex InfraWorks (₹35,000, 12 mo warranty).",
        details={"work_order_no": "WO-2026-440", "cost": 35000.0},
        actor="Apex InfraWorks Ltd",
    )
    record_memory_event(
        db=db,
        asset_id=a1.id,
        issue_id=iss1.id,
        event_type="WARRANTY_BREACH",
        severity="Critical",
        summary="Defect recurred 45 days after repair under Work Order WO-2026-440 (Warranty: 12 mos).",
        details={"contractor": "Apex InfraWorks Ltd", "warranty_months": 12, "days_elapsed": 45},
        actor="City Memory Auditor",
    )
    record_memory_event(
        db=db,
        asset_id=a1.id,
        issue_id=iss1.id,
        event_type="RECURRENCE_DETECTED",
        severity="Critical",
        summary="Dashcam AI detected pothole recurrence at AST-RD-MG-101 (Cycle #2).",
        details={"model": "iwatchroad-v2-yolo", "confidence": 0.94},
        actor="iWatchRoad AI Engine",
    )
    record_memory_event(
        db=db,
        asset_id=a1.id,
        issue_id=iss1.id,
        event_type="RISK_ESCALATION",
        severity="Critical",
        summary="Asset risk score escalated to 6.8/10 (High Risk). Monitored for monsoon cave-in.",
        details={"risk_score": 6.8, "health_score": 48},
        actor="City Memory Intelligence",
    )

    return {"status": "success", "message": "Demonstration dataset seeded successfully"}


@router.post("/trigger-recurrence", summary="Trigger instant recurrence scenario")
def trigger_recurrence_scenario(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Demonstration accelerator: Simulates a vehicle dashcam driving over MG Road and triggering recurrence live."""
    asset = db.query(Asset).filter(Asset.asset_code == "AST-RD-MG-101").first()
    if not asset:
        seed_demo_data(db)
        asset = db.query(Asset).filter(Asset.asset_code == "AST-RD-MG-101").first()

    issue = db.query(Issue).filter(Issue.asset_id == asset.id).first()

    result = evaluate_recurrence_and_update_risk(
        db=db,
        asset_id=asset.id,
        issue=issue,
        trigger_channel="Dashcam Telemetry AI",
    )

    return {
        "status": "recurrence_triggered",
        "asset": asset.name,
        "asset_code": asset.asset_code,
        "new_risk_score": asset.risk_score,
        "new_health_score": asset.health_score,
        "risk_level": asset.risk_level,
        "risk_factors": asset.risk_factors,
    }
