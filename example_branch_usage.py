#!/usr/bin/env python3
"""
Example: Using GitHub branch links with AutoRebase
"""

import asyncio
from api.services.autorebase_service import AutoRebaseService

async def example_with_branches():
    """Example using GitHub branch names instead of SHAs"""
    
    print("🚀 AutoRebase with GitHub Branch Links")
    print("=" * 50)
    
    # Example 1: Using branch names
    print("📋 Example 1: Using branch names")
    branch_example = {
        "base_software_0": "main",
        "base_software_1": "develop", 
        "feature_software_0": "feature/my-feature",
        "base_repo_url": "https://github.com/user/base-repo.git",
        "feature_repo_url": "https://github.com/user/feature-repo.git",
        "base_branch": "main",
        "output_branch": "feature/merged-changes"
    }
    
    print(f"  Base SW 0: {branch_example['base_software_0']}")
    print(f"  Base SW 1: {branch_example['base_software_1']}")
    print(f"  Feature SW 0: {branch_example['feature_software_0']}")
    print(f"  Output Branch: {branch_example['output_branch']}")
    print()
    
    # Example 2: Using tags (like our current test)
    print("📋 Example 2: Using tags")
    tag_example = {
        "base_software_0": "base/v1.0.0",
        "base_software_1": "base/v1.0.1", 
        "feature_software_0": "feature/v5.0.0",
        "base_repo_url": "https://github.com/refactorproject/sample-base-sw.git",
        "feature_repo_url": "https://github.com/refactorproject/sample-feature-sw.git",
        "base_branch": "feature/v5.0.0",
        "output_branch": "feature/v5.0.1"
    }
    
    print(f"  Base SW 0: {tag_example['base_software_0']}")
    print(f"  Base SW 1: {tag_example['base_software_1']}")
    print(f"  Feature SW 0: {tag_example['feature_software_0']}")
    print(f"  Output Branch: {tag_example['output_branch']}")
    print()
    
    # Example 3: Mixed (branches and tags)
    print("📋 Example 3: Mixed branches and tags")
    mixed_example = {
        "base_software_0": "main",
        "base_software_1": "v2.0.0", 
        "feature_software_0": "feature/new-api",
        "base_repo_url": "https://github.com/user/repo.git",
        "feature_repo_url": "https://github.com/user/repo.git",
        "base_branch": "main",
        "output_branch": "feature/auto-merged"
    }
    
    print(f"  Base SW 0: {mixed_example['base_software_0']} (branch)")
    print(f"  Base SW 1: {mixed_example['base_software_1']} (tag)")
    print(f"  Feature SW 0: {mixed_example['feature_software_0']} (branch)")
    print(f"  Output Branch: {mixed_example['output_branch']}")
    print()
    
    print("✅ All these formats are now supported!")
    print("   - Branch names: 'main', 'develop', 'feature/my-feature'")
    print("   - Tag names: 'v1.0.0', 'base/v1.0.0', 'feature/v5.0.0'")
    print("   - SHAs: 'abc123def456' (still supported)")
    print()
    print("🔧 The system will automatically:")
    print("   1. Clone the repositories")
    print("   2. Check out the specified branches/tags/SHAs")
    print("   3. Run autorebase with AI conflict resolution")
    print("   4. Create a new branch with resolved changes")
    print("   5. Generate a PR (if GitHub CLI is available)")

if __name__ == "__main__":
    asyncio.run(example_with_branches())
