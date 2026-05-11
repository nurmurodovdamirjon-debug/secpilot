from dataclasses import dataclass

from src.core.security import SafetyMode
from src.services.policy_gate import PolicyDecision


@dataclass(frozen=True)
class DefensiveAdvice:
    summary: str
    recommended_actions: list[str]
    requires_human_approval: bool


class DefensiveAgent:
    """Recommendation-only agent; it never executes security actions."""

    safety_mode = SafetyMode.DEFENSIVE_ONLY

    def advise(self, evidence_summary: str, policy_decision: PolicyDecision) -> DefensiveAdvice:
        if not policy_decision.allowed:
            return DefensiveAdvice(
                summary=f"Action blocked by policy: {policy_decision.reason}",
                recommended_actions=["Review scope and collect additional evidence."],
                requires_human_approval=policy_decision.manual_approval_required,
            )
        return DefensiveAdvice(
            summary=evidence_summary,
            recommended_actions=["Continue monitoring and preserve evidence."],
            requires_human_approval=False,
        )
