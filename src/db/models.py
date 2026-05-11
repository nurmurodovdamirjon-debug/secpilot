from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="admin", server_default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))

    assets: Mapped[list["Asset"]] = relationship(back_populates="owner")


class Asset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (Index("ix_assets_owner_value", "owner_id", "value", unique=True),)

    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(512), nullable=False)
    label: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", server_default="active")

    owner: Mapped[User | None] = relationship(back_populates="assets")
    jobs: Mapped[list["Job"]] = relationship(back_populates="asset")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="asset")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="asset")


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_status_created", "status", "created_at"),)

    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("assets.id"))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued", server_default="queued")
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="normal", server_default="normal")
    requested_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)

    asset: Mapped[Asset | None] = relationship(back_populates="jobs")


class Alert(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("assets.id"))
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open", server_default="open")
    detail_jsonb: Mapped[dict | None] = mapped_column(JSONB)

    asset: Mapped[Asset | None] = relationship(back_populates="alerts")


class Incident(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "incidents"
    __table_args__ = (Index("ix_incidents_timeline", "timeline_jsonb", postgresql_using="gin"),)

    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("assets.id"))
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="open", server_default="open")
    summary: Mapped[str | None] = mapped_column(Text)
    source_ip: Mapped[str | None] = mapped_column(String(64))
    timeline_jsonb: Mapped[dict | None] = mapped_column(JSONB)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    asset: Mapped[Asset | None] = relationship(back_populates="incidents")


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_log_created", "created_at"),)

    actor_type: Mapped[str | None] = mapped_column(String(50))
    actor_id: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    object_type: Mapped[str | None] = mapped_column(String(100))
    object_id: Mapped[str | None] = mapped_column(String(255))
    result: Mapped[str | None] = mapped_column(String(100))
    meta_jsonb: Mapped[dict | None] = mapped_column(JSONB)
    prev_hash: Mapped[str | None] = mapped_column(String(128))
    entry_hash: Mapped[str | None] = mapped_column(String(128))
