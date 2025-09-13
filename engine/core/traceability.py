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
    requirement: str | None = None


def load_requirements_map(path: Path) -> list[ReqMapping]:
    """Load requirements mapping YAML file."""

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    mappings: list[ReqMapping] = []
    for item in data:
        patt = item.get("path_glob") or item.get("path") or "**/*"
        mappings.append(ReqMapping(path_glob=patt, req_ids=list(item.get("req_ids", [])), requirement=item.get("requirement")))
    return mappings


def req_ids_for_file(rel_path: str, mappings: list[ReqMapping]) -> list[str]:
    """Return all requirement IDs matching the file path via globs."""

    ids: list[str] = []
    for m in mappings:
        if fnmatch.fnmatch(rel_path, m.path_glob):
            ids.extend(m.req_ids)
    return sorted(set(ids))


def requirement_texts_for_file(rel_path: str, mappings: list[ReqMapping]) -> list[str]:
    texts: list[str] = []
    for m in mappings:
        if fnmatch.fnmatch(rel_path, m.path_glob) and m.requirement:
            texts.append(m.requirement)
    return texts
