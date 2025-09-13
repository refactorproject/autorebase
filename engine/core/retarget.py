from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .diff_types import PatchUnit, ApplyResult
from .utils import ensure_dir, write_json
from ..adapters import c_cpp, json_cfg, yaml_cfg, dtsi, text_generic


def _adapter_for_kind(kind: str):
    return {
        "c_cpp": c_cpp,
        "json": json_cfg,
        "yaml": yaml_cfg,
        "dtsi": dtsi,
        "text": text_generic,
    }.get(kind, text_generic)


def retarget(patches: List[PatchUnit], base_delta: Dict[str, Any], new_base_root: Path, out_dir: Path) -> Dict[str, Any]:
    """Apply a sequence of PatchUnits to new_base_root into out_dir, using adapter-specific retargeting.

    Returns per-file outcomes and summary stats.
    """

    ensure_dir(out_dir)
    outcomes: List[Dict[str, Any]] = []
    auto = sem = conflicts = 0
    for p in patches:
        adapter = _adapter_for_kind(p["kind"])
        adjusted = adapter.retarget(p, base_delta.get("adapters", {}).get(p["kind"], {}), new_base_root)
        # Apply to out_dir by copying new_base and then patching that file
        target_path = out_dir / p["file_path"]
        base_path = new_base_root / p["file_path"]
        if base_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(base_path.read_bytes())
        res: ApplyResult = adapter.apply(adjusted, out_dir)
        outcomes.append({"file": p["file_path"], "status": res["status"], "details": res["details"], "req_ids": p.get("req_ids", [])})
        if res["status"] == "applied":
            auto += 1
        elif res["status"] == "partial":
            sem += 1
        else:
            conflicts += 1
    summary = {"auto": auto, "semantic": sem, "conflicts": conflicts}
    return {"summary": summary, "files": outcomes}
