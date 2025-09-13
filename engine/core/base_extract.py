from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict


def extract_base(old_base: Path, new_base: Path) -> Dict[str, Any]:
    """Compute ΔB using git patches and return a simplified delta map."""

    delta: Dict[str, Any] = {
        "git_patches": {},
    }
    
    # Get all files that differ between old_base and new_base
    try:
        # Use git diff to find all changed files
        result = subprocess.run(
            ["git", "diff", "--no-index", "--name-only", str(old_base), str(new_base)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode != 0 and result.returncode != 1:  # 1 is expected for differences
            return delta
            
        changed_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        # For each changed file, generate a patch
        for file_path in changed_files:
            try:
                # Skip /dev/null entries
                if file_path == "/dev/null":
                    continue
                    
                # Convert absolute path to relative path
                if file_path.startswith(str(new_base)):
                    relative_path = Path(file_path).relative_to(new_base)
                elif file_path.startswith(str(old_base)):
                    relative_path = Path(file_path).relative_to(old_base)
                else:
                    # Try to extract relative path from the full path
                    relative_path = Path(file_path)
                
                # Generate patch for this specific file
                patch_result = subprocess.run(
                    ["git", "diff", "--no-index", str(old_base / relative_path), str(new_base / relative_path)],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )
                
                if patch_result.returncode in [0, 1]:  # 0 = no diff, 1 = differences found
                    patch_content = patch_result.stdout
                    if patch_content.strip():  # Only add if there's actual content
                        delta["git_patches"][str(relative_path)] = patch_content
                        
            except Exception:
                # Skip files that can't be processed
                continue
                
    except Exception:
        # Fallback: return empty delta if git diff fails
        pass
        
    return delta

