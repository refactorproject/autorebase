from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import Storage
from ..models import Run
import os


class ConvexStore(Storage):
    """Convex provider stubbed unless CONVEX_URL is set."""

    def __init__(self) -> None:
        self.enabled = bool(os.getenv("CONVEX_URL"))
        self._inmem: dict[str, Dict[str, Any]] = {}

    def create_run(self, meta: Dict[str, Any]) -> Run:
        if not self.enabled:
            return Run(**meta)
        self._inmem[meta["id"]] = meta
        return Run(**meta)

    def list_runs(self) -> List[Run]:
        if not self.enabled:
            return []
        return [Run(**m) for m in self._inmem.values()]

    def get_run(self, run_id: str) -> Optional[Run]:
        if not self.enabled:
            return None
        m = self._inmem.get(run_id)
        return Run(**m) if m else None

