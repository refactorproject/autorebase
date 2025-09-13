# AutoRebase Scripts

This directory contains shell scripts to automate the AutoRebase workflow.

## Available Scripts

### 1. `run_auto_rebase.sh` - Full Featured Script

**Usage:**
```bash
./scripts/run_auto_rebase.sh [workdir_name]
```

**Features:**
- ✅ Complete AutoRebase workflow in one command
- ✅ Colored output with progress indicators
- ✅ Error handling and validation
- ✅ Automatic workdir naming with timestamp
- ✅ Prerequisites checking
- ✅ Summary report generation
- ✅ Optional browser report opening

**Example:**
```bash
# Run with auto-generated workdir name
./scripts/run_auto_rebase.sh

# Run with custom workdir name
./scripts/run_auto_rebase.sh my_custom_run
```

### 2. `quick_rebase.sh` - Minimal Script

**Usage:**
```bash
./scripts/quick_rebase.sh
```

**Features:**
- ✅ Minimal, fast execution
- ✅ No interactive prompts
- ✅ Clean previous runs automatically
- ✅ Perfect for CI/CD or automated testing

## What These Scripts Do

Both scripts execute the complete AutoRebase workflow:

1. **Initialize** - Set up the run with base and feature paths
2. **Extract Feature** - Generate patches between old-base and feature
3. **Extract Base** - Generate patches between old-base and new-base  
4. **Retarget** - Apply feature patches to new-base, creating feature-NEW
5. **Validate** - Check results and generate reports
6. **Finalize** - Create git tags and traceability files

## Output Structure

```
artifacts/[workdir_name]/
├── feature_patch/
│   └── feature_patch.json
├── base_patch/
│   └── base_patch.json
├── feature_patches/          # Per-file patches
│   ├── src/main.cpp.patch
│   ├── configs/config.json.patch
│   └── ...
├── base_patches/             # Per-file patches
│   ├── src/main.cpp.patch
│   ├── configs/config.json.patch
│   └── ...
├── feature-5.1/              # Final retargeted feature
│   ├── src/main.cpp
│   ├── configs/
│   ├── dts/
│   └── retarget_results.json
├── report.html               # Human-readable report
├── report.json               # Machine-readable report
├── trace.json                # Requirement traceability
├── feature.patch             # Combined feature patch
└── base.patch                # Combined base patch
```

## Prerequisites

- Python 3.11+
- Git (optional, for enhanced functionality)
- AutoRebase dependencies installed (`pip install -r requirements.txt`)

## Sample Data

The scripts use the included sample data:
- **base-1.0**: Original base version
- **base-1.1**: Updated base version (OldAPI → NewAPI)
- **feature-5.0**: Feature with customizations (parameter 42 → 200)
- **requirements_map.yaml**: Requirement mappings

## Expected Results

After running either script, you'll have:

1. **feature-5.1/src/main.cpp** - The retargeted feature that:
   - Uses `NewAPI` (from base-1.1)
   - Preserves feature customizations (parameter 200)
   - Maintains all original functionality

2. **Comprehensive Reports** - HTML and JSON reports showing:
   - Patch application status
   - Requirement traceability
   - Validation results
   - Tool availability

3. **Git Integration** - Tagged commit with:
   - Requirement IDs in commit trailers
   - Change type metadata
   - Timestamp information

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Python Module Not Found**
   ```bash
   pip install -r requirements.txt
   ```

3. **Git Not Available**
   - Scripts will continue with reduced functionality
   - Patches will still be generated and applied

### Debug Mode

For verbose output, the scripts automatically use `--verbose` flags. Check the logs in `artifacts/[workdir]/logs/run.log` for detailed information.

## Integration

These scripts are perfect for:
- **CI/CD Pipelines** - Use `quick_rebase.sh` for automated runs
- **Development Workflows** - Use `run_auto_rebase.sh` for interactive development
- **Testing** - Both scripts clean up previous runs automatically
- **Documentation** - Generated reports provide comprehensive audit trails
