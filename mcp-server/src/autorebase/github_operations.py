"""
GitHub operations for AutoRebase
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class GitHubOperations:
    """Handle GitHub operations like creating branches and PRs"""
    
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
    
    def _get_authenticated_url(self, repo_url: str) -> str:
        """Get authenticated repository URL using token or SSH"""
        github_token = os.environ.get('GITHUB_TOKEN')
        
        # Check if SSH is preferred (no token or SSH_OVERRIDE env var)
        ssh_override = os.environ.get('SSH_OVERRIDE', 'false').lower() == 'true'
        
        if ssh_override or not github_token:
            # Convert HTTPS URL to SSH URL for authentication
            if repo_url.startswith('https://github.com/'):
                return repo_url.replace('https://github.com/', 'git@github.com:')
            elif repo_url.startswith('https://'):
                # Generic HTTPS to SSH conversion
                return repo_url.replace('https://', 'git@').replace('/', ':')
        
        # Use token authentication
        if github_token and 'github.com' in repo_url:
            # Replace https:// with https://x-access-token:token@ for authentication
            if repo_url.startswith('https://github.com/'):
                return repo_url.replace('https://github.com/', f'https://x-access-token:{github_token}@github.com/')
            elif repo_url.startswith('https://'):
                return repo_url.replace('https://', f'https://x-access-token:{github_token}@')
        
        return repo_url
    
    def create_feature_branch_and_pr(
        self, 
        feature_repo_url: str,
        feature_0_dir: Path,
        feature_51_dir: Path,
        base_branch: str = "feature/v5.0.0",
        new_branch: str = "feature/v5.0.1"
    ) -> Dict[str, Any]:
        """
        Create a new feature branch with resolved changes and create a PR
        
        Args:
            feature_repo_url: URL of the feature repository
            feature_0_dir: Directory containing the original feature-0 code
            feature_51_dir: Directory containing the resolved feature-5.1 code
            base_branch: Base branch to create PR against (default: feature/v5.0.0)
            new_branch: New branch name (default: feature/v5.0.1)
            
        Returns:
            Dict with operation results
        """
        try:
            print(f"🚀 Creating new feature branch: {new_branch}")
            print(f"   Base branch: {base_branch}")
            print(f"   Feature repo: {feature_repo_url}")
            
            # Step 1: Clone the feature repository to a new location
            feature_repo_dir = self.work_dir / "feature-repo-for-pr"
            if feature_repo_dir.exists():
                import shutil
                shutil.rmtree(feature_repo_dir)
            
            print(f"📥 Cloning feature repository to: {feature_repo_dir}")
            auth_repo_url = self._get_authenticated_url(feature_repo_url)
            clone_result = subprocess.run(
                ["git", "clone", auth_repo_url, str(feature_repo_dir)],
                capture_output=True,
                text=True
            )
            
            if clone_result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Failed to clone feature repository: {clone_result.stderr}",
                    "error": clone_result.stderr
                }
            
            # Fetch latest changes to ensure we have the most recent commits
            print(f"🔄 Fetching latest changes...")
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=feature_repo_dir,
                capture_output=True,
                text=True
            )
            
            if fetch_result.returncode != 0:
                print(f"⚠️ Warning: Failed to fetch latest changes: {fetch_result.stderr}")
            
            # Step 2: Checkout the base branch
            print(f"🔀 Checking out base branch: {base_branch}")
            checkout_result = subprocess.run(
                ["git", "checkout", base_branch],
                cwd=feature_repo_dir,
                capture_output=True,
                text=True
            )
            
            if checkout_result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Failed to checkout base branch {base_branch}: {checkout_result.stderr}",
                    "error": checkout_result.stderr
                }
            
            # Step 3: Create new branch
            print(f"🌿 Creating new branch: {new_branch}")
            branch_result = subprocess.run(
                ["git", "checkout", "-b", new_branch],
                cwd=feature_repo_dir,
                capture_output=True,
                text=True
            )
            
            if branch_result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Failed to create new branch {new_branch}: {branch_result.stderr}",
                    "error": branch_result.stderr
                }
            
            # Step 4: Copy resolved files from feature-5.1 to the new branch
            print(f"📋 Copying resolved files from {feature_51_dir} to new branch")
            files_copied = self._copy_resolved_files(feature_51_dir, feature_repo_dir)
            
            if not files_copied:
                return {
                    "success": False,
                    "message": "No files were copied to the new branch",
                    "error": "No resolved files found"
                }
            
            # Step 5: Add and commit changes
            print(f"💾 Adding and committing changes")
            commit_result = self._commit_changes(feature_repo_dir, new_branch, files_copied)
            
            if not commit_result["success"]:
                return commit_result
            
            # Step 6: Push the new branch
            print(f"🚀 Pushing new branch to remote")
            # Update remote URL to use authenticated URL
            auth_repo_url = self._get_authenticated_url(feature_repo_url)
            remote_update_result = subprocess.run(
                ["git", "remote", "set-url", "origin", auth_repo_url],
                cwd=feature_repo_dir,
                capture_output=True,
                text=True
            )
            
            push_result = subprocess.run(
                ["git", "push", "origin", new_branch],
                cwd=feature_repo_dir,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Failed to push new branch: {push_result.stderr}",
                    "error": push_result.stderr
                }
            
            # Step 7: Create PR using GitHub CLI or API
            print(f"📝 Creating pull request")
            pr_result = self._create_pull_request(feature_repo_url, base_branch, new_branch, files_copied)
            
            return {
                "success": True,
                "message": f"Successfully created branch {new_branch} and PR",
                "details": {
                    "new_branch": new_branch,
                    "base_branch": base_branch,
                    "files_copied": files_copied,
                    "commit_hash": commit_result.get("commit_hash"),
                    "pr_url": pr_result.get("pr_url"),
                    "pr_number": pr_result.get("pr_number")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating feature branch and PR: {str(e)}",
                "error": str(e)
            }
    
    def _copy_resolved_files(self, source_dir: Path, target_dir: Path) -> list:
        """Copy resolved files from feature-5.1 to the new branch"""
        files_copied = []
        
        # List of files to copy (exclude .git, .orig, .rej files)
        exclude_patterns = ['.git', '.orig', '.rej']
        
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                # Skip excluded files
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue
                
                # Calculate relative path from source_dir
                relative_path = file_path.relative_to(source_dir)
                target_file = target_dir / relative_path
                
                # Ensure target directory exists
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                import shutil
                shutil.copy2(file_path, target_file)
                files_copied.append(str(relative_path))
                print(f"  ✅ Copied: {relative_path}")
        
        return files_copied
    
    def _commit_changes(self, repo_dir: Path, branch_name: str, files_copied: list) -> Dict[str, Any]:
        """Add and commit the copied files"""
        try:
            # Add all files
            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Failed to add files: {add_result.stderr}",
                    "error": add_result.stderr
                }
            
            # Check if there are any changes to commit
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                return {
                    "success": False,
                    "message": "No changes to commit",
                    "error": "No modified files found"
                }
            
            # Create commit message
            commit_message = f"""feat: AutoRebase resolved conflicts for {branch_name}

