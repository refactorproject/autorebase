from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .diff_types import PatchUnit, ApplyResult
from .utils import ensure_dir, write_json


def retarget(patches: List[PatchUnit], base_delta: Dict[str, Any], new_base_root: Path, out_dir: Path) -> Dict[str, Any]:
    """Apply a sequence of PatchUnits to new_base_root into out_dir using git patches.

    Returns per-file outcomes and summary stats.
    """

    ensure_dir(out_dir)
    outcomes: List[Dict[str, Any]] = []
    auto = sem = conflicts = 0
    
    for p in patches:
        file_path = p["file_path"]
        patch_content = p["patch_content"]
        
        # Copy the file from new_base to out_dir
        target_path = out_dir / file_path
        base_path = new_base_root / file_path
        
        if base_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(base_path.read_bytes())
        
        # Try to apply the patch using git apply
        try:
            # Write patch to temporary file
            patch_file = out_dir / f".{file_path.replace('/', '_')}.patch"
            patch_file.write_text(patch_content)
            
            # Apply the patch
            result = subprocess.run(
                ["git", "apply", "--reject", str(patch_file)],
                cwd=out_dir,
                capture_output=True,
                text=True
            )
            
            # Clean up patch file
            patch_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                # Patch applied successfully
                status = "applied"
                details = "git apply successful"
                auto += 1
            else:
                # Check for reject files
                reject_files = list(out_dir.rglob("*.rej"))
                if reject_files:
                    status = "conflict"
                    details = f"git apply failed, {len(reject_files)} reject files"
                    conflicts += 1
                else:
                    status = "partial"
                    details = "git apply failed but no rejects"
                    sem += 1
                    
        except Exception as e:
            status = "conflict"
            details = f"Error applying patch: {str(e)}"
            conflicts += 1
        
        outcomes.append({
            "file": file_path,
            "status": status,
            "details": details,
            "req_ids": p.get("req_ids", [])
        })
    
    summary = {"auto": auto, "semantic": sem, "conflicts": conflicts}
    return {"summary": summary, "files": outcomes}
