from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List

from .diff_types import PatchUnit
from .utils import list_files, rel_to
from .traceability import load_requirements_map, req_ids_for_file, requirement_texts_for_file


def extract_feature(old_base: Path, feature: Path, req_map_path: Path) -> List[PatchUnit]:
    """Extract ΔF patch units from feature vs old_base using git patches."""

    mappings = load_requirements_map(req_map_path)
    units: List[PatchUnit] = []
    
    # Get all files that differ between old_base and feature
    try:
        # Use git diff to find all changed files
        result = subprocess.run(
            ["git", "diff", "--no-index", "--name-only", str(old_base), str(feature)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode not in [0, 1]:  # 0 = no diff, 1 = differences found
            return units
            
        changed_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        # For each changed file, generate a patch
        for file_path in changed_files:
            try:
                # Skip /dev/null entries
                if file_path == "/dev/null":
                    continue
                    
                # Convert absolute path to relative path
                if file_path.startswith(str(feature)):
                    relative_path = Path(file_path).relative_to(feature)
                elif file_path.startswith(str(old_base)):
                    relative_path = Path(file_path).relative_to(old_base)
                else:
                    # Try to extract relative path from the full path
                    relative_path = Path(file_path)
                
                # Generate patch for this specific file
                patch_result = subprocess.run(
                    ["git", "diff", "--no-index", str(old_base / relative_path), str(feature / relative_path)],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )
                
                if patch_result.returncode in [0, 1]:  # 0 = no diff, 1 = differences found
                    patch_content = patch_result.stdout
                    if patch_content.strip():  # Only add if there's actual content
                        unit: PatchUnit = {
                            "file_path": str(relative_path),
                            "patch_content": patch_content,
                            "req_ids": req_ids_for_file(str(relative_path), mappings),
                            "requirements": requirement_texts_for_file(str(relative_path), mappings)
                        }
                        units.append(unit)
                        
            except Exception:
                # Skip files that can't be processed
                continue
                
    except Exception:
        # Fallback: return empty list if git diff fails
        pass
        
    return units
