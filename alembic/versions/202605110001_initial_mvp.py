"""initial mvp schema

Revision ID: 202605110001
Revises:
Create Date: 2026-05-11 00:01:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "202605110001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), server_default="admin", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)

    op.create_table(
        "assets",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("value", sa.String(length=512), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="active", nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name=op.f("fk_assets_owner_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assets")),
    )
    op.create_index("ix_assets_owner_value", "assets", ["owner_id", "value"], unique=True)

    op.create_table(
        "audit_log",
        sa.Column("actor_type", sa.String(length=50), nullable=True),
        sa.Column("actor_id", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("object_type", sa.String(length=100), nullable=True),
        sa.Column("object_id", sa.String(length=255), nullable=True),
        sa.Column("result", sa.String(length=100), nullable=True),
        sa.Column("meta_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("prev_hash", sa.String(length=128), nullable=True),
        sa.Column("entry_hash", sa.String(length=128), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
    )
    op.create_index("ix_audit_log_created", "audit_log", ["created_at"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="open", nullable=False),
        sa.Column("detail_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_alerts_asset_id_assets")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_alerts")),
    )

    op.create_table(
        "incidents",
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("state", sa.String(length=50), server_default="open", nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_ip", sa.String(length=64), nullable=True),
        sa.Column("timeline_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_incidents_asset_id_assets")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_incidents")),
    )
    op.create_index("ix_incidents_timeline", "incidents", ["timeline_jsonb"], unique=False, postgresql_using="gin")

    op.create_table(
        "jobs",
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="queued", nullable=False),
        sa.Column("priority", sa.String(length=50), server_default="normal", nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_jobs_asset_id_assets")),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], name=op.f("fk_jobs_requested_by_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
    )
    op.create_index("ix_jobs_status_created", "jobs", ["status", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_jobs_status_created", table_name="jobs")
    op.drop_table("jobs")
    op.drop_index("ix_incidents_timeline", table_name="incidents", postgresql_using="gin")
    op.drop_table("incidents")
    op.drop_table("alerts")
    op.drop_index("ix_audit_log_created", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_index("ix_assets_owner_value", table_name="assets")
    op.drop_table("assets")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")
