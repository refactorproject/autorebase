#!/usr/bin/env python3
"""
Force conflict test to demonstrate the complete workflow.
"""

import os
import shutil
import subprocess
from pathlib import Path
from engine.core.ai_resolve import resolve_rejects

def force_conflict_test():
    """Force a conflict and test AI resolution."""
    
    # Setup test environment
    test_dir = Path("force_conflict_test")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Copy new base to test directory
    shutil.copytree("data/sample/base-1.1", test_dir)
    
    print("🚀 Force Conflict Test")
    print(f"📁 Test directory: {test_dir}")
    print()
    
    # Show initial state
    main_cpp = test_dir / "src" / "main.cpp"
    print("📄 Initial state:")
    print(main_cpp.read_text())
    print()
    
    # Create a patch that will definitely conflict
    patch_content = """--- main.cpp	2025-09-13 12:12:50
+++ main.cpp	2025-09-13 12:13:08
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
    
    patch_file = test_dir / "src" / "conflict.patch"
    patch_file.write_text(patch_content)
    
    # Apply patch with rejection
    print("📋 Applying conflicting patch...")
    try:
        result = subprocess.run(
            ["git", "apply", "--reject", "--no-3way", "-p0", "conflict.patch"],
            cwd=test_dir / "src",
            capture_output=True,
            text=True
        )
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check for rejection files
    rej_files = list(test_dir.rglob("*.rej"))
    print(f"\n🔍 Found {len(rej_files)} rejection files:")
    for rej in rej_files:
        print(f"  - {rej}")
        print(f"Content:\n{rej.read_text()}")
    
    if rej_files:
        # Apply AI resolution
        print("\n🤖 Applying AI resolution...")
        requirements = ["Feature: While calling API we need to pass 200 as input"]
        remaining = resolve_rejects(rej_files, requirements)
        
        print(f"✅ Resolution complete. Remaining rejects: {len(remaining)}")
        
        # Show final result
        print("\n🎯 Final result:")
        print(main_cpp.read_text())
    else:
        print("❌ No rejection files found!")
        print("Current file content:")
        print(main_cpp.read_text())
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("\n🧹 Cleanup complete")

if __name__ == "__main__":
    force_conflict_test()
