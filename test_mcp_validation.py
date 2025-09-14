#!/usr/bin/env python3

import sys
import os
import json
import asyncio
import httpx

async def validate_sha(sha: str, repo_owner: str, repo_name: str):
    """Validate if a GitHub SHA exists in the repository"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{sha}"
            response = await client.get(url)
            
            if response.status_code == 200:
                commit_data = response.json()
                return {
                    "valid": True,
                    "sha": commit_data["sha"],
                    "message": commit_data["commit"]["message"],
                    "author": commit_data["commit"]["author"]["name"],
                    "date": commit_data["commit"]["author"]["date"]
                }
            else:
                return {
                    "valid": False,
                    "error": f"Commit not found: {response.status_code}"
                }
        except httpx.RequestError as e:
            return {
                "valid": False,
                "error": f"Request failed: {str(e)}"
            }

async def main():
    if len(sys.argv) != 3:
        print(json.dumps({"valid": False, "message": "Usage: python test_mcp_validation.py <repo_url> <sha_or_tag>"}))
        return
    
    repo_url = sys.argv[1]
    sha_or_tag = sys.argv[2]
    
    # Extract repo info
    if 'github.com' not in repo_url:
        result = {
            "valid": False,
            "message": "Only GitHub repositories are supported"
        }
        print(json.dumps(result))
        return
        
    # Extract owner and repo name
    parts = repo_url.replace('.git', '').split('/')
    if len(parts) < 2:
        result = {
            "valid": False,
            "message": "Invalid repository URL format"
        }
        print(json.dumps(result))
        return
        
    owner = parts[-2]
    repo_name = parts[-1]
    
    # Validate the SHA/tag
    validation_result = await validate_sha(sha_or_tag, owner, repo_name)
    
    result = {
        "valid": validation_result.get("valid", False),
        "message": validation_result.get("error", "Validation completed"),
        "sha": validation_result.get("sha"),
        "commit_message": validation_result.get("message"),
        "author": validation_result.get("author"),
        "date": validation_result.get("date")
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(main())
