#!/usr/bin/env python3
"""
Test script to run complete AutoRebase process on sample data
"""

import asyncio
from pathlib import Path
from api.autorebase.core import AutoRebase

async def test_autorebase_sample():
    """Test the complete AutoRebase process with sample data"""
    
    print("🚀 Testing Complete AutoRebase Process")
    print("=" * 50)
    
    # Set up directories (simulating cloned repositories)
    base_0_dir = Path("data/sample/base-1.0")
    base_1_dir = Path("data/sample/base-1.1") 
    feature_0_dir = Path("data/sample/feature-5.0")
    work_dir = Path("data/sample")
    
    print(f"📁 Working with sample data:")
    print(f"  Base 0: {base_0_dir}")
    print(f"  Base 1: {base_1_dir}")
    print(f"  Feature 0: {feature_0_dir}")
    print(f"  Work Dir: {work_dir}")
    
    # Check if directories exist
    missing_dirs = []
    for dir_path, name in [(base_0_dir, "Base 0"), (base_1_dir, "Base 1"), (feature_0_dir, "Feature 0")]:
        if not dir_path.exists():
            missing_dirs.append(f"{name}: {dir_path}")
    
    if missing_dirs:
        print(f"❌ Missing directories:")
        for missing in missing_dirs:
            print(f"  - {missing}")
        return
    
    print("✅ All directories found")
    
    # Initialize AutoRebase
    print(f"\n🔧 Initializing AutoRebase...")
    autorebase = AutoRebase(work_dir=str(work_dir))
    
    # Override the directory paths to point to our sample data
    autorebase.base_0_dir = base_0_dir
    autorebase.base_1_dir = base_1_dir
    autorebase.feature_0_dir = feature_0_dir
    
    print(f"  Base 0 Dir: {autorebase.base_0_dir}")
    print(f"  Base 1 Dir: {autorebase.base_1_dir}")
    print(f"  Feature 0 Dir: {autorebase.feature_0_dir}")
    
    # Run the complete AutoRebase process
    print(f"\n🔄 Running AutoRebase process...")
    print("-" * 30)
    
    try:
        result = await autorebase.run_autorebase()
        
        print(f"\n📊 AutoRebase Results:")
        print(f"  Success: {result['success']}")
        print(f"  Message: {result['message']}")
        
        if 'details' in result:
            details = result['details']
            print(f"\n📈 Detailed Results:")
            print(f"  Files processed: {details.get('files_processed', 0)}")
            print(f"  Patches generated: {details.get('patches_generated', 0)}")
            
            # Step 1 results
            if 'step1_results' in details:
                step1 = details['step1_results']
                print(f"\n  Step 1 (base_0 -> feature_0 patches to base_1):")
                print(f"    Success: {step1.get('success', False)}")
                print(f"    Applied patches: {len(step1.get('applied_patches', []))}")
                print(f"    Failed patches: {len(step1.get('failed_patches', []))}")
                
                if step1.get('applied_patches'):
                    print(f"    Applied to files:")
                    for file in step1['applied_patches']:
                        print(f"      ✅ {file}")
                
                if step1.get('failed_patches'):
                    print(f"    Failed on files:")
                    for file in step1['failed_patches']:
                        print(f"      ❌ {file}")
            
            # Step 2 results
            if 'step2_results' in details:
                step2 = details['step2_results']
                print(f"\n  Step 2 (base_0 -> base_1 patches to feature_0):")
                print(f"    Success: {step2.get('success', False)}")
                print(f"    Applied patches: {len(step2.get('applied_patches', []))}")
                print(f"    Failed patches: {len(step2.get('failed_patches', []))}")
                
                if step2.get('applied_patches'):
                    print(f"    Applied to files:")
                    for file in step2['applied_patches']:
                        print(f"      ✅ {file}")
                
                if step2.get('failed_patches'):
                    print(f"    Failed on files:")
                    for file in step2['failed_patches']:
                        print(f"      ❌ {file}")
            
            # Changelog summary
            if 'changelog' in details:
                changelog = details['changelog']
                print(f"\n📋 Changelog Summary:")
                print(f"  Files processed: {len(changelog.get('files_processed', []))}")
                print(f"  Patches generated: {len(changelog.get('patches_generated', []))}")
                print(f"  Patches applied: {len(changelog.get('patches_applied', []))}")
                print(f"  Backup files (.orig): {len(changelog.get('backup_files', []))}")
                print(f"  Reject files (.rej): {len(changelog.get('reject_files', []))}")
                print(f"  3-way merge calls: {len(changelog.get('three_way_merges', []))}")
                
                # Show files processed
                if changelog.get('files_processed'):
                    print(f"\n  Files processed:")
                    for file in changelog['files_processed']:
                        print(f"    📄 {file}")
                
                # Show 3-way merge details
                if changelog.get('three_way_merges'):
                    print(f"\n  🔀 3-way merge attempts:")
                    for merge in changelog['three_way_merges']:
                        status = merge.get('status', 'unknown')
                        if status == 'success':
                            print(f"    ✅ {merge['target_file']} (patch: {merge['patch_name']}) - AI resolved")
                            print(f"       Conflict type: {merge.get('conflict_type', 'unknown')}")
                            print(f"       Changes applied: {merge.get('changes_applied', [])}")
                        elif status == 'failed':
                            print(f"    ❌ {merge['target_file']} (patch: {merge['patch_name']}) - AI failed")
                            print(f"       Error: {merge.get('error', 'unknown')}")
                        elif status == 'failed_no_requirements':
                            print(f"    ⚠️  {merge['target_file']} (patch: {merge['patch_name']}) - No requirements found")
                        else:
                            print(f"    🔄 {merge['target_file']} (patch: {merge['patch_name']}) - Status: {status}")
            
            # Changelog file location
            if 'changelog_path' in details:
                print(f"\n📄 Changelog saved to: {details['changelog_path']}")
        
        # Check for generated files
        print(f"\n🔍 Checking for generated files...")
        
        # Check for .orig files in feature-5.1 directory
        f1_dir = Path("data/sample/feature-5.1")
        orig_files = []
        if f1_dir.exists():
            orig_files.extend(list(f1_dir.rglob("*.orig")))
        
        if orig_files:
            print(f"  📦 Backup files (.orig) created:")
            for orig_file in orig_files:
                print(f"    - {orig_file}")
        else:
            print(f"  ℹ️  No backup files (.orig) found")
        
        # Check for .rej files in feature-5.1 directory
        rej_files = []
        if f1_dir.exists():
            rej_files.extend(list(f1_dir.rglob("*.rej")))
        
        if rej_files:
            print(f"  🚫 Reject files (.rej) created:")
            for rej_file in rej_files:
                print(f"    - {rej_file}")
        else:
            print(f"  ℹ️  No reject files (.rej) found")
        
        # Check for created f1 files
        f1_files = []
        if f1_dir.exists():
            f1_files = [f for f in f1_dir.rglob("*") if f.is_file() and not f.name.endswith(('.orig', '.rej', '.patch'))]
        
        if f1_files:
            print(f"  📄 F1 files created:")
            for f1_file in f1_files:
                print(f"    - {f1_file}")
        else:
            print(f"  ℹ️  No f1 files created")
        
        print(f"\n✅ AutoRebase test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ AutoRebase test failed with error:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_autorebase_sample())
