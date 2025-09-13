from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

from ..core import utils
from ..core.diff_types import PatchUnit, ApplyResult, ValidationIssue, Conflict


KIND = "c_cpp"


FUNC_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")


def detect_env() -> dict:
    return {
        "clang_tidy": bool(utils.which("clang-tidy")),
        "gumtree": bool(utils.which("gumtree")),
        "coccinelle": bool(utils.which("spatch")),
    }


def _extract_symbols(text: str) -> Set[str]:
    return set(m.group(1) for m in FUNC_RE.finditer(text))


def extract_feature(old_base: Path, feature: Path) -> List[PatchUnit]:
    patches: List[PatchUnit] = []
    for f in utils.list_files(feature):
        if f.suffix.lower() not in {".c", ".h", ".cpp", ".hpp", ".cc"}:
            continue
        rel = utils.rel_to(f, feature)
        oldp = old_base / rel
        anchors = None
        if oldp.exists():
            before = oldp.read_text(encoding="utf-8")
            after = f.read_text(encoding="utf-8")
            anchors = {
                "symbols_old": sorted(_extract_symbols(before)),
                "symbols_new": sorted(_extract_symbols(after)),
            }
            ops = [{"op": "text_diff", "diff": ""}]  # defer to generic apply
        else:
            ops = [{"op": "add_file", "content": f.read_text(encoding="utf-8")}]
        patches.append(PatchUnit(file_path=rel, kind=KIND, ops=ops, anchors=anchors, req_ids=[], notes=None))
    return patches


def extract_base(old_base: Path, new_base: Path) -> Dict[str, Any]:
    # Detect simple function renames per file.
    delta: Dict[str, Any] = {"func_renames": {}, "files": {}}
    for f in utils.list_files(old_base):
        if f.suffix.lower() not in {".c", ".h", ".cpp", ".hpp", ".cc"}:
            continue
        rel = utils.rel_to(f, old_base)
        newp = new_base / rel
        if not newp.exists():
            delta["files"][rel] = {"status": "deleted"}
            continue
        a = f.read_text(encoding="utf-8")
        b = newp.read_text(encoding="utf-8")
        syms_a = _extract_symbols(a)
        syms_b = _extract_symbols(b)
        removed = syms_a - syms_b
        added = syms_b - syms_a
        if removed and added:
            # naive map removed->added one-to-one by order
            for old_sym, new_sym in zip(sorted(removed), sorted(added)):
                delta["func_renames"].setdefault(rel, {})[old_sym] = new_sym
    return delta


def retarget(patch: PatchUnit, base_delta_map: dict, new_base_root: Path) -> PatchUnit | Conflict:
    # If function rename detected, annotate notes for informational relocation.
    rel = patch["file_path"]
    rename_map = base_delta_map.get("func_renames", {}).get(rel, {})
    if rename_map:
        patch["notes"] = f"retarget assisted by func renames: {rename_map}"
    return patch


def apply(patch: PatchUnit, target_root: Path) -> ApplyResult:
    # Delegate to text_generic strategy for simplicity
    from . import text_generic

    # Use same ops but ensure the file exists
    return text_generic.apply(patch, target_root)


def validate(target_root: Path) -> List[ValidationIssue]:
    # Optionally clang-tidy could run; here skip for demo
    return []

