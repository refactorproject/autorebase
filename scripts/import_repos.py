#!/usr/bin/env python3
"""
Script to import repositories into the data folder
"""

import subprocess
import os
import sys
from pathlib import Path

# Configuration - Update these with your actual repository URLs and tags
REPO_CONFIG = {
    "base_repo_url": "https://github.com/your-org/base-repo.git",  # Update this
    "feature_repo_url": "https://github.com/your-org/feature-repo.git",  # Update this
    "base_0_tag": "base-0",  # Update this
    "base_1_tag": "base-1",  # Update this
    "feature_0_tag": "feature-0"  # Update this
}

DATA_DIR = Path("data/repos")

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def clone_repository(repo_url, target_dir, tag=None):
    """Clone a repository to the target directory"""
    print(f"Cloning {repo_url} to {target_dir}")
    
    # Remove target directory if it exists
    if target_dir.exists():
        print(f"Removing existing directory: {target_dir}")
        run_command(f"rm -rf {target_dir}")
    
    # Clone the repository
    clone_cmd = f"git clone {repo_url} {target_dir}"
    if tag:
        clone_cmd += f" --branch {tag}"
    
    result = run_command(clone_cmd)
    if result is None:
        return False
    
    # If we specified a tag, checkout to that tag
    if tag:
        checkout_cmd = f"git checkout {tag}"
        result = run_command(checkout_cmd, cwd=target_dir)
        if result is None:
            return False
    
    print(f"Successfully cloned {repo_url} to {target_dir}")
    return True

def import_repositories():
    """Import all three repositories"""
    print("Starting repository import process...")
    
    # Create data directory structure
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clone base repository with base-0 tag
    base_0_dir = DATA_DIR / "base-0"
    success_1 = clone_repository(
        REPO_CONFIG["base_repo_url"], 
        base_0_dir, 
        REPO_CONFIG["base_0_tag"]
    )
    
    # Clone base repository with base-1 tag
    base_1_dir = DATA_DIR / "base-1"
    success_2 = clone_repository(
        REPO_CONFIG["base_repo_url"], 
        base_1_dir, 
        REPO_CONFIG["base_1_tag"]
    )
    
    # Clone feature repository
    feature_0_dir = DATA_DIR / "feature-0"
    success_3 = clone_repository(
        REPO_CONFIG["feature_repo_url"], 
        feature_0_dir, 
        REPO_CONFIG["feature_0_tag"]
    )
    
    # Report results
    print("\n" + "="*50)
    print("IMPORT RESULTS:")
    print("="*50)
    print(f"Base-0 repository: {'✅ SUCCESS' if success_1 else '❌ FAILED'}")
    print(f"Base-1 repository: {'✅ SUCCESS' if success_2 else '❌ FAILED'}")
    print(f"Feature-0 repository: {'✅ SUCCESS' if success_3 else '❌ FAILED'}")
    
    if all([success_1, success_2, success_3]):
        print("\n🎉 All repositories imported successfully!")
        return True
    else:
        print("\n❌ Some repositories failed to import. Check the errors above.")
        return False

def list_imported_repos():
    """List the imported repositories"""
    print("\n" + "="*50)
    print("IMPORTED REPOSITORIES:")
    print("="*50)
    
    for repo_dir in DATA_DIR.iterdir():
        if repo_dir.is_dir():
            print(f"\n📁 {repo_dir.name}:")
            
            # Get git info
            git_info = run_command("git log --oneline -1", cwd=repo_dir)
            if git_info:
                print(f"   Latest commit: {git_info}")
            
            # Get current branch/tag
            branch_info = run_command("git branch --show-current", cwd=repo_dir)
            tag_info = run_command("git describe --tags --exact-match HEAD 2>/dev/null", cwd=repo_dir)
            
            if tag_info:
                print(f"   Current tag: {tag_info}")
            elif branch_info:
                print(f"   Current branch: {branch_info}")
            
            # Count files
            file_count = run_command("find . -type f | wc -l", cwd=repo_dir)
            if file_count:
                print(f"   Files: {file_count}")

if __name__ == "__main__":
    print("AutoRebase Repository Importer")
    print("="*50)
    print("⚠️  Please update the REPO_CONFIG in this script with your actual repository URLs and tags")
    print()
    
    # Check if user wants to proceed
    response = input("Do you want to proceed with the import? (y/N): ")
    if response.lower() != 'y':
        print("Import cancelled.")
        sys.exit(0)
    
    success = import_repositories()
    
    if success:
        list_imported_repos()
    else:
        print("\nImport failed. Please check the configuration and try again.")
        sys.exit(1)
