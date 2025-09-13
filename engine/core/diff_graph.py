from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple


class DiffGraph:
    """Minimal cross-file change graph.

    Tracks file-level adds/modifies and a simple name-based move detection heuristic.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Tuple[str, str, str]] = []  # (src, dst, kind)

    def add_file(self, path: str, status: str) -> None:
        self.nodes[path] = {"status": status}

    def add_edge(self, src: str, dst: str, kind: str) -> None:
        self.edges.append((src, dst, kind))

    def export_anchor_map(self) -> Dict[str, str]:
        """Export a trivial anchor map of old->new file paths for moves/renames."""
        return {src: dst for src, dst, kind in self.edges if kind in {"moved", "renamed"}}

