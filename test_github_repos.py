#!/usr/bin/env python3
"""
Test AutoRebase with actual GitHub repositories
"""

import asyncio
import json
from pathlib import Path
from api.services.autorebase_service import AutoRebaseService

async def test_github_repos():
    """Test AutoRebase with real GitHub repositories"""
    
    print("🚀 Testing AutoRebase with Real GitHub Repositories")
    print("=" * 60)
    
    # GitHub repository data
    github_data = {
        "base_software_0": {
            "repo_url": "https://github.com/refactorproject/sample-base-sw.git",
            "sha": "19938f5dda2d4dd4f63183bc68035e443e1a2915",
            "branch": "base/v1.0.0"
        },
        "base_software_1": {
            "repo_url": "https://github.com/refactorproject/sample-base-sw.git", 
            "sha": "9b22ac11839bdb9fce1946e48073ab3ac6db19c6",
            "branch": "base/v1.0.1"
        },
        "feature_software_0": {
            "repo_url": "https://github.com/refactorproject/sample-feature-sw.git",
            "sha": "ccbefae20f7a140c336f3327fe9762a7855fe149", 
            "branch": "feature/v5.0.0"
        }
    }
    
    print("📋 Repository Information:")
    print(f"  Base SW 0: {github_data['base_software_0']['repo_url']}")
    print(f"    SHA: {github_data['base_software_0']['sha']}")
    print(f"    Branch: {github_data['base_software_0']['branch']}")
    print()
    print(f"  Base SW 1: {github_data['base_software_1']['repo_url']}")
    print(f"    SHA: {github_data['base_software_1']['sha']}")
    print(f"    Branch: {github_data['base_software_1']['branch']}")
    print()
    print(f"  Feature SW 0: {github_data['feature_software_0']['repo_url']}")
    print(f"    SHA: {github_data['feature_software_0']['sha']}")
    print(f"    Branch: {github_data['feature_software_0']['branch']}")
    print()
    print("🎯 PR Configuration:")
    print(f"  Base Branch: feature/v5.0.0")
    print(f"  Output Branch: feature/v5.0.1")
    print()
    
    # Initialize AutoRebase service
    print("🔧 Initializing AutoRebase Service...")
    autorebase_service = AutoRebaseService()
    
    try:
        # Create AutoRebase request
        from api.models.autorebase_models import AutoRebaseRequest
        
        request = AutoRebaseRequest(
            base_software_0=github_data['base_software_0']['sha'],
            base_software_1=github_data['base_software_1']['sha'],
            feature_software_0=github_data['feature_software_0']['sha'],
            base_repo_url=github_data['base_software_0']['repo_url'],
            feature_repo_url=github_data['feature_software_0']['repo_url'],
            work_dir="data/github_repos",
            base_branch="feature/v5.0.0",
            output_branch="feature/v5.0.1"
        )
        
        # Process the repositories
        print("🔄 Processing GitHub repositories...")
        print("-" * 40)
        
        response = await autorebase_service.process_autorebase(request)
        
        print("\n📊 AutoRebase Results:")
        print("=" * 40)
        print(f"Success: {response.success}")
        print(f"Message: {response.message}")
        
        # Show clone results
        if response.clone_results:
            print(f"\n📥 Clone Results:")
            for key, clone_result in response.clone_results.items():
                print(f"  {key}:")
                print(f"    Success: {clone_result.success}")
                print(f"    Message: {clone_result.message}")
                print(f"    Directory: {clone_result.directory}")
                print(f"    SHA: {clone_result.sha}")
                if clone_result.error:
                    print(f"    Error: {clone_result.error}")
        
        # Show autorebase results
        if response.autorebase_results:
            autorebase_result = response.autorebase_results
            print(f"\n🔄 AutoRebase Results:")
            print(f"  Success: {autorebase_result.success}")
            print(f"  Message: {autorebase_result.message}")
            
            if autorebase_result.details:
                details = autorebase_result.details
                print(f"\n📈 Detailed Results:")
                print(f"  Base 0 Dir: {details.get('base_0_dir', 'N/A')}")
                print(f"  Base 1 Dir: {details.get('base_1_dir', 'N/A')}")
                print(f"  Feature 0 Dir: {details.get('feature_0_dir', 'N/A')}")
                print(f"  Files Processed: {details.get('files_processed', 'N/A')}")
                print(f"  Patches Generated: {details.get('patches_generated', 'N/A')}")
                
                # Show step1 results
                if 'step1_results' in details:
                    step1 = details['step1_results']
                    print(f"\n🔧 Step 1 Results:")
                    print(f"  Success: {step1.get('success', 'N/A')}")
                    print(f"  Applied Patches: {step1.get('applied_patches', 'N/A')}")
                    print(f"  Failed Patches: {step1.get('failed_patches', 'N/A')}")
                    
                    if 'applied_to_files' in step1:
                        print(f"  ✅ Applied to files:")
                        for file in step1['applied_to_files']:
                            print(f"    - {file}")
                    
                    if 'failed_on_files' in step1:
                        print(f"  ❌ Failed on files:")
                        for file in step1['failed_on_files']:
                            print(f"    - {file}")
                
                # Show changelog summary
                if 'changelog' in details:
                    changelog = details['changelog']
                    print(f"\n📋 Changelog Summary:")
                    print(f"  Files Processed: {changelog.get('files_processed', 'N/A')}")
                    print(f"  Patches Generated: {changelog.get('patches_generated', 'N/A')}")
                    print(f"  Patches Applied: {changelog.get('patches_applied', 'N/A')}")
                    print(f"  Backup Files (.orig): {len(changelog.get('backup_files', []))}")
                    print(f"  Reject Files (.rej): {len(changelog.get('reject_files', []))}")
                    print(f"  3-way Merge Calls: {len(changelog.get('three_way_merges', []))}")
                    
                    # Show 3-way merge attempts
                    if 'three_way_merges' in changelog:
                        print(f"\n🔀 3-way Merge Attempts:")
                        for merge in changelog['three_way_merges']:
                            status = merge.get('status', 'unknown')
                            target_file = merge.get('target_file', 'unknown')
                            patch_name = merge.get('patch_name', 'unknown')
                            
                            if status == 'success':
                                conflict_type = merge.get('conflict_type', 'unknown')
                                changes_applied = merge.get('changes_applied', [])
                                print(f"  ✅ {target_file} (patch: {patch_name}) - AI resolved")
                                print(f"     Conflict type: {conflict_type}")
                                print(f"     Changes applied: {changes_applied}")
                            elif status == 'fallback_ai_failed':
                                error = merge.get('error', 'unknown')
                                print(f"  ❌ {target_file} (patch: {patch_name}) - AI failed: {error}")
                            elif status == 'fallback_no_requirements':
                                print(f"  ⚠️  {target_file} (patch: {patch_name}) - No requirements found")
                            elif status == 'fallback_exception':
                                error = merge.get('error', 'unknown')
                                print(f"  ❌ {target_file} (patch: {patch_name}) - Exception: {error}")
                            else:
                                print(f"  🔄 {target_file} (patch: {patch_name}) - Status: {status}")
                
                # Show changelog path
                if 'changelog_path' in details:
                    print(f"\n📄 Changelog saved to: {details['changelog_path']}")
                
                # Show PR results if available
                if 'pr_results' in details:
                    pr_results = details['pr_results']
                    print(f"\n🚀 PR Creation Results:")
                    print(f"  Success: {pr_results.get('success', 'N/A')}")
                    print(f"  Message: {pr_results.get('message', 'N/A')}")
                    
                    if pr_results.get('success'):
                        pr_details = pr_results.get('details', {})
                        print(f"  New Branch: {pr_details.get('new_branch', 'N/A')}")
                        print(f"  Base Branch: {pr_details.get('base_branch', 'N/A')}")
                        print(f"  Files Copied: {len(pr_details.get('files_copied', []))}")
                        print(f"  Commit Hash: {pr_details.get('commit_hash', 'N/A')}")
                        print(f"  PR URL: {pr_details.get('pr_url', 'N/A')}")
                        print(f"  PR Number: {pr_details.get('pr_number', 'N/A')}")
                        
                        if pr_details.get('files_copied'):
                            print(f"  📋 Files in PR:")
                            for file in pr_details['files_copied'][:10]:  # Show first 10 files
                                print(f"    - {file}")
                            if len(pr_details['files_copied']) > 10:
                                print(f"    ... and {len(pr_details['files_copied']) - 10} more files")
                    else:
                        print(f"  Error: {pr_results.get('error', 'N/A')}")
        
        # Show error if any
        if response.error:
            print(f"\n❌ Error: {response.error}")
        
        # Check for generated files
        print(f"\n🔍 Checking for generated files...")
        work_dir = Path(response.work_dir)
        if work_dir.exists():
            feature_51_dir = work_dir / "feature-5.1"
            if feature_51_dir.exists():
                print(f"  📦 Feature-5.1 directory created:")
                for file_path in feature_51_dir.rglob("*"):
                    if file_path.is_file():
                        print(f"    - {file_path}")
            else:
                print(f"  ❌ Feature-5.1 directory not found")
        else:
            print(f"  ❌ Data directory not found")
        
        print(f"\n✅ GitHub repository test completed!")
        
        return response
        
    except Exception as e:
        print(f"❌ Error during GitHub repository test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the test
    response = asyncio.run(test_github_repos())
    
    if response:
        print(f"\n🎯 Test Summary:")
        print(f"  Success: {response.success}")
        print(f"  Message: {response.message}")
    else:
        print(f"\n❌ Test failed")
