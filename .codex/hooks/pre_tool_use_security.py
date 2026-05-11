"""Block dangerous shell commands before tool execution."""

from hook_utils import command_matches, extract_command, read_event, respond, safe_exit, setup_logging


LOGGER = setup_logging("pre_tool_use_security")


DANGEROUS_PATTERNS = [
    ("root_recursive_delete", r"\brm\s+-[^\n]*r[^\n]*f[^\n]*(\s+/|\s+/\s|--no-preserve-root)"),
    ("world_writable_recursive", r"\bchmod\s+777\s+-r\b|\bchmod\s+-r\s+777\b"),
    ("curl_pipe_shell", r"\b(curl|wget)\b[^\n|;]*(\||>)\s*(sh|bash|zsh|powershell|pwsh)\b"),
    ("netcat_reverse_shell", r"\b(nc|netcat|ncat)\b[^\n]*(\s-e\s|\s-c\s|/bin/sh|/bin/bash|powershell)"),
    ("exploit_download", r"\b(curl|wget)\b[^\n]*(exploit-db|exploit|cve-[0-9]{4}|payload)"),
    ("metasploit", r"\b(msfconsole|msfvenom|metasploit)\b"),
    ("ransomware_keywords", r"\b(ransomware|encrypt\s+all|mass\s+encrypt|decryptor)\b"),
    ("credential_dumping", r"\b(mimikatz|lsass|secretsdump|samdump|hashdump|credential\s+dump)\b"),
    ("ssh_bruteforce", r"\bssh\b[^\n]*(brute|password-list|wordlist)|\bhydra\b[^\n]*\bssh\b"),
    ("hydra", r"\bhydra\b"),
    ("sqlmap", r"\bsqlmap\b"),
    ("destructive_docker_prune", r"\bdocker\b[^\n]*\bsystem\s+prune\b[^\n]*(--all|-a|--volumes)"),
    ("production_database_drop", r"\b(drop\s+database|dropdb)\b[^\n]*(prod|production|main|secpilot)"),
    ("iptables_flush", r"\biptables\b[^\n]*(\s-f\b|--flush)\b|\bufw\b[^\n]*\breset\b"),
]


def main() -> None:
    event = read_event()
    command = extract_command(event)
    match = command_matches(command, DANGEROUS_PATTERNS)
    if match:
        LOGGER.warning("denied_command", extra={"reason": match})
        respond(
            decision="deny",
            status=f"Denied by SecPilot security hook: {match}.",
            reason=match,
        )
        return
    respond(status="SecPilot security hook passed.")


safe_exit(LOGGER, main)
