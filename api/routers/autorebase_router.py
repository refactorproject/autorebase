"""
Router for AutoRebase operations
"""

from fastapi import APIRouter, HTTPException
from ..models.autorebase_models import AutoRebaseRequest, AutoRebaseResponse
from ..services.autorebase_service import AutoRebaseService

router = APIRouter(prefix="/autorebase", tags=["AutoRebase Operations"])

# Initialize the service
autorebase_service = AutoRebaseService()


@router.post("/process", response_model=AutoRebaseResponse)
async def process_autorebase(request: AutoRebaseRequest):
    """
    Process AutoRebase operation: clone repositories and run autorebase
    
    This endpoint takes GitHub SHAs and repository URLs, clones the repositories
    to specific SHAs, and runs the autorebase process.
    
    Args:
        request: Contains repository URLs, SHAs, and working directory
        
    Returns:
        AutoRebaseResponse: Contains results of cloning and autorebase operations
    """
    try:
        result = await autorebase_service.process_autorebase(request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for AutoRebase service"""
    return {"status": "healthy", "service": "AutoRebase Processor"}


@router.get("/")
async def root():
    """Root endpoint with AutoRebase API information"""
    return {
        "message": "AutoRebase Processing API",
        "version": "1.0.0",
        "endpoints": {
            "process": "/autorebase/process",
            "health": "/autorebase/health"
        },
        "description": "Clone repositories and run autorebase operations"
    }
