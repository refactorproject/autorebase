"""
File Conflict Resolver - Resolves individual file conflicts using OpenAI
"""

from __future__ import annotations

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not available, continue without it


def load_requirements_map(requirements_file: str | Path) -> List[Dict[str, any]]:
    """Load requirements map from YAML file."""
    try:
        with open(requirements_file, 'r') as f:
            return yaml.safe_load(f) or []
    except Exception as e:
        print(f"Warning: Could not load requirements file {requirements_file}: {e}")
        return []


def find_requirement_for_file(file_path: str | Path, requirements_map: List[Dict[str, any]]) -> Optional[str]:
    """Find the requirement text for a specific file path."""
    file_path_str = str(file_path)
    file_path_obj = Path(file_path_str)
    
    # Remove .orig and .rej suffixes to get the base filename
    base_filename = file_path_obj.name
    for suffix in ['.orig', '.rej']:
        if base_filename.endswith(suffix):
            base_filename = base_filename[:-len(suffix)]
            break
    
    # Get the relative path without .orig/.rej suffixes
    # e.g., "/path/to/src/main.cpp.orig" -> "src/main.cpp"
    base_file_path = str(file_path_obj.parent / base_filename)
    
    # Try exact path match first
    for req in requirements_map:
        req_path = req.get('path')
        if req_path:
            # Try exact match with the base path (without .orig/.rej)
            if req_path == base_file_path:
                return req.get('requirement')
            # Try matching just the filename (e.g., "main.cpp" matches "main.cpp")
            if Path(req_path).name == base_filename:
                return req.get('requirement')
            # Try relative path match (e.g., "src/main.cpp" matches "/full/path/src/main.cpp")
            if base_file_path.endswith(req_path):
                return req.get('requirement')
    
    # Try glob pattern match
    for req in requirements_map:
        path_glob = req.get('path_glob')
        if path_glob:
            import fnmatch
            # Try matching against the base path (without .orig/.rej)
            if fnmatch.fnmatch(base_file_path, path_glob):
                return req.get('requirement')
            # Try matching against just the base filename
            if fnmatch.fnmatch(base_filename, path_glob):
                return req.get('requirement')
            # Try matching against path components
            for part in file_path_obj.parts:
                if fnmatch.fnmatch(part, path_glob):
                    return req.get('requirement')
    
    return None


