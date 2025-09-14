from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.github_models import GitHubSHARequest, GitHubSHAResponse
from ..services.github_service import GitHubService

router = APIRouter(prefix="/github", tags=["GitHub AutoRebase"])

# Initialize the service
github_service = GitHubService()


@router.post("/autorebase", response_model=GitHubSHAResponse)
async def run_autorebase(request: GitHubSHARequest):
    """
    Run the complete AutoRebase process with three GitHub repositories: Base Software 0, Base Software 1, and Feature Software 0.

    This endpoint validates the provided GitHub SHAs/tags against their respective repositories, 
    clones the repositories, runs the AutoRebase process with AI conflict resolution, and creates a Pull Request.

    Args:
        request: Contains the three GitHub SHAs/tags and their repository URLs

    Returns:
        GitHubSHAResponse: Contains validation results, AutoRebase results, and PR creation details
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
    return {"status": "healthy", "service": "GitHub AutoRebase Processor"}


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GitHub AutoRebase API",
        "version": "1.0.0",
        "endpoints": {
            "autorebase": "/github/autorebase",
            "health": "/github/health"
        },
        "description": "Runs complete AutoRebase process with AI conflict resolution and PR creation"
    }
