#!/usr/bin/env bash
set -euo pipefail

ART="artifacts/run1"
mkdir -p "$ART"

python -m engine.cli.auto_rebase init --old-base data/sample/base-1.0 --new-base data/sample/base-1.1 --feature data/sample/feature-5.0 --req-map data/sample/requirements_map.yaml --workdir "$ART"
python -m engine.cli.auto_rebase extract-feature --out "$ART/feature_patch"
python -m engine.cli.auto_rebase extract-base --out "$ART/base_patch"
python -m engine.cli.auto_rebase retarget --feature-patch "$ART/feature_patch" --base-patch "$ART/base_patch" --new-base data/sample/base-1.1 --out "$ART/feature-5.1"
python -m engine.cli.auto_rebase validate --path "$ART/feature-5.1" --report "$ART/report.html"
python -m engine.cli.auto_rebase finalize --path "$ART/feature-5.1" --tag v5.1 --trace "$ART/trace.json"

echo "Demo complete. See $ART"

