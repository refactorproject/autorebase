"""
Core AutoRebase functionality
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio


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
        Clone a repository and checkout specific SHA
        
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
        
        This is the main method that will be implemented in following steps.
        Currently returns a placeholder response.
        
        Returns:
            Dict with autorebase results
        """
        # TODO: Implement actual autorebase logic
        # This will be filled in the following steps
        
        return {
            "success": True,
            "message": "AutoRebase process completed successfully",
            "details": {
                "base_0_dir": str(self.base_0_dir),
                "base_1_dir": str(self.base_1_dir),
                "feature_0_dir": str(self.feature_0_dir),
                "status": "placeholder - implementation pending"
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
