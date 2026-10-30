"""NAGARPAALAN AI — API v1 Router Aggregation.

Mounts all core civic and AI intelligence endpoints into a single router.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.assets import router as assets_router
from app.api.v1.endpoints.complaints import router as complaints_router
from app.api.v1.endpoints.demo import router as demo_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.issues import router as issues_router
from app.api.v1.endpoints.maintenance import router as maintenance_router
from app.api.v1.endpoints.vision import router as vision_router

router = APIRouter()

router.include_router(health_router)
router.include_router(assets_router)
router.include_router(issues_router)
router.include_router(complaints_router)
router.include_router(vision_router)
router.include_router(maintenance_router)
router.include_router(analytics_router)
router.include_router(demo_router)
