from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models import Run


class Storage(ABC):
    @abstractmethod
    def create_run(self, meta: Dict[str, Any]) -> Run: ...

    @abstractmethod
    def list_runs(self) -> List[Run]: ...

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[Run]: ...

