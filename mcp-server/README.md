# AutoRebase MCP Server

MCP server for AutoRebase with AI conflict resolution on public GitHub repositories.

## Features

- **AutoRebase Processing**: Clone repositories, generate patches, apply changes
- **AI Conflict Resolution**: Resolve merge conflicts using AI
- **GitHub Operations**: Create branches, push changes, generate PRs
- **Flexible Transport**: Support for both stdio and HTTP transport modes

## Installation

```bash
npm install
npm run build
```

## Usage

### Stdio Transport (Default)

The server runs on stdio by default, suitable for MCP client integration:

```bash
npm start
# or
npm run dev
```

### HTTP Transport

Run the server as an HTTP service with configurable port:

```bash
# Production
MCP_TRANSPORT=http MCP_PORT=3000 npm start

# Development
MCP_TRANSPORT=http MCP_PORT=3000 npm run dev

# Using npm scripts
npm run start:http
npm run dev:http
```

#### Environment Variables

- `MCP_TRANSPORT`: Transport mode (`stdio` or `http`, default: `stdio`)
- `MCP_PORT`: HTTP port number (default: `3000`)

#### HTTP Endpoints

When running in HTTP mode, the server provides:

- **SSE Endpoint**: `http://localhost:3000/message` - Server-Sent Events for MCP communication
- **Health Check**: `http://localhost:3000/health` - Server health status

### Example HTTP Usage

```bash
# Start server on port 3000
MCP_TRANSPORT=http MCP_PORT=3000 npm start

# Start server on custom port
MCP_TRANSPORT=http MCP_PORT=8080 npm start
```

## Available Tools

### `autorebase`
Run complete AutoRebase process with AI conflict resolution.

**Parameters:**
- `base_repo_url`: Base repository URL
- `feature_repo_url`: Feature repository URL  
- `base_software_0`: Base software version 0 (SHA/tag)
- `base_software_1`: Base software version 1 (SHA/tag)
- `feature_software_0`: Feature software version 0 (SHA/tag)
- `base_branch`: Base branch name (optional)
- `output_branch`: New branch name (optional)
- `github_token`: GitHub token (optional)
- `use_ssh`: Use SSH authentication (optional)

### `validate_repository`
Validate repository and SHA/tag combination.

**Parameters:**
- `repo_url`: Repository URL
- `sha_or_tag`: SHA or tag to validate

## Configuration

The server uses environment variables for configuration:

```bash
# GitHub authentication
export GITHUB_TOKEN="your_github_token"

# OpenAI API key for AI conflict resolution
export OPENAI_API_KEY="your_openai_api_key"

# Transport configuration
export MCP_TRANSPORT="http"  # or "stdio"
export MCP_PORT="3000"
```

## Development

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Run in development mode
npm run dev

# Run in HTTP development mode
npm run dev:http

# Clean build artifacts
npm run clean
```

## Integration with MCP Clients

### Stdio Mode
Configure your MCP client to use stdio transport:

```json
{
  "mcpServers": {
    "autorebase": {
      "command": "node",
      "args": ["/path/to/autorebase/mcp-server/dist/index.js"],
      "env": {
        "GITHUB_TOKEN": "your_token",
        "OPENAI_API_KEY": "your_key"
      }
    }
  }
}
```

### HTTP Mode
Configure your MCP client to use HTTP transport:

```json
{
  "mcpServers": {
    "autorebase": {
      "command": "node",
      "args": ["/path/to/autorebase/mcp-server/dist/index.js"],
      "env": {
        "MCP_TRANSPORT": "http",
        "MCP_PORT": "3000",
        "GITHUB_TOKEN": "your_token",
        "OPENAI_API_KEY": "your_key"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the `MCP_PORT` environment variable
2. **Authentication errors**: Verify `GITHUB_TOKEN` is valid and has necessary permissions
3. **AI resolution failures**: Check `OPENAI_API_KEY` is valid and has sufficient credits

### Logs

The server logs to stderr, so you can redirect logs:

```bash
# Stdio mode
node dist/index.js 2> server.log

# HTTP mode  
MCP_TRANSPORT=http node dist/index.js 2> server.log
```

## License

MIT