"""Create City Memory core entities (Assets, Issues, Complaints, Observations, Maintenance, Events).

Revision ID: 002_city_memory_entities
Revises: 001_initial_postgis
Create Date: 2026-10-30 23:30:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_city_memory_entities"
down_revision: Union[str, None] = "001_initial_postgis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Contractors
    op.create_table(
        "contractors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("contractor_code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("contact_person", sa.String(128), nullable=True),
        sa.Column("email", sa.String(128), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("performance_rating", sa.Float(), default=4.0),
        sa.Column("warranty_adherence_rate", sa.Float(), default=90.0),
        sa.Column("recurrence_rate", sa.Float(), default=10.0),
        sa.Column("active_contracts", sa.Integer(), default=1),
        sa.Column("total_spend", sa.Float(), default=0.0),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contractor_code"),
    )
    op.create_index("ix_contractors_code", "contractors", ["contractor_code"])

    # Assets
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("asset_code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("asset_type", sa.String(64), nullable=True),
        sa.Column("ward", sa.String(64), nullable=False),
        sa.Column("zone", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), default="Operational"),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("address", sa.String(255), nullable=True),
        sa.Column("health_score", sa.Integer(), default=90),
        sa.Column("risk_score", sa.Float(), default=1.5),
        sa.Column("risk_level", sa.String(32), default="Low"),
        sa.Column("risk_factors", sa.JSON(), nullable=True),
        sa.Column("install_year", sa.Integer(), nullable=True),
        sa.Column("last_inspected_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_code"),
    )
    op.create_index("ix_assets_code", "assets", ["asset_code"])

    # Issues
    op.create_table(
        "issues",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("issue_code", sa.String(64), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(32), default="Medium"),
        sa.Column("status", sa.String(32), default="Open"),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("recurrence_count", sa.Integer(), default=0),
        sa.Column("is_recurrence", sa.Boolean(), default=False),
        sa.Column("recurrence_notes", sa.Text(), nullable=True),
        sa.Column("first_reported_at", sa.DateTime(), nullable=False),
        sa.Column("last_reported_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("issue_code"),
    )
    op.create_index("ix_issues_code", "issues", ["issue_code"])

    # Complaints
    op.create_table(
        "complaints",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_number", sa.String(64), nullable=False),
        sa.Column("issue_id", sa.Integer(), sa.ForeignKey("issues.id", ondelete="SET NULL"), nullable=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("citizen_name", sa.String(128), default="Citizen Reporter"),
        sa.Column("citizen_phone", sa.String(32), nullable=True),
        sa.Column("citizen_email", sa.String(128), nullable=True),
        sa.Column("channel", sa.String(64), default="Citizen App"),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("address_landmark", sa.String(255), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), default="Submitted"),
        sa.Column("match_status", sa.String(32), default="New"),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("match_reasons", sa.JSON(), nullable=True),
        sa.Column("potential_duplicate_of_id", sa.Integer(), sa.ForeignKey("complaints.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_number"),
    )
    op.create_index("ix_complaints_ticket", "complaints", ["ticket_number"])

    # Observations
    op.create_table(
        "observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("observation_code", sa.String(64), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("issue_id", sa.Integer(), sa.ForeignKey("issues.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_channel", sa.String(64), default="Dashcam"),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("bounding_box", sa.JSON(), nullable=True),
        sa.Column("frame_reference", sa.String(128), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(32), default="1.0.0"),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("defect_confirmed", sa.Boolean(), default=True),
        sa.Column("defect_classification", sa.String(64), nullable=True),
        sa.Column("notes", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("observation_code"),
    )
    op.create_index("ix_observations_code", "observations", ["observation_code"])

    # Repairs
    op.create_table(
        "repairs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("work_order_no", sa.String(64), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issue_id", sa.Integer(), sa.ForeignKey("issues.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contractor_id", sa.Integer(), sa.ForeignKey("contractors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("repair_type", sa.String(128), nullable=False),
        sa.Column("materials", sa.String(255), nullable=True),
        sa.Column("cost", sa.Float(), default=0.0),
        sa.Column("budget_code", sa.String(64), default="CIVIC-CAPEX-2026"),
        sa.Column("status", sa.String(32), default="Scheduled"),
        sa.Column("warranty_months", sa.Integer(), default=12),
        sa.Column("scheduled_date", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("recurred_during_warranty", sa.Boolean(), default=False),
        sa.Column("completion_photo_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("work_order_no"),
    )
    op.create_index("ix_repairs_wo", "repairs", ["work_order_no"])

    # Inspections
    op.create_table(
        "inspections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("inspection_code", sa.String(64), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("inspector_name", sa.String(128), nullable=False),
        sa.Column("inspector_role", sa.String(64), default="Municipal Quality Inspector"),
        sa.Column("finding", sa.String(64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("inspected_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inspection_code"),
    )
    op.create_index("ix_inspections_code", "inspections", ["inspection_code"])

    # City Memory Events
    op.create_table(
        "city_memory_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issue_id", sa.Integer(), sa.ForeignKey("issues.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(32), default="Info"),
        sa.Column("summary", sa.String(255), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("actor", sa.String(128), default="System"),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memory_asset_id", "city_memory_events", ["asset_id"])


def downgrade() -> None:
    op.drop_table("city_memory_events")
    op.drop_table("inspections")
    op.drop_table("repairs")
    op.drop_table("observations")
    op.drop_table("complaints")
    op.drop_table("issues")
    op.drop_table("assets")
    op.drop_table("contractors")
