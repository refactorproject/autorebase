#!/usr/bin/env python3

import sys
import os
import json
import asyncio

# Add the api directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from services.autorebase_service import AutoRebaseService
from models.autorebase_models import AutoRebaseRequest

async def test_autorebase():
    if len(sys.argv) != 2:
        print(json.dumps({"success": False, "message": "Usage: python test_mcp_autorebase.py <request_json>"}))
        return
    
    try:
        # Parse the request
        request_data = json.loads(sys.argv[1])
        
        # Create the request object
        autorebase_request = AutoRebaseRequest(**request_data)
        
        # Initialize the service
        service = AutoRebaseService()
        
        # Process the autorebase
        result = await service.process_autorebase(autorebase_request)
        
        # Check what attributes exist
        print("Available attributes:", dir(result), file=sys.stderr)
        print("Has resolved_files:", hasattr(result, 'resolved_files'), file=sys.stderr)
        print("Has processing_details:", hasattr(result, 'processing_details'), file=sys.stderr)
        
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
            "clone_results": getattr(result, 'clone_results', None),
            "autorebase_results": getattr(result, 'autorebase_results', None)
        }
        
        print(json.dumps(result_dict))
        
    except Exception as e:
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
    asyncio.run(test_autorebase())
