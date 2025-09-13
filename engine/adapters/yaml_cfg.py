from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from ..core import utils
from ..core.diff_types import PatchUnit, ApplyResult, ValidationIssue, Conflict


KIND = "yaml"


def detect_env() -> dict:
    return {
        "yq": bool(utils.which("yq")),
        "yamale": False,  # Not bundled; fallback only
    }


def _load_yaml(p: Path) -> Any:
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _yaml_diff_ops(a: Any, b: Any, base_path: str = "") -> List[Dict[str, Any]]:
    ops: List[Dict[str, Any]] = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a.keys() - b.keys():
            ops.append({"op": "remove", "path": f"{base_path}/{k}"})
        for k in b.keys() - a.keys():
            ops.append({"op": "add", "path": f"{base_path}/{k}", "value": b[k]})
        for k in a.keys() & b.keys():
            ops.extend(_yaml_diff_ops(a[k], b[k], f"{base_path}/{k}"))
    elif a != b:
        ops.append({"op": "replace", "path": base_path or "/", "value": b})
    return ops


def extract_feature(old_base: Path, feature: Path) -> List[PatchUnit]:
    patches: List[PatchUnit] = []
    for f in utils.list_files(feature):
        if f.suffix.lower() not in {".yml", ".yaml"}:
            continue
        rel = utils.rel_to(f, feature)
        oldp = old_base / rel
        if not oldp.exists():
            ops = [{"op": "add_file", "content": f.read_text(encoding="utf-8")}]
        else:
            before = _load_yaml(oldp)
            after = _load_yaml(f)
            if before is None or after is None:
                ops = [{"op": "text_fallback", "content": f.read_text(encoding="utf-8")}]
            else:
                ops = _yaml_diff_ops(before, after)
        patches.append(PatchUnit(file_path=rel, kind=KIND, ops=ops, anchors=None, req_ids=[], notes=None))
    return patches


def extract_base(old_base: Path, new_base: Path) -> Dict[str, Any]:
    delta: Dict[str, Any] = {"files": {}}
    old_files = {utils.rel_to(p, old_base): p for p in utils.list_files(old_base) if p.suffix.lower() in {".yml", ".yaml"}}
    new_files = {utils.rel_to(p, new_base): p for p in utils.list_files(new_base) if p.suffix.lower() in {".yml", ".yaml"}}
    for rel, p in old_files.items():
        if rel not in new_files:
            delta["files"][rel] = {"status": "deleted"}
        else:
            a = _load_yaml(p)
            b = _load_yaml(new_files[rel])
            if a != b:
                delta["files"][rel] = {"status": "modified"}
    for rel in new_files.keys() - old_files.keys():
        delta["files"][rel] = {"status": "added"}
    return delta


def retarget(patch: PatchUnit, base_delta_map: dict, new_base_root: Path) -> PatchUnit | Conflict:
    return patch


def apply(patch: PatchUnit, target_root: Path) -> ApplyResult:
    rel = patch["file_path"]
    path = target_root / rel
    data: Any = {}
    if path.exists():
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            return ApplyResult(file_path=rel, status="conflict", details="invalid YAML at target")
    for op in patch.get("ops", []):
        k = op.get("op")
        if k == "add_file" or k == "text_fallback":
            utils.write_text(path, op.get("content", "{}"))
            return ApplyResult(file_path=rel, status="applied", details="file added")
        pth = [x for x in op.get("path", "/").split("/") if x]
        cur = data
        if len(pth) == 1:
            key = pth[0]
            if k == "remove":
                cur.pop(key, None)
            else:
                cur[key] = op.get("value")
        elif len(pth) == 2:
            if pth[0] not in cur or not isinstance(cur.get(pth[0]), dict):
                cur[pth[0]] = {}
            if k == "remove":
                cur[pth[0]].pop(pth[1], None)
            else:
                cur[pth[0]][pth[1]] = op.get("value")
    utils.write_text(path, yaml.safe_dump(data, sort_keys=True))
    return ApplyResult(file_path=rel, status="applied", details="yaml ops applied")


def validate(target_root: Path) -> List[ValidationIssue]:
    return []

