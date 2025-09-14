"""
Core AutoRebase functionality
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
from .diff_patch import DiffPatchManager
from .github_operations import GitHubOperations


class AutoRebase:
    """
    Main AutoRebase class for processing repositories
    
    Takes base0, base1, and feature0 directories as input and performs
    automated rebasing operations.
    """
    
    def __init__(self, work_dir: str = "data/repos"):
        """
        Initialize AutoRebase with working directory
        
        Args:
            work_dir: Directory where repositories will be cloned and processed
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Repository paths
        self.base_0_dir = self.work_dir / "base-0"
        self.base_1_dir = self.work_dir / "base-1"
        self.feature_0_dir = self.work_dir / "feature-0"
    
    async def clone_repository(self, repo_url: str, target_dir: Path, sha: str) -> Dict[str, Any]:
        """
        Clone a repository and checkout specific SHA, always fetching latest changes
        
        Args:
            repo_url: GitHub repository URL
            target_dir: Target directory for cloning
            sha: Specific SHA to checkout
            
        Returns:
            Dict with operation result
        """
        try:
            # Remove existing directory if it exists
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            # Clone repository
            clone_cmd = ["git", "clone", repo_url, str(target_dir)]
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Always fetch latest changes to ensure we have the most recent commits
            fetch_cmd = ["git", "fetch", "origin"]
            result = subprocess.run(
                fetch_cmd,
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Checkout specific SHA
            checkout_cmd = ["git", "checkout", sha]
            result = subprocess.run(
                checkout_cmd,
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "success": True,
                "message": f"Successfully cloned and checked out {sha}",
                "directory": str(target_dir),
                "sha": sha
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "message": f"Failed to clone repository: {e.stderr}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error during cloning: {str(e)}",
                "error": str(e)
            }
    
    async def clone_all_repositories(self, base_repo_url: str, feature_repo_url: str, 
                                   base_0_sha: str, base_1_sha: str, feature_0_sha: str) -> Dict[str, Any]:
        """
        Clone all three repositories (base-0, base-1, feature-0)
        
        Args:
            base_repo_url: Base repository URL
            feature_repo_url: Feature repository URL
            base_0_sha: SHA for base-0
            base_1_sha: SHA for base-1
            feature_0_sha: SHA for feature-0
            
        Returns:
            Dict with results of all cloning operations
        """
        results = {}
        
        # Clone base-0
        results["base_0"] = await self.clone_repository(
            base_repo_url, self.base_0_dir, base_0_sha
        )
        
        # Clone base-1
        results["base_1"] = await self.clone_repository(
            base_repo_url, self.base_1_dir, base_1_sha
        )
        
        # Clone feature-0
        results["feature_0"] = await self.clone_repository(
            feature_repo_url, self.feature_0_dir, feature_0_sha
        )
        
        # Check if all operations were successful
        all_successful = all(result["success"] for result in results.values())
        
        return {
            "success": all_successful,
            "message": "All repositories cloned successfully" if all_successful else "Some repositories failed to clone",
            "results": results
        }
    
    async def run_autorebase(self) -> Dict[str, Any]:
        """
        Run the autorebase process
        
        This implements the core AutoRebase algorithm:
        1. Find common files between base_0 and feature_0
        2. Generate diff patches for base_0 -> feature_0 and base_0 -> base_1
        3. Apply patches in two steps:
           - Step 1: Apply base_0 -> feature_0 patches to base_1
           - Step 2: Apply base_0 -> base_1 patches to feature_0
        
        Returns:
            Dict with autorebase results
        """
        try:
            print("Starting AutoRebase process...")
            
            # Initialize diff and patch manager
            diff_manager = DiffPatchManager(
                base_0_dir=self.base_0_dir,
                base_1_dir=self.base_1_dir,
                feature_0_dir=self.feature_0_dir,
                work_dir=self.work_dir
            )
            
            # Step 1: Generate diff patches
            print("Generating diff patches...")
            patches = diff_manager.generate_diff_patches()
            
            if not patches:
                return {
                    "success": True,
                    "message": "No common files found between base_0 and feature_0",
                    "details": {
                        "files_processed": 0,
                        "patches_generated": 0,
                        "step1_applied": 0,
                        "step2_applied": 0
                    }
                }
            
            print(f"Generated patches for {len(patches)} files")
            
            # Step 2: Apply base_0 -> feature_0 patches to base_1 and create f2 files
            print("Applying base_0 -> feature_0 patches to base_1...")
            step1_results = diff_manager.apply_patch_step1(patches)
            
            # Get changelog
            changelog = diff_manager.get_changelog()
            
            # Save changelog
            changelog_path = self.work_dir / "autorebase_changelog.json"
            diff_manager.save_changelog(changelog_path)
            
            # Determine overall success
            overall_success = step1_results["success"]
            
            return {
                "success": overall_success,
                "message": "AutoRebase process completed successfully" if overall_success else "AutoRebase process completed with some failures",
                "details": {
                    "base_0_dir": str(self.base_0_dir),
                    "base_1_dir": str(self.base_1_dir),
                    "feature_0_dir": str(self.feature_0_dir),
                    "files_processed": len(patches),
                    "patches_generated": len(changelog["patches_generated"]),
                    "step1_results": step1_results,
                    "changelog_path": str(changelog_path),
                    "changelog": changelog
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"AutoRebase process failed: {str(e)}",
                "details": {
                    "error": str(e),
                    "base_0_dir": str(self.base_0_dir),
                    "base_1_dir": str(self.base_1_dir),
                    "feature_0_dir": str(self.feature_0_dir)
                }
            }
    
    async def process_repositories(self, base_repo_url: str, feature_repo_url: str,
                                 base_0_sha: str, base_1_sha: str, feature_0_sha: str) -> Dict[str, Any]:
        """
        Complete process: clone repositories and run autorebase
        
        Args:
            base_repo_url: Base repository URL
            feature_repo_url: Feature repository URL
            base_0_sha: SHA for base-0
            base_1_sha: SHA for base-1
            feature_0_sha: SHA for feature-0
            
        Returns:
            Dict with complete process results
        """
        try:
            # Step 1: Clone all repositories
            clone_results = await self.clone_all_repositories(
                base_repo_url, feature_repo_url,
                base_0_sha, base_1_sha, feature_0_sha
            )
            
            if not clone_results["success"]:
                return {
                    "success": False,
                    "message": "Failed to clone repositories",
                    "clone_results": clone_results,
                    "autorebase_results": None
                }
            
            # Step 2: Run autorebase process
            autorebase_results = await self.run_autorebase()
            
            return {
                "success": True,
                "message": "Complete process finished successfully",
                "clone_results": clone_results,
                "autorebase_results": autorebase_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Process failed: {str(e)}",
                "error": str(e)
            }
    
    async def create_feature_pr(
        self, 
        feature_repo_url: str,
        base_branch: str = "feature/v5.0.0",
        new_branch: str = "feature/v5.0.1"
    ) -> Dict[str, Any]:
        """
        Create a new feature branch with resolved changes and create a PR
        
        Args:
            feature_repo_url: URL of the feature repository
            base_branch: Base branch to create PR against (default: feature/v5.0.0)
            new_branch: New branch name (default: feature/v5.0.1)
            
        Returns:
            Dict with PR creation results
        """
        try:
            print(f"🚀 Creating feature PR: {new_branch} -> {base_branch}")
            
            # Initialize GitHub operations
            github_ops = GitHubOperations(self.work_dir)
            
            # Get the feature-5.1 directory path
            feature_51_dir = self.base_1_dir.parent / "feature-5.1"
            
            if not feature_51_dir.exists():
                return {
                    "success": False,
                    "message": f"Feature-5.1 directory not found: {feature_51_dir}",
                    "error": "Run autorebase first to generate resolved files"
                }
            
            # Create the PR
            pr_result = github_ops.create_feature_branch_and_pr(
                feature_repo_url=feature_repo_url,
                feature_0_dir=self.feature_0_dir,
                feature_51_dir=feature_51_dir,
                base_branch=base_branch,
                new_branch=new_branch
            )
            
            return pr_result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating feature PR: {str(e)}",
                "error": str(e)
            }
