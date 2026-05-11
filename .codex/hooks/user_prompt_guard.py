"""Block harmful cybersecurity prompts while allowing defensive work."""

from hook_utils import extract_prompt, has_safe_defensive_context, read_event, respond, safe_exit, setup_logging


LOGGER = setup_logging("user_prompt_guard")


HARMFUL_TERMS = (
    "malware",
    "phishing",
    "exploit",
    "credential theft",
    "steal credentials",
    "hack-back",
    "hack back",
    "account takeover",
    "bypass",
    "ransomware",
    "persistence",
    "evasion",
    "keylogger",
    "reverse shell",
)


ACTION_TERMS = (
    "create",
    "write",
    "build",
    "generate",
    "make",
    "deploy",
    "run",
    "execute",
    "payload",
    "kit",
)


def main() -> None:
    event = read_event()
    prompt = extract_prompt(event)
    normalized = prompt.lower()

    harmful = any(term in normalized for term in HARMFUL_TERMS)
    action = any(term in normalized for term in ACTION_TERMS)
    defensive = has_safe_defensive_context(normalized)

    if harmful and (action or not defensive):
        LOGGER.warning("prompt_denied")
        respond(
            decision="deny",
            status="Denied: prompt conflicts with SecPilot defensive-only cybersecurity policy.",
            reason="harmful_cybersecurity_request",
        )
        return

    respond(status="Prompt passed SecPilot defensive cybersecurity guard.")


safe_exit(LOGGER, main)
