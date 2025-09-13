from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Storage
from ..models import Run


class SQLiteStore(Storage):
    """Simple JSON-file backed store for demo fallback."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / "runs.json"
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> List[Dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, lst: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(lst, indent=2), encoding="utf-8")

    def create_run(self, meta: Dict[str, Any]) -> Run:
        lst = self._load()
        lst.append(meta)
        self._save(lst)
        return Run(**meta)

    def list_runs(self) -> List[Run]:
        return [Run(**m) for m in self._load()]

    def get_run(self, run_id: str) -> Optional[Run]:
        for m in self._load():
            if m["id"] == run_id:
                return Run(**m)
        return None

