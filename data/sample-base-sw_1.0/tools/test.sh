#!/usr/bin/env bash
set -euo pipefail
echo "[test] running unit checks..."
python3 tools/run_checks.py
./build/camera || (echo "[test] camera binary failed" && exit 1)
echo "[test] OK"
