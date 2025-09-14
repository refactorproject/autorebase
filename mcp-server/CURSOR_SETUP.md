# 🚀 AutoRebase MCP Server - Cursor Integration

## Overview
This MCP server provides AutoRebase functionality directly to your Cursor AI agent, allowing it to:
- Run complete AutoRebase processes with AI conflict resolution
- Validate GitHub repositories and SHAs/tags
- Access detailed changelog information

## 🛠️ Setup Instructions

### 1. Build the MCP Server
```bash
cd /Users/apurva/Desktop/Projects/autorebase/mcp-server
npm install
npm run build
```

### 2. Configure Cursor
Add this configuration to your Cursor settings:

**Option A: Global Configuration**
1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Go to "Extensions" → "MCP Servers"
3. Add the following configuration:

```json
{
  "mcpServers": {
    "autorebase": {
      "command": "node",
      "args": ["/Users/apurva/Desktop/Projects/autorebase/mcp-server/dist/index.js"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "DEBUG": "true"
      }
    }
  }
}
```

**Option B: Workspace Configuration**
1. Create `.cursor/mcp.json` in your workspace root:
```bash
mkdir -p .cursor
cp mcp-server/cursor-mcp-config.json .cursor/mcp.json
```

### 3. Environment Variables
Make sure these are set in your environment:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_TOKEN="your-github-token"  # Optional for SSH auth
```

### 4. Restart Cursor
Restart Cursor to load the MCP server configuration.

## 🎯 Available Tools

### 1. `autorebase`
Run complete AutoRebase process with AI conflict resolution.

**Parameters:**
- `base_software_0`: Base software 0 SHA or tag
- `base_software_1`: Base software 1 SHA or tag  
- `feature_software_0`: Feature software 0 SHA or tag
- `base_repo_url`: Base repository URL
- `feature_repo_url`: Feature repository URL
- `base_branch`: Target branch (optional, default: "feature/v5.0.0")
- `output_branch`: New branch to create (optional, default: "feature/v5.0.1")
- `github_token`: GitHub token (optional)
- `use_ssh`: Use SSH authentication (optional, default: false)

**Example:**
```json
{
  "base_software_0": "base/v1.0.0",
  "base_software_1": "base/v1.0.1", 
  "feature_software_0": "feature/v5.0.0",
  "base_repo_url": "https://github.com/user/base-repo.git",
  "feature_repo_url": "https://github.com/user/feature-repo.git",
  "use_ssh": true
}
```

### 2. `validate_repository`
Validate GitHub repository and SHA/tag combination.

**Parameters:**
- `repo_url`: Repository URL to validate
- `sha_or_tag`: SHA or tag to validate

### 3. `get_changelog`
Get the latest AutoRebase changelog information.

**Parameters:**
- `changelog_path`: Path to changelog file (optional)

## 🧪 Testing

### Test MCP Server Directly
```bash
# List available tools
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node mcp-server/dist/index.js

# Test autorebase
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "autorebase", "arguments": {"base_software_0": "base/v1.0.0", "base_software_1": "base/v1.0.1", "feature_software_0": "feature/v5.0.0", "base_repo_url": "https://github.com/refactorproject/sample-base-sw.git", "feature_repo_url": "https://github.com/refactorproject/sample-feature-sw.git", "use_ssh": true}}}' | node mcp-server/dist/index.js

# Test changelog
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_changelog", "arguments": {"changelog_path": "data/sample/autorebase_changelog.json"}}}' | node mcp-server/dist/index.js
```

### Test in Cursor
Once configured, you can ask Cursor:
- "Run an AutoRebase process on these repositories..."
- "Show me the latest changelog"
- "Validate this repository and SHA"

## 🔧 Troubleshooting

### Common Issues

1. **"Command not found"**
   - Make sure Node.js is installed and in PATH
   - Verify the path to `dist/index.js` is correct

2. **"Permission denied"**
   - Check file permissions on the MCP server files
   - Ensure Cursor has access to the directory

3. **"Environment variables not found"**
   - Set OPENAI_API_KEY in your environment
   - Optionally set GITHUB_TOKEN for authentication

4. **"MCP server not responding"**
   - Check the server logs in Cursor's developer console
   - Verify the server builds without errors (`npm run build`)

### Debug Mode
Set `DEBUG=true` in the environment to see detailed logs.

## 📁 File Structure
```
mcp-server/
├── dist/                    # Built TypeScript files
├── src/                     # Source TypeScript files
│   ├── index.ts            # Main server entry point
│   ├── tools.ts            # MCP tool definitions
│   ├── types.ts            # TypeScript interfaces
│   └── python-bridge.ts    # Python integration
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
├── cursor-mcp-config.json  # Cursor configuration template
└── CURSOR_SETUP.md         # This file
```

## 🎉 Success!
Once configured, your Cursor AI agent will have access to powerful AutoRebase functionality, including:
- Automated conflict resolution using AI
- Detailed changelog tracking
- Repository validation
- SSH and token authentication support

The MCP server runs locally and integrates seamlessly with your existing AutoRebase Python backend.



