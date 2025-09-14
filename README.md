# AutoRebase — Automated Re-targeting of Feature Customizations

## Overview

AutoRebase helps re-target feature customizations when a Base SW updates. Given base-OLD, base-NEW, and feature-OLD, it produces feature-NEW with re-applied customizations, machine-readable patchsets, and a human report with traceability and validation.

## 🚀 Quick Start Options

### Option 1: MCP Server (Recommended for AI Integration)

The MCP (Model Context Protocol) server provides AI-powered conflict resolution and is perfect for integration with AI models like Cursor.

**Setup:**
```bash
cd mcp-server
npm install
npm run build
```

**Usage with Cursor:**
1. Copy `mcp-server/cursor-mcp-config.json` to your Cursor MCP configuration
2. Restart Cursor
3. Use AI to call AutoRebase tools directly

**Available Tools:**
- `autorebase`: Complete AutoRebase process with AI conflict resolution
- `validate_repository`: Validate GitHub repositories and SHAs

See `mcp-server/README.md` for detailed MCP setup instructions.

### Option 2: FastAPI Server

REST API for programmatic access to AutoRebase functionality.

**Setup:**
```bash
pip install -r api/requirements.txt
python api/main.py
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/autorebase" \
  -H "Content-Type: application/json" \
  -d '{
    "base_software_0": "main",
    "base_software_1": "main", 
    "feature_software_0": "main",
    "base_repo_url": "https://github.com/user/base-repo.git",
    "feature_repo_url": "https://github.com/user/feature-repo.git"
  }'
```

See `README_FASTAPI.md` for detailed API documentation.

### Option 3: Engine CLI (Legacy)

Command-line interface for direct AutoRebase operations.

**Setup:**
```bash
bash scripts/install_tools.sh
```

**Usage:**
```bash
python -m engine.cli.auto_rebase init --old-base data/sample/base-1.0 --new-base data/sample/base-1.1 --feature data/sample/feature-5.0 --req-map data/sample/requirements_map.yaml --workdir artifacts/run1
python -m engine.cli.auto_rebase extract-feature --out artifacts/run1/feature_patch
python -m engine.cli.auto_rebase extract-base --out artifacts/run1/base_patch
python -m engine.cli.auto_rebase retarget --feature-patch artifacts/run1/feature_patch --base-patch artifacts/run1/base_patch --new-base data/sample/base-1.1 --out artifacts/run1/feature-5.1
python -m engine.cli.auto_rebase validate --path artifacts/run1/feature-5.1 --report artifacts/run1/report.html
python -m engine.cli.auto_rebase finalize --path artifacts/run1/feature-5.1 --tag v5.1 --trace artifacts/run1/trace.json
```

## 🎯 What You Get

- **feature-NEW tree** with applied changes
- **Machine-readable ΔF and ΔB patchsets**
- **Complete changelog** with detailed processing information
- **AI-powered conflict resolution** using OpenAI
- **Requirements-based resolution** respecting REQUIREMENTS_MAP.yml
- **report.html and report.json** (schema-validated)
- **trace.json** listing requirement IDs per patch unit
- **Optional git tag and commit trailers**

## 🏗️ Architecture

### MCP Server (`mcp-server/`)
- Model Context Protocol server for AI integration
- TypeScript/Node.js implementation
- Provides tools for AI models to call AutoRebase functionality
- Supports local SSH authentication and GitHub token authentication

### FastAPI Server (`api/`)
- REST API for programmatic access
- Python implementation with Pydantic models
- Async/await support for concurrent operations
- Comprehensive error handling and validation

### Engine (`engine/`)
- Core AutoRebase logic and algorithms
- Adapter pattern for different file types
- Fallback strategies for missing external tools
- Python implementation with extensive testing

### Web Interface (`web/`)
- Next.js web application
- User-friendly interface for AutoRebase operations
- Real-time progress tracking and results visualization

## 🔧 Environment Requirements

- **Python**: 3.11+ recommended
- **Node.js**: 18+ for MCP server and Next.js app
- **OpenAI API Key**: Required for AI conflict resolution
- **Git**: Required for repository operations
- **Optional external tools**: difftastic, gumtree, clang-tidy, coccinelle, dtc, yq, comby

## 🚀 Key Features

### AI-Powered Conflict Resolution
- Uses OpenAI GPT models to intelligently resolve merge conflicts
- Respects REQUIREMENTS_MAP.yml for context-aware resolution
- Validates resolutions with confidence scoring
- Handles complex multi-file conflicts

### Automatic Changelog Generation
- Complete processing history with timestamps
- Detailed file-by-file change tracking
- Patch application success/failure logging
- AI resolution statistics and validation scores

### Flexible Authentication
- **SSH**: Uses local SSH keys for GitHub operations
- **GitHub Token**: Supports personal access tokens
- **Public Repositories**: No authentication required for read operations
- **Local Credentials**: Falls back to system Git configuration

### Robust Error Handling
- Graceful degradation when external tools are missing
- Comprehensive validation of inputs and outputs
- Detailed error messages with troubleshooting guidance
- Fallback strategies for edge cases

## 🧪 Development

- **Formatting/lint**: ruff, black, isort configured in `pyproject.toml`
- **Tests**: `pytest` (see `tests/`)
- **CI**: GitHub Actions in `.github/workflows/ci.yml`
- **Type Safety**: TypeScript for MCP server, Pydantic for Python APIs

## 🔒 Security & Privacy

- **Local Processing**: All operations happen on your machine
- **No Data Storage**: No sensitive data is stored or transmitted
- **Secure Authentication**: Multiple authentication methods supported
- **API Key Management**: Secure handling of OpenAI and GitHub tokens
- **Public Repository Focus**: Designed for open-source workflows

## 📚 Documentation

- **MCP Server**: `mcp-server/README.md` - AI integration guide
- **FastAPI**: `README_FASTAPI.md` - REST API documentation  
- **Cursor Setup**: `mcp-server/CURSOR_SETUP.md` - Cursor AI integration
- **Engine**: `engine/README.md` - Core algorithm documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (unit tests + integration tests)
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

