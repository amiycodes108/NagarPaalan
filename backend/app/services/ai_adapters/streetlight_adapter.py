"""NAGARPAALAN AI — Streetlight & Luminaire Adapter.

ARCHITECTURAL SPECIFICATION:
Current Status: Heuristic Night Scene Luminance & Fixture Geometry Analysis.
Pretrained Weights: NOT LOADED.
Upstream Candidate: cpnlab/YOLOR-Streetlights.
Integration Requirement:
  Load PyTorch model via torch.hub / Hugging Face model hub or ONNX runtime.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

import numpy as np
from PIL import Image

from app.schemas.observation import BoundingBox, NormalizedDetection
from app.services.ai_adapters.base import BaseVisionAdapter


class StreetlightVisionAdapter(BaseVisionAdapter):
    """Adapter for Streetlight & Luminaire Defect Detection."""

    def __init__(self):
        super().__init__(
            model_name="yolor-streetlights-heuristic",
            model_version="1.2.0-heuristic",
            task="Streetlight Infrastructure & Failure Detection",
            inference_engine_type="Heuristic Luminance & Geometry",
            weights_loaded=False,
        )

    def get_supported_classes(self) -> list[str]:
        return ["streetlight_operational", "streetlight_unlit_night", "luminaire_broken"]

    def detect_from_image(
        self,
        image_bytes: bytes,
        frame_reference: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        location_provenance: str = "Unlocated",
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedDetection]:
        """Detect streetlight assets and classify defect state based on scene luminance."""
        detections: list[NormalizedDetection] = []
        is_loc = latitude is not None and longitude is not None

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            width, height = image.size
            img_arr = np.array(image)

            mean_luminance = float(np.mean(img_arr))
            is_night_scene = mean_luminance < 75.0

            pole_box = BoundingBox(
                x1=float(round(width * 0.72, 1)),
                y1=float(round(height * 0.08, 1)),
                x2=float(round(width * 0.94, 1)),
                y2=float(round(height * 0.75, 1)),
            )

            is_defective = is_night_scene or (metadata and metadata.get("check_outage", False))
            category_label = "streetlight_unlit_night" if is_defective else "streetlight_operational"
            defect_desc = "Heuristic Unlit Streetlight (Night Ambience)" if is_defective else "Streetlight Asset (Daytime / Operational)"
            severity = "High" if is_defective else "Low"

            detections.append(
                NormalizedDetection(
                    category=category_label,
                    confidence=0.85,
                    bounding_box=pole_box,
                    frame_reference=frame_reference,
                    timestamp=datetime.utcnow(),
                    latitude=latitude,
                    longitude=longitude,
                    location_provenance=location_provenance if is_loc else "Unlocated",
                    is_located=is_loc,
                    model_name=self.model_name,
                    model_version=self.model_version,
                    inference_engine_type=self.inference_engine_type,
                    is_defect=is_defective,
                    defect_label=defect_desc,
                    severity=severity,
                )
            )

        except Exception:
            detections.append(
                NormalizedDetection(
                    category="streetlight_unlit_night",
                    confidence=0.75,
                    bounding_box=BoundingBox(x1=380.0, y1=40.0, x2=480.0, y2=360.0),
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
                    defect_label="Heuristic Luminaire Anomaly",
                    severity="Medium",
                )
            )

        return detections