This commit contains AI-resolved conflicts from the AutoRebase process.

Files updated:
{chr(10).join(f'- {file}' for file in files_copied)}

Generated by AutoRebase on {datetime.now().isoformat()}
"""
            
            # Commit changes
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Failed to commit changes: {commit_result.stderr}",
                    "error": commit_result.stderr
                }
            
            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            
            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
            
            return {
                "success": True,
                "message": "Successfully committed changes",
                "commit_hash": commit_hash,
                "files_committed": files_copied
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error committing changes: {str(e)}",
                "error": str(e)
            }
    
    def _create_pull_request(self, repo_url: str, base_branch: str, new_branch: str, files_copied: list) -> Dict[str, Any]:
        """Create a pull request using GitHub CLI or API"""
        try:
            # Extract repo owner and name from URL
            # Format: https://github.com/owner/repo.git
            repo_parts = repo_url.replace("https://github.com/", "").replace(".git", "")
            owner, repo_name = repo_parts.split("/")
            
            # Create PR title and body
            pr_title = f"feat: AutoRebase resolved conflicts for {new_branch}"
            pr_body = f"""## 🤖 AutoRebase Conflict Resolution

This PR contains AI-resolved conflicts from the AutoRebase process.

### 📋 Changes Made

The following files were updated with AI-resolved conflicts:

{chr(10).join(f'- `{file}`' for file in files_copied)}

### 🔧 Process Details

- **Base Branch**: `{base_branch}`
- **New Branch**: `{new_branch}`
- **Resolution Method**: AI-powered 3-way merge
- **Generated**: {datetime.now().isoformat()}

### ✅ Verification

Please review the changes to ensure they meet your requirements. The AI resolution was based on the requirements specified in the `requirements_map.yaml` file.

### 🚀 Next Steps

1. Review the changes
2. Test the resolved code
3. Merge if approved
4. Delete the feature branch after merge
"""
            
            # Try GitHub CLI first
            try:
                pr_result = subprocess.run(
                    [
                        "gh", "pr", "create",
                        "--title", pr_title,
                        "--body", pr_body,
                        "--base", base_branch,
                        "--head", new_branch,
                        "--repo", f"{owner}/{repo_name}"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if pr_result.returncode == 0:
                    # Extract PR URL from output
                    output_lines = pr_result.stdout.strip().split('\n')
                    pr_url = None
                    pr_number = None
                    
                    for line in output_lines:
                        if "https://github.com" in line and "/pull/" in line:
                            pr_url = line.strip()
                            # Extract PR number from URL
                            pr_number = pr_url.split("/pull/")[-1]
                            break
                    
                    return {
                        "success": True,
                        "message": "Successfully created PR using GitHub CLI",
                        "pr_url": pr_url,
                        "pr_number": pr_number,
                        "method": "github_cli"
                    }
                else:
                    print(f"GitHub CLI failed: {pr_result.stderr}")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("GitHub CLI not available or timed out")
            
            # Fallback: Return success without creating PR (manual creation needed)
            return {
                "success": True,
                "message": "Branch created successfully. Please create PR manually.",
                "pr_url": f"https://github.com/{owner}/{repo_name}/compare/{base_branch}...{new_branch}",
                "pr_number": None,
                "method": "manual",
                "instructions": f"Visit https://github.com/{owner}/{repo_name}/compare/{base_branch}...{new_branch} to create the PR manually"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating PR: {str(e)}",
                "error": str(e)
            }
