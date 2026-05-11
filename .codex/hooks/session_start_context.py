"""Provide SecPilot context reminders at session start."""

from hook_utils import respond, safe_exit, setup_logging


LOGGER = setup_logging("session_start_context")


def main() -> None:
    message = (
        "SecPilot context: read AGENTS.md before significant work; preserve modular monolith; "
        "review docs/ARCHITECTURE.md and docs/security/SECURITY_POLICY.md when changing architecture or security; "
        "defensive-only cybersecurity; target whitelist, manual approval, reversible defense, audit logging, and secret masking are mandatory."
    )
    respond(status=message, extra={"context": message})


safe_exit(LOGGER, main)
