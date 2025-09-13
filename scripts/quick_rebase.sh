#!/bin/bash

# Quick AutoRebase Script - Minimal version
# Usage: ./scripts/quick_rebase.sh

set -e

WORKDIR="artifacts/quick_run"
OLD_BASE="data/sample/base-1.0"
NEW_BASE="data/sample/base-1.1"
FEATURE="data/sample/feature-5.0"
REQ_MAP="data/sample/requirements_map.yaml"

echo "🚀 Quick AutoRebase Run"
echo "Workdir: $WORKDIR"
echo

# Clean up previous run
rm -rf "$WORKDIR"

# Run the complete workflow
python -m engine.cli.auto_rebase init --old-base "$OLD_BASE" --new-base "$NEW_BASE" --feature "$FEATURE" --req-map "$REQ_MAP" --workdir "$WORKDIR"
python -m engine.cli.auto_rebase extract-feature --out "$WORKDIR/feature_patch" --git-patch "$WORKDIR/feature.patch" --patch-dir "$WORKDIR/feature_patches"
python -m engine.cli.auto_rebase extract-base --out "$WORKDIR/base_patch" --git-patch "$WORKDIR/base.patch" --patch-dir "$WORKDIR/base_patches"
python -m engine.cli.auto_rebase retarget --feature-patch "$WORKDIR/feature_patch/feature_patch.json" --base-patch "$WORKDIR/base_patch/base_patch.json" --new-base "$NEW_BASE" --out "$WORKDIR/feature-5.1" --patch-dir "$WORKDIR/feature_patches"
python -m engine.cli.auto_rebase validate --path "$WORKDIR/feature-5.1" --report "$WORKDIR/report.html"
python -m engine.cli.auto_rebase finalize --path "$WORKDIR/feature-5.1" --tag v5.1 --trace "$WORKDIR/trace.json"

echo "✅ Quick AutoRebase completed!"
echo "📁 Results in: $WORKDIR"
echo "📄 Report: $WORKDIR/report.html"
