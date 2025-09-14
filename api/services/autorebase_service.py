"""
Service for AutoRebase operations
"""

from typing import Dict, Any
from ..models.autorebase_models import AutoRebaseRequest, AutoRebaseResponse, CloneResult, AutoRebaseResult
from ..autorebase.core import AutoRebase


class AutoRebaseService:
    """Service for handling AutoRebase operations"""
    
    def __init__(self):
        """Initialize the AutoRebase service"""
        pass
    
    async def process_autorebase(self, request: AutoRebaseRequest) -> AutoRebaseResponse:
        """
        Process AutoRebase request: clone repositories and run autorebase
        
        Args:
            request: AutoRebase request with repository URLs and SHAs
            
        Returns:
            AutoRebaseResponse with complete results
        """
        try:
            # Initialize AutoRebase with working directory
            autorebase = AutoRebase(work_dir=request.work_dir)
            
            # Process repositories: clone and run autorebase
            results = await autorebase.process_repositories(
                base_repo_url=request.base_repo_url,
                feature_repo_url=request.feature_repo_url,
                base_0_sha=request.base_software_0,
                base_1_sha=request.base_software_1,
                feature_0_sha=request.feature_software_0
            )
            
            # Convert results to response format
            clone_results = None
            if "clone_results" in results:
                clone_results = {}
                for key, result in results["clone_results"]["results"].items():
                    clone_results[key] = CloneResult(**result)
            
            autorebase_results = None
            if "autorebase_results" in results:
                autorebase_results = AutoRebaseResult(**results["autorebase_results"])
            
            # Create feature branch and PR if autorebase was successful OR if some files were processed
            pr_results = None
            if (results["success"] or (results.get("autorebase_results") and 
                results["autorebase_results"].get("details", {}).get("step1_results", {}).get("applied_patches", []))) and request.output_branch:
                from ..autorebase.github_operations import GitHubOperations
                from pathlib import Path
                github_ops = GitHubOperations(Path(request.work_dir))
                # Construct f1_dir the same way as DiffPatchManager does
                f1_dir = autorebase.base_1_dir.parent / "feature-5.1"
                pr_results = github_ops.create_feature_branch_and_pr(
                    feature_repo_url=request.feature_repo_url,
                    feature_0_dir=autorebase.feature_0_dir,
                    feature_51_dir=f1_dir,
                    base_branch=request.base_branch,
                    new_branch=request.output_branch
                )
            
            return AutoRebaseResponse(
                success=results["success"],
                message=results["message"],
                base_software_0=request.base_software_0,
                base_software_1=request.base_software_1,
                feature_software_0=request.feature_software_0,
                base_repo_url=request.base_repo_url,
                feature_repo_url=request.feature_repo_url,
                work_dir=request.work_dir,
                clone_results=clone_results,
                autorebase_results=autorebase_results,
                pr_results=pr_results,
                error=results.get("error")
            )
            
        except Exception as e:
            return AutoRebaseResponse(
                success=False,
                message=f"AutoRebase processing failed: {str(e)}",
                base_software_0=request.base_software_0,
                base_software_1=request.base_software_1,
                feature_software_0=request.feature_software_0,
                base_repo_url=request.base_repo_url,
                feature_repo_url=request.feature_repo_url,
                work_dir=request.work_dir,
                error=str(e)
            )
