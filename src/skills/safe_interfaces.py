from dataclasses import dataclass

from src.services.policy_gate import ActionRisk


@dataclass(frozen=True)
class DefensiveSkillRequest:
    target: str
    risk: ActionRisk
    dry_run: bool = True


@dataclass(frozen=True)
class DefensiveSkillResult:
    accepted: bool
    message: str
    dry_run: bool
