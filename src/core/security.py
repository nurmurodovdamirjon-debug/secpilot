from enum import StrEnum


class SafetyMode(StrEnum):
    DEFENSIVE_ONLY = "defensive_only"


FORBIDDEN_CAPABILITIES = frozenset(
    {
        "malware",
        "phishing",
        "exploit_delivery",
        "credential_theft",
        "hack_back",
        "unauthorized_scanning",
        "account_takeover",
    }
)
