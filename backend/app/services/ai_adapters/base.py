"""NAGARPAALAN AI — Base AI Vision Adapter.

Defines the contract for all civic defect detection engines.
Guarantees normalization into the standard schema defined in Section 5.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.observation import NormalizedDetection


class BaseVisionAdapter(ABC):
    """Abstract base class for all computer vision adapters."""

    def __init__(
        self,
        model_name: str,
        model_version: str,
        task: str,
        inference_engine_type: str = "Heuristic Rule-Based",
        weights_loaded: bool = False,
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.task = task
        self.inference_engine_type = inference_engine_type
        self.weights_loaded = weights_loaded

    @abstractmethod
    def detect_from_image(
        self,
        image_bytes: bytes,
        frame_reference: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        location_provenance: str = "Unlocated",
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedDetection]:
        """Perform inference on image bytes and return normalized detections."""
        pass

    @abstractmethod
    def get_supported_classes(self) -> list[str]:
        """Return list of classes this model can detect."""
        pass
