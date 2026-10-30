"""NAGARPAALAN AI — Civic Vision & Dashcam Intelligence Endpoints.

STRICT GPS INTEGRITY:
- Verifiable coordinates only (Manual Input, EXIF, or GPX).
- Unlocated observations remain null in latitude and longitude.
- Transparently distinguishes heuristic CV from pretrained neural nets.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.issue import Issue
from app.models.observation import Observation
from app.schemas.analytics import AIModelInfo
from app.schemas.observation import ObservationResponse, VideoProcessingResponse
from app.services.ai_adapters.pipeline_manager import pipeline_manager
from app.services.city_memory import evaluate_recurrence_and_update_risk, record_memory_event
from app.services.geo_similarity import find_nearest_asset

router = APIRouter(prefix="/vision", tags=["civic-vision"])


@router.get("/models", response_model=list[AIModelInfo], summary="List registered AI models")
def list_ai_models() -> list[AIModelInfo]:
    """Retrieve metadata, licensing, and exact weights status for all vision pipelines."""
    return pipeline_manager.list_available_models()


@router.get("/observations", response_model=list[ObservationResponse], summary="List AI observations")
def list_observations(
    category: str | None = None,
    channel: str | None = None,
    defect_confirmed: bool | None = None,
    located_only: bool | None = None,
    db: Session = Depends(get_db),
) -> list[ObservationResponse]:
    """List historical AI observations with GPS provenance and location status."""
    query = db.query(Observation)
    if category:
        query = query.filter(Observation.category.ilike(f"%{category}%"))
    if channel:
        query = query.filter(Observation.source_channel == channel)
    if defect_confirmed is not None:
        query = query.filter(Observation.defect_confirmed == defect_confirmed)
    if located_only is True:
        query = query.filter(Observation.is_located == True)  # noqa: E712
    elif located_only is False:
        query = query.filter(Observation.is_located == False)  # noqa: E712

    obs_list = query.order_by(Observation.created_at.desc()).limit(100).all()

    results: list[ObservationResponse] = []
    for o in obs_list:
        asset_name = o.asset.name if o.asset else None
        res = ObservationResponse(
            id=o.id,
            observation_code=o.observation_code,
            asset_id=o.asset_id,
            issue_id=o.issue_id,
            source_channel=o.source_channel,
            category=o.category,
            confidence=o.confidence,
            bounding_box=o.bounding_box,
            frame_reference=o.frame_reference,
            timestamp=o.timestamp,
            latitude=o.latitude,
            longitude=o.longitude,
            location_provenance=o.location_provenance,
            is_located=o.is_located,
            model_name=o.model_name,
            model_version=o.model_version,
            inference_engine_type=o.inference_engine_type,
            image_url=o.image_url,
            defect_confirmed=o.defect_confirmed,
            defect_classification=o.defect_classification,
            notes=o.notes,
            created_at=o.created_at,
            asset_name=asset_name,
        )
        results.append(res)

    return results


@router.post("/analyze-image", response_model=list[ObservationResponse], summary="Analyze single image")
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    category_hint: str | None = Form(None),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    source_channel: str = Form("Civic Vision"),
    db: Session = Depends(get_db),
) -> list[ObservationResponse]:
    """Upload photo and execute vision adapter.

    GPS coordinates are stored only if explicitly provided by user or found in EXIF tags.
    Never invents or defaults coordinates.
    """
    image_bytes = await file.read()

    manual_prov = "Manual Input" if (latitude is not None and longitude is not None) else None

    detections, raw_url, annotated_url = pipeline_manager.analyze_image(
        image_bytes=image_bytes,
        category_hint=category_hint,
        frame_reference=file.filename,
        latitude=latitude,
        longitude=longitude,
        manual_provenance=manual_prov,
    )

    created_obs: list[ObservationResponse] = []
    assets = db.query(Asset).all()

    for det in detections:
        det_lat = det.latitude
        det_lon = det.longitude
        is_loc = det_lat is not None and det_lon is not None
        prov = det.location_provenance if is_loc else "Unlocated"

        # Match to nearest physical asset ONLY if genuine coordinates exist
        asset_id = None
        nearest = None
        matched_issue = None

        if is_loc:
            nearest = find_nearest_asset(det_lat, det_lon, assets, max_distance_m=180.0)
            asset_id = nearest[0].id if nearest else None
            if asset_id:
                matched_issue = (
                    db.query(Issue)
                    .filter(Issue.asset_id == asset_id)
                    .filter(Issue.category.ilike(f"%{det.category}%"))
                    .first()
                )

        code = f"OBS-{datetime.utcnow().year}-{uuid.uuid4().hex[:5].upper()}"
        obs = Observation(
            observation_code=code,
            asset_id=asset_id,
            issue_id=matched_issue.id if matched_issue else None,
            source_channel=source_channel,
            category=det.category,
            confidence=det.confidence,
            bounding_box=det.bounding_box.model_dump() if det.bounding_box else None,
            frame_reference=det.frame_reference,
            timestamp=det.timestamp,
            latitude=det_lat,
            longitude=det_lon,
            location_provenance=prov,
            is_located=is_loc,
            model_name=det.model_name,
            model_version=det.model_version,
            inference_engine_type=det.inference_engine_type,
            image_url=annotated_url,
            defect_confirmed=det.is_defect,
            defect_classification=det.defect_label,
            notes=f"Engine: {det.inference_engine_type} | Provenance: {prov}",
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)

        # Trigger City Memory recurrence only if asset was verifiably matched
        if asset_id:
            record_memory_event(
                db=db,
                asset_id=asset_id,
                issue_id=matched_issue.id if matched_issue else None,
                event_type="AI_OBSERVATION",
                severity="Warning" if det.is_defect else "Info",
                summary=f"Vision Engine ({det.model_name}) identified {det.category} (Provenance: {prov}).",
                details={
                    "observation_code": obs.observation_code,
                    "confidence": det.confidence,
                    "engine_type": det.inference_engine_type,
                    "location_provenance": prov,
                },
                actor=det.model_name,
            )

            evaluate_recurrence_and_update_risk(
                db=db,
                asset_id=asset_id,
                issue=matched_issue,
                trigger_channel=f"Vision Adapter ({det.model_name})",
            )

        asset_name = nearest[0].name if nearest else None
        created_obs.append(
            ObservationResponse(
                id=obs.id,
                observation_code=obs.observation_code,
                asset_id=obs.asset_id,
                issue_id=obs.issue_id,
                source_channel=obs.source_channel,
                category=obs.category,
                confidence=obs.confidence,
                bounding_box=obs.bounding_box,
                frame_reference=obs.frame_reference,
                timestamp=obs.timestamp,
                latitude=obs.latitude,
                longitude=obs.longitude,
                location_provenance=obs.location_provenance,
                is_located=obs.is_located,
                model_name=obs.model_name,
                model_version=obs.model_version,
                inference_engine_type=obs.inference_engine_type,
                image_url=obs.image_url,
                defect_confirmed=obs.defect_confirmed,
                defect_classification=obs.defect_classification,
                notes=obs.notes,
                created_at=obs.created_at,
                asset_name=asset_name,
            )
        )

    return created_obs


@router.post("/dashcam-upload", response_model=VideoProcessingResponse, summary="Ingest dashcam stream")
async def dashcam_upload_endpoint(
    video: UploadFile = File(...),
    gpx_telemetry: UploadFile | None = File(None),
    manual_latitude: float | None = Form(None),
    manual_longitude: float | None = Form(None),
    db: Session = Depends(get_db),
) -> VideoProcessingResponse:
    """Ingest dashcam video recording with verifiable GPS telemetry (GPX file or explicit coordinates).

    If no GPS data or GPX is supplied, frames remain strictly unlocated (null coordinates).
    """
    video_bytes = await video.read()

    gpx_str = None
    if gpx_telemetry:
        gpx_bytes = await gpx_telemetry.read()
        gpx_str = gpx_bytes.decode("utf-8", errors="ignore")

    detections, annotated_urls, total_frames = pipeline_manager.extract_and_analyze_video(
        video_bytes=video_bytes,
        filename=video.filename,
        gpx_data=gpx_str,
        manual_latitude=manual_latitude,
        manual_longitude=manual_longitude,
    )

    created_obs: list[ObservationResponse] = []
    recurrence_alerts: list[dict[str, Any]] = []
    matched_asset_ids = set()
    unlocated_count = 0

    assets = db.query(Asset).all()

    for idx, det in enumerate(detections):
        det_lat = det.latitude
        det_lon = det.longitude
        is_loc = det_lat is not None and det_lon is not None

        if not is_loc:
            unlocated_count += 1
            asset_id = None
            nearest = None
            matched_issue = None
            prov = "Unlocated"
        else:
            prov = det.location_provenance
            nearest = find_nearest_asset(det_lat, det_lon, assets, max_distance_m=180.0)
            asset_id = nearest[0].id if nearest else None
            if asset_id:
                matched_asset_ids.add(asset_id)

            matched_issue = None
            if asset_id:
                matched_issue = (
                    db.query(Issue)
                    .filter(Issue.asset_id == asset_id)
                    .filter(Issue.category.ilike(f"%{det.category}%"))
                    .first()
                )

        img_url = annotated_urls[idx] if idx < len(annotated_urls) else None
        code = f"OBS-DASH-{uuid.uuid4().hex[:6].upper()}"

        obs = Observation(
            observation_code=code,
            asset_id=asset_id,
            issue_id=matched_issue.id if matched_issue else None,
            source_channel="Dashcam",
            category=det.category,
            confidence=det.confidence,
            bounding_box=det.bounding_box.model_dump() if det.bounding_box else None,
            frame_reference=det.frame_reference,
            timestamp=det.timestamp,
            latitude=det_lat,
            longitude=det_lon,
            location_provenance=prov,
            is_located=is_loc,
            model_name=det.model_name,
            model_version=det.model_version,
            inference_engine_type=det.inference_engine_type,
            image_url=img_url,
            defect_confirmed=det.is_defect,
            defect_classification=det.defect_label,
            notes=f"Dashcam Frame: {det.frame_reference} | Location: {prov}",
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)

        # Recurrence check ONLY on verifiably matched assets
        if asset_id:
            rec_result = evaluate_recurrence_and_update_risk(
                db=db,
                asset_id=asset_id,
                issue=matched_issue,
                trigger_channel="Dashcam Telemetry AI",
            )
            if rec_result.get("is_recurring"):
                recurrence_alerts.append({
                    "asset_code": rec_result["asset_code"],
                    "asset_name": nearest[0].name,
                    "risk_score": rec_result["risk_score"],
                    "warranty_breach": rec_result["warranty_breach"],
                    "factors": rec_result["risk_factors"],
                })

        created_obs.append(
            ObservationResponse(
                id=obs.id,
                observation_code=obs.observation_code,
                asset_id=obs.asset_id,
                issue_id=obs.issue_id,
                source_channel=obs.source_channel,
                category=obs.category,
                confidence=obs.confidence,
                bounding_box=obs.bounding_box,
                frame_reference=obs.frame_reference,
                timestamp=obs.timestamp,
                latitude=obs.latitude,
                longitude=obs.longitude,
                location_provenance=obs.location_provenance,
                is_located=obs.is_located,
                model_name=obs.model_name,
                model_version=obs.model_version,
                inference_engine_type=obs.inference_engine_type,
                image_url=obs.image_url,
                defect_confirmed=obs.defect_confirmed,
                defect_classification=obs.defect_classification,
                notes=obs.notes,
                created_at=obs.created_at,
                asset_name=nearest[0].name if nearest else None,
            )
        )

    return VideoProcessingResponse(
        video_id=uuid.uuid4().hex[:8],
        filename=video.filename,
        total_frames_extracted=total_frames,
        detections_found=len(created_obs),
        matched_assets_count=len(matched_asset_ids),
        unlocated_detections_count=unlocated_count,
        recurrence_alerts=recurrence_alerts,
        observations=created_obs,
    )
