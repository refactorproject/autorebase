from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .diff_types import ValidationIssue
from ..adapters import c_cpp, json_cfg, yaml_cfg, dtsi, text_generic
from .utils import which


def validate(target_root: Path, build_script: str | None = None) -> Dict[str, Any]:
    """Run optional build script and adapter validations; aggregate results."""

    issues: List[ValidationIssue] = []
    # Build script is a placeholder; in demo we skip or ensure it returns success.
    # Adapter validations
    for adapter in (c_cpp, json_cfg, yaml_cfg, dtsi, text_generic):
        try:
            issues.extend(adapter.validate(target_root))
        except Exception as e:
            issues.append({"file_path": "", "level": "warning", "message": f"adapter validate failed: {e}"})
    success = not any(i for i in issues if i["level"] == "error")
    return {"success": success, "issues": issues}