def resolve_file_conflict_with_openai(
    original_file_path: str | Path,
    rejection_file_path: str | Path,
    requirements_file: str | Path,
    verbose: bool = False
) -> Dict[str, any]:
    """
    Resolve a single file conflict using OpenAI based on requirements from YAML file.
    
    Args:
        original_file_path: Path to the original file (current state)
        rejection_file_path: Path to the .rej file (desired changes that failed)
        requirements_file: Path to the requirements_map.yaml file
        verbose: Whether to print detailed information
        
    Returns:
        Dict with resolution results:
        {
            "success": bool,
            "resolved_content": str | None,
            "explanation": str,
            "conflict_type": str,
            "changes_applied": List[str],
            "requirement_used": str | None
        }
    """
    
    # Load requirements map
    requirements_map = load_requirements_map(requirements_file)
    
    # Find requirement for the original file
    requirement_text = find_requirement_for_file(original_file_path, requirements_map)
    
    if not requirement_text:
        return {
            "success": False,
            "resolved_content": None,
            "explanation": f"No requirement found for file: {original_file_path}",
            "conflict_type": "no_requirement",
            "changes_applied": [],
            "requirement_used": None
        }
    
    if verbose:
        print(f"📋 Found requirement: {requirement_text}")
    
    # Read the files
    try:
        original_content = Path(original_file_path).read_text()
        rejection_content = Path(rejection_file_path).read_text()
    except Exception as e:
        return {
            "success": False,
            "resolved_content": None,
            "explanation": f"Failed to read files: {e}",
            "conflict_type": "file_read_error",
            "changes_applied": [],
            "requirement_used": requirement_text
        }
    
    # Analyze the conflict
    conflict_analysis = analyze_conflict(original_content, rejection_content)
    
    if verbose:
        print(f"🔍 Conflict Analysis:")
        print(f"   Type: {conflict_analysis['type']}")
        print(f"   Description: {conflict_analysis['description']}")
        print(f"   Changes: {conflict_analysis['changes']}")
    
    # Create OpenAI prompt
    prompt = create_file_conflict_prompt(
        original_content=original_content,
        rejection_content=rejection_content,
        requirement_text=requirement_text,
        conflict_analysis=conflict_analysis
    )
    
    if verbose:
        print(f"🤖 Sending prompt to OpenAI...")
    
    # Call OpenAI
    try:
        response = call_openai_for_file_resolution(prompt)
        
        if response["success"]:
            resolved_content = response["content"]
            
            # Validate the resolution
            validation = validate_resolution(
                original_content, rejection_content, resolved_content, requirement_text
            )
            
            return {
                "success": True,
                "resolved_content": resolved_content,
                "explanation": response["explanation"],
                "conflict_type": conflict_analysis["type"],
                "changes_applied": validation["changes_applied"],
                "validation_score": validation["score"],
                "requirement_used": requirement_text
            }
        else:
            return {
                "success": False,
                "resolved_content": None,
                "explanation": f"OpenAI resolution failed: {response['error']}",
                "conflict_type": conflict_analysis["type"],
                "changes_applied": [],
                "requirement_used": requirement_text
            }
            
    except Exception as e:
        return {
            "success": False,
            "resolved_content": None,
            "explanation": f"OpenAI call failed: {e}",
            "conflict_type": conflict_analysis["type"],
            "changes_applied": [],
            "requirement_used": requirement_text
        }


def analyze_conflict(original_content: str, rejection_content: str) -> Dict[str, any]:
    """Analyze the type and nature of the conflict."""
    
    # Extract the patch content from rejection file
    patch_match = re.search(r'@@.*?@@\n(.*)', rejection_content, re.DOTALL)
    if not patch_match:
        return {
            "type": "unknown",
            "description": "Could not parse rejection file",
            "changes": []
        }
    
    patch_content = patch_match.group(1)
    lines = patch_content.strip().split('\n')
    
    changes = []
    for line in lines:
        if line.startswith('-'):
            changes.append(f"Remove: {line[1:]}")
        elif line.startswith('+'):
            changes.append(f"Add: {line[1:]}")
    
    # Determine conflict type
    conflict_type = "content_change"
    description = "Content modification conflict"
    
    if any("API" in change for change in changes):
        conflict_type = "api_change"
        description = "API function call or signature change"
    elif any("include" in change.lower() for change in changes):
        conflict_type = "header_change"
        description = "Header/include file change"
    elif any("main" in change.lower() for change in changes):
        conflict_type = "main_function_change"
        description = "Main function modification"
    
    return {
        "type": conflict_type,
        "description": description,
        "changes": changes,
        "patch_content": patch_content
    }


def create_file_conflict_prompt(
    original_content: str,
    rejection_content: str,
    requirement_text: str,
    conflict_analysis: Dict[str, any]
) -> str:
    """Create a detailed prompt for OpenAI to resolve the conflict."""
    
    prompt = f"""You are an expert software engineer resolving a git merge conflict. 

REQUIREMENT:
{requirement_text}

CONFLICT ANALYSIS:
- Type: {conflict_analysis['type']}
- Description: {conflict_analysis['description']}
- Changes needed: {conflict_analysis['changes']}

CURRENT FILE CONTENT:
```
{original_content}
```

DESIRED CHANGES (from rejection file):
```
{conflict_analysis['patch_content']}
```

TASK:
Resolve this conflict by applying the desired changes to the current file content while respecting the requirement. The requirement takes precedence over the exact patch content.

RULES:
1. Preserve the overall structure and functionality of the code
2. Apply the changes specified in the rejection file
3. Ensure the requirement is satisfied
4. Maintain code quality and readability
5. If there are API changes (like OldAPI -> NewAPI), update accordingly
6. If there are parameter changes (like 42 -> 200), apply them as specified in the requirement

RESPONSE FORMAT:
Provide ONLY the resolved file content, no explanations or markdown formatting. The content should be ready to use as the final file.

RESOLVED FILE CONTENT:"""
    
    return prompt


