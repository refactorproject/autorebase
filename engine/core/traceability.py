from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml


@dataclass
class ReqMapping:
    path_glob: str
    req_ids: list[str]


def load_requirements_map(path: Path) -> list[ReqMapping]:
    """Load requirements mapping YAML file."""

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    mappings: list[ReqMapping] = []
    for item in data:
        mappings.append(ReqMapping(path_glob=item["path_glob"], req_ids=list(item.get("req_ids", []))))
    return mappings


def req_ids_for_file(rel_path: str, mappings: list[ReqMapping]) -> list[str]:
    """Return all requirement IDs matching the file path via globs."""

    ids: list[str] = []
    for m in mappings:
        if fnmatch.fnmatch(rel_path, m.path_glob):
            ids.extend(m.req_ids)
    return sorted(set(ids))

