"""Review elevated permission requests for SecPilot safety."""

from hook_utils import command_matches, extract_command, read_event, respond, safe_exit, setup_logging


LOGGER = setup_logging("permission_request_policy")


DENY_PATTERNS = [
    ("curl_wget_execute", r"\b(curl|wget)\b[^\n]*(\||;|&&)\s*(sh|bash|zsh|python|python3|powershell|pwsh)\b"),
    ("dangerous_network_tool", r"\b(hydra|sqlmap|msfconsole|msfvenom|metasploit|nmap\s+-a|masscan)\b"),
    ("production_database_drop", r"\b(drop\s+database|dropdb)\b[^\n]*(prod|production|main|secpilot)"),
    ("destructive_docker_prune", r"\bdocker\b[^\n]*\bsystem\s+prune\b[^\n]*(--all|-a|--volumes)"),
    ("iptables_flush", r"\biptables\b[^\n]*(\s-f\b|--flush)\b|\bufw\b[^\n]*\breset\b"),
    ("root_recursive_delete", r"\brm\s+-[^\n]*r[^\n]*f[^\n]*(\s+/|\s+/\s|--no-preserve-root)"),
    ("credential_dumping", r"\b(mimikatz|lsass|secretsdump|samdump|hashdump)\b"),
]


def main() -> None:
    event = read_event()
    command = extract_command(event)
    match = command_matches(command, DENY_PATTERNS)
    if match:
        LOGGER.warning("permission_denied", extra={"reason": match})
        respond(
            decision="deny",
            status=f"Denied elevated permission request: {match}.",
            reason=match,
        )
        return
    respond(status="Permission request passed SecPilot policy review.")


safe_exit(LOGGER, main)
