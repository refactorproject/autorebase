# AutoRebase MCP Server

A Model Context Protocol (MCP) server that provides AI-powered conflict resolution for Git repositories through the AutoRebase system.

## 🚀 Features

- **Complete AutoRebase Process**: Clone repositories, generate patches, resolve conflicts
- **AI-Powered Conflict Resolution**: Uses OpenAI to intelligently resolve merge conflicts
- **Requirements-Based Resolution**: Respects REQUIREMENTS_MAP.yml for conflict resolution
- **Automatic Changelog**: Returns complete changelog information with every autorebase operation
- **Local Authentication**: Uses your local Git credentials (SSH keys or GitHub tokens)
- **Public Repository Support**: Works with public GitHub repositories

## 🛠️ Available Tools

### 1. `autorebase`

Runs the complete AutoRebase process with AI conflict resolution and automatically includes changelog information.

**Parameters:**
- `base_software_0` (required): Base software 0 SHA or tag
- `base_software_1` (required): Base software 1 SHA or tag  
- `feature_software_0` (required): Feature software 0 SHA or tag
- `base_repo_url` (required): Base repository URL
- `feature_repo_url` (required): Feature repository URL
- `base_branch` (optional): Target branch for PR creation (default: "feature/v5.0.0")
- `output_branch` (optional): New branch to create (default: "feature/v5.0.1")
- `github_token` (optional): GitHub personal access token for authentication
- `use_ssh` (optional): Use SSH authentication instead of token (default: false)

**Response includes:**
- Resolved files with conflict resolution details
- Complete changelog with processing history
- AI resolution statistics and validation scores
- Patch application success/failure details

**Example:**
```json
{
  "name": "autorebase",
  "arguments": {
    "base_software_0": "main",
    "base_software_1": "main",
    "feature_software_0": "main",
    "base_repo_url": "https://github.com/apurva/sample-base-sw.git",
    "feature_repo_url": "https://github.com/apurva/sample-feature-sw.git",
    "use_ssh": true
  }
}
```

### 2. `validate_repository`

Validates a GitHub repository and SHA/tag combination.

**Parameters:**
- `repo_url` (required): Repository URL to validate
- `sha_or_tag` (required): SHA or tag to validate

**Example:**
```json
{
  "name": "validate_repository",
  "arguments": {
    "repo_url": "https://github.com/apurva/sample-base-sw.git",
    "sha_or_tag": "main"
  }
}
```

## 🔧 Installation

1. **Install Dependencies:**
   ```bash
   cd mcp-server
   npm install
   ```

2. **Build the Server:**
   ```bash
   npm run build
   ```

3. **Set Environment Variables:**
   
   **Option A: Using .env file (Recommended):**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```
   
   **Option B: Using environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export GITHUB_TOKEN="your-github-token"  # Optional, for GitHub operations
   export SSH_OVERRIDE="true"  # Optional, to force SSH authentication
   export DEBUG="true"  # Optional, for verbose logging
   ```

## 🚀 Usage

### Running the Server

```bash
npm start
```

### Development Mode

```bash
npm run dev
```

### Testing the Server

```bash
# Test with a simple autorebase operation
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "autorebase", "arguments": {"base_software_0": "main", "base_software_1": "main", "feature_software_0": "main", "base_repo_url": "https://github.com/apurva/sample-base-sw.git", "feature_repo_url": "https://github.com/apurva/sample-feature-sw.git", "use_ssh": true}}}' | node dist/index.js
```

## 🔗 Integration with Cursor AI

### Setup for Cursor

1. **Copy the MCP configuration:**
   ```bash
   cp mcp-server/cursor-mcp-config.json ~/.cursor/mcp.json
   ```

2. **Update the configuration** with your actual paths and environment variables

3. **Restart Cursor**

4. **Use AI to call AutoRebase tools:**
   - Ask Cursor to "run autorebase on repositories X and Y"
   - Cursor will automatically call the MCP tools
   - Review the results including changelog information

See `CURSOR_SETUP.md` for detailed Cursor integration instructions.

## 📋 Requirements

- **Node.js**: >= 18.0.0
- **Python**: >= 3.8 (for AutoRebase functionality)
- **OpenAI API Key**: Required for AI conflict resolution
- **Git**: Required for repository operations
- **Local Git Credentials**: SSH keys or GitHub token for repository access

## 🔒 Security & Authentication

- **Local Processing**: All operations happen on your machine
- **SSH Authentication**: Uses your local SSH keys for GitHub operations
- **GitHub Token**: Optional personal access token for enhanced access
- **No Data Storage**: No sensitive data is stored or transmitted
- **Secure API Keys**: OpenAI API key handled via environment variables
- **Public Repository Focus**: Designed for open-source workflows

## 🐛 Troubleshooting

### Common Issues

1. **Python Import Errors**: Ensure you're running from the correct directory
2. **OpenAI API Errors**: Check your API key and quota
3. **Repository Access**: Ensure repositories are public and accessible
4. **Git Operations**: Ensure Git is installed and accessible
5. **Authentication Issues**: Check your SSH keys or GitHub token

### Debug Mode

Set `DEBUG=true` environment variable for verbose logging.

### Testing Authentication

```bash
# Test SSH access to GitHub
ssh -T git@github.com

# Test GitHub token (if using)
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

## 📝 Example Workflow

1. **Validate Input**: Use `validate_repository` to check repositories and SHAs
2. **Run AutoRebase**: Use `autorebase` to process the repositories
3. **Review Results**: Examine resolved files, conflict resolution details, and complete changelog
4. **Manual PR Creation**: Create pull requests manually using the resolved files

## 🎯 What You Get

Every autorebase operation returns:
- **Resolved Files**: Complete file contents with conflict resolution details
- **Changelog**: Detailed processing history including:
  - Files processed and patches generated
  - Successful and failed patch applications
  - AI resolution statistics and validation scores
  - Backup files and reject files created
  - Three-way merge operations performed
- **Processing Details**: Clone results and autorebase statistics
- **File Locations**: Paths to saved changelog and resolved files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.
