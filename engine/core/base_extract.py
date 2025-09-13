from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..adapters import c_cpp, json_cfg, yaml_cfg, dtsi, text_generic


def extract_base(old_base: Path, new_base: Path) -> Dict[str, Any]:
    """Compute ΔB across adapters and return a merged delta map."""

    delta: Dict[str, Any] = {
        "adapters": {},
    }
    # Aggregate per-adapter delta
    delta["adapters"]["c_cpp"] = c_cpp.extract_base(old_base, new_base)
    delta["adapters"]["json"] = json_cfg.extract_base(old_base, new_base)
    delta["adapters"]["yaml"] = yaml_cfg.extract_base(old_base, new_base)
    delta["adapters"]["dtsi"] = dtsi.extract_base(old_base, new_base)
    delta["adapters"]["text"] = text_generic.extract_base(old_base, new_base)
    return delta

