from dataclasses import dataclass
from enum import StrEnum


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
    """Fail-closed safety gate for authorized defensive actions."""

    def __init__(self, allowed_targets: set[str], fail_closed: bool = True) -> None:
        self.allowed_targets = {target.lower() for target in allowed_targets}
        self.fail_closed = fail_closed

    def evaluate_target_action(self, target: str, risk: ActionRisk) -> PolicyDecision:
        normalized_target = target.strip().lower()
        if not normalized_target or normalized_target not in self.allowed_targets:
            return PolicyDecision(
                allowed=False,
                reason="target_not_whitelisted",
                manual_approval_required=False,
            )

        if risk is ActionRisk.HIGH:
            return PolicyDecision(
                allowed=False,
                reason="manual_approval_required",
                manual_approval_required=True,
            )

        return PolicyDecision(allowed=True, reason="allowed", manual_approval_required=False)
