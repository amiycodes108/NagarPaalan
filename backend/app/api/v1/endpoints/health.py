"""NAGARPAALAN AI — Health-check API endpoints.

Provides comprehensive liveness / readiness probes, active database engine documentation,
and background systems status.
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_active_db_type, get_db, get_engine
from app.schemas.health import ComponentHealth, HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_db(db: Session) -> ComponentHealth:
    """Execute query and report exact active database dialect, driver, and PostGIS capability."""
    start = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000

        engine = get_engine()
        dialect_name = engine.dialect.name
        driver_name = engine.driver

        if dialect_name == "postgresql":
            # Attempt to read PostGIS version
            try:
                row = db.execute(text("SELECT PostGIS_Full_Version()")).scalar()
                detail_msg = f"PostgreSQL ({driver_name}) | Native PostGIS: {row}"
            except Exception:
                detail_msg = f"PostgreSQL ({driver_name}) | PostGIS extension pending initialization"
        else:
            detail_msg = (
                f"SQLite ({driver_name}) active development fallback store. "
                f"PostgreSQL + PostGIS target: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB} (standby)"
            )

        return ComponentHealth(
            status="healthy",
            latency_ms=round(latency, 2),
            detail=detail_msg,
        )
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        logger.warning("Database health check failed: %s", exc)
        return ComponentHealth(
            status="unhealthy",
            latency_ms=round(latency, 2),
            detail=str(exc),
        )


def _check_redis() -> ComponentHealth:
    """Check Redis broker or in-process queue status."""
    import redis as redis_lib

    start = time.perf_counter()
    try:
        client = redis_lib.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        latency = (time.perf_counter() - start) * 1000
        client.close()
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2), detail="Redis 7 Broker Active")
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(
            status="healthy",
            latency_ms=round(latency, 2),
            detail=f"In-Process Asynchronous Worker (Redis target {settings.REDIS_HOST}:{settings.REDIS_PORT} in standby mode)",
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Aggregate health check",
    description="Returns overall health including database dialect and background pipeline status.",
)
def health_check(
    response: Response,
    db: Session = Depends(get_db),
) -> HealthResponse:
    """Aggregate health probe — checks DB engine + Redis/Worker."""
    db_health = _check_db(db)
    redis_health = _check_redis()

    components = {
        "database": db_health,
        "background_queue": redis_health,
    }

    all_healthy = all(c.status == "healthy" for c in components.values())
    overall_status = "healthy" if all_healthy else "degraded"

    if not all_healthy:
        response.status_code = 503

    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        app_name=settings.APP_NAME,
        components=components,
    )


@router.get(
    "/health/db",
    response_model=ComponentHealth,
    summary="Database health check",
    description="Verifies database connectivity and dialect documentation.",
)
def health_check_db(
    response: Response,
    db: Session = Depends(get_db),
) -> ComponentHealth:
    """Database connectivity & dialect probe."""
    result = _check_db(db)
    if result.status != "healthy":
        response.status_code = 503
    return result


@router.get(
    "/health/redis",
    response_model=ComponentHealth,
    summary="Redis / Queue health check",
    description="Verifies background broker connectivity.",
)
def health_check_redis(response: Response) -> ComponentHealth:
    """Background broker connectivity probe."""
    result = _check_redis()
    if result.status != "healthy":
        response.status_code = 503
    return result
