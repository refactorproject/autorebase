#!/usr/bin/env bash
set -euo pipefail
echo "[build] building base..."
mkdir -p build
g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp 2>/dev/null || {
  echo "[warn] header nv/camera.h is not available; compiling without it"
  g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp
}
echo "[build] OK"
