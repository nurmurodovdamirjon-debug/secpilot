"""Shared helpers for SecPilot Codex hooks."""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


HOOK_DIR = Path(__file__).resolve().parent
LOG_FILE = HOOK_DIR / "hooks.log"


def setup_logging(name: str) -> logging.Logger:
    handlers: list[logging.Handler]
    try:
        HOOK_DIR.mkdir(parents=True, exist_ok=True)
        handlers = [logging.FileHandler(LOG_FILE, encoding="utf-8")]
    except OSError:
        handlers = [logging.StreamHandler(sys.stderr)]
    logging.basicConfig(
        handlers=handlers,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )
    return logging.getLogger(name)


def read_event() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {"payload": data}
    except json.JSONDecodeError:
        return {"raw": raw}


def respond(
    *,
    decision: str = "allow",
    status: str = "ok",
    reason: str | None = None,
    continuation_prompt: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "permissionDecision": decision,
        "statusMessage": status,
    }
    if reason:
        payload["reason"] = reason
    if continuation_prompt:
        payload["continuationPrompt"] = continuation_prompt
        payload["continue"] = True
    if extra:
        payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False))


def repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / "AGENTS.md").exists():
            return candidate
    return current


def run_git(args: list[str], root: Path, timeout: int = 5) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    return str(value)


def extract_command(event: dict[str, Any]) -> str:
    candidates = [
        event.get("command"),
        event.get("cmd"),
        event.get("tool_input", {}).get("command") if isinstance(event.get("tool_input"), dict) else None,
        event.get("tool_input", {}).get("cmd") if isinstance(event.get("tool_input"), dict) else None,
        event.get("parameters", {}).get("command") if isinstance(event.get("parameters"), dict) else None,
        event.get("input", {}).get("command") if isinstance(event.get("input"), dict) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return flatten_text(event)


def extract_prompt(event: dict[str, Any]) -> str:
    for key in ("prompt", "user_prompt", "message", "text", "raw"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return flatten_text(event)


def normalize_command(command: str) -> str:
    collapsed = re.sub(r"\s+", " ", command).strip().lower()
    return collapsed.replace("`", "").replace("\r", "")


def changed_files(root: Path) -> list[str]:
    result = run_git(["diff", "--name-only"], root)
    staged = run_git(["diff", "--cached", "--name-only"], root)
    names = set()
    if result.returncode == 0:
        names.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    if staged.returncode == 0:
        names.update(line.strip() for line in staged.stdout.splitlines() if line.strip())
    return sorted(names)


def file_line_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def command_matches(command: str, patterns: list[tuple[str, str]]) -> str | None:
    normalized = normalize_command(command)
    for label, pattern in patterns:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return label
    return None


def has_safe_defensive_context(text: str) -> bool:
    safe_terms = (
        "defensive",
        "authorized",
        "detection",
        "detect",
        "monitoring",
        "logging",
        "audit",
        "incident response",
        "honeypot",
        "canary",
        "policygate",
        "guardrail",
        "whitelist",
        "blue team",
        "prevention",
        "mitigation",
    )
    normalized = text.lower()
    return any(term in normalized for term in safe_terms)


def safe_exit(logger: logging.Logger, func: Any) -> None:
    try:
        func()
    except Exception as exc:  # Hooks must be deterministic and fail safely.
        logger.exception("hook_failed")
        respond(
            decision="deny",
            status="SecPilot hook failed closed. Inspect .codex/hooks/hooks.log.",
            reason=f"hook_error:{exc.__class__.__name__}",
        )
