#!/usr/bin/env python3
"""
Standalone script to run AutoRebase from MCP server
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add the parent directory (autorebase) to Python path to access the main API
current_dir = Path(__file__).parent
parent_dir = current_dir.parent  # This is the autorebase directory
sys.path.insert(0, str(parent_dir))

# Also add the parent directory to PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(parent_dir) + ':' + os.environ.get('PYTHONPATH', '')

# Change to the parent directory to ensure imports work correctly
os.chdir(parent_dir)

from api.services.autorebase_service import AutoRebaseService
from api.models.autorebase_models import AutoRebaseRequest

async def main():
    try:
        # Parse the request from command line arguments
        if len(sys.argv) < 2:
            print(json.dumps({
                "success": False,
                "message": "No request data provided"
            }))
            return
            
        request_data = json.loads(sys.argv[1])
        
        # Create the request object
        autorebase_request = AutoRebaseRequest(**request_data)
        
        # Initialize the service
        service = AutoRebaseService()
        
        # Set GitHub token if provided
        github_token = request_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        use_ssh = request_data.get('use_ssh', False)
        
        if use_ssh:
            os.environ['SSH_OVERRIDE'] = 'true'
        elif github_token:
            os.environ['GITHUB_TOKEN'] = github_token
        
        # Redirect stdout to stderr to prevent debug output from breaking JSON parsing
        import contextlib
        from io import StringIO
        
        # Capture stdout and redirect to stderr
        original_stdout = sys.stdout
        sys.stdout = sys.stderr
        
        # Process the autorebase
        result = await service.process_autorebase(autorebase_request)
        
        # Restore stdout and print final JSON result
        sys.stdout = original_stdout
        
        # Convert to dict and return
        result_dict = {
            "success": result.success,
            "message": result.message,
            "base_software_0": result.base_software_0,
            "base_software_1": result.base_software_1,
            "feature_software_0": result.feature_software_0,
            "base_repo_url": result.base_repo_url,
            "feature_repo_url": result.feature_repo_url,
            "work_dir": result.work_dir,
            "resolved_files": getattr(result, 'resolved_files', []),
            "processing_details": getattr(result, 'processing_details', None),
            "clone_results": {k: v.dict() if hasattr(v, 'dict') else v for k, v in (getattr(result, 'clone_results', {}) or {}).items()},
            "autorebase_results": getattr(result, 'autorebase_results', None).dict() if getattr(result, 'autorebase_results', None) and hasattr(getattr(result, 'autorebase_results', None), 'dict') else getattr(result, 'autorebase_results', None),
            "pr_results": getattr(result, 'pr_results', None)
        }
        
        # Add changelog information if available
        if hasattr(result, 'autorebase_results') and result.autorebase_results and hasattr(result.autorebase_results.details, 'changelog'):
            result_dict["changelog"] = result.autorebase_results.details.changelog
        if hasattr(result, 'autorebase_results') and result.autorebase_results and hasattr(result.autorebase_results.details, 'changelog_path'):
            result_dict["changelog_path"] = result.autorebase_results.details.changelog_path
        
        print(json.dumps(result_dict))

    except Exception as e:
        # Restore stdout in case of error
        if 'original_stdout' in locals():
            sys.stdout = original_stdout
        
        error_result = {
            "success": False,
            "message": f"Python execution error: {str(e)}",
            "base_software_0": request_data.get("base_software_0", ""),
            "base_software_1": request_data.get("base_software_1", ""),
            "feature_software_0": request_data.get("feature_software_0", ""),
            "base_repo_url": request_data.get("base_repo_url", ""),
            "feature_repo_url": request_data.get("feature_repo_url", ""),
            "resolved_files": [],
            "processing_details": None
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    asyncio.run(main())
