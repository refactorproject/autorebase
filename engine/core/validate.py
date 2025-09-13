from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .diff_types import ValidationIssue
from .utils import which


def validate(target_root: Path, build_script: str | None = None) -> Dict[str, Any]:
    """Run basic validation checks on the target directory."""

    issues: List[ValidationIssue] = []
    
    # Basic file system validation
    if not target_root.exists():
        issues.append({"file_path": "", "level": "error", "message": "Target directory does not exist"})
        return {"success": False, "issues": issues}
    
    # Check for common issues
    reject_files = list(target_root.rglob("*.rej"))
    if reject_files:
        for reject_file in reject_files:
            issues.append({
                "file_path": str(reject_file.relative_to(target_root)),
                "level": "warning", 
                "message": "Reject file found - patch conflicts not resolved"
            })
    
    # Check for empty files
    empty_files = []
    for file_path in target_root.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size == 0:
            empty_files.append(str(file_path.relative_to(target_root)))
    
    if empty_files:
        issues.append({
            "file_path": "",
            "level": "warning",
            "message": f"Found {len(empty_files)} empty files: {', '.join(empty_files[:5])}"
        })
    
    # Build script validation (placeholder)
    if build_script:
        issues.append({
            "file_path": "",
            "level": "info",
            "message": f"Build script '{build_script}' validation skipped in simplified mode"
        })
    
    success = not any(i for i in issues if i["level"] == "error")
    return {"success": success, "issues": issues}

