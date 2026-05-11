from sqlalchemy.orm import Session

from src.db.models import AuditLog, Asset
from src.services.policy_gate import ActionRisk, PolicyDecision, PolicyGate


def test_unknown_target_is_denied(db_session: Session) -> None:
    gate = PolicyGate(db_session)

    decision = gate.evaluate_target_action("unknown.example", ActionRisk.LOW)

    assert decision == PolicyDecision(
        allowed=False,
        reason="target_not_whitelisted",
        manual_approval_required=False,
    )


def test_whitelisted_low_risk_target_is_allowed(db_session: Session) -> None:
    db_session.add(Asset(asset_type="domain", value="example.com", normalized_value="example.com"))
    db_session.commit()
    gate = PolicyGate(db_session)

    decision = gate.evaluate_target_action("example.com", ActionRisk.LOW)

    assert decision.allowed is True
    assert decision.reason == "allowed"
    assert decision.manual_approval_required is False


def test_whitelisted_cidr_allows_ip_inside_network(db_session: Session) -> None:
    db_session.add(Asset(asset_type="cidr", value="192.0.2.0/24", normalized_value="192.0.2.0/24"))
    db_session.commit()
    gate = PolicyGate(db_session)

    decision = gate.evaluate_target_action("192.0.2.42", ActionRisk.LOW)

    assert decision.allowed is True
    assert decision.reason == "allowed"


def test_high_risk_action_requires_manual_approval(db_session: Session) -> None:
    db_session.add(Asset(asset_type="domain", value="example.com", normalized_value="example.com"))
    db_session.commit()
    gate = PolicyGate(db_session)

    decision = gate.evaluate_target_action("example.com", ActionRisk.HIGH)

    assert decision.allowed is False
    assert decision.reason == "manual_approval_required"
    assert decision.manual_approval_required is True


def test_policy_decisions_are_audit_logged(db_session: Session) -> None:
    db_session.add(Asset(asset_type="domain", value="example.com", normalized_value="example.com"))
    db_session.commit()
    gate = PolicyGate(db_session)

    gate.evaluate_target_action("example.com", ActionRisk.LOW, actor_type="api_key", actor_id="default")

    audit_row = db_session.query(AuditLog).one()
    assert audit_row.action == "policy.evaluate_target_action"
    assert audit_row.result == "allowed"
