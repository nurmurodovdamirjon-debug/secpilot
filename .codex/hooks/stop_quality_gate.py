"""Final quality gate for SecPilot sessions."""

import json
from pathlib import Path

from hook_utils import changed_files, repo_root, respond, run_git, safe_exit, setup_logging


LOGGER = setup_logging("stop_quality_gate")


def pytest_last_failed(root: Path) -> bool:
    lastfailed = root / ".pytest_cache" / "v" / "cache" / "lastfailed"
    if not lastfailed.exists():
        return False
    try:
        data = json.loads(lastfailed.read_text(encoding="utf-8"))
        return bool(data)
    except (OSError, json.JSONDecodeError):
        return False


def main() -> None:
    root = repo_root()
    issues: list[str] = []

    compile_result = run_git(["ls-files", "src", "tests", "alembic"], root)
    if compile_result.returncode == 0 and compile_result.stdout.strip():
        import subprocess
        import sys

        py_compile = subprocess.run(
            [sys.executable, "-m", "compileall", "-q", "src", "tests", "alembic"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        if py_compile.returncode != 0:
            issues.append("Python syntax or import compilation failed.")

    files = changed_files(root)
    if any(name in files for name in ("src/core/config.py", "requirements.txt", "docker-compose.yml")):
        if ".env.example" not in files and not (root / ".env.example").exists():
            issues.append("Config-affecting change detected but .env.example is missing.")

    if any(name.startswith("src/") or name in ("docker-compose.yml", "Dockerfile") for name in files):
        if "README.md" not in files and not (root / "README.md").exists():
            issues.append("Implementation/deploy change detected but README.md is missing.")

    if pytest_last_failed(root):
        issues.append("Pytest cache reports previously failed tests; rerun and fix before completion.")

    if issues:
        prompt = (
            "Continue the SecPilot task. Resolve these quality-gate issues before final response: "
            + " ".join(issues)
            + " Then rerun relevant validation commands and summarize evidence."
        )
        respond(
            decision="allow",
            status="SecPilot stop quality gate requested continuation.",
            continuation_prompt=prompt,
            extra={"issues": issues},
        )
        return

    respond(status="SecPilot stop quality gate passed.")


safe_exit(LOGGER, main)
