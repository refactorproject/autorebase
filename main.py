from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.github_router import router as github_router
from api.routers.autorebase_router import router as autorebase_router
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="AutoRebase API",
    description="API for processing GitHub SHAs and software versioning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(github_router)
app.include_router(autorebase_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AutoRebase API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AutoRebase API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
