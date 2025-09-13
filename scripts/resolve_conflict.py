#!/usr/bin/env python3
"""
Simple CLI script to resolve file conflicts using OpenAI
"""

import argparse
import sys
from pathlib import Path

# Add the project root to the path so we can import engine
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.core.file_conflict_resolver import resolve_file_conflict_with_openai


def main():
    parser = argparse.ArgumentParser(description="Resolve file conflicts using OpenAI")
    parser.add_argument("original_file", help="Path to the original file")
    parser.add_argument("rejection_file", help="Path to the .rej file")
    parser.add_argument("requirements_file", help="Path to the requirements_map.yaml file")
    parser.add_argument("-o", "--output", help="Output file path (default: resolved_<original_file>)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        original_path = Path(args.original_file)
        output_file = f"resolved_{original_path.name}"
    
    print("🔧 File Conflict Resolver")
    print(f"📁 Original file: {args.original_file}")
    print(f"🚫 Rejection file: {args.rejection_file}")
    print(f"📋 Requirements file: {args.requirements_file}")
    print(f"💾 Output file: {output_file}")
    print()
    
    # Resolve the conflict
    result = resolve_file_conflict_with_openai(
        original_file_path=args.original_file,
        rejection_file_path=args.rejection_file,
        requirements_file=args.requirements_file,
        verbose=args.verbose
    )
    
    # Print results
    print("📊 RESULT:")
    print(f"   Success: {result['success']}")
    print(f"   Conflict Type: {result['conflict_type']}")
    print(f"   Explanation: {result['explanation']}")
    print(f"   Changes Applied: {result['changes_applied']}")
    if result.get('requirement_used'):
        print(f"   Requirement Used: {result['requirement_used']}")
    
    if result['success'] and result['resolved_content']:
        # Save the resolved content
        Path(output_file).write_text(result['resolved_content'])
        print(f"\n✅ RESOLVED CONTENT SAVED TO: {output_file}")
        print("\n📄 RESOLVED CONTENT:")
        print("-" * 50)
        print(result['resolved_content'])
        print("-" * 50)
        
        return 0
    else:
        print(f"\n❌ FAILED TO RESOLVE CONFLICT")
        print(f"   Error: {result['explanation']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
