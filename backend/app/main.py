"""NAGARPAALAN AI — FastAPI application entry-point.

Creates the ASGI application, wires middleware, mounts routers,
and manages the application lifespan (startup / shutdown).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Redis dependency
# ---------------------------------------------------------------------------

_redis_client = None


def get_redis():
    """FastAPI dependency — returns the shared Redis client or mock worker."""
    return _redis_client


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown logic."""
    global _redis_client

    # ── Startup ───────────────────────────────────────────────────────
    setup_logging(settings.LOG_LEVEL)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # Initialize Database Schema
    try:
        init_db()
    except Exception as exc:
        logger.error("Database initialization error: %s", exc)

    # Initialize Redis client lazily / non-blocking
    try:
        import redis
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
    except Exception as exc:
        logger.info("Redis not initialized (%s). Standby mode active.", exc)
        _redis_client = None

    yield

    # ── Shutdown ──────────────────────────────────────────────────────
    logger.info("Shutting down %s …", settings.APP_NAME)
    if _redis_client is not None:
        try:
            _redis_client.close()
        except Exception:
            pass
        _redis_client = None
    logger.info("Shutdown complete.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads / media directory
uploads_dir = os.path.join(os.getcwd(), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount versioned API
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

@app.get("/", tags=["root"], summary="Application identity")
def root() -> dict[str, Any]:
    """Return basic application identity and version."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs",
    }
