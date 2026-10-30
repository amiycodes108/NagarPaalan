"""NAGARPAALAN AI — SQLAlchemy declarative base.

All ORM models should inherit from ``Base`` defined here so that
Alembic auto-generation picks them up via ``Base.metadata``.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all NAGARPAALAN ORM models."""

    pass
