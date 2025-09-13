You are an expert repo bootstrapper. Populate the current repository with a Feature Software tree that represents customizations built on top of the Base SW 1.0 semantics. Include C++, Python, JSON, YAML; make it runnable with `make build` and `make test`. Create one commit tagged feature/v5.0.

## Directory layout (create exactly):
src/
  vision/camera_pipeline.cpp
  common/math/metrics.cpp      # stays in old path (will conflict with base move later)
configs/
  rvc/camera.json
  system/telemetry.yaml
tools/
  build.sh
  test.sh
  run_checks.py
data/
  requirements_map.yaml
Makefile
README.md

### Commit: Feature SW 5.0  (tag: feature/v5.0)

Feature goals:
- Customize camera init (change default width, clamp height, add logging).
- Add a new metric `Median` in C++.
- Tighten telemetry interval and add tags.
- Increase timeout & change exposure mode, add log_level in JSON.
- Keep everything runnable.

Create these files:

# src/vision/camera_pipeline.cpp
#include <iostream>
#include <vector>
#include <numeric>
#include "nv/camera.h"  // still builds without the header present
static int NvOldAPI(int width, int height) { return width > 0 && height > 0 ? 0 : -1; }
static int clampH(int h) { return h < 480 ? 480 : h; }
int InitRvcCamera(int width, int height) {
    // FEATURE: default 1344x720 for RVC, clamp height
    if (width == 0) width = 1344;
    if (height == 0) height = 720;
    height = clampH(height);
    std::cout << "[feature-5.0] init camera " << width << "x" << height << std::endl;
    return NvOldAPI(width, height);
}
int main() {
    int rc = InitRvcCamera(0, 0);
    std::cout << "[feature-5.0] InitRvcCamera -> " << rc << std::endl;
    return rc == 0 ? 0 : 1;
}

# src/common/math/metrics.cpp
#include <algorithm>
#include <vector>
#include <numeric>
// FEATURE: add Median
double Mean(const std::vector<double>& xs) {
    double s = 0.0; for (double v : xs) s += v; return xs.empty()?0.0:s/xs.size();
}
double Clamp(double v, double lo, double hi) { return std::max(lo, std::min(v, hi)); }
double Median(std::vector<double> xs) {
    if (xs.empty()) return 0.0;
    std::sort(xs.begin(), xs.end());
    size_t n = xs.size();
    if (n % 2 == 1) return xs[n/2];
    return 0.5*(xs[n/2 - 1] + xs[n/2]);
}

# configs/rvc/camera.json
{
  "camera": {
    "rvc": {
      "timeout_ms": 800,
      "exposure": "manual",
      "log_level": "info"
    }
  }
}

# configs/system/telemetry.yaml
telemetry:
  enabled: true
  upload_interval_sec: 30
  tags: ["rvc", "debug"]

# tools/build.sh
#!/usr/bin/env bash
set -euo pipefail
echo "[build] building feature..."
mkdir -p build
g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp 2>/dev/null || {
  echo "[warn] camera header not available; compiling anyway"
  g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp
}
echo "[build] OK"

# tools/test.sh
#!/usr/bin/env bash
set -euo pipefail
echo "[test] running feature checks..."
python3 tools/run_checks.py
./build/camera || (echo "[test] camera binary failed" && exit 1)
echo "[test] OK"

# tools/run_checks.py
#!/usr/bin/env python3
import json, sys, pathlib
import yaml
root = pathlib.Path(__file__).resolve().parents[1]
camera_json = json.loads((root/"configs/rvc/camera.json").read_text())
telemetry_yaml = yaml.safe_load((root/"configs/system/telemetry.yaml").read_text())
assert camera_json["camera"]["rvc"]["timeout_ms"] == 800
assert camera_json["camera"]["rvc"]["exposure"] == "manual"
assert telemetry_yaml["telemetry"]["upload_interval_sec"] == 30
assert "debug" in telemetry_yaml["telemetry"]["tags"]
print("[checks] feature-5.0 configs look good")

# data/requirements_map.yaml
- path_glob: "src/vision/**"
  req_ids: ["REQ-RVC-201","REQ-RVC-318"]
- path_glob: "configs/rvc/*.json"
  req_ids: ["REQ-RVC-411"]
- path_glob: "services/*.service"
  req_ids: ["REQ-OPS-021"]

# Makefile
SHELL:=/bin/bash
.PHONY: build test
build:
\tbash tools/build.sh
test: build
\tbash tools/test.sh

# README.md
# Feature SW 5.0
Feature customizations built conceptually on Base 1.0:
- wider default, height clamp, logging in camera init
- Median() metric
- tighter telemetry interval with tags
- JSON tweaks for RVC (timeout, exposure, log_level)

Make all scripts executable:
- chmod +x tools/build.sh tools/test.sh tools/run_checks.py

Git commit & tag:
- git add -A
- git commit -m "seed: Feature SW 5.0 over Base 1.0 semantics"
- git tag -a feature/v5.0 -m "Feature SW 5.0"