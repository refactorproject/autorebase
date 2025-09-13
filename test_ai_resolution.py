#!/usr/bin/env python3
"""
Test script to demonstrate the complete AutoRebase workflow with AI resolution.
This script forces the creation of .rej files and then applies AI resolution.
"""

import os
import shutil
from pathlib import Path
from engine.core.ai_resolve import resolve_rejects
from engine.core.vcs import apply_patch_dir_with_reject

def test_ai_resolution():
    """Test the complete AI resolution workflow."""
    
    # Setup test environment
    test_dir = Path("test_ai_workflow")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Copy new base to test directory
    shutil.copytree("data/sample/base-1.1", test_dir)
    
    print("🚀 Testing AI Resolution Workflow")
    print(f"📁 Test directory: {test_dir}")
    print()
    
    # Apply patches with rejection
    print("📋 Applying feature patches...")
    patch_dir = Path("artifacts/test_final_run/feature_patches")
    rej_files = apply_patch_dir_with_reject(patch_dir, test_dir, strip=1)
    
    print(f"🔍 Found {len(rej_files)} rejection files:")
    for rej in rej_files:
        print(f"  - {rej}")
    
    if not rej_files:
        print("❌ No rejection files found! This means patches applied successfully.")
        print("Let's check what happened...")
        
        # Check the main.cpp file
        main_cpp = test_dir / "src" / "main.cpp"
        if main_cpp.exists():
            print(f"\n📄 Content of {main_cpp}:")
            print(main_cpp.read_text())
        
        return
    
    # Show rejection content
    print("\n📋 Rejection file content:")
    for rej in rej_files:
        print(f"\n--- {rej} ---")
        print(rej.read_text())
    
    # Apply AI resolution
    print("\n🤖 Applying AI resolution...")
    requirements = ["Feature: While calling API we need to pass 200 as input"]
    remaining = resolve_rejects(rej_files, requirements)
    
    print(f"✅ Resolution complete. Remaining rejects: {len(remaining)}")
    
    # Show final result
    print("\n🎯 Final result:")
    main_cpp = test_dir / "src" / "main.cpp"
    if main_cpp.exists():
        print(f"\n📄 Content of {main_cpp}:")
        print(main_cpp.read_text())
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("\n🧹 Cleanup complete")

if __name__ == "__main__":
    test_ai_resolution()
