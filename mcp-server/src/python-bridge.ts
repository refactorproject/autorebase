import { spawn } from 'child_process';
import { promisify } from 'util';
import { AutoRebaseRequest, AutoRebaseResponse } from './types.js';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename); 

/**
 * Python bridge for calling AutoRebase functionality
 */
export class PythonBridge {
  private pythonPath: string;
  private autorebasePath: string;

  constructor() {
    this.pythonPath = 'python3'; // Default to python3
    this.autorebasePath = './src/services/autorebase_service.py'; // Relative to mcp-server
  }

  /**
   * Call the AutoRebase service via Python
   */
  async callAutoRebase(request: AutoRebaseRequest): Promise<AutoRebaseResponse> {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(__dirname, '..', 'run_autorebase_wrapper.py');
      const workingDir = path.join(__dirname, '..');
      
      const pythonProcess = spawn(this.pythonPath, [scriptPath, JSON.stringify(request)], {
        cwd: workingDir,
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
        cwd: path.join(__dirname, '..'),
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