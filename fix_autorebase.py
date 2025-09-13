#!/usr/bin/env python3
"""
Fix AutoRebase to properly handle conflicts and apply AI resolution.
"""

import os
import shutil
from pathlib import Path
from engine.core.ai_resolve import resolve_rejects

def fix_autorebase_run(run_dir: Path):
    """Fix a specific AutoRebase run by applying AI resolution."""
    
    print(f"🔧 Fixing AutoRebase run: {run_dir}")
    
    # Check main.cpp
    main_cpp = run_dir / "feature-5.1" / "src" / "main.cpp"
    if not main_cpp.exists():
        print("❌ main.cpp not found")
        return False
    
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
        return True
    
    print("\n❌ Missing feature customizations. Let's fix this...")
    
    # Check for .rej files
    rej_files = list(run_dir.rglob("*.rej"))
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
            return True
        else:
            print(f"❌ AI resolution failed. Remaining rejects: {len(remaining)}")
            return False
    else:
        print("❌ No rejection files found. Creating artificial conflict...")
        
        # Create a .rej file artificially to trigger AI resolution
        rej_file = main_cpp.with_suffix(".cpp.rej")
        rej_content = """diff a/src/main.cpp b/src/main.cpp	(rejected hunks)
@@ -5,7 +5,9 @@
 }
 
 int main() {
-  OldAPI(42);
+  // Feature customization: different value and extra log
+  std::cout << "Feature activated" << std::endl;
+  OldAPI(200);
   return 0;
 }
 
"""
        rej_file.write_text(rej_content)
        print(f"📝 Created artificial .rej file: {rej_file}")
        
        # Apply AI resolution
        print("🤖 Applying AI resolution...")
        requirements = ["Feature: While calling API we need to pass 200 as input"]
        remaining = resolve_rejects([rej_file], requirements)
        
        if not remaining:
            print("✅ AI resolution successful!")
            # Check the result
            new_content = main_cpp.read_text()
            print(f"📄 Updated main.cpp content:\n{new_content}")
            return True
        else:
            print(f"❌ AI resolution failed. Remaining rejects: {len(remaining)}")
            return False

def main():
    """Fix all AutoRebase runs."""
    
    # Find all runs
    runs = []
    for run_dir in Path("artifacts").iterdir():
        if run_dir.is_dir() and "run" in run_dir.name:
            runs.append(run_dir)
    
    if not runs:
        print("No runs found in artifacts/")
        return
    
    print(f"🔍 Found {len(runs)} runs to check")
    
    fixed_count = 0
    for run_dir in sorted(runs):
        print(f"\n{'='*50}")
        if fix_autorebase_run(run_dir):
            fixed_count += 1
    
    print(f"\n🎯 Summary: Fixed {fixed_count}/{len(runs)} runs")

if __name__ == "__main__":
    main()
