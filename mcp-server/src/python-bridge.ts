import { spawn } from 'child_process';
import { promisify } from 'util';
import { AutoRebaseRequest, AutoRebaseResponse } from './types.js';

/**
 * Python bridge for calling AutoRebase functionality
 */
export class PythonBridge {
  private pythonPath: string;
  private autorebasePath: string;

  constructor() {
    this.pythonPath = 'python3'; // Default to python3
    this.autorebasePath = '../api/services/autorebase_service.py'; // Relative to mcp-server
  }

  /**
   * Call the AutoRebase service via Python
   */
  async callAutoRebase(request: AutoRebaseRequest): Promise<AutoRebaseResponse> {
    return new Promise((resolve, reject) => {
      const pythonScript = `
import sys
import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the api directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'api'))

from services.autorebase_service import AutoRebaseService
from models.autorebase_models import AutoRebaseRequest

async def main():
    try:
        # Parse the request
        request_data = json.loads(sys.argv[1])
        
        # Create the request object
        autorebase_request = AutoRebaseRequest(**request_data)
        
        # Initialize the service
        service = AutoRebaseService()
        
        # Set GitHub token if provided
        github_token = request_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        if github_token:
            os.environ['GITHUB_TOKEN'] = github_token
            print(f"Using GitHub token: {github_token[:8]}...", file=sys.stderr)
        else:
            print("No GitHub token provided, using local credentials", file=sys.stderr)
        
        # Process the autorebase
        result = await service.process_autorebase(autorebase_request)
        
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
            "autorebase_results": getattr(result, 'autorebase_results', None).dict() if getattr(result, 'autorebase_results', None) and hasattr(getattr(result, 'autorebase_results', None), 'dict') else getattr(result, 'autorebase_results', None)
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
    asyncio.run(main())
`;

      const pythonProcess = spawn(this.pythonPath, ['-c', pythonScript, JSON.stringify(request)], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python process exited with code ${code}: ${stderr}`));
          return;
        }

        try {
          const result = JSON.parse(stdout.trim());
          resolve(result);
        } catch (error) {
          reject(new Error(`Failed to parse Python output: ${error}\nOutput: ${stdout}`));
        }
      });

      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error}`));
      });
    });
  }

  /**
   * Validate a repository and SHA/tag
   */
  async validateRepository(repoUrl: string, shaOrTag: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const pythonScript = `
import sys
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
    try:
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
        
    except Exception as e:
        error_result = {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    asyncio.run(main())
`;

      const pythonProcess = spawn(this.pythonPath, ['-c', pythonScript, repoUrl, shaOrTag], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python process exited with code ${code}: ${stderr}`));
          return;
        }

        try {
          const result = JSON.parse(stdout.trim());
          resolve(result);
        } catch (error) {
          reject(new Error(`Failed to parse Python output: ${error}\nOutput: ${stdout}`));
        }
      });

      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error}`));
      });
    });
  }
}