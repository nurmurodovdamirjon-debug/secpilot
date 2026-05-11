from src.services.policy_gate import ActionRisk, PolicyDecision, PolicyGate


def test_unknown_target_is_denied() -> None:
    gate = PolicyGate(allowed_targets={"example.com"})

    decision = gate.evaluate_target_action("unknown.example", ActionRisk.LOW)

    assert decision == PolicyDecision(
        allowed=False,
        reason="target_not_whitelisted",
        manual_approval_required=False,
    )


def test_whitelisted_low_risk_target_is_allowed() -> None:
    gate = PolicyGate(allowed_targets={"example.com"})

    decision = gate.evaluate_target_action("example.com", ActionRisk.LOW)

    assert decision.allowed is True
    assert decision.reason == "allowed"
    assert decision.manual_approval_required is False


def test_high_risk_action_requires_manual_approval() -> None:
    gate = PolicyGate(allowed_targets={"example.com"})

    decision = gate.evaluate_target_action("example.com", ActionRisk.HIGH)

    assert decision.allowed is False
    assert decision.reason == "manual_approval_required"
    assert decision.manual_approval_required is True
