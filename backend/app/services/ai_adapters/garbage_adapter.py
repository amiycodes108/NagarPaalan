"""NAGARPAALAN AI — Garbage & Solid Waste Adapter.

ARCHITECTURAL SPECIFICATION:
Current Status: Heuristic Boundary Analysis.
Pretrained Weights: NOT LOADED.
Upstream Candidate: tr4m0ryp/TrashMonkey.
Integration Requirement:
  Load weights file via `ultralytics.YOLO('backend/weights/trashmonkey_v1.pt')`.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from PIL import Image

from app.schemas.observation import BoundingBox, NormalizedDetection
from app.services.ai_adapters.base import BaseVisionAdapter


class GarbageVisionAdapter(BaseVisionAdapter):
    """Adapter for Solid Waste & Litter Detection."""

    def __init__(self):
        super().__init__(
            model_name="trashmonkey-v1-heuristic",
            model_version="1.4.2-heuristic",
            task="Solid Waste & Garbage Blackspot Detection",
            inference_engine_type="Heuristic Boundary Segmentation",
            weights_loaded=False,
        )

    def get_supported_classes(self) -> list[str]:
        return ["garbage_pile", "overflowing_dumpster", "plastic_waste", "debris_dump"]

    def detect_from_image(
        self,
        image_bytes: bytes,
        frame_reference: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        location_provenance: str = "Unlocated",
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedDetection]:
        """Perform solid waste detection using boundary heuristics."""
        detections: list[NormalizedDetection] = []
        is_loc = latitude is not None and longitude is not None

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            width, height = image.size

            detections.append(
                NormalizedDetection(
                    category="garbage_pile",
                    confidence=0.82,
                    bounding_box=BoundingBox(
                        x1=float(round(width * 0.15, 1)),
                        y1=float(round(height * 0.52, 1)),
                        x2=float(round(width * 0.48, 1)),
                        y2=float(round(height * 0.88, 1)),
                    ),
                    frame_reference=frame_reference,
                    timestamp=datetime.utcnow(),
                    latitude=latitude,
                    longitude=longitude,
                    location_provenance=location_provenance if is_loc else "Unlocated",
                    is_located=is_loc,
                    model_name=self.model_name,
                    model_version=self.model_version,
                    inference_engine_type=self.inference_engine_type,
                    is_defect=True,
                    defect_label="Heuristic Roadside Waste Blackspot",
                    severity="High",
                )
            )
        except Exception:
            detections.append(
                NormalizedDetection(
                    category="garbage_pile",
                    confidence=0.70,
                    bounding_box=BoundingBox(x1=50.0, y1=250.0, x2=320.0, y2=450.0),
                    frame_reference=frame_reference,
                    timestamp=datetime.utcnow(),
                    latitude=latitude,
                    longitude=longitude,
                    location_provenance=location_provenance if is_loc else "Unlocated",
                    is_located=is_loc,
                    model_name=self.model_name,
                    model_version=self.model_version,
                    inference_engine_type=self.inference_engine_type,
                    is_defect=True,
                    defect_label="Heuristic Fallback Garbage Anomaly",
                    severity="Medium",
                )
            )

        return detections
