from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.github_models import GitHubSHARequest, GitHubSHAResponse
from ..services.github_service import GitHubService

router = APIRouter(prefix="/github", tags=["GitHub SHA Processing"])

# Initialize the service
github_service = GitHubService()


@router.post("/input-repos", response_model=GitHubSHAResponse)
async def input_repositories(request: GitHubSHARequest):
    """
    Process three GitHub SHAs with their repository URLs: Base Software 0, Base Software 1, and Feature Software 0.

    This endpoint validates the provided GitHub SHAs against their respective repositories, 
    clones the repositories to the specified SHAs, and automatically runs the AutoRebase process.

    Args:
        request: Contains the three GitHub SHAs and their repository URLs

    Returns:
        GitHubSHAResponse: Contains validation results, commit information, and AutoRebase results
    """
    try:
        result = await github_service.process_shas(request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "GitHub SHA Processor"}


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GitHub SHA Processing and AutoRebase API",
        "version": "1.0.0",
        "endpoints": {
            "input_repos": "/github/input-repos",
            "health": "/github/health"
        },
        "description": "Validates GitHub SHAs, clones repositories, and runs AutoRebase process automatically"
    }
