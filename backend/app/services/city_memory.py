"""NAGARPAALAN AI — City Memory Central Engine.

Connects:
- Assets
- Issues
- Complaints
- AI Observations
- Repairs & Work Orders
- Recurrence Detection & Explainable Risk Scoring
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.city_memory import CityMemoryEvent
from app.models.issue import Issue
from app.models.maintenance import Repair


def record_memory_event(
    db: Session,
    asset_id: int,
    event_type: str,
    summary: str,
    details: dict[str, Any] | None = None,
    issue_id: int | None = None,
    severity: str = "Info",
    actor: str = "System",
) -> CityMemoryEvent:
    """Record an immutable chronological event in City Memory."""
    event = CityMemoryEvent(
        asset_id=asset_id,
        issue_id=issue_id,
        event_type=event_type,
        summary=summary,
        details=details or {},
        severity=severity,
        actor=actor,
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def evaluate_recurrence_and_update_risk(
    db: Session,
    asset_id: int,
    issue: Issue | None = None,
    trigger_channel: str = "AI Dashcam",
) -> dict[str, Any]:
    """Check if an issue has recurred post-repair and recalculate explainable risk for the asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return {"status": "asset_not_found"}

    is_recurring = False
    warranty_breach = False

    # Check recent repairs on this asset/issue
    if issue:
        recent_repairs = (
            db.query(Repair)
            .filter(Repair.asset_id == asset_id)
            .filter(Repair.status.in_(["Completed", "Under Warranty"]))
            .order_by(Repair.completed_at.desc())
            .all()
        )

        for rep in recent_repairs:
            # If issue was previously marked repaired or repair completed within warranty period
            if issue.status in ["Repaired", "Under Repair"] or rep.issue_id == issue.id:
                is_recurring = True
                issue.recurrence_count += 1
                issue.is_recurrence = True
                issue.status = "Recurring"
                issue.recurrence_notes = (
                    f"Recurrence detected via {trigger_channel} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}. "
                    f"Prior repair: {rep.work_order_no} ({rep.repair_type})."
                )

                # Check warranty breach
                if rep.completed_at:
                    days_since_repair = (datetime.utcnow() - rep.completed_at).days
                    warranty_days = rep.warranty_months * 30
                    if days_since_repair <= warranty_days:
                        rep.recurred_during_warranty = True
                        warranty_breach = True
                        record_memory_event(
                            db=db,
                            asset_id=asset_id,
                            issue_id=issue.id,
                            event_type="WARRANTY_BREACH",
                            severity="Critical",
                            summary=f"Defect recurred {days_since_repair} days after repair under Work Order {rep.work_order_no} (Warranty: {rep.warranty_months} mos).",
                            details={
                                "work_order_no": rep.work_order_no,
                                "contractor_id": rep.contractor_id,
                                "repair_type": rep.repair_type,
                                "days_elapsed": days_since_repair,
                            },
                            actor=trigger_channel,
                        )

                record_memory_event(
                    db=db,
                    asset_id=asset_id,
                    issue_id=issue.id,
                    event_type="RECURRENCE_DETECTED",
                    severity="Critical",
                    summary=f"Defect '{issue.title}' recurred at Asset {asset.asset_code} (Cycle #{issue.recurrence_count}).",
                    details={
                        "issue_code": issue.issue_code,
                        "recurrence_count": issue.recurrence_count,
                        "detected_via": trigger_channel,
                    },
                    actor=trigger_channel,
                )
                break

    # Recalculate Composite Asset Risk & Health Score
    all_issues = db.query(Issue).filter(Issue.asset_id == asset_id).all()
    active_issues = [i for i in all_issues if i.status in ["Open", "In Review", "Assigned", "Under Repair", "Recurring"]]
    recurring_issues = [i for i in all_issues if i.is_recurrence or i.recurrence_count > 0]
    total_recurrences = sum(i.recurrence_count for i in all_issues)

    # Risk scoring formula (0.0 to 10.0 scale)
    base_risk = 1.0
    active_penalty = len(active_issues) * 0.8
    recurrence_penalty = total_recurrences * 2.2
    warranty_penalty = 2.0 if warranty_breach else 0.0

    raw_risk = base_risk + active_penalty + recurrence_penalty + warranty_penalty
    composite_risk = round(min(10.0, max(0.5, raw_risk)), 1)

    # Health score: 100 - (risk * 8.5)
    composite_health = max(15, min(100, int(100 - (composite_risk * 8.5))))

    risk_factors = []
    if total_recurrences > 0:
        risk_factors.append(f"{total_recurrences} recurring defect cycles recorded in City Memory")
    if warranty_breach:
        risk_factors.append("Contractor warranty failure (premature surface degradation)")
    if len(active_issues) > 1:
        risk_factors.append(f"{len(active_issues)} concurrent unresolved physical defects")
    if composite_risk >= 7.0:
        risk_factors.append("Monsoon failure probability elevated (>75% risk of structural cave-in)")
    if not risk_factors:
        risk_factors.append("Standard operational wear; no chronic failure cycles")

    risk_level = "Critical" if composite_risk >= 7.5 else ("High" if composite_risk >= 5.0 else ("Medium" if composite_risk >= 3.0 else "Low"))
    asset_status = "Critical" if composite_risk >= 7.5 else ("Degraded" if composite_risk >= 4.0 else "Operational")

    asset.risk_score = composite_risk
    asset.health_score = composite_health
    asset.risk_level = risk_level
    asset.risk_factors = risk_factors
    asset.status = asset_status

    if composite_risk >= 7.0:
        record_memory_event(
            db=db,
            asset_id=asset_id,
            event_type="RISK_ESCALATION",
            severity="Critical",
            summary=f"Asset risk score escalated to {composite_risk}/10 ({risk_level}). Preventive overhaul recommended.",
            details={
                "risk_score": composite_risk,
                "health_score": composite_health,
                "factors": risk_factors,
            },
            actor="City Memory Intelligence",
        )

    db.commit()
    db.refresh(asset)

    return {
        "asset_code": asset.asset_code,
        "is_recurring": is_recurring,
        "warranty_breach": warranty_breach,
        "risk_score": composite_risk,
        "health_score": composite_health,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
    }
