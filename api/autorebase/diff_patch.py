"""
Diff and Patch functionality for AutoRebase
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime


class DiffPatchManager:
    """
    Manages diff generation and patch application for AutoRebase
    """
    
    def __init__(self, base_0_dir: Path, base_1_dir: Path, feature_0_dir: Path, work_dir: Path = None):
        """
        Initialize with the three repository directories
        
        Args:
            base_0_dir: Path to base-0 directory
            base_1_dir: Path to base-1 directory  
            feature_0_dir: Path to feature-0 directory
            work_dir: Path to work directory (for changelog and requirements)
        """
        self.base_0_dir = base_0_dir
        self.base_1_dir = base_1_dir
        self.feature_0_dir = feature_0_dir
        self.work_dir = work_dir or base_1_dir.parent
        
        # Create f1 directory for output files (feature-5.1)
        self.f1_dir = base_1_dir.parent / "feature-5.1"
        self.f1_dir.mkdir(exist_ok=True)
        
        # Changelog to track all file changes
        self.changelog = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": [],
            "patches_generated": [],
            "patches_applied": [],
            "f1_files_created": []
        }
    
    def find_common_files(self) -> List[str]:
        """
        Find files that exist in both base_0 and feature_0 directories
        
        Returns:
            List of relative file paths that exist in both directories
        """
        common_files = []
        
        # Get all files in base_0 directory (recursively)
        base_0_files = set()
        for root, dirs, files in os.walk(self.base_0_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.base_0_dir)
                base_0_files.add(rel_path)
        
        # Get all files in feature_0 directory (recursively)
        feature_0_files = set()
        for root, dirs, files in os.walk(self.feature_0_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.feature_0_dir)
                feature_0_files.add(rel_path)
        
        # Find intersection
        common_files = list(base_0_files.intersection(feature_0_files))
        
        # Sort for consistent ordering
        common_files.sort()
        
        return common_files
    
    def generate_diff_patches(self) -> Dict[str, Dict[str, str]]:
        """
        Generate diff patches for all common files
        
        Generates two diffs per file:
        1. base_0 -> feature_0 (b0_to_f0)
        2. base_0 -> base_1 (b0_to_b1)
        
        Returns:
            Dict with file paths as keys and diff patches as values
        """
        common_files = self.find_common_files()
        patches = {}
        
        print(f"Found {len(common_files)} common files to process")
        
        for file_path in common_files:
            print(f"Processing file: {file_path}")
            
            file_patches = {}
            
            # Generate base_0 -> feature_0 diff
            b0_to_f0_diff = self._generate_diff(
                self.base_0_dir / file_path,
                self.feature_0_dir / file_path,
                f"base_0_to_feature_0_{file_path.replace('/', '_')}"
            )
            if b0_to_f0_diff:
                file_patches["b0_to_f0"] = b0_to_f0_diff
            
            # Generate base_0 -> base_1 diff
            b0_to_b1_diff = self._generate_diff(
                self.base_0_dir / file_path,
                self.base_1_dir / file_path,
                f"base_0_to_base_1_{file_path.replace('/', '_')}"
            )
            if b0_to_b1_diff:
                file_patches["b0_to_b1"] = b0_to_b1_diff
            
            if file_patches:
                patches[file_path] = file_patches
                self.changelog["files_processed"].append(file_path)
                self.changelog["patches_generated"].extend(list(file_patches.keys()))
        
        return patches
    
    def _generate_diff(self, file_a: Path, file_b: Path, patch_name: str) -> Optional[str]:
        """
        Generate a unified diff between two files
        
        Args:
            file_a: Path to first file
            file_b: Path to second file
            patch_name: Name for the patch (for logging)
            
        Returns:
            Diff content as string, or None if files are identical
        """
        try:
            # Check if both files exist
            if not file_a.exists() or not file_b.exists():
                print(f"Warning: One or both files don't exist: {file_a}, {file_b}")
                return None
            
            # Generate diff using git diff
            result = subprocess.run(
                ["git", "diff", "--no-index", str(file_a), str(file_b)],
                capture_output=True,
                text=True
            )
            
            # If files are identical, git diff returns exit code 0 with empty output
            if result.returncode == 0 and not result.stdout.strip():
                print(f"Files are identical: {file_a.name}")
                return None
            
            # If there are differences, git diff returns exit code 1 with diff output
            if result.returncode == 1 and result.stdout.strip():
                print(f"Generated diff for {file_b}.patch")
                return result.stdout
            
            # Handle other cases
            if result.stderr:
                print(f"Warning: git diff stderr for {file_b}: {result.stderr}")
            
            return None
            
        except Exception as e:
            print(f"Error generating diff for {file_b}: {str(e)}")
            return None
    
    def apply_patch_step1(self, patches: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Apply patches in Step 1: Apply base_0 -> feature_0 patches to base_1 and create feature-5.1 files
        
        This creates new files in the feature-5.1 directory with the same names as base_1 files,
        but with feature_0 changes applied
        
        Args:
            patches: Dictionary of patches generated by generate_diff_patches
            
        Returns:
            Dictionary with results of patch application
        """
        results = {
            "success": True,
            "applied_patches": [],
            "failed_patches": [],
            "f1_files_created": [],
            "step": "step1_b0_to_f0_to_f1"
        }
        
        print("Step 1: Applying base_0 -> feature_0 patches to create f1 files")
        
        for file_path, file_patches in patches.items():
            if "b0_to_f0" not in file_patches:
                continue
                
            print(f"Creating f1 file: {file_path}")
            print(f"    Base 1 file: {self.base_1_dir / file_path}")
            print(f"    F1 file: {self.f1_dir / file_path}")
            
            # Create the f1 file by applying the patch to base_1 file
            success = self._create_f1_file(
                patch_content=file_patches["b0_to_f0"],
                base_1_file=self.base_1_dir / file_path,
                f1_file=self.f1_dir / file_path,
                patch_name=f"step1_{file_path.replace('/', '_')}"
            )
            
            if success:
                results["applied_patches"].append(file_path)
                results["f1_files_created"].append(str(self.f1_dir / file_path))
                self.changelog["patches_applied"].append({
                    "file": file_path,
                    "patch_type": "b0_to_f0",
                    "step": "step1",
                    "timestamp": datetime.now().isoformat()
                })
                self.changelog["f1_files_created"].append({
                    "file": str(self.f1_dir / file_path),
                    "source_file": str(self.base_1_dir / file_path),
                    "patch_type": "b0_to_f0",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                results["failed_patches"].append(file_path)
                results["success"] = False
        
        return results
    
    def apply_patch_step2(self, patches: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Apply patches in Step 2: Apply base_0 -> base_1 patches to feature_0
        
        This creates a new version of feature_0 with base_1 changes applied
        
        Args:
            patches: Dictionary of patches generated by generate_diff_patches
            
        Returns:
            Dictionary with results of patch application
        """
        results = {
            "success": True,
            "applied_patches": [],
            "failed_patches": [],
            "step": "step2_b0_to_b1_on_f0"
        }
        
        print("Step 2: Applying base_0 -> base_1 patches to feature_0")
        
        for file_path, file_patches in patches.items():
            if "b0_to_b1" not in file_patches:
                continue
                
            print(f"Applying b0_to_b1 patch to: {file_path}")
            
            # Apply the patch
            success = self._apply_patch_to_file(
                patch_content=file_patches["b0_to_b1"],
                target_file=self.feature_0_dir / file_path,
                patch_name=f"step2_{file_path.replace('/', '_')}"
            )
            
            if success:
                results["applied_patches"].append(file_path)
                self.changelog["patches_applied"].append({
                    "file": file_path,
                    "patch_type": "b0_to_b1",
                    "step": "step2",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                results["failed_patches"].append(file_path)
                results["success"] = False
        
        return results
    
    def _apply_patch_to_file(self, patch_content: str, target_file: Path, patch_name: str) -> bool:
        """
        Apply a patch to a specific file
        
        Args:
            patch_content: The patch content to apply
            target_file: Path to the target file
            patch_name: Name for logging
            
        Returns:
            True if patch was applied successfully, False otherwise
        """
        try:
            # Create a temporary patch file
            patch_file = target_file.parent / f"{patch_name}.patch"
            
            with open(patch_file, 'w') as f:
                f.write(patch_content)
            
            # Apply the patch
            result = subprocess.run(
                ["patch", str(target_file), str(patch_file)],
                capture_output=True,
                text=True,
                cwd=target_file.parent
            )
            
            # Clean up temporary patch file
            patch_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                print(f"Successfully applied patch to {target_file}")
                return True
            else:
                print(f"Failed to apply patch to {target_file}: {result.stderr}")
                
                # Check for .orig and .rej files generated by patch command
                orig_file = target_file.with_suffix(target_file.suffix + '.orig')
                rej_file = target_file.with_suffix(target_file.suffix + '.rej')
                
                if orig_file.exists():
                    print(f"Backup file created: {orig_file}")
                    # Store the .orig file path in changelog
                    self.changelog.setdefault("backup_files", []).append({
                        "file": str(orig_file),
                        "original_file": str(target_file),
                        "patch_name": patch_name,
                        "timestamp": datetime.now().isoformat()
                    })
                
                if rej_file.exists():
                    print(f"Reject file created: {rej_file}")
                    # Store the .rej file path in changelog
                    self.changelog.setdefault("reject_files", []).append({
                        "file": str(rej_file),
                        "original_file": str(target_file),
                        "patch_name": patch_name,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Call process_3way_merge for rejected patches
                    self.process_3way_merge(target_file, orig_file, rej_file, patch_name)
                
                return False
                
        except Exception as e:
            print(f"Error applying patch to {target_file}: {str(e)}")
            return False
    
    def _create_f1_file(self, patch_content: str, base_1_file: Path, f1_file: Path, patch_name: str) -> bool:
        """
        Create an f1 file by applying a patch to a base_1 file
        
        Args:
            patch_content: The patch content to apply
            base_1_file: Path to the base_1 source file
            f1_file: Path to the f1 output file
            patch_name: Name for logging
            
        Returns:
            True if f1 file was created successfully, False otherwise
        """
        try:
            print(f"    Ensuring directory exists: {f1_file.parent}")
            # Ensure the f1 file directory exists
            f1_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"    Copying base_1 file to f1 file...")
            # Copy base_1 file to f1 file first
            import shutil
            shutil.copy2(base_1_file, f1_file)
            print(f"    Copy completed")
            
            # Create a temporary patch file
            patch_file = f1_file.parent / f"{patch_name}.patch"
            
            with open(patch_file, 'w') as f:
                f.write(patch_content)
            
            # Apply the patch to the f1 file
            print(f"    Applying patch: patch {f1_file} {patch_file}")
            result = subprocess.run(
                ["patch", "--batch", str(f1_file), str(patch_file)],
                capture_output=True,
                text=True
            )
            
            # Clean up temporary patch file
            patch_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                print(f"Successfully created f1 file: {f1_file}")
                return True
            else:
                print(f"Failed to create f1 file {f1_file}: {result.stderr}")
                
                # Check for .orig and .rej files generated by patch command
                orig_file = f1_file.with_suffix(f1_file.suffix + '.orig')
                rej_file = f1_file.with_suffix(f1_file.suffix + '.rej')
                
                if orig_file.exists():
                    print(f"Backup file created: {orig_file}")
                    # Store the .orig file path in changelog
                    self.changelog.setdefault("backup_files", []).append({
                        "file": str(orig_file),
                        "original_file": str(f1_file),
                        "patch_name": patch_name,
                        "timestamp": datetime.now().isoformat()
                    })
                
                if rej_file.exists():
                    print(f"Reject file created: {rej_file}")
                    # Store the .rej file path in changelog
                    self.changelog.setdefault("reject_files", []).append({
                        "file": str(rej_file),
                        "original_file": str(f1_file),
                        "patch_name": patch_name,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Call process_3way_merge for rejected patches
                    self.process_3way_merge(f1_file, orig_file, rej_file, patch_name)
                
                return False
                
        except Exception as e:
            print(f"Error creating f1 file {f1_file}: {str(e)}")
            return False
    
    def process_3way_merge(self, target_file: Path, orig_file: Path, rej_file: Path, patch_name: str) -> None:
        """
        Process 3-way merge for rejected patches using AI conflict resolution

        This method is called when a patch fails and generates .rej files.
        It uses OpenAI to resolve conflicts based on requirements from YAML file.

        Args:
            target_file: Path to the target file that failed to patch
            orig_file: Path to the .orig backup file
            rej_file: Path to the .rej reject file
            patch_name: Name of the patch that failed
        """
        print(f"🤖 Starting AI-powered 3-way merge for: {target_file}")
        print(f"  Original backup: {orig_file}")
        print(f"  Reject file: {rej_file}")
        print(f"  Patch name: {patch_name}")

        try:
            # Import the conflict resolver
            from autorebase.file_conflict_resolver import resolve_file_conflict_with_openai
            
            # Find the requirements file (look for it in the cloned repositories)
            requirements_file = None
            
            # Priority order for finding requirements_map.yaml:
            # 1. Feature repository root (most important - this is the default)
            # 2. Feature repository data folder (if exists)
            # 3. Base repository root
            # 4. Base repository data folder (if exists)
            # 5. Work directory fallback
            
            if self.feature_0_dir and (self.feature_0_dir / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.feature_0_dir / "REQUIREMENTS_MAP.yml"
            elif self.feature_0_dir and (self.feature_0_dir / "data" / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.feature_0_dir / "data" / "REQUIREMENTS_MAP.yml"
            elif self.base_0_dir and (self.base_0_dir / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.base_0_dir / "REQUIREMENTS_MAP.yml"
            elif self.base_1_dir and (self.base_1_dir / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.base_1_dir / "REQUIREMENTS_MAP.yml"
            elif self.base_0_dir and (self.base_0_dir / "data" / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.base_0_dir / "data" / "REQUIREMENTS_MAP.yml"
            elif self.base_1_dir and (self.base_1_dir / "data" / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.base_1_dir / "data" / "REQUIREMENTS_MAP.yml"
            # Fallback to work directory
            elif (self.work_dir / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.work_dir / "REQUIREMENTS_MAP.yml"
            elif (self.work_dir.parent / "REQUIREMENTS_MAP.yml").exists():
                requirements_file = self.work_dir.parent / "REQUIREMENTS_MAP.yml"
            
            if not requirements_file or not requirements_file.exists():
                print(f"⚠️  Requirements file not found at {requirements_file}")
                print(f"   Falling back to original behavior for {target_file}")
                
                # Store failed 3-way merge attempt in changelog
                self.changelog.setdefault("three_way_merges", []).append({
                    "target_file": str(target_file),
                    "orig_file": str(orig_file),
                    "rej_file": str(rej_file),
                    "patch_name": patch_name,
                    "timestamp": datetime.now().isoformat(),
                    "status": "fallback_no_requirements",
                    "error": "Requirements file not found, using original behavior"
                })
                
                # Fall back to original behavior (just print method called)
                print(f"process_3way_merge() method called (fallback)")
                print(f"  Target file: {target_file}")
                print(f"  Original backup: {orig_file}")
                print(f"  Reject file: {rej_file}")
                print(f"  Patch name: {patch_name}")
                return
            
            print(f"📋 Using requirements file: {requirements_file}")
            
            # Resolve the conflict using AI
            # Note: orig_file is the backup (.orig), but we want to resolve conflicts in the target_file
            resolution_result = resolve_file_conflict_with_openai(
                original_file_path=target_file,
                rejection_file_path=rej_file,
                requirements_file=requirements_file,
                verbose=True
            )
            
            if resolution_result["success"]:
                print(f"✅ AI resolution successful!")
                print(f"   Conflict type: {resolution_result['conflict_type']}")
                print(f"   Changes applied: {resolution_result['changes_applied']}")
                
                # Write the resolved content to the target file
                target_file.write_text(resolution_result["resolved_content"])
                print(f"💾 Resolved content written to: {target_file}")
                
                # Store successful 3-way merge in changelog
                self.changelog.setdefault("three_way_merges", []).append({
                    "target_file": str(target_file),
                    "orig_file": str(orig_file),
                    "rej_file": str(rej_file),
                    "patch_name": patch_name,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "conflict_type": resolution_result["conflict_type"],
                    "changes_applied": resolution_result["changes_applied"],
                    "requirement_used": resolution_result["requirement_used"],
                    "validation_score": resolution_result.get("validation_score", 0)
                })
                
            else:
                print(f"❌ AI resolution failed: {resolution_result['explanation']}")
                print(f"   Falling back to original behavior for {target_file}")
                
                # Store failed 3-way merge attempt in changelog
                self.changelog.setdefault("three_way_merges", []).append({
                    "target_file": str(target_file),
                    "orig_file": str(orig_file),
                    "rej_file": str(rej_file),
                    "patch_name": patch_name,
                    "timestamp": datetime.now().isoformat(),
                    "status": "fallback_ai_failed",
                    "error": resolution_result["explanation"],
                    "conflict_type": resolution_result.get("conflict_type", "unknown")
                })
                
                # Fall back to original behavior (just print method called)
                print(f"process_3way_merge() method called (fallback)")
                print(f"  Target file: {target_file}")
                print(f"  Original backup: {orig_file}")
                print(f"  Reject file: {rej_file}")
                print(f"  Patch name: {patch_name}")
                
        except Exception as e:
            print(f"❌ Error during 3-way merge: {str(e)}")
            print(f"   Falling back to original behavior for {target_file}")
            
            # Store error in changelog
            self.changelog.setdefault("three_way_merges", []).append({
                "target_file": str(target_file),
                "orig_file": str(orig_file),
                "rej_file": str(rej_file),
                "patch_name": patch_name,
                "timestamp": datetime.now().isoformat(),
                "status": "fallback_exception",
                "error": str(e)
            })
            
            # Fall back to original behavior (just print method called)
            print(f"process_3way_merge() method called (fallback)")
            print(f"  Target file: {target_file}")
            print(f"  Original backup: {orig_file}")
            print(f"  Reject file: {rej_file}")
            print(f"  Patch name: {patch_name}")
    
    def get_changelog(self) -> Dict[str, Any]:
        """
        Get the changelog of all operations performed
        
        Returns:
            Dictionary containing the changelog
        """
        return self.changelog
    
    def save_changelog(self, output_path: Path) -> bool:
        """
        Save the changelog to a JSON file
        
        Args:
            output_path: Path where to save the changelog
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(self.changelog, f, indent=2)
            print(f"Changelog saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving changelog: {str(e)}")
            return False
