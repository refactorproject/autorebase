"""
Pydantic models for AutoRebase operations
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class AutoRebaseRequest(BaseModel):
    """Request model for AutoRebase operations"""
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
    work_dir: Optional[str] = Field(
        default="data/repos",
        description="Working directory for repository cloning and processing"
    )
    output_branch: Optional[str] = Field(
        default="feature/v5.0.1",
        description="Output branch name for the new feature branch with resolved conflicts"
    )
    base_branch: Optional[str] = Field(
        default="feature/v5.0.0",
        description="Base branch name to create PR against (defaults to the feature branch from input)"
    )


class CloneResult(BaseModel):
    """Result of repository cloning operation"""
    success: bool = Field(description="Whether the cloning was successful")
    message: str = Field(description="Result message")
    directory: Optional[str] = Field(description="Directory where repository was cloned")
    sha: Optional[str] = Field(description="SHA that was checked out")
    error: Optional[str] = Field(default=None, description="Error message if operation failed")


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
        default=None,
        description="Results of repository cloning operations"
    )
    autorebase_results: Optional[AutoRebaseResult] = Field(
        default=None,
        description="Results of autorebase operation"
    )
    resolved_files: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of resolved files with their content and conflict resolution details"
    )
    changelog: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Complete changelog information from the autorebase process"
    )
    changelog_path: Optional[str] = Field(
        default=None,
        description="Path to the saved changelog file"
    )
    error: Optional[str] = Field(description="Error message if operation failed")
