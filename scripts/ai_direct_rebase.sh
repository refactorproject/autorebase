#!/bin/bash

# AI Direct Rebase Script
# This script performs AI-based direct rebase without the traditional retarget step
# Usage: ./scripts/ai_direct_rebase.sh [workdir_name]

set -e  # Exit on any error

# Configuration
WORKDIR_NAME=${1:-"ai_rebase_$(date +%Y%m%d_%H%M%S)"}
WORKDIR="artifacts/$WORKDIR_NAME"
OLD_BASE="data/sample-base-sw_1.0"
NEW_BASE="data/sample-base-sw_1.1"
FEATURE="data/sample-feature-sw_5.0"
REQ_MAP="data/sample/requirements_map.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_warning "$1 not found, but continuing..."
        return 1
    fi
    return 0
}

# Function to run command with error handling
run_cmd() {
    local cmd="$1"
    local description="$2"
    
    print_step "$description"
    echo "Running: $cmd"
    
    if eval "$cmd"; then
        print_success "$description completed"
    else
        print_error "$description failed"
        exit 1
    fi
    echo
}

# Main execution
echo -e "${GREEN}🚀 Starting AI Direct Rebase Workflow${NC}"
echo "Workdir: $WORKDIR"
echo "Old Base: $OLD_BASE"
echo "New Base: $NEW_BASE"
echo "Feature: $FEATURE"
echo "Requirements Map: $REQ_MAP"
echo

# Check prerequisites
print_step "Checking Prerequisites"
check_command "python3"
check_command "git"
echo

# Step 1: Initialize the run (to create workdir structure)
run_cmd "python -m engine.cli.auto_rebase init --old-base $OLD_BASE --new-base $NEW_BASE --feature $FEATURE --req-map $REQ_MAP --workdir $WORKDIR --verbose" \
        "Initialize AutoRebase Run"

# Step 2: Extract feature patches
run_cmd "python -m engine.cli.auto_rebase extract-feature --out $WORKDIR/feature_patch --git-patch $WORKDIR/feature.patch --patch-dir $WORKDIR/feature_patches --verbose" \
        "Extract Feature Patches"

# Step 3: Extract base patches
run_cmd "python -m engine.cli.auto_rebase extract-base --out $WORKDIR/base_patch --git-patch $WORKDIR/base.patch --patch-dir $WORKDIR/base_patches --verbose" \
        "Extract Base Patches"

# Step 4: AI Direct Rebase - Apply feature patches directly to new base using AI
print_step "AI Direct Rebase"
echo "This step applies feature patches directly to the new base using AI conflict resolution"
echo "No traditional retarget step needed!"

run_cmd "python -m engine.cli.auto_rebase ai-rebase --feature-patches $WORKDIR/feature_patches --base-patches $WORKDIR/base_patches --new-base $NEW_BASE --req-map $REQ_MAP --out $WORKDIR/feature-5.1 --verbose" \
        "AI Direct Rebase"

# Step 5: Validate the results
run_cmd "python -m engine.cli.auto_rebase validate --path $WORKDIR/feature-5.1 --report $WORKDIR/report.html --verbose" \
        "Validate Results"

# Step 6: Finalize with git tag
run_cmd "python -m engine.cli.auto_rebase finalize --path $WORKDIR/feature-5.1 --tag v5.1 --trace $WORKDIR/trace.json --verbose" \
        "Finalize with Git Tag"

# Summary
print_step "AI Direct Rebase Summary"
echo "📁 Workdir: $WORKDIR"
echo "📄 Reports:"
echo "  - HTML Report: $WORKDIR/report.html"
echo "  - JSON Report: $WORKDIR/report.json"
echo "  - Trace: $WORKDIR/trace.json"
echo "  - AI Rebase Results: $WORKDIR/feature-5.1/ai_rebase_results.json"
echo
echo "📦 Generated Patches:"
echo "  - Base patches: $WORKDIR/base_patches/"
echo "  - Feature patches: $WORKDIR/feature_patches/"
echo "  - Combined patches: $WORKDIR/base.patch, $WORKDIR/feature.patch"
echo
echo "🎯 Final Feature (AI Rebased): $WORKDIR/feature-5.1/"
echo
echo "🤖 AI Resolution Features:"
echo "  - Automatic conflict detection between feature and base patches"
echo "  - OpenAI-based conflict resolution (if API key available)"
echo "  - Heuristic fallback for common patterns"
echo "  - Requirement-aware customization application"

# Optional: Open the HTML report
if command -v open &> /dev/null; then
    echo
    read -p "Open HTML report in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$WORKDIR/report.html"
    fi
fi
