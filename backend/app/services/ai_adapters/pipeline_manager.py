"""NAGARPAALAN AI — Unified Vision Pipeline Manager.

STRICT DATA INTEGRITY & TRANSPARENCY:
- Verifiable GPS provenance only (Manual Input, EXIF, or GPX).
- Zero default coordinate fallbacks or fabricated route displacements.
- Unlocated frames remain strictly null with provenance 'Unlocated'.
- Explicitly labels heuristic computer vision vs pretrained weights.
"""

from __future__ import annotations

import io
import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

from PIL import Image, ImageDraw

from app.schemas.analytics import AIModelInfo
from app.schemas.observation import NormalizedDetection
from app.services.ai_adapters.garbage_adapter import GarbageVisionAdapter
from app.services.ai_adapters.road_damage_adapter import RoadDamageVisionAdapter
from app.services.ai_adapters.streetlight_adapter import StreetlightVisionAdapter


class VisionPipelineManager:
    """Singleton manager orchestrating all AI vision adapters."""

    def __init__(self):
        self.road_adapter = RoadDamageVisionAdapter()
        self.garbage_adapter = GarbageVisionAdapter()
        self.streetlight_adapter = StreetlightVisionAdapter()

        self.uploads_dir = os.path.join(os.getcwd(), "uploads")
        self.annotated_dir = os.path.join(self.uploads_dir, "annotated")
        os.makedirs(self.annotated_dir, exist_ok=True)

    def list_available_models(self) -> list[AIModelInfo]:
        """List registered vision adapters with transparent weights and inference status."""
        return [
            AIModelInfo(
                id="iwatchroad-v2-heuristic",
                name="iWatchRoad Road Defect Adapter (Heuristic Analysis)",
                task="Road Damage",
                architecture="Heuristic Pavement Luminance & Dark Concavity (Weights Standby)",
                source_candidate="https://github.com/smlab-niser/iwatchroad",
                version="2.1.0-heuristic",
                status="Active (Heuristic Engine; Weights Standby)",
                classes_detected=self.road_adapter.get_supported_classes(),
                license="MIT / Academic Open Source",
            ),
            AIModelInfo(
                id="trashmonkey-v1-heuristic",
                name="TrashMonkey Waste Boundary Adapter (Heuristic Analysis)",
                task="Garbage & Waste",
                architecture="Heuristic Boundary Segmentation (Weights Standby)",
                source_candidate="https://github.com/tr4m0ryp/TrashMonkey",
                version="1.4.2-heuristic",
                status="Active (Heuristic Engine; Weights Standby)",
                classes_detected=self.garbage_adapter.get_supported_classes(),
                license="Apache 2.0",
            ),
            AIModelInfo(
                id="yolor-streetlights-heuristic",
                name="YOLOR Streetlight Defect Head (Heuristic Analysis)",
                task="Streetlight Infrastructure",
                architecture="Heuristic Scene Luminance Classifier (Weights Standby)",
                source_candidate="https://huggingface.co/cpnlab/YOLOR-Streetlights",
                version="1.2.0-heuristic",
                status="Active (Heuristic Engine; Weights Standby)",
                classes_detected=self.streetlight_adapter.get_supported_classes(),
                license="OpenRAIL / Hugging Face Community",
            ),
        ]

    def extract_exif_gps(self, image_bytes: bytes) -> tuple[float | None, float | None, str]:
        """Extract genuine GPS coordinates from image EXIF metadata if present.

        Never fabricates coordinates. Returns (None, None, 'Unlocated') if absent.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            exif = image.getexif()
            if not exif:
                return None, None, "Unlocated"

            # Check for GPSInfo tag (34853 = 0x8825)
            gps_ifd = None
            if hasattr(exif, "get_ifd"):
                gps_ifd = exif.get_ifd(34853)
            if not gps_ifd:
                gps_ifd = exif.get(34853)

            if not gps_ifd or not isinstance(gps_ifd, dict):
                return None, None, "Unlocated"

            lat_data = gps_ifd.get(2)
            lat_ref = gps_ifd.get(1)
            lon_data = gps_ifd.get(4)
            lon_ref = gps_ifd.get(3)

            if not lat_data or not lon_data:
                return None, None, "Unlocated"

            def _dms_to_dd(dms: Any) -> float:
                d = float(dms[0])
                m = float(dms[1])
                s = float(dms[2])
                return d + (m / 60.0) + (s / 3600.0)

            lat = _dms_to_dd(lat_data)
            if lat_ref == "S":
                lat = -lat

            lon = _dms_to_dd(lon_data)
            if lon_ref == "W":
                lon = -lon

            return round(lat, 6), round(lon, 6), "EXIF"
        except Exception:
            return None, None, "Unlocated"

    def parse_gpx_telemetry(self, gpx_content: str) -> list[tuple[float, float]]:
        """Parse genuine GPX track points from standard XML."""
        pts = []
        try:
            root = ET.fromstring(gpx_content)
            for elem in root.iter():
                if elem.tag.endswith("trkpt"):
                    lat = float(elem.attrib.get("lat", 0))
                    lon = float(elem.attrib.get("lon", 0))
                    if lat != 0 and lon != 0:
                        pts.append((lat, lon))
        except Exception:
            pass
        return pts

    def annotate_and_save(
        self,
        image_bytes: bytes,
        detections: list[NormalizedDetection],
        filename_prefix: str = "detection",
    ) -> tuple[str, str]:
        """Save raw image and draw color-coded bounding boxes on annotated image."""
        unique_id = uuid.uuid4().hex[:10]
        raw_filename = f"{filename_prefix}_{unique_id}_raw.jpg"
        annotated_filename = f"{filename_prefix}_{unique_id}_annotated.jpg"

        raw_path = os.path.join(self.uploads_dir, raw_filename)
        annotated_path = os.path.join(self.annotated_dir, annotated_filename)

        with open(raw_path, "wb") as f:
            f.write(image_bytes)

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(image)

        for det in detections:
            if det.bounding_box:
                bb = det.bounding_box
                box = [(bb.x1, bb.y1), (bb.x2, bb.y2)]

                if not det.is_defect:
                    color = "#22c55e"
                elif det.severity == "High":
                    color = "#ef4444"
                else:
                    color = "#f59e0b"

                draw.rectangle(box, outline=color, width=3)
                label_text = f"{det.category.upper()} {int(det.confidence * 100)}% ({det.inference_engine_type[:9]})"
                draw.rectangle([(bb.x1, max(0, bb.y1 - 22)), (bb.x1 + len(label_text) * 7.5, bb.y1)], fill=color)
                draw.text((bb.x1 + 4, max(2, bb.y1 - 18)), label_text, fill="#ffffff")

        image.save(annotated_path, "JPEG", quality=90)

        raw_url = f"/uploads/{raw_filename}"
        annotated_url = f"/uploads/annotated/{annotated_filename}"
        return raw_url, annotated_url

    def analyze_image(
        self,
        image_bytes: bytes,
        category_hint: str | None = None,
        frame_reference: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        manual_provenance: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[list[NormalizedDetection], str, str]:
        """Analyze image with verifiable GPS integrity."""
        provenance = "Unlocated"

        if latitude is not None and longitude is not None:
            provenance = manual_provenance or "Manual Input"
        else:
            exif_lat, exif_lon, exif_prov = self.extract_exif_gps(image_bytes)
            if exif_lat is not None and exif_lon is not None:
                latitude = exif_lat
                longitude = exif_lon
                provenance = exif_prov

        detections: list[NormalizedDetection] = []
        cat_lower = (category_hint or "").lower()

        if "garbage" in cat_lower or "trash" in cat_lower or "waste" in cat_lower:
            detections = self.garbage_adapter.detect_from_image(
                image_bytes, frame_reference, latitude, longitude, provenance, metadata
            )
        elif "light" in cat_lower or "lamp" in cat_lower or "electric" in cat_lower:
            detections = self.streetlight_adapter.detect_from_image(
                image_bytes, frame_reference, latitude, longitude, provenance, metadata
            )
        else:
            detections = self.road_adapter.detect_from_image(
                image_bytes, frame_reference, latitude, longitude, provenance, metadata
            )

        raw_url, annotated_url = self.annotate_and_save(
            image_bytes=image_bytes,
            detections=detections,
            filename_prefix=category_hint or "vision",
        )

        return detections, raw_url, annotated_url

    def extract_and_analyze_video(
        self,
        video_bytes: bytes,
        filename: str,
        gpx_data: str | None = None,
        manual_latitude: float | None = None,
        manual_longitude: float | None = None,
    ) -> tuple[list[NormalizedDetection], list[str], int]:
        """Extract frames from dashcam video and run defect detection pipeline.

        STRICT GPS INTEGRITY:
        Uses genuine GPX track points if provided.
        Uses manual coordinates if provided.
        Otherwise leaves coordinates as None (Unlocated).
        NO fabricated route displacement.
        """
        import cv2

        video_id = uuid.uuid4().hex[:8]
        temp_video_path = os.path.join(self.uploads_dir, f"dashcam_{video_id}.mp4")

        with open(temp_video_path, "wb") as f:
            f.write(video_bytes)

        gpx_points = self.parse_gpx_telemetry(gpx_data) if gpx_data else []

        cap = cv2.VideoCapture(temp_video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = int(cap.get(cv2.CAP_PROP_FPS) or 25)
        step = max(1, fps)

        sampled_detections: list[NormalizedDetection] = []
        annotated_urls: list[str] = []

        frame_idx = 0
        extracted_count = 0

        while cap.isOpened() and extracted_count < 8:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % step == 0:
                extracted_count += 1
                _, buffer = cv2.imencode(".jpg", frame)
                frame_bytes = buffer.tobytes()

                # Determine verifiable location
                if extracted_count <= len(gpx_points):
                    frame_lat, frame_lon = gpx_points[extracted_count - 1]
                    frame_prov = "GPX"
                elif manual_latitude is not None and manual_longitude is not None:
                    frame_lat, frame_lon = manual_latitude, manual_longitude
                    frame_prov = "Manual Input"
                else:
                    frame_lat, frame_lon = None, None
                    frame_prov = "Unlocated"

                frame_ref = f"{filename}_frame_{extracted_count:03d}.jpg"
                dets = self.road_adapter.detect_from_image(
                    image_bytes=frame_bytes,
                    frame_reference=frame_ref,
                    latitude=frame_lat,
                    longitude=frame_lon,
                    location_provenance=frame_prov,
                )

                if dets:
                    _, ann_url = self.annotate_and_save(
                        image_bytes=frame_bytes,
                        detections=dets,
                        filename_prefix=f"dashcam_f{extracted_count}",
                    )
                    annotated_urls.append(ann_url)
                    sampled_detections.extend(dets)

            frame_idx += 1

        cap.release()
        try:
            os.remove(temp_video_path)
        except Exception:
            pass

        return sampled_detections, annotated_urls, total_frames


pipeline_manager = VisionPipelineManager()
