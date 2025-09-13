from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .utils import write_json


@dataclass
class RunManifest:
    """Metadata for a single auto-rebase run."""

    run_id: str
    old_base: str
    new_base: str
    feature_old: str
    req_map: str
    workdir: str
    created_at: str


def new_run_manifest(old_base: Path, new_base: Path, feature: Path, req_map: Path, workdir: Path) -> RunManifest:
    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    return RunManifest(
        run_id=run_id,
        old_base=str(old_base),
        new_base=str(new_base),
        feature_old=str(feature),
        req_map=str(req_map),
        workdir=str(workdir),
        created_at=datetime.utcnow().isoformat() + "Z",
    )


def persist_manifest(manifest: RunManifest, artifacts_dir: Path) -> Path:
    out = artifacts_dir / "run.json"
    write_json(out, manifest.__dict__)
    return out

