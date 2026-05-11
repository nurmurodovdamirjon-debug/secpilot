from dataclasses import dataclass
from enum import StrEnum
from ipaddress import ip_address, ip_network

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.db.models import Asset
from src.services.audit_log import write_audit_event
from src.services.target_normalization import normalize_target_candidates


class ActionRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    manual_approval_required: bool


class PolicyGate:
    """Fail-closed DB-backed safety gate for authorized defensive actions."""

    def __init__(self, db: Session, fail_closed: bool = True) -> None:
        self.db = db
        self.fail_closed = fail_closed

    def evaluate_target_action(
        self,
        target: str,
        risk: ActionRisk,
        *,
        actor_type: str = "system",
        actor_id: str = "policy_gate",
    ) -> PolicyDecision:
        candidates = normalize_target_candidates(target)
        if not candidates:
            return self._record_decision(
                PolicyDecision(
                    allowed=False,
                    reason="invalid_target",
                    manual_approval_required=False,
                ),
                target=target,
                risk=risk,
                actor_type=actor_type,
                actor_id=actor_id,
            )

        asset = self._find_active_asset(candidates)
        if asset is None:
            return self._record_decision(
                PolicyDecision(
                    allowed=False,
                    reason="target_not_whitelisted",
                    manual_approval_required=False,
                ),
                target=target,
                risk=risk,
                actor_type=actor_type,
                actor_id=actor_id,
            )

        if risk is ActionRisk.HIGH:
            return self._record_decision(
                PolicyDecision(
                    allowed=False,
                    reason="manual_approval_required",
                    manual_approval_required=True,
                ),
                target=target,
                risk=risk,
                actor_type=actor_type,
                actor_id=actor_id,
                asset=asset,
            )

        return self._record_decision(
            PolicyDecision(allowed=True, reason="allowed", manual_approval_required=False),
            target=target,
            risk=risk,
            actor_type=actor_type,
            actor_id=actor_id,
            asset=asset,
        )

    def _find_active_asset(self, candidates: list[tuple[str, str]]) -> Asset | None:
        exact_filters = [
            (Asset.asset_type == asset_type) & (Asset.normalized_value == normalized_value)
            for asset_type, normalized_value in candidates
        ]
        statement = select(Asset).where(Asset.status == "active", or_(*exact_filters))
        exact_asset = self.db.scalars(statement).first()
        if exact_asset is not None:
            return exact_asset

        ip_candidate = next(
            (normalized_value for asset_type, normalized_value in candidates if asset_type == "ip"),
            None,
        )
        if ip_candidate is None:
            return None
        target_ip = ip_address(ip_candidate)
        cidr_assets = self.db.scalars(select(Asset).where(Asset.status == "active", Asset.asset_type == "cidr")).all()
        for asset in cidr_assets:
            if target_ip in ip_network(asset.normalized_value, strict=True):
                return asset
        return None

    def _record_decision(
        self,
        decision: PolicyDecision,
        *,
        target: str,
        risk: ActionRisk,
        actor_type: str,
        actor_id: str,
        asset: Asset | None = None,
    ) -> PolicyDecision:
        write_audit_event(
            self.db,
            actor_type=actor_type,
            actor_id=actor_id,
            action="policy.evaluate_target_action",
            result="allowed" if decision.allowed else "denied",
            object_type="asset" if asset else "target",
            object_id=str(asset.id) if asset else None,
            meta={
                "target": target,
                "risk": risk.value,
                "reason": decision.reason,
                "manual_approval_required": decision.manual_approval_required,
            },
        )
        return decision
