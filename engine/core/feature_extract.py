from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .diff_types import PatchUnit
from .utils import list_files, rel_to
from .traceability import load_requirements_map, req_ids_for_file
from ..adapters import c_cpp, json_cfg, yaml_cfg, dtsi, text_generic


def _choose_adapter(path: Path):
    suf = path.suffix.lower()
    if suf in {".c", ".h", ".cpp", ".hpp", ".cc"}:
        return c_cpp
    if suf == ".json":
        return json_cfg
    if suf in {".yml", ".yaml"}:
        return yaml_cfg
    if suf in {".dts", ".dtsi"}:
        return dtsi
    return text_generic


def extract_feature(old_base: Path, feature: Path, req_map_path: Path) -> List[PatchUnit]:
    """Extract ΔF patch units from feature vs old_base, attaching requirement IDs."""

    mappings = load_requirements_map(req_map_path)
    units: List[PatchUnit] = []
    # Call each adapter once; adapters filter by suffix internally
    for adapter in (c_cpp, json_cfg, yaml_cfg, dtsi, text_generic):
        units.extend(adapter.extract_feature(old_base, feature))
    # Attach req_ids per file
    for u in units:
        u["req_ids"] = req_ids_for_file(u["file_path"], mappings)
    return units
