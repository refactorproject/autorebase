# AutoRebase API Endpoint Summary

## 🚀 **Main Endpoint: POST `/github/autorebase`**

This is the **primary API endpoint** that runs the complete AutoRebase process.

### 📍 **Endpoint Details**
- **URL**: `POST /github/autorebase`
- **Function**: `run_autorebase()`
- **Purpose**: Complete AutoRebase workflow with AI conflict resolution

### 📥 **Request Format**
```json
{
  "base_software_0": "base/v1.0.0",           // SHA or tag/branch
  "base_software_1": "base/v1.0.1",           // SHA or tag/branch  
  "feature_software_0": "feature/v5.0.0",     // SHA or tag/branch
  "base_repo_url": "https://github.com/refactorproject/sample-base-sw.git",
  "feature_repo_url": "https://github.com/refactorproject/sample-feature-sw.git",
  "base_branch": "feature/v5.0.0",            // Target branch for PR (optional)
  "output_branch": "feature/v5.0.1"           // New branch to create (optional)
}
```

### 🔄 **What This Endpoint Does**

1. **✅ Validates GitHub SHAs/tags** for all three repositories
2. **✅ Clones all three repositories** to local workspace
3. **✅ Runs the complete AutoRebase process**:
   - Generates patches between base0 ↔ feature0
   - Applies patches to base1 to create feature-5.1
   - Uses AI to resolve any conflicts
   - Preserves requirements from REQUIREMENTS_MAP.yml
4. **✅ Creates a new branch** (`feature/v5.0.1`) in the feature repository
5. **✅ Commits all resolved changes** to the new branch
6. **✅ Generates a Pull Request** URL for review

### 📤 **Response Format**
```json
{
  "success": true,
  "message": "AutoRebase completed successfully",
  "clone_results": { ... },
  "autorebase_results": { ... },
  "pr_results": { ... }
}
```

### 🎯 **Usage Example**
```bash
curl -X POST "http://localhost:8000/github/autorebase" \
  -H "Content-Type: application/json" \
  -d '{
    "base_software_0": "base/v1.0.0",
    "base_software_1": "base/v1.0.1", 
    "feature_software_0": "feature/v5.0.0",
    "base_repo_url": "https://github.com/refactorproject/sample-base-sw.git",
    "feature_repo_url": "https://github.com/refactorproject/sample-feature-sw.git",
    "base_branch": "feature/v5.0.0",
    "output_branch": "feature/v5.0.1"
  }'
```

## 🔧 **Other Endpoints**

### **GET `/github/health`**
- Health check endpoint
- Returns: `{"status": "healthy", "service": "GitHub AutoRebase Processor"}`

### **GET `/github/`**
- Root endpoint with API information
- Returns: API version, available endpoints, and description

## 🎉 **Key Benefits**

- **Single API Call**: One endpoint handles the entire workflow
- **AI-Powered**: Automatic conflict resolution using OpenAI
- **Flexible Input**: Supports both SHAs and human-readable tags/branches
- **Complete Integration**: From GitHub repos to Pull Request creation
- **Robust Error Handling**: Comprehensive fallback mechanisms
- **Requirements Preservation**: Respects REQUIREMENTS_MAP.yml constraints

**This single API call replaces the entire manual AutoRebase process!** 🚀



