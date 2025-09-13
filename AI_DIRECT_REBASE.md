# AI Direct Rebase

## Overview

The AI Direct Rebase functionality provides an intelligent, automated approach to applying feature patches directly onto new base versions without requiring the traditional retarget step. This simplified approach uses AI to analyze conflicts between git patches and automatically resolves them while preserving all feature customizations.

**Key Simplification**: All file types are handled uniformly using git patches - no more adapter complexity for different file types (C/C++, JSON, YAML, etc.).

## Key Features

- **🤖 AI-Powered Conflict Resolution**: Automatically detects and resolves conflicts between git patches
- **📋 Requirement-Aware**: Uses requirement mappings to understand the intent behind feature customizations
- **🔄 Universal File Support**: Handles all file types uniformly using git patch analysis
- **⚡ Direct Application**: Skips the traditional retarget step for faster processing
- **🛡️ Fallback Support**: Uses heuristic resolution when AI is unavailable
- **📊 Comprehensive Reporting**: Detailed conflict analysis and resolution results
- **🎯 Simplified Architecture**: No more adapter complexity - everything works with git patches

## How It Works

### Traditional Approach
```
Extract Patches → Retarget → Apply → Validate
```

### AI Direct Approach
```
Extract Patches → AI Resolve Conflicts → Apply → Validate
```

## Usage

### Command Line Interface

```bash
# Run AI Direct Rebase
python -m engine.cli.auto_rebase ai-rebase \
    --feature-patches <feature_patches_dir> \
    --base-patches <base_patches_dir> \
    --new-base <new_base_dir> \
    --req-map <requirements_map.yaml> \
    --out <output_dir> \
    --verbose
```

### Script Usage

```bash
# Run complete AI Direct Rebase workflow
./scripts/ai_direct_rebase.sh [workdir_name]

# Compare traditional vs AI approaches
./scripts/compare_approaches.sh
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for AI-powered conflict resolution
- `OPENAI_MODEL`: Model to use (default: "gpt-4o-mini")

### Requirements Mapping

The AI resolver uses requirement mappings to understand feature customizations:

```yaml
- path_glob: "src/**"
  req_ids: ["AD-REQ-201", "AD-REQ-318"]
- path: "src/main.cpp"
  req_ids: ["AD-REQ-601"]
  requirement: "Feature: While calling API we need to pass 200 as input"
```

## Conflict Resolution

### Automatic Conflict Detection

The AI resolver automatically detects conflicts by analyzing git patch content:

- **API Changes**: Function renames detected by comparing added/removed lines
- **Parameter Changes**: Function signature changes detected through pattern matching
- **Header Changes**: Include file changes detected in patch additions/removals
- **Structural Changes**: File organization changes (new/deleted files)
- **Content Changes**: General additions and removals in patches

### Resolution Strategies

1. **OpenAI Resolution** (if API key available):
   - Comprehensive analysis of conflicts
   - Intelligent adaptation to API changes
   - Preservation of all feature customizations

2. **Heuristic Resolution** (fallback):
   - Git patch content analysis
   - Pattern-based conflict resolution
   - Requirement-specific customizations
   - Universal file type support

## Example

### Input Files

**Feature Patch** (base X → feature X):
```cpp
// Feature customizations
if (width == 0) width = 1344;  // Changed from 1280
height = clampH(height);       // Added height clamping
std::cout << "[feature-5.0] init camera " << width << "x" << height << std::endl;
return NvOldAPI(width, height);
```

**Base Patch** (base X → base X+1):
```cpp
// API changes
#include "nv/camera_utils.h"  // Header renamed
static int NvNewAPI(int width, int height) { return width > 0 && height > 0 ? 0 : -2; }
struct NvCtx { int reserved{0}; };
int InitRvcCamera(const NvCtx& ctx, int width, int height) {  // Signature changed
    (void)ctx;
    return NvNewAPI(width, height);
}
```

### AI Resolution Output

```cpp
// AI-resolved result (feature X+1)
#include "nv/camera_utils.h"  // Updated header
static int clampH(int h) { return h < 480 ? 480 : h; }  // Preserved feature function
static int NvNewAPI(int width, int height) { return width > 0 && height > 0 ? 0 : -2; }
struct NvCtx { int reserved{0}; };
int InitRvcCamera(const NvCtx& ctx, int width, int height) {
    if (width == 0) width = 1344;  // Preserved feature customization
    if (height == 0) height = 720;
    height = clampH(height);       // Preserved feature customization
    (void)ctx;
    std::cout << "[feature-5.1] init camera " << width << "x" << height << std::endl;  // Preserved feature logging
    return NvNewAPI(width, height);  // Updated API call
}
```

## Results and Reporting

### AI Rebase Results

The AI resolver generates detailed results in `ai_rebase_results.json`:

```json
{
  "summary": {
    "total_files": 4,
    "resolved": 4,
    "errors": 0,
    "auto": 4,
    "semantic": 0,
    "conflicts": 0
  },
  "files": [
    {
      "file": "src/vision/camera_pipeline.cpp",
      "status": "resolved",
      "method": "heuristic",
      "req_ids": ["AD-REQ-201", "AD-REQ-318"],
      "conflicts": {
        "api_changes": [{"old_api": "NvOldAPI", "new_api": "NvNewAPI"}],
        "parameter_changes": [{"old_signature": "InitRvcCamera(int width, int height)", "new_signature": "InitRvcCamera(const NvCtx& ctx, int width, int height)"}],
        "header_changes": [{"old_header": "nv/camera.h", "new_header": "nv/camera_utils.h"}]
      }
    }
  ]
}
```

## Benefits

1. **🚀 Faster Processing**: Eliminates the retarget step
2. **🎯 Intelligent Resolution**: AI understands context and requirements
3. **🔧 Automatic Adaptation**: Handles API changes without manual intervention
4. **📈 Better Success Rate**: Reduces conflicts through intelligent analysis
5. **🔄 Consistent Results**: Produces predictable, high-quality outputs
6. **🎯 Simplified Architecture**: No adapter complexity - works with any file type
7. **⚡ Universal Support**: Same logic for C++, JSON, YAML, Python, etc.

## Limitations

- Requires OpenAI API key for optimal performance
- Heuristic fallback may not handle all edge cases
- Performance depends on AI model capabilities

## Future Enhancements

- Enhanced git patch conflict detection patterns
- Integration with other AI models
- Batch processing capabilities
- Custom resolution strategies
- Improved heuristic fallback algorithms

## Troubleshooting

### Common Issues

1. **No files processed**: Check that patch directories contain `.patch` files
2. **JSON serialization errors**: Ensure all Path objects are converted to strings
3. **Validation failures**: Check that results contain required summary fields

### Debug Mode

Use `--verbose` flag for detailed logging:

```bash
python -m engine.cli.auto_rebase ai-rebase --verbose ...
```

## Integration

The AI Direct Rebase functionality integrates seamlessly with the existing AutoRebase pipeline:

- Uses the same patch extraction process
- Compatible with existing validation and reporting
- Maintains the same output format for consistency
- Can be used alongside traditional retargeting

This new approach represents a significant advancement in automated patch application, making the rebase process more intelligent, efficient, and reliable.
