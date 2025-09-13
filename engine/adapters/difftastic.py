from __future__ import annotations

from ..core.utils import which


def detect_env() -> dict:
    return {"difftastic": bool(which("difftastic"))}

