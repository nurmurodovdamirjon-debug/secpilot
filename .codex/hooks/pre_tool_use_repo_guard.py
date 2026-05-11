"""Protect repository invariants before tool execution."""

from pathlib import Path

from hook_utils import extract_command, flatten_text, normalize_command, read_event, repo_root, respond, run_git, safe_exit, setup_logging


LOGGER = setup_logging("pre_tool_use_repo_guard")


SECRET_PATTERNS = (
    "BEGIN PRIVATE KEY",
    "ghp_",
    "sk-",
    "xoxb-",
    "BOT_TOKEN=",
    "POSTGRES_PASSWORD=",
    "JWT_SECRET_KEY=",
)


def staged_secret_detected(root: Path) -> bool:
    diff = run_git(["diff", "--cached", "-U0"], root)
    if diff.returncode != 0:
        return False
    return any(pattern.lower() in diff.stdout.lower() for pattern in SECRET_PATTERNS)


def main() -> None:
    event = read_event()
    root = repo_root()
    command = normalize_command(extract_command(event))
    event_text = flatten_text(event).lower()

    if "git add" in command and (".env " in command or command.endswith(".env")) and ".env.example" not in command:
        respond(decision="deny", status="Denied: .env must not be staged or pushed.", reason="env_file_stage")
        return

    if ("git add -a" in command or "git add ." in command) and (root / ".env").exists():
        ignored = run_git(["check-ignore", ".env"], root)
        if ignored.returncode != 0:
            respond(decision="deny", status="Denied: .env exists but is not ignored.", reason="env_not_ignored")
            return

    if "git commit" in command and staged_secret_detected(root):
        respond(decision="deny", status="Denied: staged diff appears to contain secrets.", reason="secret_in_staged_diff")
        return

    if ("git rm" in command or "remove-item" in command or " rm " in f" {command} ") and "docker-compose.yml" in command:
        respond(decision="deny", status="Denied: docker-compose.yml deletion is blocked.", reason="compose_delete")
        return

    warnings: list[str] = []
    if "src/db/models.py" in event_text and "alembic/versions" not in event_text:
        warnings.append("DB model edit detected without migration path in the same tool input.")
    if ("delete" in event_text or "remove-item" in event_text or "git rm" in command) and (
        "agents.md" in event_text or "docs/security" in event_text
    ):
        warnings.append("AGENTS.md or security docs deletion requested; verify this is intentional.")

    if warnings:
        respond(status="SecPilot repo guard warning: " + " ".join(warnings), extra={"warnings": warnings})
        return
    respond(status="SecPilot repo guard passed.")


safe_exit(LOGGER, main)
