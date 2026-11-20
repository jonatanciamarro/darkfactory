#!/usr/bin/env python3
"""
session_start.py - Antigravity Lifecycle Hook for Corp-Pipeline Initialization.
Executes on SessionStart event, verifies state.md, and injects orchestrator guidance.
Contract: Reads JSON on stdin, outputs valid protojson on stdout.
"""

import json
import sys
from pathlib import Path


def get_workspace_root() -> Path:
    """Resolve repository workspace root from cwd or script location."""
    current = Path.cwd().resolve()
    # If launched from .agents/
    if current.name == ".agents":
        return current.parent
    # Otherwise check up the directory tree
    for parent in [current] + list(current.parents):
        if (parent / "state.md").exists() or (parent / ".git").exists():
            return parent
    return current


def run_session_start_hook() -> None:
    # Read stdin safely if piped
    try:
        if not sys.stdin.isatty():
            raw_input = sys.stdin.read()
            if raw_input.strip():
                _ = json.loads(raw_input)
    except (json.JSONDecodeError, OSError):
        pass

    root = get_workspace_root()
    state_file = root / "state.md"

    # Extract high-level summary from state.md if present
    state_info = "State file present" if state_file.exists() else "No state.md found"
    if state_file.exists():
        try:
            content = state_file.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                if "Testes (Pytest" in line or "Linter" in line:
                    state_info = "Metrics synced from state.md"
                    break
        except OSError:
            pass

    welcome_lines = [
        "🟢 Corp-Pipeline Master Orchestrator: ACTIVE",
        f"• Framework: corporate-engineer (Python 3.10+ target py311)",
        f"• Living State: {state_info} (read state.md before acting)",
        "• Capability Intelligence: Registries loaded from .agents/orchestration/",
        "• Execution Standard: 6-Phase Corp-Pipeline with Shift-Left TDD & Pre-Flight Gates",
        "• Continuous Improvement: Ideas presented via [CORP-PIPELINE / IMPROVEMENT DETECTED]",
    ]

    src_dir = str(root / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    try:
        from corporate_engineer.git_utils import generate_pr_url, get_current_branch

        branch = get_current_branch(root)
        if branch.startswith(("feat/", "fix/", "chore/", "refactor/")):
            pr_info = generate_pr_url(repo_path=root, branch=branch)
            welcome_lines.append(f"• Pre-filled 1-Click PR URL: {pr_info['url']}")
    except Exception:  # noqa: BLE001
        pass

    welcome_msg = "\n".join(welcome_lines)

    output = {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": welcome_msg
                }
            }
        ]
    }

    # Write pure JSON to stdout
    sys.stdout.write(json.dumps(output, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    run_session_start_hook()
