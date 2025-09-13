#!/usr/bin/env python3
"""
Validation script to check if patch application results are correct.
"""

import os
import shutil
from pathlib import Path
from engine.core.ai_resolve import resolve_rejects

def validate_and_fix_patch_result():
    """Validate patch results and fix if needed."""
    
    # Check the latest run
    latest_run = None
    for run_dir in Path("artifacts").iterdir():
        if run_dir.is_dir() and run_dir.name.startswith("run"):
            latest_run = run_dir
    
    # Also check for other run patterns
    if not latest_run:
        for run_dir in Path("artifacts").iterdir():
            if run_dir.is_dir() and "run" in run_dir.name:
                latest_run = run_dir
                break
    
    if not latest_run:
        print("No runs found in artifacts/")
        return
    
    print(f"🔍 Checking run: {latest_run}")
    
    # Check main.cpp
    main_cpp = latest_run / "feature-5.1" / "src" / "main.cpp"
    if not main_cpp.exists():
        print("❌ main.cpp not found")
        return
    
    content = main_cpp.read_text()
    print(f"📄 Current main.cpp content:\n{content}")
    
    # Check if feature customizations are present
    has_feature_logging = "Feature activated" in content
    has_parameter_200 = "200" in content
    uses_new_api = "NewAPI" in content
    
    print(f"\n📋 Validation results:")
    print(f"  ✅ Has feature logging: {has_feature_logging}")
    print(f"  ✅ Has parameter 200: {has_parameter_200}")
    print(f"  ✅ Uses NewAPI: {uses_new_api}")
    
    if has_feature_logging and has_parameter_200 and uses_new_api:
        print("🎉 All feature customizations are present!")
        return
    
    print("\n❌ Missing feature customizations. Let's fix this...")
    
    # Check for .rej files
    rej_files = list(latest_run.rglob("*.rej"))
    print(f"🔍 Found {len(rej_files)} rejection files")
    
    if rej_files:
        print("🤖 Applying AI resolution...")
        requirements = ["Feature: While calling API we need to pass 200 as input"]
        remaining = resolve_rejects(rej_files, requirements)
        
        if not remaining:
            print("✅ AI resolution successful!")
            # Check the result
            new_content = main_cpp.read_text()
            print(f"📄 Updated main.cpp content:\n{new_content}")
        else:
            print(f"❌ AI resolution failed. Remaining rejects: {len(remaining)}")
    else:
        print("❌ No rejection files found. Manual intervention needed.")

if __name__ == "__main__":
    validate_and_fix_patch_result()
