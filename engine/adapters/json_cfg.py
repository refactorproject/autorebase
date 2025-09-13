from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from ..core.diff_types import PatchUnit, ApplyResult, ValidationIssue, Conflict
from ..core import utils


KIND = "json"


def detect_env() -> dict:
    return {
        "jsonschema": True,  # provided via requirements
    }


def _load_json(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _json_diff_ops(a: Any, b: Any, base_path: str = "") -> List[Dict[str, Any]]:
    ops: List[Dict[str, Any]] = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a.keys() - b.keys():
            ops.append({"op": "remove", "path": f"{base_path}/{k}"})
        for k in b.keys() - a.keys():
            ops.append({"op": "add", "path": f"{base_path}/{k}", "value": b[k]})
        for k in a.keys() & b.keys():
            ops.extend(_json_diff_ops(a[k], b[k], f"{base_path}/{k}"))
    elif a != b:
        ops.append({"op": "replace", "path": base_path or "/", "value": b})
    return ops


def extract_feature(old_base: Path, feature: Path) -> List[PatchUnit]:
    patches: List[PatchUnit] = []
    for f in utils.list_files(feature):
        if f.suffix.lower() != ".json":
            continue
        rel = utils.rel_to(f, feature)
        oldp = old_base / rel
        if not oldp.exists():
            ops = [{"op": "add_file", "content": f.read_text(encoding="utf-8")}]
        else:
            before = _load_json(oldp)
            after = _load_json(f)
            if before is None or after is None:
                ops = [{"op": "text_fallback", "content": f.read_text(encoding="utf-8")}]
            else:
                ops = _json_diff_ops(before, after)
        patches.append(PatchUnit(file_path=rel, kind=KIND, ops=ops, anchors=None, req_ids=[], notes=None))
    return patches


def extract_base(old_base: Path, new_base: Path) -> Dict[str, Any]:
    delta: Dict[str, Any] = {"json_moves": {}, "files": {}}
    old_files = {utils.rel_to(p, old_base): p for p in utils.list_files(old_base) if p.suffix.lower() == ".json"}
    new_files = {utils.rel_to(p, new_base): p for p in utils.list_files(new_base) if p.suffix.lower() == ".json"}
    for rel, p in old_files.items():
        if rel in new_files:
            a = _load_json(p)
            b = _load_json(new_files[rel])
            if isinstance(a, dict) and isinstance(b, dict):
                # Heuristic: detect key renames at first level
                for k in a.keys():
                    if k not in b and any(k in kk for kk in a.keys()):
                        pass
                # Demo: detect specific pattern rvc -> rvcs
                if "camera" in a and "camera" in b and isinstance(a["camera"], dict) and isinstance(b["camera"], dict):
                    if "rvc" in a["camera"] and "rvcs" in b["camera"]:
                        delta["json_moves"][f"/{rel}#/camera/rvc"] = f"/{rel}#/camera/rvcs"
        else:
            delta["files"][rel] = {"status": "deleted"}
    for rel in new_files.keys() - old_files.keys():
        delta["files"][rel] = {"status": "added"}
    return delta


def retarget(patch: PatchUnit, base_delta_map: dict, new_base_root: Path) -> PatchUnit | Conflict:
    # Adjust jsonpatch paths if a known move exists
    ops: List[Dict[str, Any]] = []
    moves = base_delta_map.get("json_moves", {})
    for op in patch.get("ops", []):
        newop = deepcopy(op)
        if op.get("op") in {"replace", "add", "remove"}:
            path = op.get("path", "")
            # include file context if present
            file_key = f"/{patch['file_path']}#"
            key = file_key + path if not path.startswith("/") else file_key + path
            if key in moves:
                new_path = moves[key].split("#", 1)[-1]
                newop["path"] = new_path
        ops.append(newop)
    patch["ops"] = ops
    return patch


def apply(patch: PatchUnit, target_root: Path) -> ApplyResult:
    rel = patch["file_path"]
    path = target_root / rel
    data: Any = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return ApplyResult(file_path=rel, status="conflict", details="invalid JSON at target")
    for op in patch.get("ops", []):
        k = op.get("op")
        if k == "add_file":
            utils.write_text(path, op.get("content", "{}"))
            return ApplyResult(file_path=rel, status="applied", details="file added")
        if k in {"replace", "add", "remove"}:
            # For demo, only support top-level or one-level dict paths: /a or /a/b
            pth = [x for x in op.get("path", "/").split("/") if x]
            cur = data
            if len(pth) == 1:
                key = pth[0]
                if k == "remove":
                    cur.pop(key, None)
                elif k == "add" or k == "replace":
                    cur[key] = op.get("value")
            elif len(pth) == 2 and isinstance(cur.get(pth[0], {}), dict):
                if pth[0] not in cur:
                    cur[pth[0]] = {}
                if k == "remove":
                    cur[pth[0]].pop(pth[1], None)
                else:
                    cur[pth[0]][pth[1]] = op.get("value")
            else:
                return ApplyResult(file_path=rel, status="partial", details="unsupported jsonpath depth")
        elif k == "text_fallback":
            utils.write_text(path, op.get("content", "{}"))
        else:
            return ApplyResult(file_path=rel, status="conflict", details=f"unsupported op {k}")
    utils.write_text(path, json.dumps(data, indent=2))
    return ApplyResult(file_path=rel, status="applied", details="json ops applied")


def validate(target_root: Path) -> List[ValidationIssue]:
    # Placeholder: could validate JSON with schema if provided
    return []

