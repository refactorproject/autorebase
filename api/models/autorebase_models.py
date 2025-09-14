"""
Pydantic models for AutoRebase operations
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AutoRebaseRequest(BaseModel):
    """Request model for AutoRebase operations"""
    base_software_0: str = Field(
        ..., 
        description="GitHub SHA for Base Software 0",
        min_length=7,
        max_length=40,
        pattern=r"^[a-f0-9]+$"
    )
    base_software_1: str = Field(
        ..., 
        description="GitHub SHA for Base Software 1", 
        min_length=7,
        max_length=40,
        pattern=r"^[a-f0-9]+$"
    )
    feature_software_0: str = Field(
        ..., 
        description="GitHub SHA for Feature Software 0",
        min_length=7,
        max_length=40,
        pattern=r"^[a-f0-9]+$"
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
    work_dir: Optional[str] = Field(
        default="data/repos",
        description="Working directory for repository cloning and processing"
    )


class CloneResult(BaseModel):
    """Result of repository cloning operation"""
    success: bool = Field(description="Whether the cloning was successful")
    message: str = Field(description="Result message")
    directory: Optional[str] = Field(description="Directory where repository was cloned")
    sha: Optional[str] = Field(description="SHA that was checked out")
    error: Optional[str] = Field(description="Error message if operation failed")


class AutoRebaseResult(BaseModel):
    """Result of autorebase operation"""
    success: bool = Field(description="Whether the autorebase was successful")
    message: str = Field(description="Result message")
    details: Optional[Dict[str, Any]] = Field(description="Detailed results")


class AutoRebaseResponse(BaseModel):
    """Response model for AutoRebase operations"""
    success: bool = Field(description="Whether the complete operation was successful")
    message: str = Field(description="Overall result message")
    base_software_0: str = Field(description="Base Software 0 SHA processed")
    base_software_1: str = Field(description="Base Software 1 SHA processed")
    feature_software_0: str = Field(description="Feature Software 0 SHA processed")
    base_repo_url: str = Field(description="Base repository URL used")
    feature_repo_url: str = Field(description="Feature repository URL used")
    work_dir: str = Field(description="Working directory used")
    clone_results: Optional[Dict[str, CloneResult]] = Field(
        description="Results of repository cloning operations"
    )
    autorebase_results: Optional[AutoRebaseResult] = Field(
        description="Results of autorebase operation"
    )
    error: Optional[str] = Field(description="Error message if operation failed")
