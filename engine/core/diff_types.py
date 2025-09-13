from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol, TypedDict, Optional, Any


class PatchUnit(TypedDict, total=False):
    """A unit of change for a single file with optional semantic ops.

    - file_path: relative path of the file the patch applies to
    - kind: language/adapter kind
    - ops: adapter-specific operations; for text fallback, may contain a unified diff
    - anchors: optional anchors/symbols to aid semantic relocation
    - req_ids: requirement IDs attached via traceability
    - notes: optional note
    """

    file_path: str
    kind: Literal["c_cpp", "json", "yaml", "dtsi", "text"]
    ops: list[dict]
    anchors: Optional[dict]
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


class Adapter(Protocol):
    def detect_env(self) -> dict: ...

    def extract_feature(self, old_base: Path, feature: Path) -> list[PatchUnit]: ...

    def extract_base(self, old_base: Path, new_base: Path) -> dict: ...

    def retarget(self, patch: PatchUnit, base_delta_map: dict, new_base_root: Path) -> PatchUnit | Conflict: ...

    def apply(self, patch: PatchUnit, target_root: Path) -> ApplyResult: ...

    def validate(self, target_root: Path) -> list[ValidationIssue]: ...
