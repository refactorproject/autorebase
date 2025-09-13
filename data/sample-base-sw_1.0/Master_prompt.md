You are an expert repo bootstrapper. Populate the current repository with a minimal but runnable Base Software tree that includes C++, Python, JSON, and YAML. Then create two commits, tagged as base/v1.0 and base/v1.1. Ensure code runs and tests pass on a typical Linux/macOS dev box with git, bash, python3, and g++.

## Goals
- Provide realistic content that downstream feature repos can customize.
- Make artifacts verifiable via `make build` and `make test`.
- Use simple, standard tooling only (bash, make, python3, g++).

## Directory layout (create exactly):
src/
  vision/camera_pipeline.cpp
  shared/metrics/            # will be used in v1.1; initially empty in v1.0
  common/math/metrics.cpp    # exists in v1.0, moved in v1.1
configs/
  rvc/camera.json
  system/telemetry.yaml
tools/
  build.sh
  test.sh
  run_checks.py
Makefile
README.md

### Commit A: Base SW 1.0  (tag: base/v1.0)

1) Files & contents:

# src/vision/camera_pipeline.cpp
#include <iostream>
#include <vector>
#include <numeric>
#include "nv/camera.h"  // header name only; compile won't include it
// Simulate an old vendor API
static int NvOldAPI(int width, int height) {
    return width > 0 && height > 0 ? 0 : -1;
}
// Classic init: default 1280x720 if missing
int InitRvcCamera(int width, int height) {
    if (width == 0) width = 1280;
    if (height == 0) height = 720;
    return NvOldAPI(width, height);
}
// Small C++ demo main so we can compile/run something
int main() {
    int rc = InitRvcCamera(0, 0);
    std::cout << "[base-1.0] InitRvcCamera -> " << rc << std::endl;
    return rc == 0 ? 0 : 1;
}

# src/common/math/metrics.cpp
#include <algorithm>
#include <vector>
double Mean(const std::vector<double>& xs) {
    double s = 0.0; for (double v : xs) s += v; return xs.empty()?0.0:s/xs.size();
}
double Clamp(double v, double lo, double hi) {
    return std::max(lo, std::min(v, hi));
}

# configs/rvc/camera.json
{
  "camera": {
    "rvc": {
      "timeout_ms": 500,
      "exposure": "auto"
    }
  }
}

# configs/system/telemetry.yaml
telemetry:
  enabled: true
  upload_interval_sec: 60

# tools/build.sh
#!/usr/bin/env bash
set -euo pipefail
echo "[build] building base..."
mkdir -p build
g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp 2>/dev/null || {
  echo "[warn] header nv/camera.h is not available; compiling without it"
  g++ -std=c++17 -O2 -o build/camera src/vision/camera_pipeline.cpp
}
echo "[build] OK"

# tools/test.sh
#!/usr/bin/env bash
set -euo pipefail
echo "[test] running unit checks..."
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

assert camera_json["camera"]["rvc"]["timeout_ms"] == 500
assert telemetry_yaml["telemetry"]["upload_interval_sec"] == 60
print("[checks] base-1.0 configs look good")

# Makefile
SHELL:=/bin/bash
.PHONY: build test
build:
\tbash tools/build.sh
test: build
\tbash tools/test.sh

# README.md
# Base SW
This repository contains a tiny, runnable base with C++ (a small camera init), Python checks, and JSON/YAML configs.

2) Make scripts executable:
- chmod +x tools/build.sh tools/test.sh tools/run_checks.py

3) Git commit & tag:
- git add -A
- git commit -m "seed: Base SW 1.0"
- git tag -a base/v1.0 -m "Base SW 1.0"

### Commit B: Base SW 1.1  (tag: base/v1.1)

Upstream changes that are logical but induce interesting merges later:
- Rename old vendor API to `NvNewAPI`.
- Add a new context parameter `const NvCtx& ctx` to `InitRvcCamera`.
- Move `metrics.cpp` from `src/common/math/` to `src/shared/metrics/`.
- Change JSON path from `camera.rvc` → `camera.rvcs` and tweak defaults.
- Rename YAML field `upload_interval_sec` → `interval_seconds` and add `max_payload_kb`.

Apply the following edits:

# src/vision/camera_pipeline.cpp  (overwrite)
#include <iostream>
#include <vector>
#include <numeric>
#include "nv/camera_utils.h" // upstream header name
static int NvNewAPI(int width, int height) { return width > 0 && height > 0 ? 0 : -2; }
struct NvCtx { int reserved{0}; };
int InitRvcCamera(const NvCtx& ctx, int width, int height) {
    if (width == 0) width = 1280;
    if (height == 0) height = 720;
    (void)ctx;
    return NvNewAPI(width, height);
}
int main() {
    NvCtx ctx{};
    int rc = InitRvcCamera(ctx, 0, 0);
    std::cout << "[base-1.1] InitRvcCamera -> " << rc << std::endl;
    return rc == 0 ? 0 : 1;
}

# MOVE: src/common/math/metrics.cpp → src/shared/metrics/metrics.cpp
# (same content, but we can add a tiny constexpr to show drift)
#include <algorithm>
#include <vector>
constexpr double mean0 = 0.0;
double Mean(const std::vector<double>& xs) {
    double s = 0.0; for (double v : xs) s += v; return xs.empty()?mean0:s/xs.size();
}
double Clamp(double v, double lo, double hi) { return std::max(lo, std::min(v, hi)); }

# configs/rvc/camera.json  (overwrite)
{
  "camera": {
    "rvcs": {
      "timeout_ms": 500,
      "exposure": "auto-v2",
      "hdr": false
    }
  }
}

# configs/system/telemetry.yaml  (overwrite)
telemetry:
  enabled: true
  interval_seconds: 60
  max_payload_kb: 256

# tools/run_checks.py  (append extra assertions at end)
# Ensure new keys are present for base-1.1
camera = camera_json["camera"].get("rvcs") or {}
assert "hdr" in camera
print("[checks] base-1.1 config keys OK")

Re-run chmod (if needed), then:
- git add -A
- git commit -m "upstream: Base SW 1.1 changes"
- git tag -a base/v1.1 -m "Base SW 1.1"

Finally, print a short summary of files and tags created.