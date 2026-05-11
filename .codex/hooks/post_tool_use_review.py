"""Review repository changes after tool execution."""

from pathlib import Path

from hook_utils import changed_files, file_line_count, repo_root, respond, run_git, safe_exit, setup_logging


LOGGER = setup_logging("post_tool_use_review")


def main() -> None:
    root = repo_root()
    warnings: list[str] = []

    diff_stat = run_git(["diff", "--numstat"], root)
    if diff_stat.returncode == 0:
        changed_lines = 0
        changed_file_count = 0
        for line in diff_stat.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                changed_file_count += 1
                for value in parts[:2]:
                    if value.isdigit():
                        changed_lines += int(value)
        if changed_file_count > 50 or changed_lines > 2500:
            warnings.append(f"Massive rewrite detected: {changed_file_count} files, {changed_lines} changed lines.")

    for name in changed_files(root):
        path = root / name
        if name.startswith("src/") and name.endswith(".py") and path.exists():
            lines = file_line_count(path)
            if lines > 600:
                warnings.append(f"Giant module detected: {name} has {lines} lines.")
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                text = ""
            if "TODO" not in text and "__init__.py" not in name:
                warnings.append(f"No TODO marker found in changed module: {name}.")
            if name.startswith("src/api/") and "from src.db.models import" in text:
                warnings.append(f"Architecture warning: API module imports DB models directly: {name}.")

    if warnings:
        respond(status="SecPilot post-tool review warnings found.", extra={"warnings": warnings})
        return
    respond(status="SecPilot post-tool review passed.")


safe_exit(LOGGER, main)
