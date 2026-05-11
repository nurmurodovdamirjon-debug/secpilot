"""add asset normalized value

Revision ID: 202605110002
Revises: 202605110001
Create Date: 2026-05-11 00:02:00
"""

from alembic import op
import sqlalchemy as sa


revision = "202605110002"
down_revision = "202605110001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("normalized_value", sa.String(length=512), nullable=True))
    op.execute("UPDATE assets SET normalized_value = lower(value) WHERE normalized_value IS NULL")
    op.alter_column("assets", "normalized_value", existing_type=sa.String(length=512), nullable=False)
    op.create_index(
        "ix_assets_type_normalized_value",
        "assets",
        ["asset_type", "normalized_value"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_assets_type_normalized_value", table_name="assets")
    op.drop_column("assets", "normalized_value")
