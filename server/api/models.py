from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Run:
    id: str
    status: str
    created_at: str
    old_base: str
    new_base: str
    feature_old: str
    req_map: str
    artifacts_path: str

