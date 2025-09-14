#!/usr/bin/env bash
set -euo pipefail
echo "[build] building feature..."
mkdir -p build
g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp 2>/dev/null || {
  echo "[warn] camera header not available; compiling anyway"
  g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp
}
echo "[build] OK"
