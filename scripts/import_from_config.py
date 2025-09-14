#!/usr/bin/env python3
"""
Import repositories using YAML configuration
"""

import yaml
import subprocess
import os
import sys
from pathlib import Path

def load_config(config_file="config/repos.yaml"):
    """Load repository configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML configuration: {e}")
        sys.exit(1)

def run_command(cmd, cwd=None, check=True):
    """Run a shell command"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None, e.stderr

def clone_repository(repo_url, target_dir, tag=None, remove_existing=True):
    """Clone a repository to the target directory"""
    print(f"📥 Cloning {repo_url} to {target_dir}")
    
    # Remove existing directory if requested
    if remove_existing and target_dir.exists():
        print(f"🗑️  Removing existing directory: {target_dir}")
        run_command(f"rm -rf {target_dir}")
    
    # Create parent directory
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    
    # Clone the repository
    clone_cmd = f"git clone {repo_url} {target_dir}"
    stdout, stderr = run_command(clone_cmd)
    
    if stdout is None:
        return False
    
    # Checkout specific tag if provided
    if tag:
        print(f"🏷️  Checking out tag: {tag}")
        checkout_cmd = f"git checkout {tag}"
        stdout, stderr = run_command(checkout_cmd, cwd=target_dir)
        
        if stdout is None:
            print(f"❌ Failed to checkout tag: {tag}")
            return False
    
    print(f"✅ Successfully cloned {repo_url}")
    return True

def get_repo_info(repo_dir):
    """Get information about a repository"""
    info = {}
    
    # Get latest commit
    stdout, _ = run_command("git log --oneline -1", cwd=repo_dir, check=False)
    if stdout:
        info['latest_commit'] = stdout
    
    # Get current tag
    stdout, _ = run_command("git describe --tags --exact-match HEAD 2>/dev/null", cwd=repo_dir, check=False)
    if stdout:
        info['current_tag'] = stdout
    else:
        # Get current branch
        stdout, _ = run_command("git branch --show-current", cwd=repo_dir, check=False)
        if stdout:
            info['current_branch'] = stdout
    
    # Count files
    stdout, _ = run_command("find . -type f | wc -l", cwd=repo_dir, check=False)
    if stdout:
        info['file_count'] = stdout
    
    return info

def import_repositories():
    """Import all repositories based on configuration"""
    config = load_config()
    
    print("AutoRebase Repository Importer (YAML Config)")
    print("=" * 50)
    
    # Get import settings
    import_settings = config.get('import', {})
    remove_existing = import_settings.get('remove_existing', True)
    checkout_tags = import_settings.get('checkout_tags', True)
    
    # Get repository configurations
    repos_config = config['repositories']
    data_config = config['data']
    
    results = {}
    
    # Import base-0 repository
    print("\n📁 Importing Base-0 repository...")
    base_0_dir = Path(data_config['base_0_dir'])
    base_0_tag = repos_config['base']['tags']['base-0']
    results['base-0'] = clone_repository(
        repos_config['base']['url'], 
        base_0_dir, 
        base_0_tag if checkout_tags else None,
        remove_existing
    )
    
    # Import base-1 repository
    print("\n📁 Importing Base-1 repository...")
    base_1_dir = Path(data_config['base_1_dir'])
    base_1_tag = repos_config['base']['tags']['base-1']
    results['base-1'] = clone_repository(
        repos_config['base']['url'], 
        base_1_dir, 
        base_1_tag if checkout_tags else None,
        remove_existing
    )
    
    # Import feature-0 repository
    print("\n📁 Importing Feature-0 repository...")
    feature_0_dir = Path(data_config['feature_0_dir'])
    feature_0_tag = repos_config['feature']['tags']['feature-0']
    results['feature-0'] = clone_repository(
        repos_config['feature']['url'], 
        feature_0_dir, 
        feature_0_tag if checkout_tags else None,
        remove_existing
    )
    
    # Report results
    print("\n" + "=" * 50)
    print("IMPORT RESULTS:")
    print("=" * 50)
    
    all_success = True
    for repo_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{repo_name}: {status}")
        if not success:
            all_success = False
    
    if all_success:
        print("\n🎉 All repositories imported successfully!")
        
        # List imported repositories
        print("\n" + "=" * 50)
        print("IMPORTED REPOSITORIES:")
        print("=" * 50)
        
        repo_dirs = {
            'base-0': Path(data_config['base_0_dir']),
            'base-1': Path(data_config['base_1_dir']),
            'feature-0': Path(data_config['feature_0_dir'])
        }
        
        for repo_name, repo_dir in repo_dirs.items():
            if repo_dir.exists():
                print(f"\n📁 {repo_name}:")
                info = get_repo_info(repo_dir)
                
                if 'latest_commit' in info:
                    print(f"   Latest commit: {info['latest_commit']}")
                
                if 'current_tag' in info:
                    print(f"   Current tag: {info['current_tag']}")
                elif 'current_branch' in info:
                    print(f"   Current branch: {info['current_branch']}")
                
                if 'file_count' in info:
                    print(f"   Files: {info['file_count']}")
        
        return True
    else:
        print("\n❌ Some repositories failed to import. Check the errors above.")
        return False

if __name__ == "__main__":
    # Check if PyYAML is available
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML is required. Install it with: pip install PyYAML")
        sys.exit(1)
    
    success = import_repositories()
    sys.exit(0 if success else 1)
