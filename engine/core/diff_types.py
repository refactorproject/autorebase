from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol, TypedDict, Optional, Any


class PatchUnit(TypedDict, total=False):
    """A unit of change for a single file using git patches.

    - file_path: relative path of the file the patch applies to
    - patch_content: git patch content for this file
    - req_ids: requirement IDs attached via traceability
    - notes: optional note
    """

    file_path: str
    patch_content: str
    req_ids: list[str]
    notes: Optional[str]
    requirements: list[str]


class Conflict(TypedDict):
    file_path: str
    reason: str
    details: str


class ApplyResult(TypedDict):
    file_path: str
    status: Literal["applied", "partial", "conflict"]
    details: str


class ValidationIssue(TypedDict):
    file_path: str
    level: Literal["info", "warning", "error"]
    message: str


# Adapter protocol removed - all file types handled uniformly with git patches
