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
            
            # Step 3: Create feature PR if autorebase completed (even with some failures)
            pr_results = None
            if results.get("success") and results.get("autorebase_results"):
                print("🚀 Creating feature PR...")
                pr_results = await autorebase.create_feature_pr(
                    feature_repo_url=request.feature_repo_url,
                    base_branch=request.base_branch,
                    new_branch=request.output_branch
                )
                print(f"PR creation result: {pr_results.get('success', False)}")
            
            # Convert results to response format
            clone_results = None
            if "clone_results" in results:
                clone_results = {}
                for key, result in results["clone_results"]["results"].items():
                    clone_results[key] = CloneResult(**result)
            
            autorebase_results = None
            if "autorebase_results" in results:
                autorebase_results = AutoRebaseResult(**results["autorebase_results"])
            
            # Add PR results to autorebase results if available
            if pr_results and autorebase_results:
                if autorebase_results.details is None:
                    autorebase_results.details = {}
                autorebase_results.details["pr_results"] = pr_results
            
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
