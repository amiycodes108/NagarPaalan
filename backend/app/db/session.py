"""NAGARPAALAN AI — Database engine and session management.

Supports PostgreSQL + PostGIS as primary production architecture with
resilient local fallback so the application functions reliably in any environment.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None
_active_db_type = "unknown"


def get_engine():
    """Lazily initialize and return the SQLAlchemy engine."""
    global _engine, _SessionLocal, _active_db_type

    if _engine is not None:
        return _engine

    primary_url = settings.DATABASE_URL
    try:
        # Attempt PostgreSQL connection
        candidate_engine = create_engine(
            primary_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.DEBUG,
            connect_args={"connect_timeout": 3},
        )
        with candidate_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _engine = candidate_engine
        _active_db_type = "postgresql"
        logger.info("Connected successfully to PostgreSQL + PostGIS database.")
    except Exception as exc:
        logger.warning(
            "PostgreSQL database not accessible (%s). Initializing persistent SQLite fallback engine.",
            exc,
        )
        sqlite_url = "sqlite:///./nagarpaalan.db"
        _engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )
        _active_db_type = "sqlite"

    _SessionLocal = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    return _engine


def get_session_factory():
    """Get the active session factory."""
    if _SessionLocal is None:
        get_engine()
    return _SessionLocal


def get_active_db_type() -> str:
    """Return 'postgresql' or 'sqlite'."""
    if _engine is None:
        get_engine()
    return _active_db_type


def get_db() -> Generator[Session, Any, None]:
    """FastAPI dependency that yields an active database session and ensures cleanup."""
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables and verify connectivity."""
    engine = get_engine()
    try:
        # Import all models to ensure registered in Base.metadata
        from app import models  # noqa: F401

        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(
            "Database initialized successfully with %s engine.",
            get_active_db_type(),
        )
    except Exception:
        logger.exception("Failed to initialize database tables.")
        raise
