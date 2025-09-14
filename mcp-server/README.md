# AutoRebase MCP Server

A Model Context Protocol (MCP) server that provides AI-powered conflict resolution for Git repositories through the AutoRebase system.

## 🚀 Features

- **Complete AutoRebase Process**: Clone repositories, generate patches, resolve conflicts
- **AI-Powered Conflict Resolution**: Uses OpenAI to intelligently resolve merge conflicts
- **Requirements-Based Resolution**: Respects REQUIREMENTS_MAP.yml for conflict resolution
- **Public Repository Support**: Works with public GitHub repositories (no authentication required)
- **Read-Only Operation**: Returns resolved files without pushing to repositories

## 🛠️ Available Tools

### 1. `autorebase`

Runs the complete AutoRebase process with AI conflict resolution.

**Parameters:**
- `base_software_0` (required): Base software 0 SHA or tag
- `base_software_1` (required): Base software 1 SHA or tag  
- `feature_software_0` (required): Feature software 0 SHA or tag
- `base_repo_url` (required): Base repository URL
- `feature_repo_url` (required): Feature repository URL
- `base_branch` (optional): Target branch for PR creation (default: "feature/v5.0.0")
- `output_branch` (optional): New branch to create (default: "feature/v5.0.1")
- `github_token` (optional): GitHub personal access token for authentication

**Example:**
```json
{
  "name": "autorebase",
  "arguments": {
    "base_software_0": "base/v1.0.0",
    "base_software_1": "base/v1.0.1",
    "feature_software_0": "feature/v5.0.0",
    "base_repo_url": "https://github.com/refactorproject/sample-base-sw.git",
    "feature_repo_url": "https://github.com/refactorproject/sample-feature-sw.git"
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
    "repo_url": "https://github.com/refactorproject/sample-base-sw.git",
    "sha_or_tag": "base/v1.0.0"
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
   export GITHUB_TOKEN="your-github-token"  # Optional, for authentication
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

## 🔗 Integration with AI Models

This MCP server can be integrated with AI models that support the Model Context Protocol. The AI model can:

1. **Discover Available Tools**: List tools using the MCP protocol
2. **Execute AutoRebase**: Call the `autorebase` tool with repository information
3. **Validate Repositories**: Use `validate_repository` to check inputs
4. **Process Results**: Receive resolved files and conflict resolution details

## 📋 Requirements

- **Node.js**: >= 18.0.0
- **Python**: >= 3.8 (for AutoRebase functionality)
- **OpenAI API Key**: Required for AI conflict resolution
- **Public GitHub Repositories**: Only public repositories are supported

## 🔒 Security

- **Flexible Authentication**: Supports GitHub tokens or local credentials
- **Public Repository Support**: Works with public repositories without authentication
- **Secure Token Handling**: GitHub tokens handled via environment variables or parameters
- **Local Processing**: All operations happen locally
- **Secure API Keys**: OpenAI API key handled via environment variables

## 🐛 Troubleshooting

### Common Issues

1. **Python Import Errors**: Ensure you're running from the correct directory
2. **OpenAI API Errors**: Check your API key and quota
3. **Repository Access**: Ensure repositories are public and accessible
4. **Git Operations**: Ensure Git is installed and accessible

### Debug Mode

Set `DEBUG=true` environment variable for verbose logging.

## 📝 Example Workflow

1. **Validate Input**: Use `validate_repository` to check repositories and SHAs
2. **Run AutoRebase**: Use `autorebase` to process the repositories
3. **Review Results**: Examine resolved files and conflict resolution details
4. **Manual PR Creation**: Create pull requests manually using the resolved files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.
