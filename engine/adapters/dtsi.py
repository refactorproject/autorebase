from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..core import utils
from ..core.diff_types import PatchUnit, ApplyResult, ValidationIssue, Conflict


KIND = "dtsi"


def detect_env() -> dict:
    return {
        "dtc": bool(utils.which("dtc")),
    }


def extract_feature(old_base: Path, feature: Path) -> List[PatchUnit]:
    patches: List[PatchUnit] = []
    for f in utils.list_files(feature):
        if f.suffix.lower() not in {".dts", ".dtsi"}:
            continue
        rel = utils.rel_to(f, feature)
        oldp = old_base / rel
        if not oldp.exists():
            ops = [{"op": "add_file", "content": f.read_text(encoding="utf-8")}]
        else:
            before = oldp.read_text(encoding="utf-8")
            after = f.read_text(encoding="utf-8")
            ops = [{"op": "text_diff", "diff": ""}]  # simplify
        patches.append(PatchUnit(file_path=rel, kind=KIND, ops=ops, anchors=None, req_ids=[], notes=None))
    return patches


def extract_base(old_base: Path, new_base: Path) -> Dict[str, Any]:
    # Record simple file changes.
    delta: Dict[str, Any] = {"files": {}}
    old_files = {utils.rel_to(p, old_base): p for p in utils.list_files(old_base) if p.suffix.lower() in {".dts", ".dtsi"}}
    new_files = {utils.rel_to(p, new_base): p for p in utils.list_files(new_base) if p.suffix.lower() in {".dts", ".dtsi"}}
    for rel, p in old_files.items():
        if rel not in new_files:
            delta["files"][rel] = {"status": "deleted"}
        else:
            a = p.read_text(encoding="utf-8")
            b = new_files[rel].read_text(encoding="utf-8")
            if a != b:
                delta["files"][rel] = {"status": "modified"}
    for rel in new_files.keys() - old_files.keys():
        delta["files"][rel] = {"status": "added"}
    return delta


def retarget(patch: PatchUnit, base_delta_map: dict, new_base_root: Path) -> PatchUnit | Conflict:
    return patch


def apply(patch: PatchUnit, target_root: Path) -> ApplyResult:
    from . import text_generic

    return text_generic.apply(patch, target_root)


def validate(target_root: Path) -> List[ValidationIssue]:
    return []