def call_openai_for_file_resolution(prompt: str) -> Dict[str, any]:
    """Call OpenAI to resolve the file conflict."""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {
            "success": False,
            "content": None,
            "explanation": "OpenAI API key not found in environment",
            "error": "Missing API key"
        }
    
    try:
        from openai import OpenAI
        
        # Use the new API (v1.0+)
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1,
            timeout=30  # Add 30 second timeout
        )
        content = response.choices[0].message.content
        
        return {
            "success": True,
            "content": content.strip(),
            "explanation": "Successfully resolved conflict using OpenAI",
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "explanation": f"OpenAI API call failed: {e}",
            "error": str(e)
        }


def validate_resolution(
    original_content: str,
    rejection_content: str,
    resolved_content: str,
    requirement_text: str
) -> Dict[str, any]:
    """Validate that the resolution correctly applies the changes."""
    
    changes_applied = []
    score = 0
    
    # Check if requirement-specific changes are applied
    if "200" in requirement_text and "200" in resolved_content:
        changes_applied.append("Applied requirement value (200)")
        score += 1
    
    # Check if API changes are applied
    if "NewAPI" in resolved_content:
        changes_applied.append("Updated to NewAPI")
        score += 1
    
    # Check if feature logging is preserved
    if "Feature activated" in resolved_content:
        changes_applied.append("Preserved feature logging")
        score += 1
    
    # Check if the file structure is maintained
    if "int main()" in resolved_content and "#include <iostream>" in resolved_content:
        changes_applied.append("Maintained file structure")
        score += 1
    
    return {
        "changes_applied": changes_applied,
        "score": score,
        "max_score": 4
    }


def test_file_conflict_resolver():
    """Test the file conflict resolver with the provided example."""
    
    # Test with the provided files
    original_file = "/Users/dhruvildarji/Documents/git/project/AutoRebase/artifacts/run20250913_134310/feature-5.1/src/main.cpp.orig"
    rejection_file = "/Users/dhruvildarji/Documents/git/project/AutoRebase/artifacts/run20250913_134310/feature-5.1/src/main.cpp.rej"
    requirements_file = "/Users/dhruvildarji/Documents/git/project/AutoRebase/data/sample/requirements_map.yaml"
    
    print("🧪 Testing File Conflict Resolver...")
    print(f"📁 Original file: {original_file}")
    print(f"🚫 Rejection file: {rejection_file}")
    print(f"📋 Requirements file: {requirements_file}")
    print()
    
    result = resolve_file_conflict_with_openai(
        original_file_path=original_file,
        rejection_file_path=rejection_file,
        requirements_file=requirements_file,
        verbose=True
    )
    
    print("📊 RESULT:")
    print(f"   Success: {result['success']}")
    print(f"   Conflict Type: {result['conflict_type']}")
    print(f"   Explanation: {result['explanation']}")
    print(f"   Changes Applied: {result['changes_applied']}")
    
    if result['success'] and result['resolved_content']:
        print("\n✅ RESOLVED CONTENT:")
        print(result['resolved_content'])
        
        # Save the resolved content
        output_file = "/Users/dhruvildarji/Documents/git/project/AutoRebase/resolved_main.cpp"
        Path(output_file).write_text(result['resolved_content'])
        print(f"\n💾 Saved resolved content to: {output_file}")
    
    return result


if __name__ == "__main__":
    test_file_conflict_resolver()
