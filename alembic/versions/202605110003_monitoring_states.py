"""add monitoring states

Revision ID: 202605110003
Revises: 202605110002
Create Date: 2026-05-11 00:03:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "202605110003"
down_revision = "202605110002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "monitoring_states",
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_check_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(length=50), nullable=True),
        sa.Column("last_detail", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_monitoring_states_asset_id_assets")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_monitoring_states")),
    )
    op.create_index("ix_monitoring_states_asset_id", "monitoring_states", ["asset_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_monitoring_states_asset_id", table_name="monitoring_states")
    op.drop_table("monitoring_states")
