import httpx
from typing import Dict, Any
from ..models.github_models import GitHubSHARequest, GitHubSHAResponse


class GitHubService:
    """Service for handling GitHub SHA operations"""
    
    def __init__(self):
        self.github_api_base = "https://api.github.com"
        self.timeout = 30.0
    
    async def validate_sha(self, sha: str, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Validate if a GitHub SHA exists in the repository"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"{self.github_api_base}/repos/{repo_owner}/{repo_name}/commits/{sha}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    commit_data = response.json()
                    return {
                        "valid": True,
                        "sha": commit_data["sha"],
                        "message": commit_data["commit"]["message"],
                        "author": commit_data["commit"]["author"]["name"],
                        "date": commit_data["commit"]["author"]["date"]
                    }
                else:
                    return {
                        "valid": False,
                        "error": f"Commit not found: {response.status_code}"
                    }
            except httpx.RequestError as e:
                return {
                    "valid": False,
                    "error": f"Request failed: {str(e)}"
                }
    
    def extract_repo_info(self, repo_url: str) -> tuple[str, str]:
        """Extract owner and repo name from GitHub URL"""
        # Expected format: https://github.com/owner/repo.git
        parts = repo_url.replace("https://github.com/", "").replace(".git", "")
        owner, repo_name = parts.split("/", 1)
        return owner, repo_name

    async def process_shas(self, request: GitHubSHARequest) -> GitHubSHAResponse:
        """Process the three GitHub SHAs"""
        try:
            # Extract repo info from URLs
            base_owner, base_repo = self.extract_repo_info(request.base_repo_url)
            feature_owner, feature_repo = self.extract_repo_info(request.feature_repo_url)
            
            # Validate all three SHAs
            base_0_validation = await self.validate_sha(request.base_software_0, base_owner, base_repo)
            base_1_validation = await self.validate_sha(request.base_software_1, base_owner, base_repo)
            feature_0_validation = await self.validate_sha(request.feature_software_0, feature_owner, feature_repo)
            
            # Check if all SHAs are valid
            all_valid = all([
                base_0_validation["valid"],
                base_1_validation["valid"], 
                feature_0_validation["valid"]
            ])
            
            if all_valid:
                return GitHubSHAResponse(
                    success=True,
                    message="All GitHub SHAs validated successfully",
                    base_software_0=request.base_software_0,
                    base_software_1=request.base_software_1,
                    feature_software_0=request.feature_software_0,
                    base_repo_url=request.base_repo_url,
                    feature_repo_url=request.feature_repo_url,
                    processing_details={
                        "base_0_info": base_0_validation,
                        "base_1_info": base_1_validation,
                        "feature_0_info": feature_0_validation
                    }
                )
            else:
                # Collect validation errors
                errors = []
                if not base_0_validation["valid"]:
                    errors.append(f"Base Software 0: {base_0_validation['error']}")
                if not base_1_validation["valid"]:
                    errors.append(f"Base Software 1: {base_1_validation['error']}")
                if not feature_0_validation["valid"]:
                    errors.append(f"Feature Software 0: {feature_0_validation['error']}")
                
                return GitHubSHAResponse(
                    success=False,
                    message=f"Validation failed: {'; '.join(errors)}",
                    base_software_0=request.base_software_0,
                    base_software_1=request.base_software_1,
                    feature_software_0=request.feature_software_0,
                    base_repo_url=request.base_repo_url,
                    feature_repo_url=request.feature_repo_url,
                    processing_details={
                        "validation_errors": errors
                    }
                )
                
        except Exception as e:
            return GitHubSHAResponse(
                success=False,
                message=f"Processing failed: {str(e)}",
                base_software_0=request.base_software_0,
                base_software_1=request.base_software_1,
                feature_software_0=request.feature_software_0,
                base_repo_url=request.base_repo_url,
                feature_repo_url=request.feature_repo_url
            )
