from __future__ import annotations

from pathlib import Path
from typing import Optional

from .utils import which, run_cmd


def commit_and_tag(path: Path, tag: str, trailers: dict[str, str]) -> None:
    """Create a git commit with trailers and tag it. Best-effort if git present."""

    if not which("git"):
        return
    try:
        run_cmd(["git", "init"], cwd=path)
        run_cmd(["git", "add", "."], cwd=path)
        message = "Auto-Rebase finalize\n\n" + "\n".join(f"{k}: {v}" for k, v in trailers.items())
        run_cmd(["git", "commit", "-m", message], cwd=path)
        run_cmd(["git", "tag", tag], cwd=path)
    except Exception:
        # Best-effort only
        pass

