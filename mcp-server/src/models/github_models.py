from pydantic import BaseModel, Field
from typing import Optional


class GitHubSHARequest(BaseModel):
    """Request model for GitHub SHA inputs with repository URLs"""
    base_software_0: str = Field(
        ..., 
        description="GitHub SHA or tag for Base Software 0 (e.g., 'abc123' or 'base/v1.0.0')",
        min_length=3,
        max_length=100,
        pattern=r"^[a-f0-9]+$|^[a-zA-Z0-9/._-]+$"
    )
    base_software_1: str = Field(
        ..., 
        description="GitHub SHA or tag for Base Software 1 (e.g., 'abc123' or 'base/v1.0.1')", 
        min_length=3,
        max_length=100,
        pattern=r"^[a-f0-9]+$|^[a-zA-Z0-9/._-]+$"
    )
    feature_software_0: str = Field(
        ..., 
        description="GitHub SHA or tag for Feature Software 0 (e.g., 'abc123' or 'feature/v5.0.0')",
        min_length=3,
        max_length=100,
        pattern=r"^[a-f0-9]+$|^[a-zA-Z0-9/._-]+$"
    )
    base_repo_url: str = Field(
        ...,
        description="GitHub repository URL for base software (used for base_software_0 and base_software_1)",
        pattern=r"^https://github\.com/[^/]+/[^/]+\.git$"
    )
    feature_repo_url: str = Field(
        ...,
        description="GitHub repository URL for feature software (used for feature_software_0)",
        pattern=r"^https://github\.com/[^/]+/[^/]+\.git$"
    )


class GitHubSHAResponse(BaseModel):
    """Response model for GitHub SHA processing"""
    success: bool = Field(description="Whether the operation was successful")
    message: str = Field(description="Response message")
    base_software_0: str = Field(description="Processed Base Software 0 SHA")
    base_software_1: str = Field(description="Processed Base Software 1 SHA") 
    feature_software_0: str = Field(description="Processed Feature Software 0 SHA")
    base_repo_url: str = Field(description="Base repository URL used")
    feature_repo_url: str = Field(description="Feature repository URL used")
    processing_details: Optional[dict] = Field(
        default=None, 
        description="Additional processing details"
    )
